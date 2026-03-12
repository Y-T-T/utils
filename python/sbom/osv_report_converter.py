"""
Converts OSV HTML reports (Default dark mode) to a light mode version and generates a PDF.
"""

import os
import asyncio
import argparse
from datetime import datetime
from pathlib import Path
from copy import deepcopy
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

async def html_to_pdf(html_path, pdf_path):
    """
    Uses Playwright to render the HTML and save it as a PDF. 
    This ensures that all CSS styles are applied correctly in the output.
    """
    async with async_playwright() as p:
        # Added standard args for better headless rendering
        browser = await p.chromium.launch(args=["--font-render-hinting=none", "--disable-web-security"])
        context = await browser.new_context(viewport={"width": 1400, "height": 900})
        page = await context.new_page()

        # Load the HTML file using a file URL
        absolute_path = f"file://{Path(html_path).resolve()}"
        await page.goto(absolute_path, wait_until='networkidle')
        
        # Wait to ensure Google Fonts are downloaded and applied
        await page.evaluate_handle('document.fonts.ready')

        # Extra buffer time for Chromium to render complex tables
        await asyncio.sleep(1)
        
        # Generate PDF with appropriate settings for better styling
        await page.pdf(
            path=pdf_path,
            format="A4",
            scale=0.75, # Adjust scale for better fit and readability
            display_header_footer=False,
            print_background=True, # Ensure background colors and images are included
            margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"}
        )
        await browser.close()

def get_osv_db_mtime():
    """
    Retrieves the latest modification time of the OSV offline database by checking all "all.zip" files.
    """
    # Get the cache directory from environment variables
    cache_dir = os.environ.get("OSV_SCANNER_LOCAL_DB_CACHE_DIRECTORY")
    if not cache_dir:
        return None
    
    cache_path = Path(cache_dir)
    # Check if the cache directory exists
    zip_files = list(cache_path.rglob("all.zip"))
    
    if not zip_files:
        return None
        
    # Find the latest modification time among all files
    latest_mtime = max(f.stat().st_mtime for f in zip_files)
    
    # Format the timestamp into a human-readable format
    return datetime.fromtimestamp(latest_mtime).strftime("%Y-%m-%d %H:%M")

def convert_osv_report(input_path, sbom_dir=None, generate_pdf=False):
    input_path = Path(input_path) # Convert input_path to a Path object
    if not input_path.exists():
        print(f"[-] Cannot find file: {input_path}")
        return

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')
    except Exception as e:
        print(f"[-] Failed to read or parse the HTML file: {e}")
        return

    # Injecting Google Fonts via <link> is more reliable for headless PDF generation than @import
    light_mode_font_injection = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Overpass+Mono:wght@300;400;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    """

    light_mode_style_f = """
    <style>
        /* Global override to ensure NO default browser fonts leak into the PDF */
        *, *::before, *::after, body, html, table, td, th, pre, code, div, span, p, a, input:not(i) {
            font-family: 'Overpass Mono', monospace !important;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }

        .material-icons {
            font-family: 'Material Icons' !important;
        }

        body {
            margin: 0;
            padding: 0;
            background: #ffffff !important;
            color: #1a1a1a !important;
            overflow-y: scroll;
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

        h1, h2, h3, .package-detail-title { color: #000000 !important; }
        a { color: #0056b3 !important; text-decoration: underline; }
        
        .vuln-table { color: #212529 !important; }
        .vuln-table th { border-bottom: 1px solid #dee2e6 !important; color: #000 !important; }
        .table-tr:hover { background-color: #f8f9fa !important; }
        .table-tr-details > td { border-bottom: 1px solid #eeeeee !important; }

        .critical { background-color: #ad0300 !important; color: #ffffff !important; }
        .high { background-color: #ffa500 !important; color: #ffffff !important; }
        .medium { background-color: #ffd700 !important; color: #292929 !important; }
        .low { background-color: #53aa33 !important; color: #292929 !important; }
        .unknown { background-color: #80868d !important; color: #ffffff !important; }

        .package-details {
            background: #fdfdfd !important;
            border: 1px solid #ddd !important;
            color: #333 !important;
            max-height: none !important;
            height: auto !important;
            overflow: visible !important;
        }

        .search-box { border: 1px solid #cccccc !important; background-color: #fcfcfc !important; }
        .search-box input[type="text"] { color: #000000 !important; }
        .filter { border: 1px solid #cccccc !important; color: #33 !important; }
        #header-left .vl { border-left: 2px solid #333 !important; }
        #tab-switch { border-bottom: 1px solid #dee2e6 !important; }
        .tab-button-text-container p { color: #6c757d !important; }
        
        .tab-button-text-container:hover p, 
        .tab-switch-button-selected p { color: #000000 !important; }
        .uncalled-text { color: #666666 !important; }

        .filter { background-color: #ffffff !important; color: #333333 !important; border: 1px solid #cccccc !important; }
        .filter-option-container { background-color: #ffffff !important; color: #333333 !important; border: 1px solid #dddddd !important; box-shadow: 0px 8px 16px 0px rgba(0, 0, 0, 0.1) !important; }
        .filter-option { background-color: #ffffff !important; color: #333333 !important; border-bottom: 1px dotted #eeeeee !important; }
        .filter-option:hover { background-color: #f5f5f5 !important; }
        .filter-option label, .filter-selected { color: #333333 !important; }
        .filter-icon i { color: #666666 !important; }

        .no-fix { background-color: #f8f9fa !important; color: #6c757d !important; border: 1px solid #dee2e6 !important; }
        .has-fix { background-color: #e8f5e9 !important; color: #2e7d32 !important; border: 1px solid #c8e6c9 !important; }
        .fixable-tag { text-shadow: none !important; font-weight: 500 !important; }

        .open-in-tab-tag { border: 1px solid #cccccc !important; color: #5f6368 !important; background-color: #f8f9fa !important; }
        .table-tr:hover .open-in-tab-tag { border-color: #007bff !important; color: #007bff !important; background-color: #e7f3ff !important; }
        .open-in-tab-cell { color: #5f6368 !important; }

        iframe {
            filter: invert(1) hue-rotate(180deg) brightness(1.2) contrast(1.2);
            background-color: white;
            border: 1px solid #ddd !important;
            border-radius: 8px;
        }
        .iframe-spinner { border: 5px solid #333 !important; border-bottom-color: transparent !important; }

        @media print {
            * {
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
            }
            body, .container {
                width: 100% !important;
                min-width: 0 !important;
                max-width: none !important;
                overflow: visible !important;
            }
            tr { page-break-inside: avoid !important; }
        }

    """
    light_mode_style_b_html = """
        .passed { display: block !important; }
    </style>
    """

    light_mode_style_b_pdf = """
        .hide-block { display: block !important; }
    </style>
    """

    # Update header to include last updated timestamp and remove feedback link
    header_right = soup.find(id="header-right")
    if header_right:
        header_right.clear() # Clear existing feedback link instead of decomposing
        
        # Get current execution time
        sync_time = get_osv_db_mtime() + " (UTC+8)" or "Unknown (Offline)"
        
        # Create a professional timestamp element
        timestamp_tag = soup.new_tag("div", attrs={
            "style": "text-align: right; font-size: 10pt; color: #5f6368; font-weight: 400;"
        })
        timestamp_tag.string = f"OSV Database Last Updated: {sync_time}"
        header_right.append(timestamp_tag)

    # Find the "Passed (No Known Vulnerabilities)" section and inject SBOM sources if provided
    if sbom_dir:
        try:
            src = Path(sbom_dir)

            existing_sources = {
                Path(span.get_text(strip=True).replace("sbom:", "")).resolve() 
                for span in soup.find_all("span", class_="source-path")
            }

            sbom_patterns = [
                "*.spdx.json", "*.spdx", "*.spdx.yml", "*.spdx.rdf", "*.spdx.rdf.xml", # SPDX
                "bom.json", "*.cdx.json", "bom.xml", "*.cdx.xml"                       # CycloneDX
            ]

            vuln_tab = soup.find(id="vuln-tab")
            if not vuln_tab:
                new_vuln_tab = soup.new_tag("div", id="vuln-tab", attrs={"class": "view-tab"})
                global_tab = soup.find(id="summary-tab")
                if global_tab:
                    global_tab.append(new_vuln_tab)
                elif soup.body:
                    soup.body.append(new_vuln_tab)
                vuln_tab = new_vuln_tab

            if vuln_tab:
                passed_container = None
                sources_wrapper = None
                processed_files = set()

                for pattern in sbom_patterns:
                    for sbom_file in src.rglob(pattern):
                        abs_sbom = sbom_file.resolve()
                        
                        if abs_sbom not in existing_sources and abs_sbom not in processed_files:
                            processed_files.add(abs_sbom)

                            if passed_container is None:
                                passed_container = soup.new_tag("div", attrs={"class": "ecosystem-container project-type passed"})
                                h2 = soup.new_tag("h2", attrs={"class": "ecosystem-heading"})
                                h2.string = "Passed (No Known Vulnerabilities)"
                                passed_container.append(h2)
                                sources_wrapper = soup.new_tag("div", attrs={"class": "ecosystem-sources-container"})
                                passed_container.append(sources_wrapper)

                            source_div = soup.new_tag("div", attrs={"class": "source-container passed"})
                            h3 = soup.new_tag("h3", attrs={"class": "source-heading"})
                            h3.string = "Source: "
                            span = soup.new_tag("span", attrs={"class": "source-path"})
                            span.string = f"sbom:{abs_sbom.as_posix()}"
                            h3.append(span)
                            
                            p_tag = soup.new_tag("p")
                            p_tag.string = "經 OSV 資料庫比對，未偵測到已知弱點 (No known vulnerabilities detected)"
                            
                            source_div.append(h3)
                            source_div.append(p_tag)
                            sources_wrapper.append(source_div)

                if passed_container:
                    vuln_tab.append(passed_container)
                    print(f"[*] Found and injected {len(processed_files)} safe sources.")
                else:
                    print("[*] No additional safe sources found. Skipping injection.")
                    
        except Exception as e:
            print(f"[!] Error processing SBOM directory: {e}")

    html_soup = deepcopy(soup)
    html_inject = light_mode_font_injection + light_mode_style_f + light_mode_style_b_html
    pdf_inject = light_mode_font_injection + light_mode_style_f + light_mode_style_b_pdf

    # Inject fonts and style into the <head>
    if soup.head:
        html_soup.head.append(BeautifulSoup(html_inject, 'html.parser'))
        soup.head.append(BeautifulSoup(pdf_inject, 'html.parser'))
    else:
        new_html_head = html_soup.new_tag('head')
        new_html_head.append(BeautifulSoup(html_inject, 'html.parser'))
        html_soup.insert(0, new_html_head)

        new_pdf_head = soup.new_tag('head')
        new_pdf_head.append(BeautifulSoup(pdf_inject, 'html.parser'))
        soup.insert(0, new_pdf_head)

    html_content = str(html_soup).replace("osv-scanner-OSV-logo-darkmode.png", "osv-scanner-OSV-logo-lightmode.png")

    # Save the modified content to a new file
    dir_name = input_path.parent
    base_name = input_path.name
    p = Path(input_path)
    prefix = p.parent.name if p.parent.name else p.stem
    html_output = dir_name / f"{prefix}_SBOM_Report_{datetime.now().strftime("%m%d")}.html"
    
    print(f"[*] Saving modified HTML report to: {html_output}")
    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(html_content)

    if generate_pdf:
        # Convert tooltip content from HTML-escaped to actual HTML elements
        tooltips = soup.find_all("div", class_="tooltip")
        for div in tooltips:
            classes = div.get('class', [])
            if len(classes) != 1 or classes[0] != 'tooltip':
                continue
            
            td = div.parent
            tr = td.parent if td else None

            if td and td.name == 'td' and tr and tr.name == 'tr' and tr.has_attr('data-vuln-id'):
                span = div.find("span", class_="tooltiptext")
                if span:
                    content = span.decode_contents()
                    div.clear()
                    div.append(BeautifulSoup(content, 'html.parser'))
        
        # Update arrow icons to use "expanded" class
        arrow_icon = soup.find_all("i", class_="material-icons")
        [icon.__setitem__('class', 'material-icons expanded') for icon in arrow_icon]

        # Ensure package details sections are fully expanded
        pkg_details = soup.find_all("div", class_="package-details")
        [details.__setitem__('class', 'package-details') for details in pkg_details]
        
        # Remove search box, and filter section for cleaner PDF output
        filter_section = soup.find(id="filter-section")
        if filter_section:
            filter_section.decompose()

        search_box = soup.find("div", class_="search-box")
        if search_box:
            search_box.decompose()
                    
        # Replace logo image reference
        pdf_content = str(soup).replace("osv-scanner-OSV-logo-darkmode.png", "osv-scanner-OSV-logo-lightmode.png")

        tmp_output = dir_name / f"tmp_{base_name}"
        pdf_output = dir_name / f"{prefix}_SBOM_Report_{datetime.now().strftime("%m%d")}.pdf"

        print("[*] Generating PDF from modified HTML report...")
        with open(tmp_output, 'w', encoding='utf-8') as f:
            f.write(pdf_content)

        asyncio.run(html_to_pdf(tmp_output, pdf_output))
        
        # Clean up the temporary HTML file used for PDF generation
        print(f"[*] Cleaning up temporary file...")
        if tmp_output.exists():
            tmp_output.unlink()

        print(f"[*] PDF report generated at: {pdf_output}")

    print("[*] Conversion complete.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert OSV HTML report to light mode HTML or PDF")
    parser.add_argument("report", help="Path to the OSV HTML report")
    parser.add_argument("-r", "--sbom-dir", help="Path to the SBOM directory", default=None)
    parser.add_argument("--pdf", action="store_true", help="Generate PDF instead of HTML (default: False)")
    args = parser.parse_args()

    convert_osv_report(args.report, args.sbom_dir, args.pdf)