import time
import urequests
import cyberpi

WIFI_SSID = ""
WIFI_PASS = ""

SERVER_IP = ""
SERVER_PORT = 8080

URL = "http://" + SERVER_IP + ":" + str(SERVER_PORT) + "/status"

mode = 0  # 0 = dashboard, 1 = graph


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
    # LED principal sempre ativo
    set_led(1, r, g, b)
    # LED de alerta
    if cpu < 80:
        set_led(1, r, g, b)
        set_led(2, 0, 0, 0)
    else:
        p = (cpu - 80) / 20.0
        set_led(1, r, g, b)
        set_led(
            2,
            int(r * p),
            int(g * p),
            int(b * p)
        )

    base = metric_color(ram, 60, 85)
    intensity = min(100, abs(ram_d) * 12)
    r, g, b = pulse_color(base, intensity)
    # LED principal sempre ativo
    set_led(3, r, g, b)
    # LED de alerta progressivo
    if ram < 75:
        set_led(4, 0, 0, 0)
    else:
        p = (ram - 75) / 25.0
        set_led(
            4,
            int(r * p),
            int(g * p),
            int(b * p)
        )

    base = metric_color(temp, 60, 75)
    intensity = min(100, abs(temp_d) * 10)
    r, g, b = pulse_color(base, intensity)
    if temp < 60:
        # normal
        set_led(5, r, g, b)
    elif temp < 75:
        # atenção
        set_led(5, r, g, b)
    else:
        # crítico
        # pulse = int(time.time() * 4) % 2
        # if pulse:
            set_led(5, 255, 0, 0)
        # else:
        #     set_led(5, 0, 0, 0)


def render(host, cpu, ram, temp, battery, clock):
    msg = (
        "     {}\n\n"
        " CPU  (g)  {:>3}%\n"
        " MEM  (b)  {:>3}%\n"
        " TEMP (r)  {:>3}C\n"
        " BATT (y)  {:>3}%"
        "       {}\n"
    ).format(host, int(cpu), int(ram), int(temp), battery, clock)

    cyberpi.display.show_label(msg, 0, 0)


def draw_graph(cpu, ram, temp, battery):
    cyberpi.display.set_brush(80, 255, 80) # green
    cyberpi.linechart.add(cpu)

    cyberpi.display.set_brush(80, 120, 255) # blue
    cyberpi.linechart.add(ram)
    
    cyberpi.display.set_brush(255, 80, 80) # red
    cyberpi.linechart.add(temp)

    cyberpi.display.set_brush(255, 255, 80) # yellow
    cyberpi.linechart.add(battery)


def offline_blink():

    for led in range(1, 6):
        cyberpi.led.on(255, 0, 255, led)

    time.sleep(0.2)

    for led in range(1, 6):
        cyberpi.led.on(0, 0, 0, led)


def boot_animation():
    #cyberpi.led.set_bri(100)
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
    global mode

    boot_animation()

    if not connect_wifi():
        show_message("Can't connect to " + str(WIFI_SSID))
        return

    show_message("Connected to " + str(WIFI_SSID))

    time.sleep(0.5)

    last_data = None
    last_fetch = 0

    last_cpu = 0
    last_ram = 0
    last_temp = 0

    while True:

        now = time.time()

        if cyberpi.controller.is_press("a"):
            mode = 1 - mode
            cyberpi.display.clear()
            time.sleep(0.3)

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
            clock = str(last_data.get("time", "--:--"))

            cpu_d = cpu - last_cpu
            ram_d = ram - last_ram
            temp_d = temp - last_temp

            if mode == 0:
                render(host, cpu, ram, temp, battery, clock)
            else:
                draw_graph(cpu, ram, temp, battery)

            update_leds(cpu, ram, temp, cpu_d, ram_d, temp_d)

            last_cpu = cpu
            last_ram = ram
            last_temp = temp

        else:
            offline_blink()
            show_message("Connection lost")

        time.sleep(0.5)

main()
