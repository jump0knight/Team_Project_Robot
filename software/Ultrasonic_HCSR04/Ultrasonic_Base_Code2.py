#Date: 11/03/2025
#Authour: Benjamin Attwell

from machine import Pin
import time, utime

def HCSR04(TPIN, EPIN): #setup distance sensor using pin numbers set as arguments
    
    trig = Pin(TPIN.OUT)
    echo = Pin(EPIN.IN)
    
    trig.low()
    time.sleep_us(2)
    trig.high()
    time.sleep_us(5)
    trig.low()
    
    while echo.value() == 0:
        off = utime.ticks_us()
    while echo.value() == 1:
        on = utime.ticks_us()
        
    delay = on - off
    distance = (delay*0.0343)/2
    
    return distance