import utils,heapq,socket,time
import cv2,struct,pickle,zmq
import numpy as np
from threading import Thread

qu = []

def fill_qu(sock,address):
	global qu
	data = b""
	payload_size = struct.calcsize(">LL")
	print("Payload size: {}".format(payload_size))
	while True:
		while len(data) < payload_size:
			data += sock.recv(4096)

		result = struct.unpack(">LL",data[:payload_size])

		msg_size = result[0]

		timestamp = result[1]

		data = data[payload_size:]
		while len(data) < msg_size:
			data += sock.recv(4096)
		frame_data = data[:msg_size]
		data = data[msg_size:]

		frame = pickle.loads(frame_data,fix_imports=True, encoding="bytes")
		frame = cv2.imdecode(frame,cv2.IMREAD_COLOR)

		tup = (timestamp,frame)
		heapq.heappush(qu,tup)
		print('heappushed {} bytes frame,timestamp:{} recv from {}'.format(msg_size,timestamp,address))
		#time.sleep(10)

def start_thread(sock,address):
	t = (sock,address,)
	Thread(target=fill_qu,args=t).start()

if __name__ == '__main__':
	addresses,file_name = utils.parse_command_line("Multiple sockets client")

	socks=[]

	for address in addresses:
		sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
		sock.connect(address)
		socks.append(sock)

	for sock,address in zip(socks,addresses):
		start_thread(sock,address)

	time.sleep(60)

	passed_time = 0
	while True:
		try:
			fr = heapq.heappop(qu)
			if(fr[0]<passed_time):
				cv2.waitKey(1000)
			else:
				cv2.imshow('ImageWindow',fr[1])
				cv2.waitKey(25)
				passed_time = fr[0]
		except IndexError as e:
			pass