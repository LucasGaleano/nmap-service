from enum import Enum

class TypeService():
    NEW = 'New'
    UNCOMMON = 'Uncommon'
    COMMON = 'Common'

    def __init__(self) -> None:
        super().__init__()
        with open('uncommonPorts') as unport:
            self.uncommonPorts = [port.strip() for port in unport.readlines()]

    def type(self, port):       
        if str(port) in self.uncommonPorts:
            return self.UNCOMMON
        return self.COMMON

class Repository():
    
    def __init__(self, ddbb) -> None:
        self._ddbb = ddbb
        self.connect()   

    def connect(self):
        with open(self._ddbb,'r') as services:
            self.services = [service.strip() for service in services.readlines()]

    def is_new_service(self, ip, port, protocol, state):
        return self._ddbb_format(ip, port, protocol, state) not in self.services

    def add_new_service(self, ip, port, protocol, state):
        with open(self._ddbb,'a') as services:
            service = self._ddbb_format(ip, port, protocol, state)
            services.write(service + "\n")
            services.flush()
            self.services.append(service)

    def _ddbb_format(self, ip, port, protocol, state):
        return f"{ip} {port}/{protocol} {state}"



repo = Repository('ddbb')

# print(repo.is_new_service('2.2.2.2','333','tcp'))
# print(repo.is_new_service('2.2.2.2','444','tcp'))
# print(repo.add_new_service('2.2.2.2','333','tcp'))
# print(repo.is_new_service('2.2.2.2','333','tcp'))

# ts = TypeService()
# print(ts.uncommonPorts)
# print(ts.type('23'))
# print(ts.COMMON)