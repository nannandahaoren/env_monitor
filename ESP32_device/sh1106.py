#
# MicroPython SH1106 OLED driver, I2C and SPI interfaces
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Radomir Dopieralski (@deshipu),
#               2017-2021 Robert Hammelrath (@robert-hh)
#               2021 Tim Weber (@scy)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Sample code sections for ESP8266 pin assignments
# ------------ SPI ------------------
# Pin Map SPI
#   - 3v - xxxxxx   - Vcc
#   - G  - xxxxxx   - Gnd
#   - D7 - GPIO 13  - Din / MOSI fixed
#   - D5 - GPIO 14  - Clk / Sck fixed
#   - D8 - GPIO 4   - CS (optional, if the only connected device)
#   - D2 - GPIO 5   - D/C
#   - D1 - GPIO 2   - Res
#
# for CS, D/C and Res other ports may be chosen.
#
# from machine import Pin, SPI
# import sh1106

# spi = SPI(1, baudrate=1000000)
# display = sh1106.SH1106_SPI(128, 64, spi, Pin(5), Pin(2), Pin(4))
# display.sleep(False)
# display.fill(0)
# display.text('Testing 1', 0, 0, 1)
# display.show()
#
# --------------- I2C ------------------
#
# Pin Map I2C
#   - 3v - xxxxxx   - Vcc
#   - G  - xxxxxx   - Gnd
#   - D2 - GPIO 5   - SCK / SCL
#   - D1 - GPIO 4   - DIN / SDA
#   - D0 - GPIO 16  - Res
#   - G  - xxxxxx     CS
#   - G  - xxxxxx     D/C
#
# Pin's for I2C can be set almost arbitrary
#
# from machine import Pin, I2C
# import sh1106
#
# i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
# display = sh1106.SH1106_I2C(128, 64, i2c, Pin(16), 0x3c)
# display.sleep(False)
# display.fill(0)
# display.text('Testing 1', 0, 0, 1)
# display.show()

from micropython import const
import utime as time
import framebuf


# a few register definitions
_SET_CONTRAST = const(0x81)
_SET_NORM_INV = const(0xA6)
_SET_DISP = const(0xAE)
_SET_SCAN_DIR = const(0xC0)
_SET_SEG_REMAP = const(0xA0)
_LOW_COLUMN_ADDRESS = const(0x00)
_HIGH_COLUMN_ADDRESS = const(0x10)
_SET_PAGE_ADDRESS = const(0xB0)


class SH1106(framebuf.FrameBuffer):
    def __init__(self, width, height, external_vcc, rotate=0):
        self.width = width
        self.height = height
        self.external_vcc = external_vcc  # 表示是否使用外部电源供电
        self.flip_en = rotate == 180 or rotate == 270
        self.rotate90 = rotate == 90 or rotate == 270

        # 这个属性表示显示的内容被分成了多少页，每页高度为8个像素。
        self.pages = self.height // 8  # 取整除 - 返回商的整数部分（向下取整）
        self.bufsize = self.pages * self.width  # 这个属性表示帧缓冲区的大小，即存储显示内容所需的字节数。
        self.renderbuf = bytearray(
            self.bufsize
        )  # 创建一个大小为self.bufsize的字节数组，并将其分配给self.renderbuf属性。这个属性表示用于渲染显示内容的缓冲区。
        self.pages_to_update = 0  # 这个属性表示需要更新的页数，初始值为0。d

        # 如果为true表示需要旋转90度
        if self.rotate90:
            self.displaybuf = bytearray(
                self.bufsize
            )  # 创建一个大小为self.bufsize的新字节数组，并将其分配给self.displaybuf属性。
            # HMSB is required to keep the bit order in the render buffer
            # compatible with byte-for-byte remapping to the display buffer,
            # which is in VLSB. Else we'd have to copy bit-by-bit!
            super().__init__(
                self.renderbuf, self.height, self.width, framebuf.MONO_HMSB
            )  # 用于将内容从self.renderbuf渲染到self.displaybuf。
        else:
            self.displaybuf = self.renderbuf
            super().__init__(
                self.renderbuf, self.width, self.height, framebuf.MONO_VLSB
            )

        # flip() was called rotate() once, provide backwards compatibility.
        self.rotate = self.flip
        self.init_display()

    # 初始化显示
    def init_display(self):
        self.reset()  # 调用reset()方法来进行显示设备的复位操作。
        self.fill(0)  # 将显示缓冲区中的所有像素设置为0，即清空显示内容。
        self.show()  # 更新显示设备，将显示缓冲区中的内容刷新到实际的显示屏上。
        self.poweron()  # 调用poweron()方法来打开显示设备的电源，以准备显示操作。
        # rotate90 requires a call to flip() for setting up.
        self.flip(
            self.flip_en
        )  # 根据self.flip_en属性的值，如果为True，则调用flip(True)方法来翻转显示设备，否则不进行翻转操作。

    # _SET_DISP | 0x00表示命令字节，用于设置显示设备的显示开关控制位为0，即关闭显示设备。
    # self.write_cmd(_SET_DISP | 0x00)调用write_cmd()方法，将命令字节发送给显示设备，以执行关机操作。
    def poweroff(self):
        self.write_cmd(_SET_DISP | 0x00)

    # _SET_DISP | 0x01表示命令字节，用于设置显示设备的显示开关控制位为1，即打开显示设备。
    # self.write_cmd(_SET_DISP | 0x01)调用write_cmd()方法，将命令字节发送给显示设备，以执行开机操作。
    def poweron(self):
        self.write_cmd(_SET_DISP | 0x01)
        if self.delay:
            time.sleep_ms(self.delay)

    def flip(self, flag=None, update=True):
        if flag is None:
            flag = not self.flip_en
        mir_v = flag ^ self.rotate90
        mir_h = flag
        self.write_cmd(_SET_SEG_REMAP | (0x01 if mir_v else 0x00))
        self.write_cmd(_SET_SCAN_DIR | (0x08 if mir_h else 0x00))
        self.flip_en = flag
        if update:
            self.show(True)  # full update

    """
        _SET_DISP | (not value)表示命令字节，用于设置显示设备的休眠控制位。
        value是一个布尔值,如果为True,则将休眠控制位设置为0,表示进入休眠状态;
        如果为False,则将休眠控制位设置为1,表示退出休眠状态。
        self.write_cmd(_SET_DISP | (not value))调用write_cmd()方法，将命令字节发送给显示设备，以控制休眠状态的切换。
    
    """

    def sleep(self, value):
        self.write_cmd(_SET_DISP | (not value))

    """
    在给定的代码中,contrast(self, contrast)方法用于设置显示设备的对比度。
    _SET_CONTRAST是一个表示设置对比度的命令字节。
    self.write_cmd(_SET_CONTRAST)调用write_cmd()方法，将设置对比度的命令字节发送给显示设备。
    self.write_cmd(contrast)调用write_cmd()方法，将指定的对比度值 contrast 发送给显示设备
    """

    def contrast(self, contrast):
        self.write_cmd(_SET_CONTRAST)
        self.write_cmd(contrast)

    """
        在给定的代码中,invert(self, invert)方法用于控制显示设备的反转（倒置）模式。
        _SET_NORM_INV是一个表示设置正常/反转模式的命令字节。
        (invert & 1)是一个位运算，将invert参数与1进行按位与运算，以确保只使用invert参数的最低位（LSB）。
        self.write_cmd(_SET_NORM_INV | (invert & 1))调用write_cmd()方法，将设置正常/反转模式的命令字节发送给显示设备。
    """

    def invert(self, invert):
        self.write_cmd(_SET_NORM_INV | (invert & 1))

    # 写入一次新内容，需要调用show方法
    # full_update=False是一个可选的参数，如果full_update为True，则会进行完全更新，否则仅更新需要更新的页面。
    def show(self, full_update=False):
        # self.* lookups in loops take significant time (~4fps).
        # 是将一些属性值赋给临时变量以提高循环中的性能。
        (w, p, db, rb) = (self.width, self.pages, self.displaybuf, self.renderbuf)

        # 判断是否需要旋转90度。如果self.rotate90为True，则需要进行90度旋转。
        if self.rotate90:
            # 循环遍历显示缓冲区的索引
            for i in range(self.bufsize):
                # 根据旋转和索引计算，在显示缓冲区中设置像素值。
                db[w * (i % p) + (i // p)] = rb[i]
        if full_update:
            pages_to_update = (1 << self.pages) - 1
        else:
            pages_to_update = self.pages_to_update
        # print("Updating pages: {:08b}".format(pages_to_update))
        for page in range(self.pages):
            if pages_to_update & (1 << page):
                self.write_cmd(_SET_PAGE_ADDRESS | page)
                self.write_cmd(_LOW_COLUMN_ADDRESS | 2)
                self.write_cmd(_HIGH_COLUMN_ADDRESS | 0)
                self.write_data(db[(w * page) : (w * page + w)])
        self.pages_to_update = 0

    def pixel(self, x, y, color=None):
        if color is None:
            return super().pixel(x, y)  # 用于获取指定坐标位置的像素值。如果color为None，则直接返回该像素值。
        else:
            super().pixel(x, y, color)  # 用于设置指定坐标位置的像素值为新的颜色。
            page = y // 8  # 用于计算像素所在的页面
            self.pages_to_update |= 1 << page

    def text(self, text, x, y, color=1):
        super().text(text, x, y, color)
        self.register_updates(y, y + 7)

    def line(self, x0, y0, x1, y1, color):
        super().line(x0, y0, x1, y1, color)
        self.register_updates(y0, y1)

    def hline(self, x, y, w, color):
        super().hline(x, y, w, color)
        self.register_updates(y)

    def vline(self, x, y, h, color):
        super().vline(x, y, h, color)
        self.register_updates(y, y + h - 1)

    def fill(self, color):
        super().fill(color)
        self.pages_to_update = (1 << self.pages) - 1

    def blit(self, fbuf, x, y, key=-1, palette=None):
        super().blit(fbuf, x, y, key, palette)
        self.register_updates(y, y + self.height)

    def scroll(self, x, y):
        # my understanding is that scroll() does a full screen change
        super().scroll(x, y)
        self.pages_to_update = (1 << self.pages) - 1

    def fill_rect(self, x, y, w, h, color):
        super().fill_rect(x, y, w, h, color)
        self.register_updates(y, y + h - 1)

    def rect(self, x, y, w, h, color):
        super().rect(x, y, w, h, color)
        self.register_updates(y, y + h - 1)

    def register_updates(self, y0, y1=None):
        # this function takes the top and optional bottom address of the changes made
        # and updates the pages_to_change list with any changed pages
        # that are not yet on the list
        start_page = max(0, y0 // 8)
        end_page = max(0, y1 // 8) if y1 is not None else start_page
        # rearrange start_page and end_page if coordinates were given from bottom to top
        if start_page > end_page:
            start_page, end_page = end_page, start_page
        for page in range(start_page, end_page + 1):
            self.pages_to_update |= 1 << page

    def reset(self, res):
        if res is not None:
            res(1)
            time.sleep_ms(1)
            res(0)
            time.sleep_ms(20)
            res(1)
            time.sleep_ms(20)


class SH1106_I2C(SH1106):
    def __init__(
        self,
        width,
        height,
        i2c,
        res=None,
        addr=0x3C,
        rotate=0,
        external_vcc=False,
        delay=0,
    ):
        self.i2c = i2c
        self.addr = addr
        self.res = res
        self.temp = bytearray(2)
        self.delay = delay
        if res is not None:
            res.init(res.OUT, value=1)
        super().__init__(width, height, external_vcc, rotate)

    def write_cmd(self, cmd):
        self.temp[0] = 0x80  # Co=1, D/C#=0
        self.temp[1] = cmd
        self.i2c.writeto(self.addr, self.temp)

    def write_data(self, buf):
        self.i2c.writeto(self.addr, b"\x40" + buf)

    def reset(self):
        super().reset(self.res)


class SH1106_SPI(SH1106):
    def __init__(
        self,
        width,
        height,
        spi,
        dc,
        res=None,
        cs=None,
        rotate=0,
        external_vcc=False,
        delay=0,
    ):
        dc.init(dc.OUT, value=0)
        if res is not None:
            res.init(res.OUT, value=0)
        if cs is not None:
            cs.init(cs.OUT, value=1)
        self.spi = spi
        self.dc = dc
        self.res = res
        self.cs = cs
        self.delay = delay
        super().__init__(width, height, external_vcc, rotate)

    def write_cmd(self, cmd):
        if self.cs is not None:
            self.cs(1)
            self.dc(0)
            self.cs(0)
            self.spi.write(bytearray([cmd]))
            self.cs(1)
        else:
            self.dc(0)
            self.spi.write(bytearray([cmd]))

    def write_data(self, buf):
        if self.cs is not None:
            self.cs(1)
            self.dc(1)
            self.cs(0)
            self.spi.write(buf)
            self.cs(1)
        else:
            self.dc(1)
            self.spi.write(buf)

    def reset(self):
        super().reset(self.res)
