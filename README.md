# Utils Toolbox

A collection of utility scripts, primarily for automation, system administration, and security tasks.

---

## Structure

This repository is organized by languages/categories:

* `/python`: Cross-platform Python scripts.
* `/shell`: Bash/Zsh scripts for Linux / macOS environments.
<!-- * `/powershell`: PowerShell scripts for Windows environments. -->

---

## 🐍 Python Scripts (`/python`)

Cross-platform scripts for automation, security, and various tasks.

**Featured Scripts:**
- **`ps1_reversed_shell.py`** - Generates PowerShell reverse shell payloads
- **`ps1_encoder.py`** - Encodes/decodes PowerShell scripts to Base64

📄 **[View all Python scripts →](python/README.md)**

---

## 🐧 Shell Scripts (`/shell`)

Shell scripts primarily intended for Linux / macOS environments.

**Featured Scripts:**
- **`shred-dir`** - Securely and recursively deletes directories with multi-pass overwriting
- **`pyenv_install_python_with_tkinter.sh`** - Installs Python via pyenv with tkinter support

📄 **[View all Shell scripts →](shell/README.md)**

<!-- ## 🪟 PowerShell Scripts (`/powershell`)

PowerShell scripts for Windows system administration.

| Script | Description | Usage |
| :--- | :--- | :--- |
| `clear_cache.ps1` | (Example) Clears various system caches on Windows. | `Powershell.exe -ExecutionPolicy Bypass -File .powershellclear_cache.ps1` |
| | | | -->

---

## How to Use

1.  Clone this repository:
    ```bash
    git clone https://github.com/Y-T-T/utils.git
    cd utils
    ```

2.  Navigate to the directory of interest (`python/`, `shell/`, etc.).

3.  (Recommended) Always review the script's source code before executing it.

4.  (Shell/PS) Grant execution permissions if necessary:
    ```bash
    # Linux/macOS
    chmod +x shell/script_name.sh

    # Windows (You may need to set the execution policy)
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```

## License

This project is licensed under the [MIT License](https://github.com/Y-T-T/utils/blob/main/LICENSE).