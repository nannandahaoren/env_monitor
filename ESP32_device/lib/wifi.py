
import network
import time


def do_connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        # wlan.connect('yutian', 'lj112358')
        wlan.connect('monster', 'lj112358')
        # wlan.connect('津发科技_5G', 'kingfarwuxian')
        i = 1
        while not wlan.isconnected():
            print("正在链接...{}".format(i))
            i += 1
            time.sleep(1)
    print('network config:', wlan.ifconfig())
    return wlan



