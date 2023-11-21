from camera_activator import TPLinkDeviceMonitor
import platform    # For getting the operating system name
import subprocess  # For executing a shell command
import time
import sys
"""
1. Get a UUID (some kind of android device ID thing)
https://www.uuidgenerator.net/version4

2. Turn off 2-factor verification or this won't work.

It appears that a new token is issued every time you try to connect. Will probably have to get a token live.

Run in a terminal. Submit a post request with the following payload. Replace user with email, pass with password and uuid with above
curl -s https://wap.tplinkcloud.com -H 'Content-Type: application/json' -d '{"method":"login","params":{"appType":"Kasa_Android","cloudUserName":"$ACCOUNT_EMAIL","cloudPassword":"$ACCOUNT_PASSWORD","terminalUUID":"$UUID"}}'

Get the token from the result. Example token: 

A request for devices on the network can be done like so
curl -s --request POST "https://wap.tplinkcloud.com?token=YOUR_TOKEN_HERE HTTP/1.1" --data '{"method":"getDeviceList"}' --header "Content-Type: application/json"

3. Control the device
Get the device ID for the relevant device and replace it here. This request is for smart plugs.
Also don't forget to put your token in.
curl --request POST "https://wap.tplinkcloud.com/?token=YOUR_TOKEN_HERE HTTP/1.1" --data '{"method":"passthrough", "params": {"deviceId": "YOUR_DEVICEID_HERE", "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}" }}' --header "Content-Type: application/json
"""


def ping(host):
    """
    https://stackoverflow.com/questions/2953462/pinging-servers-in-python
    Returns True if host (str) responds to a ping request.
    Remember that a host may not respond to a ping (ICMP) request even if the host name is valid.
    """

    # Option for the number of packets as a function of
    param = '-n' if platform.system().lower() == 'windows' else '-c'

    # Building the command. Ex: "ping -c 1 google.com"
    command = ['ping', param, '1', host]

    return subprocess.call(command) == 0


tp = TPLinkDeviceMonitor(sys.argv[1], sys.argv[2], "6883cc6c-e12a-4d45-81b1-8662665c9420")
start = time.time()
refresh_time = 60
while True:
    if (time.time() - start) >= refresh_time:
        if (not ping("192.168.68.62")) and (not ping("192.168.68.66")):
            tp.turn_on_all_plugs()
            refresh_time = 600
        else:
            tp.turn_off_all_plugs()
            refresh_time = 60
        start = time.time()
