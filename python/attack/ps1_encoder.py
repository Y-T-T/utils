# --------------------------------------------------------------
# PS1 Encoder Script
# This script reads a PowerShell script file, encodes its content in Base64 format
# suitable for use with PowerShell's -EncodedCommand parameter.
# --------------------------------------------------------------

import base64
import argparse

def ps1_encoder(script_content):
    """
    Encode PowerShell script content to Base64 format for -EncodedCommand.
    """
    # -------------------------------------------------------------------
    # Convert string to UTF-16LE (Little Endian) encoded bytes
    # This is the format expected by PowerShell -EncodedCommand.
    # -------------------------------------------------------------------
    utf16_le_bytes = script_content.encode('utf-16-le')

    # Perform Base64 encoding
    encoded_payload = base64.b64encode(utf16_le_bytes).decode('utf-8')

    return encoded_payload

def ps1_decoder(encoded_payload):
    """
    Decode Base64 encoded PowerShell script back to original content.
    """
    # Decode from Base64
    utf16_le_bytes = base64.b64decode(encoded_payload)

    # Convert bytes back to string
    script_content = utf16_le_bytes.decode('utf-16-le')

    return script_content

if __name__ == "__main__":
   
    parser = argparse.ArgumentParser(
        description="Encode a PowerShell script file to Base64 for -EncodedCommand."
    )
    parser.add_argument('script_path', type=str, help='Path to the PowerShell script file.')

    args = parser.parse_args()
    script_path = args.script_path

    try:
        with open(script_path, 'r') as f:
            # Read script content
            script_content = f.read()

            encoded_payload = ps1_encoder(script_content)

            # Output final payload
            print("Payload:")
            print("-" * 50)
            print(f"powershell -e {encoded_payload}")
            print("-" * 50)

    except FileNotFoundError:
        print(f"Error: File not found {script_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
