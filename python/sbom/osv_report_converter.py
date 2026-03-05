"""
Converts OSV HTML reports (Default dark mode) to a light mode version and generates a PDF.
"""

import sys
import os
import asyncio
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
        absolute_path = f"file://{os.path.abspath(html_path)}"
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

def convert_osv_report(input_path):
    if not os.path.exists(input_path):
        print(f"[-] Cannot find file: {input_path}")
        return

    with open(input_path, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Injecting Google Fonts via <link> is more reliable for headless PDF generation than @import
    light_mode_font_injection = """
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Overpass+Mono:wght@300;400;700&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
    """

    light_mode_style = """
    <style>
        /* Global override to ensure NO default browser fonts leak into the PDF */
        *, *::before, *::after, body, html, table, td, th, pre, code, div, span, p, a, input:not(i) {
            font-family: 'Overpass Mono', monospace !important;
            -webkit-font-smoothing: antialiased;
            -moz-osx-font-smoothing: grayscale;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
        }

        i.material-icons {
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
        .low { background-color: #53aa33 !important; color: #ffffff !important; }

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
    </style>
    """

    # Inject fonts and style into the <head>
    if soup.head:
        soup.head.append(BeautifulSoup(light_mode_font_injection + light_mode_style, 'html.parser'))
    else:
        new_head = soup.new_tag('head')
        new_head.append(BeautifulSoup(light_mode_font_injection + light_mode_style, 'html.parser'))
        soup.insert(0, new_head)

    html_content = str(soup).replace("osv-scanner-OSV-logo-darkmode.png", "osv-scanner-OSV-logo-lightmode.png")

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

    feedback = soup.find(id="header-right")
    if feedback:
        feedback.decompose()
    
    filter_section = soup.find(id="filter-section")
    if filter_section:
        filter_section.decompose() 

    search_box = soup.find("div", class_="search-box")
    if search_box:
        search_box.decompose() 

    # Replace logo image reference
    pdf_content = str(soup).replace("osv-scanner-OSV-logo-darkmode.png", "osv-scanner-OSV-logo-lightmode.png")

    # Save the modified content to a new file
    dir_name = os.path.dirname(input_path)
    base_name = os.path.basename(input_path)
    html_output = os.path.join(dir_name, f"light_{base_name}")
    tmp_output = os.path.join(dir_name, f"tmp_{base_name}")
    pdf_output = os.path.join(dir_name, f"light_{os.path.splitext(base_name)[0]}.pdf")
    
    print(f"[*] Saving modified HTML report to: {html_output}")
    with open(html_output, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print("[*] Generating PDF from modified HTML report...")
    with open(tmp_output, 'w', encoding='utf-8') as f:
        f.write(pdf_content)

    asyncio.run(html_to_pdf(tmp_output, pdf_output))
    
    # Clean up the temporary HTML file used for PDF generation
    print(f"[*] Cleaning up temporary file...")
    if os.path.exists(tmp_output):
        os.remove(tmp_output)

    print(f"[*] PDF report generated at: {pdf_output}")
    print("[*] Conversion complete.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python osv_report_converter.py <report.html>")
    else:
        convert_osv_report(sys.argv[1])
