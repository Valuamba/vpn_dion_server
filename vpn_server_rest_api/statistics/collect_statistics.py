#https://github.com/waterrmalann/NetworkBandwidthMonitor/blob/master/NetworkBandwidthMonitor.py
import tkinter as tk
from psutil import net_io_counters, getloadavg, Process
import psutil
from os import cpu_count, getpid

KB = float(1024)
MB = float(KB ** 2)  # 1,048,576
GB = float(KB ** 3)  # 1,073,741,824
TB = float(KB ** 4)  # 1,099,511,627,776

last_upload, last_download, upload_speed, down_speed = 0, 0, 0, 0


def size(B):
    """Credits: https://stackoverflow.com/a/31631711 (Improved version of it.)"""

    B = float(B)
    if B < KB:
        return f"{B} Bytes"
    elif KB <= B < MB:
        return f"{B / KB:.2f} KB"
    elif MB <= B < GB:
        return f"{B / MB:.2f} MB"
    elif GB <= B < TB:
        return f"{B / GB:.2f} GB"
    elif TB <= B:
        return f"{B / TB:.2f} TB"


def get_cpu():
    l1, l2, l3 = getloadavg()
    CPU_use = (l3 / cpu_count()) * 100

    return CPU_use


def get_ram():
    process = Process(getpid())
    return round(process.memory_info().rss / (10 * 6))


def get_network_statistics():
    global last_upload, last_download, upload_speed, down_speed
    counter = net_io_counters()

    upload = counter.bytes_sent
    download = counter.bytes_recv
    total = upload + download

    if last_upload > 0:
        if upload < last_upload:
            upload_speed = 0
        else:
            upload_speed = upload - last_upload

    if last_download > 0:
        if download < last_download:
            down_speed = 0
        else:
            down_speed = download - last_download

    last_upload = upload
    last_download = download

    print(f"{size(upload)} ({upload} Bytes)")
    print(f"{size(download)} ({download} Bytes)")
    print(f"{size(total)}\n")

    print(size(upload_speed))
    print(size(down_speed))

    return (upload, download, total, upload_speed, down_speed)


