# How to use these Library

## -------environment-------  Raspberry PI PICO ------ Mico Python



## First. Connect the PCA9685 

SCL - GPIO3

SDA - GPIO2

## Second. Put These three files in Pico

![image-20250311154000070](C:\Users\JUMPKINGHT\AppData\Roaming\Typora\typora-user-images\image-20250311154000070.png)

## Then. We make a main file to run the leg

```python
import leg
import math , time

print(leg.legleft1_A(160,120))
print(leg.legleft2_A(160,120))
print(leg.legright1_A(160,120))
print(leg.legright2_A(160,120))
```

## Final run  it you will see this data back . So it working.

![image-20250311154258168](C:\Users\JUMPKINGHT\AppData\Roaming\Typora\typora-user-images\image-20250311154258168.png)