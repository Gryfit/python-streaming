import socket
import numpy as np
import cv2
import struct
from multiprocessing import Process
import cmd


def send_msg(sock, msg):
    # Prefix each message with a 4-byte length (network byte order)
    print(len(msg))
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    # Helper function to recv n bytes or return None if EOF is hit
    data = b''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

def streamCamera(host):
    cap = cv2.VideoCapture('Fantastic.Beasts.and.Where.to.Find.Them.mp4')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, 5000))
        while(cap.isOpened()):
            ret, frame = cap.read()
            img_str = cv2.imencode('.jpg', frame)[1].tostring()
            send_msg(s, img_str)
    cap.release()

def displayer():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("192.168.0.150", 4000))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print('Connected by', addr)
            while True:
                data = recv_msg(conn)
                nparr = np.fromstring(data, np.uint8)
                img = cv2.imdecode(nparr, 1)
                cv2.imshow('image',img)
                cv2.waitKey(1)
    cv2.destroyAllWindows()         


disp = Process(target=displayer, args=())
disp.start()

host = input("DONE? \n")

cam = Process(target=streamCamera, args=("192.168.0.94",))
cam.start()



