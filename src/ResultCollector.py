from socket import MSG_EOR
import zmq
import numpy as np
import json
import os
from utils import *

def reconstruct_image(bufs, num):
    # rebuild your matrix here
    # make sure it'll be the correct answer

    # answer is a 2d array
    # since we split the matrix in row order, we use the column number to sort the array here
    # you can modify this for your own splitting

    image = []
    # initialize the size of the image matrix
    for buf in bufs:
        height = len(buf["image"]) - len(buf["mask"])
        width = len(buf["image"][0])
        for _ in range(height):
            image.append([0 for _ in range(width)])

    # fill the matrix by the received buffers
    for buf in bufs:
        # the lenght of the first dimension of the array == the height of the  image
        # the lenght of the first row of the array == the width of the  image
        height = len(buf["image"])
        width = len(buf["image"][0]) 
        height_mask = len(buf["mask"])
        width_mask = len(buf["mask"][0])
        # the coordinate of the upper left point
        # point: [x, y]
        point = buf["point"]

        image[point[0]: point[0] + height - height_mask ] = buf["image"][0: -height_mask]

    return image

def connect_to_consumer(context, env) -> zmq.Context:
    socket = context.socket(zmq.PULL)
    socket.bind(env["socket_consumer_collector"])
    return socket

def connect_to_system(context, env) -> zmq.Context:
    socket = context.socket(zmq.REQ)
    socket.connect(env["socket_system_server"])
    return socket

def main(env):

    context = zmq.Context()
    socket_consumer = connect_to_consumer(context, env)
    socket_server = connect_to_system(context, env)

    # wait for workers' answers
    buffs = [] # save all the answer from consumer
    src_path = None
    while True:
        msg = socket_consumer.recv()
        jmsg = json.loads(msg)

        buffs.append(jmsg)

        if len(buffs) == jmsg["total_buffers_num"]:
            src_path = jmsg["src_path"]
            break
    ans = reconstruct_image(buffs, buffs[-1]["total_buffers_num"])
    

    # show results
    # your grade would be saved in server, 
    # it would not be different if you modified this display section : )
    ################################################
    image_name = os.path.basename(src_path)
    path = f"../results/{image_name}"
    save_image(ans, path)

    ID, PSNR, total_time = show_results(socket_server, path, env)
    print("="*30)
    print(f"[Collector] {ID} finish conv2d, using {total_time} sec, PSNR = {PSNR} dB")
    print(f"[Collector] image saved at {path}")
    #################################################

if __name__ == "__main__":
    with open("SystemParameters.json", "r", encoding='utf-8') as f:
        env = json.load(f)

    main(env)
