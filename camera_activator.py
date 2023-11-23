import requests
import json
import time


class TPLinkDeviceMonitor:

    def __init__(self, email, password, uuid):
        self.email = email
        self.password = password
        self.uuid = uuid
        self.token = ""
        self.try_again_timer = -1
        self.device_list = []
        self.smart_plugs = []

    def _get_or_update_token(self):
        if self.try_again_timer != -1:
            if time.time() - self.try_again_timer < 300:
                print("Still need to wait", str(time.time() - self.try_again_timer), " before trying again.")
                self.token = ""
                return False
        api_url = "https://wap.tplinkcloud.com"
        token_req = {
            "method": "login",
            "params":
                {
                    "appType": "Kasa_Android",
                    "cloudUserName": self.email,
                    "cloudPassword": self.password,
                    "terminalUUID": self.uuid
                }
        }

        try:
            resp = requests.post(api_url, json=token_req)
        except Error as e:
            print("Error sending a request to the API trying to get token. Giving up.")
            print(e)
            return False
        if "token" in resp.text:
            self.token = resp.text.split(",")[-1].split(":")[-1][1:-3]
            self.try_again_timer = -1
            return True
        else:
            self.token = ""
            if "rate limit" in resp.text:
                print("Rate limit exceeded. Too many requests in a short time. Trying again in 5 minutes.")
            else:
                print("Failed to get token. If you have 2-factor authentication enabled it will always fail.")
                print("Trying again in 5 minutes.")
            self.try_again_timer = time.time()
            return False

    def _get_or_update_device_list(self):
        success = self._get_or_update_token()
        if not success:
            self.device_list = []
            return
        dev_req_url = "https://wap.tplinkcloud.com?token=" + self.token
        dev_req_data = {"method": "getDeviceList"}
        dev_req_header = {"Content-Type": "application/json"}

        try:
            resp = requests.post(dev_req_url, headers=dev_req_header, json=dev_req_data)
        except Error as e:
            print("Error requesting device list. Giving up.")
            print(e)
            return
        self.device_list = json.loads(resp.text)["result"]["deviceList"]

    def _get_smart_plugs(self):
        self._get_or_update_device_list()
        self.smart_plugs = []
        if not len(self.device_list):
            print("Unable to retrieve device list. Check not completed.")
            return
        for dev in self.device_list:
            try:
                if "HS10" in dev["deviceModel"]:
                    self.smart_plugs += [KasaPlug(dev)]
            except ValueError as e:
                print("Whatever info was obtained from the device list doesn't make sense. Giving up.")
                print(e)

    def turn_on_all_plugs(self):
        self._get_smart_plugs()
        if not len(self.smart_plugs):
            print("Plug device list is empty. Unable to adjust plug state.")
            return
        dev_req_url = "https://wap.tplinkcloud.com?token=" + self.token
        dev_req_header = {"Content-Type": "application/json"}
        for plug in self.smart_plugs:
            dev_req_data = {
                "method": "passthrough",
                "params": {
                    "deviceId": plug.device_id,
                    "requestData": "{\"system\":{\"set_relay_state\":{\"state\":1}}}"
                }
            }
            try:
                resp = requests.post(dev_req_url, headers=dev_req_header, json=dev_req_data)
            except Error as e:
                print("Error trying to turn plug ", plug.alias, " on. Giving up."
                                                                " Some plugs may be on while others are off now.")
                print(e)

    def turn_off_all_plugs(self):
        self._get_smart_plugs()
        if not len(self.smart_plugs):
            print("Plug device list is empty. Unable to adjust plug state.")
            return
        dev_req_url = "https://wap.tplinkcloud.com?token=" + self.token
        dev_req_header = {"Content-Type": "application/json"}
        for plug in self.smart_plugs:
            dev_req_data = {
                "method": "passthrough",
                "params": {
                    "deviceId": plug.device_id,
                    "requestData": "{\"system\":{\"set_relay_state\":{\"state\":0}}}"
                }
            }
            try:
                resp = requests.post(dev_req_url, headers=dev_req_header, json=dev_req_data)
            except Error as e:
                print("Error trying to turn plug ", plug.alias, " off. Giving up."
                                                                " Some plugs may be on while others are off now.")
                print(e)


class KasaPlug:

    def __init__(self, device_dict):
        self.alias = device_dict["alias"]
        self.hw_ver = device_dict["deviceHwVer"]
        self.device_id = device_dict["deviceId"]
        self.mac = device_dict["deviceMac"]
        self.model_name = device_dict["deviceModel"]
        self.device_name = device_dict["deviceName"]
        self.device_description = device_dict["deviceType"]




