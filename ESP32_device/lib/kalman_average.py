from machine import Pin, I2C
from time import sleep
import BME280
import array as arr


# 计算平均温度
def Average(temp, averageNum):
    total = 0
    for i in range(averageNum):
        total += temp[i]
    return total / averageNum


# temp是上一时刻的温度值，temp是存储在dataset_temp中的最后一个元素
def Kalmanfilter(pre, measure):
    currnt = pre + 0.3 * (measure - pre)
    # print("temprature after kalmanfilter is ", currnt)
    return currnt
