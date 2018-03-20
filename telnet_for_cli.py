from telnetlib import Telnet
import time

sleep_time = 0.05


class TelnetCLI:

    def __init__(self, ip=None, port=23, username=None, password=None, timeout=3, link_right_now=False):
        self.target_host = ip
        self.target_port = port
        self.read_buffer = ''
        self.username = None
        self.password = None
        self.secret = None
        self.timeout = timeout

        self.tn = None

        if link_right_now is True:
            if ip is None or username is None or password is None:
                raise Exception('Not enough arguments')
            self.connect_to_target(self.username, self.password)

    def connect_to_target(self, username, password):
        self.username = username
        self.password = password
        timeout = self.timeout
        try:
            self.tn = Telnet(self.target_host, self.target_port, timeout=timeout)
            self.tn.read_until(b'Username:')
            self.send_str(self.username)
            self.tn.read_until(b'Password:')
            self.send_str(self.password)
        except Exception:
            raise Exception('Fail to set up connection')

    def get_line(self):
        try:
            ch = self.tn.rawq_getchar().decode('ascii')
            if ch == '\n':
                return ch
            while ch == ' ' or ch == '\r':
                ch = self.tn.rawq_getchar().decode('ascii')
            read_buffer = ''
            while ch != '\r':
                read_buffer += ch
                ch = self.tn.rawq_getchar().decode('ascii')
        except Exception:
            return 'BALALA-MAGIC-POWER!'
        return self.read_buffer

    def get_all_line(self):
        line = self.get_line()
        while line != 'BALALA-MAGIC-POWER!':
            line = self.get_line()
        return None

    def send_str(self, send_string=''):
        if self.tn is None:
            raise Exception('Telnet link has not been set up!')
        self.tn.write(send_string.encode('ascii') + b'\n')
        time.sleep(sleep_time)

    def get_device_version(self):
        # TODO:
        pass

    def device_enable(self, secret=None):
        if secret is None:
            self.secret = self.password
        else:
            self.secret = secret
        try:
            self.send_str('enable')
            self.tn.read_until(b'Password:')
            self.send_str(self.secret)
        except Exception:
            raise Exception

    def device_configuration(self):
        try:
            self.send_str('conf t')
        except Exception:
            raise Exception('Error in conf t command')

    def device_interface_vlan_set(self, switch_port, vlan):
        if switch_port <= 0 or switch_port > 12:
            raise ValueError
        # TODO: ADD A FUNCTION TO CHECK CLI STATUS
        self.send_str('int gi0/' + str(switch_port))
        self.send_str('switchport access vlan ' + str(vlan))
        self.send_str('exit')

    def device_interface_vlan_cancel(self, switch_port, vlan):
        if switch_port <= 0 or switch_port > 12:
            raise ValueError
        self.send_str('int gi0/' + str(switch_port))
        self.send_str('no switchport access vlan ' + vlan)

    def device_interfaces_information(self, switch_port):
        pass


if __name__ == '__main__':
    switch_conn = TelnetCLI('10.74.82.35', timeout=1)
