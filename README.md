# Utils Toolbox

A collection of utility scripts, primarily for automation or security tasks.

---

## Structure

This repository is organized by purpose and domain:

* **`/automation`**: System automation and workflow extractors.
* **`/env-setup`**: Development environment setup scripts.
* **`/sbom`**: Software Bill of Materials (SBOM) and vulnerability scanning tools.
* **`/security`**: Security, penetration testing, and security-related tools.

---

## How to Use

1.  Clone this repository:
    ```bash
    git clone https://github.com/Y-T-T/utils.git
    cd utils
    ```

2.  Navigate to the directory of interest (`security/`, `env-setup/`, etc.).

3.  Always review the script's source code before executing it.

4.  (Shell/PS) Grant execution permissions if necessary:
    ```bash
    # Linux/macOS
    chmod +x env-setup/script_name.sh

    # Windows (You may need to bypass the execution policy for PowerShell scripts)
    Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
    ```

## License

This project is licensed under the [MIT License](https://github.com/Y-T-T/utils/blob/main/LICENSE).