import math
from servo import Servos
from machine import Pin, I2C

i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=10000)

# 初始化 Servos 对象，指定 PCA9685 地址（默认为 0x40）
s = Servos(i2c, address=0x40)

class LegComponent:
    def __init__(self, sh=None, l1=None, l2=None):
        self.sh = sh
        self.l1 = l1
        self.l2 = l2

    def __repr__(self):
        return f"( sh={self.sh}, l1={self.l1}, l2={self.l2} )"


class Leg:
    def __init__(self):
        # 初始化四个部分
        self.leg_l1 = LegComponent()
        self.leg_l2 = LegComponent()
        self.leg_r1 = LegComponent()
        self.leg_r2 = LegComponent()

    def __repr__(self):
        return (f"leg_l1:{self.leg_l1}\n"
                f"leg_l2:{self.leg_l2}\n"
                f"leg_r1:{self.leg_r1}\n"
                f"leg_r2:{self.leg_r2}\n")

leg = Leg()

leg.leg_l1.sh = (2,145)
leg.leg_l1.l1 = (3,140)
leg.leg_l1.l2 = (6,90)

leg.leg_l2.sh = (8,120)
leg.leg_l2.l1 = (9,140)
leg.leg_l2.l2 = (14,90)

leg.leg_r1.sh = (1,85)
leg.leg_r1.l1 = (0,40)
leg.leg_r1.l2 = (7,100)

leg.leg_r2.sh = (5,135)
leg.leg_r2.l1 = (4,40)
leg.leg_r2.l2 = (15,85)

lz = 0.00
lz1 = 0.00
lz2 = 0.00
lx = 0.00
hu = 7.0
hl = 7.8

def legleft1_A(data_a, data_b):
    s.position(leg.leg_l1.sh[0], leg.leg_l1.sh[1])  # s1
    s.position(leg.leg_l1.l1[0], data_a - 8)  # l1
    s.position(leg.leg_l1.l2[0], data_b + 5)  # l2
    
    rad_a = (data_a - 90) * (math.pi / 180)
    rad_b = data_b * (math.pi / 180)
    rad_th = (math.pi/2 + rad_b - rad_a)
    lz = hu * math.cos(rad_a) + hl * math.sin(rad_th)
    lz1 = hu * math.cos(rad_a)
    lz2 = hl * math.sin(rad_th)
    lx = - (hu * math.sin(rad_a) + hl * math.cos(rad_th))
    return {"lx": lx, "lz": lz , "a": data_a, "b": data_b}

def legleft2_A(data_a, data_b):
    s.position(leg.leg_l2.sh[0], leg.leg_l2.sh[1])  # s1
    s.position(leg.leg_l2.l1[0], data_a)  # l1
    s.position(leg.leg_l2.l2[0], data_b)  # l2
    
    rad_a = (data_a - 90) * (math.pi / 180)
    rad_b = data_b * (math.pi / 180)
    rad_th = (math.pi/2 + rad_b - rad_a)
    lz = hu * math.cos(rad_a) + hl * math.sin(rad_th)
    lz1 = hu * math.cos(rad_a)
    lz2 = hl * math.sin(rad_th)
    lx = - (hu * math.sin(rad_a) + hl * math.cos(rad_th))
    return {"lx": lx, "lz": lz , "a": data_a, "b": data_b}

def legright1_A(data_a, data_b):
    s.position(leg.leg_r1.sh[0], leg.leg_r1.sh[1])  # s1
    s.position(leg.leg_r1.l1[0], 180 - data_a)  # l1
    s.position(leg.leg_r1.l2[0], 180 - data_b)  # l2
    
    rad_a = (data_a - 90) * (math.pi / 180)
    rad_b = data_b * (math.pi / 180)
    rad_th = (math.pi/2 + rad_b - rad_a)
    lz = hu * math.cos(rad_a) + hl * math.sin(rad_th)
    lz1 = hu * math.cos(rad_a)
    lz2 = hl * math.sin(rad_th)
    lx = - (hu * math.sin(rad_a) + hl * math.cos(rad_th))
    return {"lx": lx, "lz": lz , "a": data_a, "b": data_b}

def legright2_A(data_a, data_b):
    s.position(leg.leg_r2.sh[0], leg.leg_r2.sh[1])  # s1
    s.position(leg.leg_r2.l1[0], 180 - data_a)  # l1
    s.position(leg.leg_r2.l2[0], 180 - data_b - 8)  # l2
    
    rad_a = (data_a - 90) * (math.pi / 180)
    rad_b = data_b * (math.pi / 180)
    rad_th = (math.pi/2 + rad_b - rad_a)
    lz = hu * math.cos(rad_a) + hl * math.sin(rad_th)
    lz1 = hu * math.cos(rad_a)
    lz2 = hl * math.sin(rad_th)
    lx = - (hu * math.sin(rad_a) + hl * math.cos(rad_th))
    return {"lx": lx, "lz": lz , "a": data_a, "b": data_b}


