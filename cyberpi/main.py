import time
import urequests
import cyberpi

WIFI_SSID = ""
WIFI_PASS = ""

SERVER_IP = ""
SERVER_PORT = 8080

URL = "http://" + SERVER_IP + ":" + str(SERVER_PORT) + "/status"


def show_message(msg):
    cyberpi.display.clear()
    cyberpi.display.show_label(str(msg), 0, 0)


def connect_wifi():

    dots = ["   ", ".  ", ".. ", "..."]

    show_message("Connecting to\n" + str(WIFI_SSID))

    try:
        cyberpi.wifi.connect(WIFI_SSID, WIFI_PASS)
    except:
        show_message("WIFI ERR")
        return False

    timeout = 20
    i = 0

    while timeout > 0:

        try:
            if cyberpi.wifi.is_connected():
                return True
        except:
            pass

        show_message("Connecting to " + str(WIFI_SSID) + dots[i % 4])

        i += 1
        time.sleep(1)
        timeout -= 1

    return False


def fetch_status():

    response = None

    try:
        response = urequests.get(URL)

        if response.status_code != 200:
            return None

        return response.json()

    except:
        return None

    finally:
        try:
            if response:
                response.close()
        except:
            pass


def set_led(led, r, g, b):
    cyberpi.led.on(r, g, b, led)


def pulse_color(base_color, intensity):
    r, g, b = base_color
    factor = 0.4 + (intensity / 100.0) * 0.6
    return (
        int(r * factor),
        int(g * factor),
        int(b * factor)
    )


def metric_color(value, warn, critical):

    if value >= critical:
        return (255, 0, 0)

    if value >= warn:
        return (255, 255, 0)

    return (0, 255, 0)


def update_leds(cpu, ram, temp, cpu_d, ram_d, temp_d):

    base = metric_color(cpu, 70, 90)
    intensity = min(100, abs(cpu_d) * 12)
    r, g, b = pulse_color(base, intensity)
    set_led(1, r, g, b)
    set_led(2, r, g, b)

    base = metric_color(ram, 60, 85)
    intensity = min(100, abs(ram_d) * 12)
    r, g, b = pulse_color(base, intensity)
    set_led(3, r, g, b)
    set_led(4, r, g, b)

    base = metric_color(temp, 60, 75)
    intensity = min(100, abs(temp_d) * 10)
    r, g, b = pulse_color(base, intensity)
    set_led(5, r, g, b)


def render(host, cpu, ram, temp, battery):

    msg = (
        "     {}\n\n"
        " CPU       {:>3}%\n"
        " MEM       {:>3}%\n"
        " TEMP      {:>3}C\n"
        " BATT      {:>3}%"
    ).format(host, int(cpu), int(ram), int(temp), battery)

    cyberpi.display.show_label(msg, 0, 0)

    update_leds(cpu, ram, temp, 0, 0, 0)


def offline_blink():

    for led in range(1, 6):
        cyberpi.led.on(255, 0, 255, led)

    time.sleep(0.2)

    for led in range(1, 6):
        cyberpi.led.on(0, 0, 0, led)


def boot_animation():

    colors = [
        (255, 0, 0),
        (255, 128, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 0, 255)
    ]

    show_message(
        "***************\n"
        "*             *\n"
        "*   CyberPi   *\n"
        "*  Telemetry  *\n"
        "*   v0.1.0    *\n"
        "*             *\n"
        "***************"
    )

    # v3
    for led in range(1, 6):
        r, g, b = colors[led - 1]
        cyberpi.led.on(r, g, b, led)
        time.sleep(0.15)

    time.sleep(0.3)

    for led in range(5, 0, -1):
        cyberpi.led.on(0, 0, 0, led)
        time.sleep(0.10)

    time.sleep(0.4)

    # v2
#     for led in range(1, 6):

#         r, g, b = colors[led - 1]

#         cyberpi.led.on(
#             r,
#             g,
#             b,
#             led
#         )

#         time.sleep(1)

#     time.sleep(1)

    # v1
#     for led in range(1, 6):
#         r, g, b = colors[led - 1]
#         cyberpi.led.on(r, g, b, led)
#         time.sleep(0.50)
#         cyberpi.led.on(0, 0, 0, led)

#     time.sleep(1)


def main():

    boot_animation()

    if not connect_wifi():
        show_message("Can't connect to " + str(WIFI_SSID))
        return

    show_message("Connected to " + str(WIFI_SSID))

    time.sleep(1)

    last_data = None
    last_fetch = 0

    last_cpu = 0
    last_ram = 0
    last_temp = 0

    while True:

        now = time.time()

        if now - last_fetch > 3:
            last_fetch = now
            data = fetch_status()
            if data:
                last_data = data

        if last_data:

            host = str(last_data.get("host", "?"))
            cpu = int(last_data.get("cpu", 0) or 0)
            ram = int(last_data.get("ram", 0) or 0)
            temp = int(last_data.get("temp", 0) or 0)
            battery = int(cyberpi.get_battery() or 0)

            cpu_d = cpu - last_cpu
            ram_d = ram - last_ram
            temp_d = temp - last_temp

            render(host, cpu, ram, temp, battery)
            update_leds(cpu, ram, temp, cpu_d, ram_d, temp_d)

            last_cpu = cpu
            last_ram = ram
            last_temp = temp

        else:
            offline_blink()
            show_message("HOST\nOFFLINE\nCHECK WIFI")

        time.sleep(0.5)

main()
