import utils,numpy as np,cv2,pickle,sys,struct,time,heapq
from threading import Thread
import server_global

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

current_milli_time = lambda: int(round(time.time() * 1000))

def start_thread(listener,address):
	t = (listener,address)
	Thread(target = utils.accept_connections_forever,args = t).start()

def update_round_time(socks,addresses):
	while True:		
		one_way_time = []
		for sock,address in zip(socks,address):
			cur_serv_time = current_milli_time()
			sock.send(struct.pack(">LL",0,cur_serv_time))
			time_taken = utils.recv_until(sock,b'?').decode('utf-8')
			time_taken = int(time_taken[:len(time_taken)-1])
			one_way_time.append((time_taken,address[1])
		one_way_time.sort()
		time_ref = one_way_time[0]
		one_way_time = [x-time_ref for x in one_way_time]
		for tup in one_way_time:
			server_global.subflow_wait_time[tup[1]] = tup[0]


if __name__ == '__main__':

	server_global.init()

	addresses,file_name = utils.parse_command_line("Multiple sockets server")
	print('Streaming:' + file_name)

	listeners = map(utils.create_srv_socket,addresses)
	
	
	cap = cv2.VideoCapture(str(file_name))
	time_ref = current_milli_time()


	for address,listener in zip(addresses,listeners):
		start_thread(listener,address)



	while(cap.isOpened()):
		ret,frame = cap.read()
		timestamp = current_milli_time()-time_ref

		if ret:
			ret,image = cv2.imencode('.jpg',frame,encode_param)
		if(ret==False):
			break

		data = pickle.dumps(image)
		sze = len(data)

		print("Main Thread: Appended " + str(sze) + " bytes, with timestamp:" + str(timestamp))
		
		server_global.qu.append(struct.pack(">LL",sze,timestamp)+data)

		#time.sleep(10)

	cap.release()
	cv2.destroyAllWindows()

	print("Main Thread exiting")