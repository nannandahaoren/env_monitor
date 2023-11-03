from machine import Pin, I2C
from time import sleep
import BME280
import array as arr

# 计算平均温度
def tempAverage(temp):
    total = 0
    for i in range(5):
        total += temp[i]
    return total / 5.0


# temp是上一时刻的温度值，temp是存储在dataset_temp中的最后一个元素
def tempKalman(temp,T):
    
    currntTemp = temp + 0.3 * (T - temp)
    print('temprature after kalmanfilter is ',currntTemp)
    return currntTemp


