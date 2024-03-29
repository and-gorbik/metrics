import asyncio

class Metrics:
    _instance = None

    # singleton
    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self._data = {}
        self._lock = asyncio.Lock()

    async def get_all(self):
        async with self._lock:
            resp = "\n".join([
                "\n".join(map(lambda val: f"{key} {val[0]} {val[1]}", self._data[key]))
                for key in self._data.keys()
            ])
        return f"ok\n{resp}\n\n"      

    async def get_by_key(self, key):
        async with self._lock:
            if self._data.get(key) is None:
                return "ok\n\n"
            resp = "\n".join(map(lambda val: f"{key} {val[0]} {val[1]}", self._data[key]))
        return f"ok\n{resp}\n\n"

    async def add(self, params):
        try:
            key, value, timestamp = params.split()
            value, timestamp = float(value), int(timestamp)
        except Exception:
            return f"error\ninvalid params: {params}\n\n"

        item = (value, timestamp)
        async with self._lock:
            if self._data.get(key) is None:
                self._data[key] = [item, ]
            else:
                if self._data[key][-1][1] == timestamp:
                    self._data[key][-1] = item
                else:
                    self._data[key].append(item)
        return "ok\n\n"

class Server:

    def __init__(self, host, port):
        self._metrics = Metrics()
        self._address = (host, port)

    async def _process_data(self, request):
        try:
            action, params = request.split(' ', 1)
            params = params.strip()
        except ValueError:
            return "error\nwrong command\n\n".encode()

        if action == 'get':
            if params == '*':
                return await self._metrics.get_all()
            else:
                return await self._metrics.get_by_key(params)
        elif action == 'put':
            return await self._metrics.add(params)
        else:
            return f"error\nwrong command\n\n"

    async def _serve(self, reader, writer):
        while True:
            data = await reader.read(4096)
            if data:
                response = await self._process_data(data.decode())
                writer.write(response.encode())
                await writer.drain()
            else:
                writer.close()
                return

    def run(self):
        loop = asyncio.get_event_loop()
        factory = asyncio.start_server(self._serve, *self._address)
        server = loop.run_until_complete(factory)
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server.close()
            loop.run_until_complete(server.wait_closed())
            loop.close()


def run_server(host, port):
    server = Server(host, port)
    server.run()

if __name__ == "__main__":
    run_server('127.0.0.1', 8888)