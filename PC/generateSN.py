import time


def generate_serial_number():
    timestamp = int(time.time() * 1000)  # 获取当前时间戳并乘以1000，精确到毫秒级别
    serial_number = "SN{}".format(timestamp)  # 拼接SN前缀和时间戳
    return serial_number


if __name__ == "__main__":
    result = generate_serial_number()
    print(result)
