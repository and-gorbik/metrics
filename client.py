import socket
from time import time

class ClientError(Exception):
    pass


class Client:
    def __init__(self, ip='127.0.0.1', port=11111, timeout=None):
        self._ip = ip
        self._port = port
        self._timeout = timeout


    def put(self, key, value, timestamp=time()):
        try:
            request = "put {} {} {}\n".format(key, value, int(timestamp))
        except ValueError:
            raise ClientError(f"Incorrect request:\n{request}\n")
        response = self._send(request)
        status, msg = response.split("\n", 1)
        if "error" in status:
            raise ClientError(f"{msg}\n")

    def get(self, key) -> dict:
        request = f"get {key}\n"
        response = self._send(request)
        status, body = response.split("\n", 1)
        if "error" in status:
            raise ClientError(f"{body}\n")
        return self._parse(body)

    def _send(self, request: str) -> str:
        with socket.create_connection((self._ip, self._port), timeout=self._timeout) as s:
            response = []
            try:
                s.sendall(request.encode())
                while True:
                    data = s.recv(4096)
                    response.append(data)
                    if len(data) < 4096:
                        break
            except socket.timeout:
                raise ClientError("Timeout error")
            except OSError:
                raise ClientError("Error with sockets")
            
            return "".join([chunk.decode() for chunk in response])

    def _parse(self, body: str) -> dict:
        lines = body.split("\n")
        result = {}
        try:
            for line in lines:
                if line:
                    key, value, timestamp = line.split(" ")
                    if result.get(key) is None:
                        result[key] = [(int(timestamp), float(value)), ]
                    else:
                        result[key].append((int(timestamp), float(value)))
        except (ValueError, TypeError):
            raise ClientError(f"Incorrect response: {body}\n")
        return result


if __name__ == "__main__":
    client = Client("127.0.0.1", 10000, timeout=2)
    client.put("test", 0.5, 1)