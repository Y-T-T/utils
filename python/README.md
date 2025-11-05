# Python Scripts

Cross-platform Python scripts for automation, security, and various tasks.

## Installation

Install required dependencies:
```bash
pip install -r requirements.txt
```

---

## Attack / Security Scripts (`/attack`)

Tools for penetration testing and security research.

| Script | Description | Usage |
| :--- | :--- | :--- |
| `ps1_encoder.py` | Encodes/decodes PowerShell scripts to Base64 format for use with `-EncodedCommand` parameter. | `python python/attack/ps1_encoder.py <script.ps1>` |
| `ps1_reversed_shell.py` | Generates PowerShell reverse shell payloads in both `.ps1` and Base64-encoded formats. | `python python/attack/ps1_reversed_shell.py <attacker_ip> <port>` |
| | | |

---

## Usage Notes

- **Always review script source code** before execution
- These tools are intended for **authorized security testing only**
- Ensure you have proper permissions before using any security-related scripts

---

[← Back to main README](../README.md)
