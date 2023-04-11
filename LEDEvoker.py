# !/usr/bin/env python3
# _*_ coding:utf-8 _*_
"""
@File     : LEDEvoker.py
@Project  : NanoBCIRobitics
@Time     : 2023/4/3 18:51
@Author   : Li JiaYi
@Software : PyCharm
@License  : (C)Copyright 2020-2030
@Last Modify Time      @Version     @Desciption
--------------------       --------        -----------
2023/4/3 18:51        1.0             None
"""
from SSVEP.Inspire.RaspberryPi import LED, loop_remote

import RPi.GPIO as GPIO
import time



if __name__ == "__main__":
    # GPIO.setmode(GPIO.BOARD)
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)

    trial_label = [1, 4, 3, 2, 1, 3, 1, 4, 2, 3, 3, 2, 4, 1, 4, 2, 3, 1, 4, 2]
    ONLINE = 0
    LED_NUM = 4

    colors1 = [LED.GREEN, LED.GREEN, LED.GREEN, LED.GREEN]
    colors2 = [LED.GREEN, LED.GREEN, LED.GREEN, LED.GREEN]
    if ONLINE:
        LED1_color = LED.GREEN
        evoke_duration = 2
        trial_duration = 3
    else:
        LED1_color = LED.YELLOW
        evoke_duration = 3
        trial_duration = 4

    # Led1 = LED([8, 12, 10], "Led1").set_color(LED1_color).set_evoke_fre(11.1)
    # Led2 = LED([11, 15, 13], "Led2").set_color(colors1[1]).set_evoke_fre(12.4)
    # Led3 = LED([22, 16, 18], "Led3").set_color(colors1[2]).set_evoke_fre(9.8)
    # Led4 = LED([7, 3, 5], "Led4").set_color(colors1[3]).set_evoke_fre(13.7)

    # Led1 = LED([12, 18, 16], "Led1").set_color(LED1_color).set_evoke_fre(11.1)
    # Led2 = LED([29, 33, 31], "Led2").set_color(colors1[1]).set_evoke_fre(12.4)
    # Led3 = LED([22, 36, 32], "Led3").set_color(colors1[2]).set_evoke_fre(9.8)
    # Led4 = LED([7, 13, 11], "Led4").set_color(colors1[3]).set_evoke_fre(13.7)
    # # 上
    # Led1 = LED([18, 24, 23], "Led1").set_color(colors1[0]).set_evoke_fre(11.1)
    # # 左
    # Led2 = LED([19, 20, 26], "Led2").set_color(colors1[1]).set_evoke_fre(12.4)
    # # 有
    # Led3 = LED([25, 16, 12], "Led3").set_color(colors1[2]).set_evoke_fre(9.8)
    # # 下
    # Led4 = LED([17, 22, 27], "Led4").set_color(colors1[3]).set_evoke_fre(13.7)

    Led1 = LED([12, 18, 16], "Led1").set_color(LED.GREEN).set_evoke_fre(11.1)
    Led2 = LED([22, 36, 32], "Led2").set_color(LED.GREEN).set_evoke_fre(12.4)
    Led3 = LED([35, 38, 37], "Led3").set_color(LED.GREEN).set_evoke_fre(9.8)
    Led4 = LED([11, 15, 13], "Led4").set_color(LED.GREEN).set_evoke_fre(13.7)

    try:
        trial_timer = time.time()
        # /dev/ttyUSB0

        # triggerbox = TriggerBox("COM1")
        #for i in trial_label:
            #  triggerbox.output_event_data(i)
        loop_remote(trial_timer,[Led4],trial_duration,evoke_duration)
        GPIO.cleanup()


    except KeyboardInterrupt:
        GPIO.cleanup()

