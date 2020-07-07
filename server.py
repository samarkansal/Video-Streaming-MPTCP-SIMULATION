import utils,numpy as np,cv2,pickle,sys,struct,time,heapq
from threading import Thread
import server_global

encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]

current_milli_time = lambda: int(round(time.time() * 1000))

def start_thread(listener,address):
	t = (listener,address)
	Thread(target = utils.accept_connections_forever,args = t).start()


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