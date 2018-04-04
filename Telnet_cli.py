from Exscript.protocols import SSH2, Telnet,exception
from Exscript import Host, Account


class TelnetCLI:

    def __init__(self, ip=None, port=23, username=None, password=None,
                 timeout=3, link_right_now=False):
        self.target_ip = ip
        self.target_port = port
        self.username = username
        self.password = password
        self.timeout = timeout
        self.connection = None
        if link_right_now is True:
            if username is None or password is None or ip is None:
                raise Exception('Too few arguments')
            self.connect_to_target(self.username, self.password)

    def connect_to_target(self, username, password):
        self.username = username
        self.password = password
        timeout = self.timeout
        try:
            self.connection = Telnet(timeout=timeout)
            self.connection.connect(hostname=self.target_ip, port=self.target_port)
            self.connection.login(Account(self.username, self.password))
        except Exception:
            raise Exception('Fail to set up connection')

    def config_mode(self):
        self.connection.execute('conf t')

    def exit_config_mode(self):
        if self.check_config_mode() is True:
            self.connection.execute('exit')
        else:
            pass

    def check_config_mode(self):
        try:
            self.connection.execute('show int status')
            return False
        except exception.InvalidCommandException:
            return True

    def set_port_vlan(self, switch_port, vlan):
        if self.check_config_mode() is False:
            self.config_mode()
        self.connection.execute('int gi0/' + str(switch_port))
        self.connection.execute('switchport access vlan ' + str(vlan))

    def get_port_vlan(self, switchport):
        if self.check_config_mode() is True:
            self.connection.execute('do show run int gi0/' + str(switchport))
        else:
            self.connection.execute('show run int gi0/' + str(switchport))

        result = self.connection.response
        pos = result.find('vlan')

        if pos == -1:
            return 1

        if result[pos + 6].isdigit():
            return result[pos + 5] + result[pos + 6]
        else:
            return result[pos + 5]

    def cancel_port_vlan(self, switch_port):
        self.set_port_vlan(switch_port, 1)

    def get_vlan_info(self, vlan):
        try:
            if self.check_config_mode() is True:
                self.connection.execute('do show vlan id ' + str(vlan))
            else:
                self.connection.execute('show vlan id ' + str(vlan))

            info = self.connection.response
            info = info[info.find('Ports') + 6:]
            info = info[info.find(str(vlan)) + len(str(vlan)):]

            ptr = 0

            # strip the space in text
            while info[ptr] == ' ':
                ptr += 1
            info = info[ptr:]
            ptr = 0

            # a method to get the word
            while info[ptr] != ' ' and info[ptr] != '\r' and info[ptr] != '\n':
                ptr += 1
            vlan_name = info[:ptr]
            info = info[ptr:]
            ptr = 0

            while info[ptr] == ' ':
                ptr += 1
            info = info[ptr:]
            ptr = 0

            while info[ptr] != ' ' and info[ptr] != '\r' and info[ptr] != '\n':
                ptr += 1
            vlan_status = info[:ptr]
            info = info[ptr:]
            ptr = 0

            # the port for port in the vlan
            port_list = []
            while info[ptr] == ' ':
                ptr += 1
            info = info[ptr:]
            ptr = 0

            position = info.find('Gi0/')
            while position != -1:
                if info[position + 5].isdigit():
                    port_list.append(int(info[position + 4: position + 6]))
                else:
                    port_list.append(int(info[position + 4]))
                info = info[position + 4:]
                position = info.find('Gi0/')

            r_json = {
                'id': vlan,
                'name': vlan_name,
                'status': vlan_status,
                'port_list': port_list,
            }

            return r_json
        except exception.InvalidCommandException:
            return {'error_message': 'No vlan ' + str(vlan) + ' in switch.'}

    def create_vlan(self, **kwargs):
        if not self.check_config_mode():
            self.config_mode()
        vlan = kwargs.get('vlan')
        if vlan is not None:
            self.connection.execute('vlan ' + str(vlan))
        else:
            vlan_list = kwargs.get('vlan_list')
            if vlan_list:
                for v in vlan_list:
                    self.connection.execute('vlan ' + str(v))
        self.connection.execute('end')

    def delete_vlan(self, vlan):
        if vlan == 1:
            raise ValueError('Can\'t remove default vlan', vlan)

        if self.check_config_mode() is False:
            self.config_mode()

        try:
            port_list = self.get_vlan_info(vlan=vlan)['port_list']
            for port in port_list:
                self.cancel_port_vlan(switch_port=port)
            self.connection.execute('no vlan ' + str(vlan))
        except exception.InvalidCommandException:
            pass


if __name__ == '__main__':
    pass