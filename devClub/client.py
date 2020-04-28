import socket 

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 8765))
sock.send(b'Test message')
sock.close()