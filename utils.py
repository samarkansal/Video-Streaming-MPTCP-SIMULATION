import argparse, socket, time,server_global,time

def parse_command_line(description):
	parser = argparse.ArgumentParser(description=description)
	parser.add_argument('host',help = 'IP or hostname')
	parser.add_argument('-f',metavar = 'file_name',default='nill',help='Video file name')
	parser.add_argument('-p',metavar='ports',type=int, nargs='*',default=[1060,1070,1080],help = 'TCP ports')
	args = parser.parse_args()
	addresses = []
	for port in args.p:
		addresses.append((args.host,port))
	return addresses,args.f

def create_srv_socket(address):
	listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	listener.bind(address)
	listener.listen(64)
	print('Listening at {}'.format(address))
	return listener

def accept_connections_forever(listener,address_serv):
	while True:
		sock,address = listener.accept()
		print(str(address_serv[1]) + ':Accepted connection from {}'.format(address))
		handle_conversation(sock, address, address_serv)

def handle_conversation(sock, address, address_serv):
	time.sleep(1)
	try:
		while True:
			send_frame(sock,address,address_serv)
	except EOFError:
		print('Client socket to {} has closed'.format(address))
	except Exception as e:
		print('Client {} error: {}'.format(address,e))
	finally:
		sock.close()

def send_frame(sock,address,address_serv):
	try:
		time.sleep(server_global.subflow_wait_time[address_serv[1]])
		sock.send(server_global.qu.popleft())
		print(str(address_serv[1]) + ' sends a packet to {}'.format(address))
	except IndexError as e:
		pass

def recv_until(sock, suffix):
    """Receive bytes over socket `sock` until we receive the `suffix`."""
    message = sock.recv(4)
    if not message:
        raise EOFError('socket closed')
    while not message.endswith(suffix):
        data = sock.recv(4)
        if not data:
            raise IOError('received {!r} then socket closed'.format(message))
        message += data
    return message
	