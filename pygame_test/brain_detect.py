import socket
import struct


def main_brain(msg_queue):
    # 创建 UDP 套接字，并绑定到指定的 IP 地址和端口号
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_socket.bind(("192.168.43.54", 6666))


    print("UDP server started, listening on port 6666...")
    while True:
        # 接收 UDP 数据包，最多接收 1024 字节的数据
        data, addr = udp_socket.recvfrom(1024)
        msg = struct.unpack('>f', data[1:])[0]
        # 输出接收到的数据和发送方的 IP 地址和端口号
        msg_queue.put(msg)
        print(f"Received data from {addr}: {msg}")


if __name__ == "__main__":
    main_brain()
