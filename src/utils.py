def show_results(socket, path, env):
    socket.send_string(f"{env['userID']} e {path}")
    msg = socket.recv_string()
    msg = msg.split()

    if len(msg) == 3:
        ID, PSNR, total_time = msg
    else:
        ID, PSNR, total_time = -1, -1, -1
    
    return ID, PSNR, total_time


def save_image(img, path):
    import cv2
    cv2.imwrite(f"{path}", np.array(img))

def load_mask():
    mask = np.array([
                [1, 4, 6, 4, 1],
                [4, 16, 24, 16, 4],
                [6, 24, 36, 24, 6],
                [4, 16, 24, 16, 4],
                [1, 4, 6, 4, 1]]) / 256
    return mask.tolist()


def send_start_signal(socket, env):
    socket.send_string(f"{env['userID']} s")