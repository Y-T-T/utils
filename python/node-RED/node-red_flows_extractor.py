import os
import sys
import json
import argparse

# Configuration
DEFAULT_INPUT_FILE = 'flows.json'
OUTPUT_DIR = 'flows'

def setup_output_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        print(f"[+] Created output directory: {directory}")
    else:
        print(f"[!] Output directory exists: {directory} (Files may be overwritten)")

def get_ext_by_format(node_format):
    format_map = {
        "html": "html",
        "handlerbars": "html",
        "json": "json",
        "text": "txt",
        "markdown": "md",
        "xml": "xml",
        "yaml": "yaml"
    }

    return format_map.get(node_format, "html")

def extract_code(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            flows = json.load(f)
    except FileNotFoundError:
        print(f"[Error] File not found: {file_path}")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"[Error] Failed to parse JSON. Please check if the file is valid.")
        sys.exit(1)

    print(f"[*] Parsing {len(flows)} nodes from {file_path}...")
    
    count_js = 0
    count_tpl = 0
    
    for node in flows:
        node_type = node.get('type', 'unknown')
        node_id = node.get('id', 'no_id')
        node_name = node.get('name', 'Unnamed Node')
        
        # Define content and extension based on node type
        content = None
        extension = None
        suffix = None
        
        # Handle Function Nodes (JavaScript)
        if node_type == 'function':
            content = node.get('func', '') # The logic code is in 'func'
            extension = 'js'
            suffix = 'function'
            count_js += 1
            
        # Handle Template Nodes (HTML/Mustache)
        # Includes standard 'template' and Dashboard 'ui_template'
        elif node_type in ['template', 'ui_template']:
            content = node.get('template', '') # The HTML is in 'template'
            node_format = node.get('format', 'html')
            extension = get_ext_by_format(node_format)
            suffix = 'template'
            count_tpl += 1
            
        # Check if have content to write
        if content is not None and extension is not None:
            # Construct filename: [NodeID]_[Type].[ext]
            filename = f"{node_id}_{suffix}.{extension}"
            file_path = os.path.join(OUTPUT_DIR, filename)
            
            # Add a header for the Auditor/SAST tool
            # This helps to trace back the finding to the original Node Name
            header_comment = ""
            if extension == 'js':
                header_comment = f"/**\n * Node-RED Source Extraction\n * Node ID: {node_id}\n * Node Name: {node_name}\n * Type: {node_type}\n */\n\n"
            
            try:
                with open(file_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(header_comment + content)
            except Exception as e:
                print(f"[Error] Failed to write {filename}: {e}")

    print("-" * 40)
    print(f"[*] Extraction Complete.")
    print(f"    - JS Files (Function Nodes): {count_js}")
    print(f"    - Templates Files:    {count_tpl}")
    print(f"    - Total Files Extracted:     {count_js + count_tpl}")
    print(f"[+] Files are saved in: ./{OUTPUT_DIR}/")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Extract Node-RED function/template code from flows JSON"
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default=DEFAULT_INPUT_FILE,
        help=f"Path to Node-RED flows JSON file (default: {DEFAULT_INPUT_FILE})"
    )
    return parser.parse_args()


def validate_input_file(file_path):
    if not os.path.isfile(file_path):
        print(f"[Error] File not found: {file_path}")
        sys.exit(1)

if __name__ == "__main__":
    args = parse_args()
    target_file = args.input_file

    # Validate input file first, then continue with setup/extraction.
    validate_input_file(target_file)
    setup_output_dir(OUTPUT_DIR)
    extract_code(target_file)