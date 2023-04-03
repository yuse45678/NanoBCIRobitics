# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : RaspberryPi.py
@Project  : NanoBCIRobitics
@Time     : 2023/4/3 15:14
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/4/3 15:14        1.0             None
"""
import RPi.GPIO as GPIO
from SSVEP.Inspire.utils import mapping
import time


def loop_remote(trial_timer, LED_List, trial_duration, evoke_duration):
    trial_time = time.time() - trial_timer
    while trial_time < trial_duration:
        if trial_time < evoke_duration:
            for Led in LED_List:
                pass_time = trial_time - Led.counter * Led.half_period * 2
                if pass_time < Led.half_period:
                    Led.turn_off()
                elif Led.half_period < pass_time < Led.half_period * 2:
                    Led.turn_on()
                elif pass_time > Led.half_period * 2:
                    Led.counter += 1
                    Led.turn_off()
        elif evoke_duration < trial_time < trial_duration:
            for Led in LED_List:
                Led.turn_off()
                print("%s: count %d" % (Led.name, Led.counter))
            break
        trial_time = time.time() - trial_timer
    for Led in LED_List:
        Led.counter = 0


class LED:

    RED = [255, 20, 5]
    GREEN = [0, 200, 0]
    BLUE = [0, 0, 255]
    WHITE = [200, 200, 200]
    YELLOW = [255, 255, 0]
    SALLOW_GREEN = [0, 150, 50]
    SALLOW_RED = [200, 50, 20]

    def __init__(self, pins, name):
        '''
        树莓派控制LED

        ----------------

        :param pins: 当前LED引脚（3位）
        :param name: 当前LED灯的标识
        '''
        self.name = name
        self.colors = [0, 0, 0]
        self.frequency = 220
        self.evoke_fre = 1.0
        self.half_period = 0.5 / self.evoke_fre
        self.state = 'off'
        self.counter = 0
        self.PWMs = []
        for pin in pins:
            GPIO.setup(pin, GPIO.OUT)
            pwm = GPIO.PWM(pin, self.frequency)
            pwm.start(0)
            self.PWMs = self.PWMs + [pwm]

    def set_color(self, colors):
        '''
        设置LED颜色

        -----------------

        :param colors: RGB颜色数组，可直接调用当前类的常量，如LED.RED
        '''
        self.colors = colors
        r_val = mapping(colors[0], 0, 255, 0, 100)  # change a num(0-255) to (0-100).
        g_val = mapping(colors[1], 0, 255, 0, 100)
        b_val = mapping(colors[2], 0, 255, 0, 100)
        self.PWMs[0].ChangeDutyCycle(100 - r_val)  # Change duty cycle
        self.PWMs[1].ChangeDutyCycle(100 - g_val)
        self.PWMs[2].ChangeDutyCycle(100 - b_val)
        return self

    def set_evoke_fre(self, evoke_fre):
        '''
        设置视觉刺激频率

        ----------------

        :param evoke_fre: 视觉刺激频率（单位：Hz）
        :return:
        '''
        self.evoke_fre = evoke_fre
        self.half_period = 0.5 / evoke_fre
        return self

    def turn_on(self):
        if self.state == 'off':
            self.set_color(self.colors)
            self.state = 'on'

    def turn_off(self):
        if self.state == 'on':
            self.PWMs[0].ChangeDutyCycle(100)
            self.PWMs[1].ChangeDutyCycle(100)
            self.PWMs[2].ChangeDutyCycle(100)
            self.state = 'off'


if __name__ == '__main__':
    pass
