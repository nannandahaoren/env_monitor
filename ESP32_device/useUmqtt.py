import time
import network
import ujson
from simple import MQTTClient  # 上面的步骤就是在下载umqtt.simple到ESP32设备
from machine import Pin
from wifi import do_connect
from umqtt import sub_cb, on_connect, on_message
import array as arr
from kalman_average import Average, Kalmanfilter
import struct
from machine import Pin, SoftI2C
from BME280 import BME280

MQTT_CLIENT = None
LED = None

# 发布订阅模式需要确定订阅什么主题
pub_topic = "temperature"
sub_topic = "sensor"
# 下面根据实际情况进行修改


# ESP32 - Pin assignment
i2c = SoftI2C(scl=Pin(22), sda=Pin(21), freq=10000)

# 存放临时数组的平均值
T = 0
averageNum = 8  # averageNum是平均几个数求平均值，此处设为8


def main():
    global MQTT_CLIENT, LED, i2c, averageNum
    global pub_topic, sub_topic

    # 1.链接WiFi
    do_connect()
    # 创建mqtt客户端
    # 第一个参数 客户端的名字
    # 第二个参数mqtt服务端的ip地址
    # 第三个参数mqtt服务端的端口号
    # 第四个参数mqtt服务端的管理员账号
    # 第五个参数mqtt服务端的管理员密码
    # 第六个参数默认设置
    MQTT_CLIENT = MQTTClient(
        "ESP32_1", "101.43.132.163", 1883, "admin", "Lj112358", keepalive=60
    )

    print("connectted to mqtt_server !")

    MQTT_CLIENT.set_callback(on_message)  # 设置回调函数
    MQTT_CLIENT.connect()  # 建立连接
    MQTT_CLIENT.subscribe(sub_topic)

    time.sleep(1)

    # 维护一个临时数组，用于存储温度值
    temp_array = arr.array("d")

    hum_array = arr.array("d")

    pres_array = arr.array("d")

    # 维护一个存储数组，用于存储到数据库中
    dataset_temp = arr.array("d")

    dataset_time = arr.array("d")

    dataset_hum = arr.array("d")

    dataset_pres = arr.array("d")

    while True:
        bme = BME280(i2c=i2c)
        current_time = time.time()

        # 下方t是读取的温度值,测量值
        str_temp = bme.temperature  # 获取带有字符串C的字符串形式的温度
        str_temp = str_temp.replace("C", "")
        temp = float(str_temp)
        temp_array.append(temp)  # 将温度值添加到临时数组中
        # print("温度的度数是：", temp)
        hum_str = bme.humidity
        hum_str = hum_str.replace("%", "")
        hum = float(hum_str)
        hum_array.append(hum)
        # print("湿度的度数是: ", hum)

        pres = bme.pressure
        pres = pres.replace("hPa", "")
        pres = float(pres)
        pres_array.append(pres)
        # print("大气压的度数是: ", pres)
        # uncomment for temperature in Fahrenheit
        # temp = (bme.read_temperature()/100) * (9/5) + 32
        # temp = str(round(temp, 2)) + 'F'

        if len(temp_array) == averageNum:
            T = Average(temp_array, averageNum)  # 当临时数组的元素的平均数
            H = Average(hum_array, averageNum)
            P = Average(pres_array, averageNum)

            length = len(dataset_temp)  # 计算dataset_temp的长度
            length = len(dataset_hum)
            length = len(dataset_pres)

            if length == 0:
                dataset_temp.append(T)
                dataset_hum.append(H)
                dataset_pres.append(P)
                dataset_time.append(current_time)
            else:
                length -= 1
                pre_T = dataset_temp[length]
                pre_H = dataset_hum[length]
                pre_P = dataset_pres[length]
                current_T = Kalmanfilter(pre_T, T)
                current_H = Kalmanfilter(pre_H, H)
                current_P = Kalmanfilter(pre_P, P)
                round_current_T = round(current_T, 1)
                round_current_H = round(current_H, 1)
                round_current_P = round(current_P, 1)

                print("-----------------------------")
                print("temprature after kalmanfilter is ", round_current_T)
                print("humidity after kalmanfilter is ", round_current_H)
                print("pressure after kalmanfilter is ", round_current_P)

                dataset_temp.append(current_T)
                dataset_hum.append(current_H)
                dataset_pres.append(current_P)
                dataset_time.append(current_time)
                derta_time = current_time - dataset_time[length]
                str_msg = (
                    str(derta_time)
                    + ","
                    + str(round_current_T)
                    + ","
                    + str(round_current_H)
                    + ","
                    + str(round_current_P)
                )

                # msg = struct.pack("f", round_number)
                msg = struct.pack("24s", str_msg.encode("utf-8"))
                MQTT_CLIENT.publish(pub_topic, msg)
            temp_array = []
            hum_array = []
            pres_array = []

        MQTT_CLIENT.check_msg()

        # msg = b"22.78"
        # 发送自动配置MQTT服务的数据包
        if len(dataset_temp) == 16:
            dataset_temp = []
            dataset_hum = []
            dataset_pres = []
            dataset_time = []

            temp_array = []
            hum_array = []
            pres_array = []

        time.sleep(0.36)


if __name__ == "__main__":
    main()
