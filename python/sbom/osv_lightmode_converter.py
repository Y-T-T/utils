import sys
import os

def convert_osv_report(input_path):
    if not os.path.exists(input_path):
        print(f"[-] Cannot find file: {input_path}")
        return

    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)

    output_filename = f"light_{base_name}"
    output_path = os.path.join(dir_name, output_filename)

    light_mode_style = """
    <style>
        body {
        margin: 0;
        padding: 0;
        background: #ffffff !important;
        color: #1a1a1a !important;
        overflow-y: scroll;
        font-family: "Overpass Mono", monospace;
        font-size: 12pt;
        font-weight: 100;
        min-width: fit-content;
        }

        .container {
        max-width: 1400px;
        margin: auto;
        padding: 20px;
        border-radius: 4px;
        background: #ffffff !important;
        box-shadow: 0 0 5px rgba(0, 0, 0, 0.1) !important;
        }

        h1, h2, h3, .package-detail-title {
        color: #000000 !important;
        }

        a {
        color: #0056b3 !important;
        text-decoration: underline;
        }

        .vuln-table {
        color: #212529 !important;
        }

        .vuln-table th {
        border-bottom: 1px solid #dee2e6 !important;
        color: #000 !important;
        }

        .table-tr:hover {
        background-color: #f8f9fa !important;
        }

        .table-tr-details > td {
        border-bottom: 1px solid #eeeeee !important;
        }

        .critical {
        background-color: #ad0300 !important;
        color: #ffffff !important;
        }

        .high {
        background-color: #ffa500 !important;
        color: #ffffff !important;
        }

        .medium {
        background-color: #ffd700 !important;
        color: #292929 !important;
        }

        .low {
        background-color: #53aa33 !important;
        color: #ffffff !important;
        }

        .package-details {
        background: #fdfdfd !important;
        border: 1px solid #ddd !important;
        color: #333 !important;
        }

        .search-box {
        border: 1px solid #cccccc !important;
        background-color: #fcfcfc !important;
        }

        .search-box input[type="text"] {
        color: #000000 !important;
        }

        .filter {
        border: 1px solid #cccccc !important;
        color: #333 !important;
        }

        #header-left .vl {
        border-left: 2px solid #333 !important;
        }

        #tab-switch {
        border-bottom: 1px solid #dee2e6 !important;
        }

        .tab-button-text-container p {
        color: #6c757d !important;
        }

        .tab-button-text-container:hover p, 
        .tab-switch-button-selected p {
        color: #000000 !important;
        }

        .uncalled-text {
        color: #666666 !important;
        }

        .filter {
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #cccccc !important;
        }

        .filter-option-container {
        background-color: #ffffff !important;
        color: #333333 !important;
        border: 1px solid #dddddd !important;
        box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.1) !important;
        }

        .filter-option {
        background-color: #ffffff !important;
        color: #333333 !important;
        border-bottom: 1px dotted #eeeeee !important;
        }

        .filter-option:hover {
        background-color: #f5f5f5 !important;
        }

        .filter-option label, 
        .filter-selected {
        color: #333333 !important;
        }

        .filter-icon i {
        color: #666666 !important;
        }

        .no-fix {
        background-color: #f8f9fa !important;
        color: #6c757d !important;
        border: 1px solid #dee2e6 !important;
        }

        .has-fix {
        background-color: #e8f5e9 !important;
        color: #2e7d32 !important;
        border: 1px solid #c8e6c9 !important;
        }

        .fixable-tag {
        text-shadow: none !important;
        font-weight: 500 !important;
        }

        .open-in-tab-tag {
        border: 1px solid #cccccc !important;
        color: #5f6368 !important;
        background-color: #f8f9fa !important;
        }

        .table-tr:hover .open-in-tab-tag {
        border-color: #007bff !important;
        color: #007bff !important;
        background-color: #e7f3ff !important;
        }

        .open-in-tab-cell {
        color: #5f6368 !important;
        }

        iframe {
        filter: invert(1) hue-rotate(180deg) brightness(1.2) contrast(1.2);
        background-color: white;
        border: 1px solid #ddd !important;
        border-radius: 8px;
        }

        .iframe-spinner {
        border: 5px solid #333 !important;
        border-bottom-color: transparent !important;
        }
    </style>
    """

    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    # Inject style: place it before </head> to ensure priority over existing styles
    if "</head>" in html_content:
        new_content = html_content.replace("</head>", f"{light_mode_style}\n</head>")
    else:
        # If there's no head tag, insert the style at the beginning
        new_content = light_mode_style + html_content

    # Replace logo image reference
    new_content = new_content.replace("osv-scanner-OSV-logo-darkmode.png", "osv-scanner-OSV-logo-lightmode.png")

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_content)

    print(f"[+] Conversion complete! Generated: {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python osv_lightmode_transfer.py <report.html>")
    else:
        convert_osv_report(sys.argv[1])
