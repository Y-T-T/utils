# Python Scripts

Cross-platform Python scripts for automation, security, and various tasks.

## Installation

Install required dependencies:
```bash
pip install -r requirements.txt
```

---

## Attack Scripts (`/attack`)

Tools for penetration testing and security research.

| Script | Description | Usage |
| :--- | :--- | :--- |
| `ps1_encoder.py` | Encodes/decodes PowerShell scripts to Base64 format for use with `-EncodedCommand` parameter. | `python attack/ps1_encoder.py <script.ps1>` |
| `ps1_reversed_shell.py` | Generates PowerShell reverse shell payloads in both `.ps1` and Base64-encoded formats. | `python attack/ps1_reversed_shell.py <attacker_ip> <port>` |
| | | |

---

## SBOM (`/sbom`)

Tools for downloading offline OSV vulnerability databases.

| Script | Description | Usage |
| :--- | :--- | :--- |
| `update_osv_database.py` | Downloads the latest OSV offline vulnerability database to the path specified by `OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY` (defaults to `osv_offline_db`). | `python sbom/update_osv_database.py` |
| `osv_report_converter.py` | Converts OSV HTML reports into a cleaner format suitable for PDF conversion, adding timestamps and removing unnecessary elements. | `python sbom/osv_report_converter.py <input_report.html> -s <sbom_source_dir>` |

[← Back to main README](../README.md)
