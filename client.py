from socket import socket, create_connection, timeout
from time import time

class ClientError(Exception):
    pass


class Client:
    def __init__(self, ip='127.0.0.1', port='11111', timeout=None):
        self._ip = ip
        self._port = port
        self._timeout = timeout


    def put(self, key, value, timestamp=int(time())):
        try:
            request = "put {} {} {}\n".format(str(key), float(value), int(timestamp))
        except (ValueError, TypeError):
            raise ClientError("Incorrect request:\n")
        
        response = self._connect_to_server(request)
        
        if response.split('\n')[0] in "error":
            raise ClientError("Incorrect response:\n")


    def get(self, key) -> dict:
        try:
            if key in "*":
                request = "get *\n"
            else:
                request = "get {}\n".format(key)
        except (ValueError, TypeError):
            raise ClientError("Incorrect request:\n")
        
        response = self._connect_to_server(request)
        
        lines = response.split('\n')
        if lines[0] in "error":
            raise ClientError(response)
        return self._parse_response(lines[1:])


    def _connect_to_server(self, request: str) -> str:
        print(f"{self._ip} : {self._port} : {self._timeout}")
        with create_connection((self._ip, self._port), timeout=self._timeout) as s:
            try:
                s.sendall(request.encode())
                response = ""
                while True:
                    data = s.recv()
                    if not data:
                        break
                    response = "".join((response, data.decode("utf-8")))
            except timeout:
                raise ClientError("Timeout error")
            except OSError:
                raise ClientError("Error with sockets")
            
            return response


    def _parse_response(self, lines: list) -> dict:
        result = {}
        try:
            for line in lines:
                key, value, timestamp = line.split(" ")[1:]
                if result.get(key) is None:
                    result[key] = [(int(timestamp), float(value)), ]
                else:
                    result[key].append((int(timestamp), float(value)))
        except (ValueError, TypeError):
            pass
        return result
