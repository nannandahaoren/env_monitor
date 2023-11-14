# MicroPython SH1106 OLED driver
#
# Pin Map I2C for ESP8266
#   - 3v - xxxxxx   - Vcc
#   - G  - xxxxxx   - Gnd
#   - D2 - GPIO 5   - SCK / SCL
#   - D1 - GPIO 4   - DIN / SDA
#   - D0 - GPIO 16  - Res (required, unless a Hardware reset circuit is connected)
#   - G  - xxxxxx     CS
#   - G  - xxxxxx     D/C
#
# Pin's for I2C can be set almost arbitrary
#
from machine import Pin, I2C
import sh1106  # 用于oled屏幕的显示


# 创建I2C对象，指定了SCL引脚和SDA引脚的GPIO编号以及通信频率
i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
# 创建sh1106.SH1106_I2C对象
# 执行显示屏的尺寸为128*64
# 使用前面创建的i2c对象进行通信
# GPIO引脚16作为复位引脚
# i2c的地址为0x3C
display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3C)
display.sleep(False)  # 这行代码调用sleep()方法，将显示屏从睡眠模式中唤醒。

# 这行代码使用fill()方法清空显示屏上的内容。参数0表示黑色，将显示屏填充为黑色，相当于清空屏幕。
display.fill(0)

# 这行代码使用text()方法在坐标（0,0）的位置显示文本内容为"Testing 1"。最后一个参数1表示颜色为白色。
display.hline(0, 0, 1, 1)
display.text("Testing 1", 0, 0, 1)
display.text("hello ", 6, 0, 1)

# 之前进行的显示操作刷新到屏幕上，使得内容可见。
display.show()
