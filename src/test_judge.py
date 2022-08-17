import time
import json
import zmq
import os
import math

def psnr(ans, test):
    import cv2
    import numpy as np

    assert os.path.isfile(ans)
    assert os.path.isfile(test)

    ans = cv2.imread(ans, cv2.IMREAD_GRAYSCALE)
    test = cv2.imread(test, cv2.IMREAD_GRAYSCALE)

    if ans.shape != test.shape:
        return -np.inf

    # print(cv2.PSNR(ans, test))
    # print("sum", np.sum(ans - test))
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

    s_path = "../img/test.jpeg"
    #  a_path = "/home/ans/test.jpeg"
    a_path = "../results/ans/test.jpeg"

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
            print(f"[System] received start signal!")
            print(f"[System] please process {s_path}")
            socket.send_string(s_path)
            # print(s_path)
        elif info == "e":
            t_end = time.time()
            PSNR = psnr(a_path, path)
            socket.send_string(f"{env['userID']} {PSNR} {t_end - t_start}")
            socket.close()
            break
