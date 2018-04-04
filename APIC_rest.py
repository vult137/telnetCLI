import requests
import json

requests.packages.urllib3.disable_warnings()


class APICrestful(object):

    def __init__(self, controller=None, auth=None):
        self.controller = controller
        self.auth = auth
        self.ticket = None

    def get_ticket(self, auth=None):
        if auth:
            self.auth = auth
            if auth['username'] is None or auth['pathword'] is None:
                raise ValueError('Invalid auth!')

        header = {"content-type": "application/json"}
        url = "https://" + self.controller + "/api/v1/ticket"
        response = requests.post(url=url, data=json.dumps(self.auth), headers=header, verify=False)
        ticket = response.json()['response']['serviceTicket']
        return ticket

    def get_topology(self):
        if not self.ticket:
            self.ticket = self.get_ticket()
        header = {"content-type": "application/json", 'X-Auth-Token': self.ticket}
        url = "https://" + self.controller + "/api/v1/topology/physical-topology"
        response = requests.get(url=url, headers=header, verify=False)
        return response.json()['response']

    def get_devices(self):
        if not self.ticket:
            self.ticket = self.get_ticket()
        header = {"content-type": "application/json", 'X-Auth-Token': self.ticket}
        url = "https://" + self.controller + "/api/v1/network-device"
        response = requests.get(url=url, headers=header, verify=False)
        return response.json()['response']

    def get_devices_count(self):
        if not self.ticket:
            self.ticket = self.get_ticket()
        header = {"content-type": "application/json", 'X-Auth-Token': self.ticket}
        url = "https://" + self.controller + "/api/v1/network-device/count"
        response = requests.get(url=url, headers=header, verify=False)
        return response.json()['response']

    def get_device_vlan_info(self, device_id):
        if not self.ticket:
            self.ticket = self.get_ticket()
        header = {"content-type": "application/json", 'X-Auth-Token': self.ticket}
        url = "https://" + self.controller + "/api/v1/network-device/" + device_id + '/vlan'

        response = requests.get(url=url, headers=header, verify=False)
        ret = response.json()['response']
        if 'errorCode' in ret:
            return
        return ret

    def get_users(self):
        if not self.ticket:
            self.ticket = self.get_ticket()
        header = {"content-type": "application/json", 'X-Auth-Token': self.ticket}
        url = 'https://' + self.controller + '/api/v1/user'
        response = requests.get(url=url, headers=header, verify=False)
        return response.json()['response']

    def show_user(self, username):
        if not self.ticket:
            self.ticket = self.get_ticket()
        header = {"content-type": "application/json", 'X-Auth-Token': self.ticket}
        url = 'https://' + self.controller + '/api/v1/user/' + username
        response = requests.get(url=url, headers=header, verify=False)
        return response.json()['response']

    def get_topology_nodes(self):
        if not self.ticket:
            self.ticket = self.get_ticket()
        url = "https://" + self.controller + "/api/v1/topology/physical-topology"
        header = {"content-type": "application/json", "X-Auth-Token": self.ticket}
        response = requests.get(url, headers=header, verify=False)
        r_json = response.json()

        net_nodes = []
        for n in r_json['response']['nodes']:
            if 'platformId' in n:
                node = n['platformId']
                family = n['family']
                label = n['label']
                management_ip = n['ip']

                link_list = []
                for i in r_json['response']['links']:
                    if 'startPortName' in i:
                        if i['source'] == n['id']:
                            for m in r_json['response']['nodes']:
                                if m['id'] == i['target']:
                                    link_list.append({
                                        'source_interface': i['startPortName'],
                                        'target': m['platformId'],
                                        'target_interface': i['endPortName'],
                                        'status': i['linkStatus']
                                    })
                                    break
                net_nodes.append({
                    'node': node,
                    'family': family,
                    'label': label,
                    'management_ip': management_ip,
                    'link_list': link_list,
                })

        return net_nodes


if __name__ == '__main__':
    handler = APICrestful(controller='sandboxapic.cisco.com', auth={"username": "devnetuser", "password": "Cisco123!"})
    handler.ticket = handler.get_ticket()
    devices_list = handler.get_devices()
    res_list = []
    for device in devices_list:
        if device['family'] == 'Switches and Hubs' or device['family'] == 'Routers':
            res_list.append(handler.get_device_vlan_info(device['id']))
    for ele in res_list:
        print(ele)
