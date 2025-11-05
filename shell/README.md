# Shell Scripts

Bash/Zsh scripts primarily intended for Linux / macOS environments.

---

## Commands (`/commands`)

General-purpose command-line utilities.

| Script | Description | Usage |
| :--- | :--- | :--- |
| `shred-dir` | **Securely and recursively deletes** a directory and all its contents using multi-pass overwriting. Addresses the limitation of the standard `shred` utility which cannot handle directories. | `sudo ./shell/commands/shred-dir /path/to/directory` |
| | | |

---

## Setup Scripts (`/setup`)

Environment setup and installation automation.

| Script | Description | Usage |
| :--- | :--- | :--- |
| `pyenv_install_python_with_tkinter.sh` | Installs a specific Python version using pyenv with tkinter support. Automatically detects and installs required dependencies on macOS (via Homebrew) and major Linux distributions (Debian/Ubuntu, Fedora, CentOS, Arch). | `./shell/setup/pyenv_install_python_with_tkinter.sh <version>` |
| | | |

---

## Usage Notes

- Grant execution permissions before running:
  ```bash
  chmod +x shell/script_name.sh
  ```
- Some scripts require `sudo` privileges
- Always review script source code before execution

---

[← Back to main README](../README.md)
