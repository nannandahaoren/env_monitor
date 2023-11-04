import paho.mqtt.client as mqtt
import random
import time
import struct
import csv
from pymysql import *

csv_file = "data.csv"
broker = "101.43.132.163"
port = 1883
client_id = f"python-mqtt-{random.randint(0, 1000)}"
username = "emqx"
password = "public"
msg = b"hello_esp32"
# 数据库device_info中表的名字，对应唯一的SN号码
dataBaseName = "device_1_SN1699081164022"


# The callback for when the client receives a CONNACK response from the server.
def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))

    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.


# The callback for when a PUBLISH message is received from the server.
# subscribe 订阅到相应的主题后，打印该主题和对应的消息，消息是字节的形式，需要转化为字符串或者数字型
def on_message(client, userdata, msg, Cursor, conn):
    float_number = struct.unpack("f", msg.payload)[0]
    print(msg.topic + " " + str(float_number))
    # 将收到的信息写入到数据库,构造执行语句
    mysql_command = "insert into" + " " + dataBaseName + " "
    mysql_command = mysql_command + "values(" + "now()" + "," + str(float_number) + ")"

    # 执行insert语句，并返回受影响的行数：添加一条数据
    count = Cursor.execute(mysql_command)
    # 提交之前的操作，如果之前已经之执行过多次的execute，那么就都进行提交
    # 必须提交这个才能使上面的语句生效
    conn.commit()


def createCursor():
    # 创建Connection连接
    #
    conn = connect(
        host="localhost",
        port=3306,
        database="env_monitor",
        user="root",
        password="lj19906788",
        charset="utf8",
    )
    # 获得Cursor对象
    cs1 = conn.cursor()

    return cs1, conn

    # # 关闭Cursor对象
    # cs1.close()
    # # 关闭Connection对象
    # conn.close()


if __name__ == "__main__":
    # 创建游标
    Cursor, conn = createCursor()

    client = mqtt.Client(client_id)
    client.on_connect = on_connect
    client.on_message = lambda client, userdata, msg: on_message(
        client, userdata, msg, Cursor=Cursor, conn=conn
    )
    client.username_pw_set(username, password)  # 设置用户名和密码
    client.connect(broker, port, 60)
    client.subscribe(topic="temperature")
    client.publish("sensor", msg)
    # print("publish_msg_is_done!")
    # Blocking call that processes network traffic, dispatches callbacks and
    # handles reconnecting.
    # Other loop*() functions are available that give a threaded interface and a
    # manual interface.
    client.loop_forever()
