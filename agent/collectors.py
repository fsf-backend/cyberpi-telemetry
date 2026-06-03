#!/usr/bin/env python3

import os
import socket
import psutil


def get_hostname():
    return socket.gethostname()


def get_cpu_percent():
    return int(psutil.cpu_percent(interval=0.2))


def get_ram_percent():
    return int(psutil.virtual_memory().percent)


def get_cpu_temp():
    temps = psutil.sensors_temperatures()

    candidates = (
        "coretemp",
        "k10temp",
        "cpu_thermal",
        "acpitz"
    )

    for name in candidates:
        if name in temps and temps[name]:
            return int(temps[name][0].current)

    try:
        with open(
            "/sys/class/thermal/thermal_zone0/temp",
            "r"
        ) as f:
            return int(int(f.read().strip()) / 1000)
    except Exception:
        pass

    return 0


def collect():

    return {
        "host": get_hostname(),
        "cpu": get_cpu_percent(),
        "ram": get_ram_percent(),
        "temp": get_cpu_temp()
    }
