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
				"\n".join(map(lambda val: f"{key} {val}", self._data[key]))
				for key in self._data.keys()
			])
		return f"ok\n{resp}\n\n"      

	async def get_by_key(self, key):
		async with self._lock:
			if self._data.get(key) is None:
				return "ok\n\n"
			resp = "\n".join(map(lambda val: f"{key} {val}", self._data[key]))
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

class ServerProtocol(asyncio.Protocol):
	_instance = None

	def __new__(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = super().__new__(cls, *args, **kwargs)
		return cls._instance

	def __init__(self, loop):
		self._loop = loop
		self._metrics = Metrics()

	def connection_made(self, transport):
		self.transport = transport

	async def _process_data(self, request):
		try:
			action, params = request.split(' ', 1)
			params = params.strip()
		except ValueError:
			return f"error\nwrong command\n\n"
		if action == 'get':
			if params == '*':
				return await self._metrics.get_all()
			else:
				return await self._metrics.get_by_key(params)
		if action == 'put':
			return await self._metrics.add(params)
		return f"error\nwrong command: {action}\n\n"

	def data_received(self, data):
		task = self._loop.create_task(self._process_data(data.decode())
		completed, _ = self._loop.run_until_complete(task())
		for c in completed:
			self.transport.write(c.result.encode())

def run_server(host, port):
	loop = asyncio.get_event_loop()
	coro = loop.create_server(
		ServerProtocol,
		host, port
	)
	server = loop.run_until_complete(coro)
	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass
	finally:
		server.close()
		loop.run_until_complete(server.wait_closed())
		loop.close()

if __name__ == "__main__":
	run_server('127.0.0.1', 8888)