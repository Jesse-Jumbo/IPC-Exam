import time
import zmq
import random
import json
import os
import math

def psnr(ans, test):
    # return -1
    import cv2
    import numpy as np

    assert os.path.isfile(ans)
    assert os.path.isfile(test)

    ans = cv2.imread(ans, cv2.IMREAD_GRAYSCALE)
    test = cv2.imread(test, cv2.IMREAD_GRAYSCALE)

    if ans.shape != test.shape:
        return -np.inf

    mse = np.mean((ans - test) ** 2)
    if mse == 0:
        return np.inf
    PIXEL_MAX = 255.0
    return 20 * math.log10(PIXEL_MAX / math.sqrt(mse))


if __name__ == "__main__":
    with open("./SystemParameters.json", "r", encoding='utf-8') as f:
        env = json.load(f)

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(env["socket_system_server"])

    s_path = env["image_path"]
    image_name = os.path.basename(s_path).split(".")[0]
    a_path = f"../results/ans/{image_name}.jpeg"
    assert os.path.isfile(s_path) == True

    t_start = -1
    t_end = -1
    PSNR = -1

    while True:        
        message = socket.recv_string()
        message = message.split()
        if len(message) == 2:
            ID, info = [str(n) for n in message]
            # print(message)
        elif len(message) == 3:
            ID, info, path = [str(n) for n in message]
        else:
            continue

        if info == "s":
            t_start = time.time()
            socket.send_string(s_path)
        elif info == "e":
            # correct answer and calculate used time
            t_end = time.time()
            PSNR = psnr(a_path, path)

            socket.send_string(f"{env['userID']} {PSNR} {t_end - t_start}")
            socket.close()
            break
        else:
            print("[Judging System] un-parsable info\n")
