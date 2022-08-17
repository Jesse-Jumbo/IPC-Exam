import zmq
import json
import os
import argparse
import numpy as np
import cv2
from utils import *

class MessageBuffer:
    def __init__(self, img, mask, point=[0,0], total_num=1):
        self.img = img
        self.mask = mask
        self.point = point
        self.total_num = total_num
        self.src_path = "../results/.test.jpeg"
    
    def set_src_path(self, path):
        self.src_path = path

    def to_dict(self):
        msg = {
                "src_path": self.src_path,
                "total_buffers_num": self.total_num,
                "point": self.point,
                "image": self.img,
                "mask": self.mask
               }
        return msg


def split_matrix(img=[[]], mask=[[]], num=1):
    """ 
        split your matrix here & write it to MessageBuffer for sending.
        img: 2d image array
        mask: 2d mask array
        num: split number
    """
    buffs = []
    height_img = len(img)
    width_img = len(img[0])
    height_mask = len(mask)
    width_mask = len(mask[0])

    # an example of split matrix by height
    # you call split the matrix here into any sub-matrix as you want
    start_row = 10.
    for n in range(num):    
        # add more rows (larger than mask size) in order to handle the border.
        buff_size = int(height_img / num)  + height_mask

        # the upper left point
        point = [start_row, 0]
        
        if start_row + buff_size < height_img:
            splitted_image = img[start_row :  start_row + buff_size]
        else:
            # padding  for the last buffer
            pad_height = buff_size - (height_img - start_row)
            pad = [[0 for _ in range(width_img)]  for _ in range(pad_height)]
            splitted_image = img[start_row : ] + pad
       
        msg = MessageBuffer(splitted_image, mask, point,  num)
        buffs.append(msg)

        # move to next start ptr
        start_row = start_row + buff_size - height_mask
        
    return buffs

def load_img(path: str):
    """ load img in grayscale as problem matrix """
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    print(f"[Producer] load img shape: {img.shape}")

    return img.tolist()

def connect_to_consumer(context, env):
    socket = context.socket(zmq.PUSH)
    socket.bind(env["socket_producer_consumer"])
    return socket

def connect_to_server(context, env):
    socket = context.socket(zmq.REQ)
    socket.connect(env["socket_system_server"])
    return socket

def recv_image_path(socket):
    return socket.recv_string()

def send_buffer(socket, buf)
    msg = json.dumps(buf.to_dict())
    socket.send_string(msg)

def main(env):
 
    context = zmq.Context()

    # push msg to clients
    socket_consumer = connect_to_consumer(context, env)

    socket_server = connect_to_server(context, env)
    send_start_signal(socket_server, env)
    env["image_path"] = recv_image_path(socket_server)
   
    # load matrix
    # mask, image: 2d array
    img = load_img("../img/1.jpeg")
    mask = load_mask()

    # recv start signal from result collector
    msg_buffers = split_matrix(img, mask, env['num_to_split'])
    for buf in msg_buffers:
        buf.set_src_path(env["image_path"])

    # send to consumers
    while len(msg_buffers) > 0:
        buf = msg_buffers.pop()
        send_buffer(socket_consumer, buf)

    print("[Producer] finish sending all message buffer")

    socket_server.close()
    socket_consumer.close()

if __name__ == "__main__":
    with open("SystemParameters.json", "r", encoding='utf-8') as f:
        env = json.load(f)
    
    main(env)
