package main

import (
	"bufio"
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"strings"
	"syscall"
	"time"
)

// -- Configuration --
const (
	HostIP   			= "127.0.0.1" // Change if Ollama is running on a different host
	OllamaURL 			= "http://" + HostIP + ":11434/v1/chat/completions"
	ModelName 			= "qwen3"
	Temperature 		= 0.5
	LLMTimeoutSeconds 	= 30
	LengthThreshold 	= 20 // Max messages before summarization
	MemoryLimit			= 5 // Max number of past interactions to keep in memory (after summarization
)

const SystemPrompt = `
You are a security assistant. You MUST respond in pure JSON format only. Do not add markdown formatting or extra text.
- You have passwordless sudo privileges. If a command requires root access, prefix it with 'sudo' (e.g., 'sudo nmap -sS 127.0.0.1').
- If you need to run a shell command, respond with exactly: {"command": "your_command"}
- If you have the final answer, respond with exactly: {"response": "your_answer"}
- When checking system resources, ALWAYS use batch-compatible commands. For example, use 'ps aux --sort=-%%cpu | head -n 10' instead of 'top'.
`

const SummarizerPrompt = `
You are a context manager. Summarize the following security investigation history. 
Identify: 
1. The original goal.
2. Actions taken and their key outcomes.
3. Current state of the system.
Keep it technical and concise.
`

// Data structure for JSON
type Message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type ChatRequest struct {
	Model       string    `json:"model"`
	Messages    []Message `json:"messages"`
	Stream	  	bool      `json:"stream"`
	Temperature float64   `json:"temperature"`
}

type ChatResponse struct {
    Choices []struct {
        Message Message `json:"message"`
    } `json:"choices"`
}

type AgentAction struct {
	Command  string `json:"command,omitempty"`
	Response string `json:"response,omitempty"`
}

func askLLM(history []Message) (string, error) {
	client := &http.Client{Timeout: time.Duration(LLMTimeoutSeconds) * time.Second}
	reqBody, _ := json.Marshal(ChatRequest{
		Model:       	ModelName,
		Messages:    	history,
		Stream:			false,
		Temperature: 	Temperature,
	})

	resp, err := client.Post(OllamaURL, "application/json", bytes.NewBuffer(reqBody))
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var chatResp ChatResponse
	if err = json.NewDecoder(resp.Body).Decode(&chatResp); err != nil {
		return "", err
	}
	if len(chatResp.Choices) == 0 {
		return "", fmt.Errorf("no response from LLM")
	}
	return chatResp.Choices[0].Message.Content, nil
}

func executeCmd(command string) (string, error) {
	fmt.Printf("\n[Agent] Agent wants to execute: %s\n", command)

	// Confirm with user before executing, comment out if you want to allow all commands without confirmation
	fmt.Print("[?] Allow this command to run? (y/n): ")
	reader := bufio.NewReader(os.Stdin)
	confirm, _ := reader.ReadString('\n')
	if strings.TrimSpace(confirm) != "y" {
		return "Command execution aborted by user.", nil
	}

	fmt.Printf("[Agent] Executing... (Press Ctrl+C to abort)\n")
	cmd := exec.Command("bash", "-c", command)
	cmd.SysProcAttr = &syscall.SysProcAttr{Setpgid: true}

	var fullOutput strings.Builder
	multi := io.MultiWriter(os.Stdout, &fullOutput)
	cmd.Stdout = multi
	cmd.Stderr = multi

	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, os.Interrupt)

	if err := cmd.Start(); err != nil {
		return fmt.Sprintf("Error starting command: %v", err), err	
	}

	done := make(chan error, 1)
	go func() {
		done <- cmd.Wait()
	}()

	select {
		case <-sigChan:
			pgid, _ := syscall.Getpgid(cmd.Process.Pid)
			syscall.Kill(-pgid, syscall.SIGKILL)
			fmt.Println("\n[!] Ctrl+C detected. Aborting command...")
			return "ERROR: Command was MANUALLY ABORTED by user.", nil
		case err := <-done:
			signal.Stop(sigChan)
			output := fullOutput.String()
			if err != nil {
				return output + "\n(Command execution error: " + err.Error() + ")", err
			}
			return output, nil
	}
}

func summarizeHistory(history []Message) ([]Message, error) {
	
	if len(history) <= LengthThreshold {
		return history, nil // No need to summarize if history is short
	}

	fmt.Println("[Agent] Optimizing history (Summarizing)...")

	systemMsg := history[0] // Keep the original system prompt
	toSummarize := history[1: len(history) - MemoryLimit] // Exclude system prompt for summarization
	recentMessages := history[len(history) - MemoryLimit:] // Keep the last MemoryLimit messages for context

	var summaryContent string
	for _, msg := range toSummarize {
		summaryContent += fmt.Sprintf("%s: %s\n", msg.Role, msg.Content)
	}

	summaryReq := []Message{
		{Role: "system", Content: SummarizerPrompt},
		{Role: "user", Content: "Please summarize this history:\n" + summaryContent},
	}

	summaryText, err := askLLM(summaryReq)
	if err != nil {
		return history, err // Return original history if summarization fails
	}

	fmt.Printf("[DEBUG] Summary:\n%s\n", summaryText)

	newHistory := []Message{
		systemMsg,
		{Role: "assistant", Content: "Summary of previous interactions:\n" + summaryText},
	}

	newHistory = append(newHistory, recentMessages...)
	return newHistory, nil
}

func main() {
	fmt.Println("=== ReAct Agent Started (Type 'exit' to quit) ===")
	history := []Message{
		{Role: "system", Content: SystemPrompt},
	}
	reader := bufio.NewReader(os.Stdin)

	for {
		fmt.Println("\n[Agent] What task would you like to perform?")
		userInput, _ := reader.ReadString('\n')
		userInput = strings.TrimSpace(userInput)

		if userInput == "exit" {
			fmt.Println("Exiting agent. Goodbye!")
			break
		}

		history = append(history, Message{Role: "user", Content: userInput})

		for {
			fmt.Println("\n[Agent] Thinking...")
			var err error
			history, err = summarizeHistory(history)
			if err != nil {
				fmt.Printf("[!] Summarization failed: %v\n", err)
				fmt.Println("[!] Continuing with full history (may cause token issues)...")
			}

			rawResp, err := askLLM(history)
			if err != nil {
				fmt.Printf("[!] LLM Error: %v\n", err)
				fmt.Println("[!] Retrying...")
				continue
			}

			history = append(history, Message{Role: "assistant", Content: rawResp})

			cleanJSON := strings.Trim(rawResp, "`\n") // Remove backticks if present
			cleanJSON = strings.TrimPrefix(cleanJSON, "json")

			var action AgentAction
			if err := json.Unmarshal([]byte(cleanJSON), &action); err != nil {
				fmt.Printf("[!] JSON Parse Error: %v\n", err)
				history = append(history, Message{Role: "user", Content: "Invalid JSON. Fix it."})	
			}
			if action.Command != "" {
				result, _ := executeCmd(action.Command)
				feedback := fmt.Sprintf("The command returned:\n%s\nAnalyze and provide next command or final response.", result)
				history = append(history, Message{Role: "user", Content: feedback})
			} else if action.Response != "" {
				fmt.Printf("\n[Agent]: %s\n", action.Response)
				break
			}
		}
	}

}