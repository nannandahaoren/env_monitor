import random
import time

from paho.mqtt import client as mqtt_client

broker = "broker.emqx.io"
port = 1883
topic = "/python/mqtt"


class MQTT:
    def __init__(self, mqtt_type):
        self.client_id = f"python-mqtt-{random.randint(0, 1000)}"
        self.client = mqtt_client.Client(client_id=self.client_id)
        self.client.on_connect = self.on_connect
        self.client.connect(broker, port)

        self.mqtt_type = mqtt_type
        if self.mqtt_type == "pub":
            self.client.on_publish = self.on_publish
        else:
            self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        # 如果是订阅, 则在连接时进行订阅
        if self.mqtt_type == "subs":
            self.client.subscribe(topic=topic)

    def on_message(self, client, userdata, msg):
        print(f"从 '{msg.topic}' 接收到的消息是 '{msg.payload.decode()}'")

    def on_publish(self):
        msg_count = 0
        while True:
            time.sleep(1)
            msg = f"Publish msg :{msg_count}"
            result = self.client.publish(topic, msg)
            # 返回值 result: [0, 1]
            status = result[0]
            if status == 0:
                print(f"给 topic '{topic}' 发送了消息: '{msg}'  ")
            else:
                print(f"给 topic {topic} 发送消息失败!")
            msg_count += 1

    # 启动网络循环
    def forever(self):
        self.client.loop_forever()
