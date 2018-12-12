from socket import socket

s = socket()
s.bind(("127.0.0.1", 11111))
s.listen()
sock, _ = s.accept()
response = bytes()
while True:
	data = sock.recv(1024)
	if not data:
		print(response.decode())
		sock.sendall(b"ok\n\n")
		break
	response += data
sock.close()
s.close()
