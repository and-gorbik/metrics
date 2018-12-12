""" прототип клиента без обработки исключений """

import socket
from time import time

class ClientError(Exception):
    pass

class Client:
    def __init__(self, ip, port, timeout=None):
        self._ip = ip
        self._port = port
        self._timeout = timeout
    
    def _connect(self, request):
        response = b""
        with socket.create_connection((self._ip, self._port), timeout=self._timeout) as s:
            s.sendall(request.encode())
            try:
                data = s.recv(1024)
                while data:
                    response += data
                    data = s.recv(1024)
            except socket.timeout:
                raise ClientError
        
        return response.decode()
    
    def _parse_response(self, lines: list) -> dict:
        result = {}
        for line in lines:
            key, value, timestamp = line.split(" ")[1:]
            if result.get(key) is None:
                result[key] = [(int(timestamp), float(value)), ]
            else:
                result[key].append((int(timestamp), float(value)))
        return result

    def put(self, key, value, timestamp=int(time())):
        request = f"put {key} {value} {timestamp}\n"
        response = self._connect(request)
        if response.split("\n")[0] not in "ok":
            raise ClientError
        print(response)
    
    def get(self, key):
        request = f"get {key}\n"
        lines = self._connect(request).split("\n")
        if lines[0] not in "ok":
            raise ClientError
        return self._parse_response(lines[1:])

if __name__ == "__main__":
    c = Client("127.0.0.1", 11111, 5)
    c.put("test", 0.5, 1)
