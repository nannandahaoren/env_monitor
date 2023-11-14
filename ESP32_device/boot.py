# This file is executed on every boot (including wake-boot from deepsleep)
# import esp
# esp.osdebug(None)
# import webrepl
# webrepl.start()

import machine


def boot():
    execfile("main.py")


if __name__ == "__main__":
    try:
        boot()
    except PermissionError:
        machine.reset()
