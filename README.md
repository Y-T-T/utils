# Utils Toolbox

A collection of utility scripts, primarily for automation, system administration, and security tasks.

---

## Structure

This repository is organized by technology/language:

<!-- * `/python`: Cross-platform Python scripts (automation, data processing). -->
* `/shell`: Bash/Zsh scripts for Linux / macOS environments.
<!-- * `/powershell`: PowerShell scripts for Windows environments. -->

---

<!-- ## 🐍 Python Scripts (`/python`)

Cross-platform scripts for various tasks.

* **Dependencies:** `pip install -r python/requirements.txt`

| Script | Description | Usage |
| :--- | :--- | :--- |
| `data_processor.py` | (Example) Cleans or transforms CSV data. | `python python/data_processor.py <input> <output>` |
| `check_ssl.py` | (Example) Checks the SSL certificate expiry date for a domain. | `python python/check_ssl.py example.com` |
| | | | -->

## 🐧 Shell Scripts (`/shell`)

Shell scripts primarily intended for Linux / macOS environments.

| Script | Description | Usage |
| :--- | :--- | :--- |
| `shred-dir.sh` | **Securely and recursively deletes** a directory and all its contents, addressing the limitation of the standard `shred` utility. | `sudo ./shell/shred-dir.sh /path/to/directory` |
<!-- | `setup_env.sh` | (Example) Sets up a new Linux development environment automatically. | `./shell/setup_env.sh` | -->
| | | |

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
    git clone [https://github.com/Y-T-T/utils.git](https://github.com/Y-T-T/utils.git)
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