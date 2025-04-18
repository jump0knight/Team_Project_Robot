import machine
import time
import uasyncio as asyncio
import leg
import math
from machine import Pin, time_pulse_us, I2C

# ---------------- MPU6050 Class ----------------
class MPU6050:
    def __init__(self, i2c, addr=0x68):
        self.i2c = i2c
        self.addr = addr
        self.i2c.writeto_mem(self.addr, 0x6B, b'\x00')  # Wake up MPU6050

    def read_raw(self, reg):
        data = self.i2c.readfrom_mem(self.addr, reg, 2)
        value = (data[0] << 8) | data[1]
        if value >= 0x8000:
            value = -((65535 - value) + 1)
        return value

    def get_accel(self):
        ax = self.read_raw(0x3B)
        ay = self.read_raw(0x3D)
        az = self.read_raw(0x3F)
        return ax, ay, az

    def get_gyro(self):
        gx = self.read_raw(0x43)
        gy = self.read_raw(0x45)
        gz = self.read_raw(0x47)
        return gx, gy, gz

# ---------------- Init ----------------
i2c = I2C(0, scl=Pin(13), sda=Pin(12), freq=400000)
mpu = MPU6050(i2c)
uart = machine.UART(1, baudrate=115200, tx=machine.Pin(4), rx=machine.Pin(5))

# ---------------- Global State ----------------
current_mode = "stop"
front_distance = 100
back_distance = 100

HEADER1 = 0xFF
HEADER2 = 0xAA
FOOTER1 = 0xBF
FOOTER2 = 0xC0

sensor1 = {'trig': Pin(16, Pin.OUT), 'echo': Pin(17, Pin.IN), 'name': 'Ultrasonic1'}
sensor2 = {'trig': Pin(14, Pin.OUT), 'echo': Pin(15, Pin.IN), 'name': 'Ultrasonic2'}

# ---------------- Gait ----------------
step_period = 1000
base_hip = 160
base_knee = 120
base_shoulder = 90
amplitude_knee = 10
phase_offset_left1 = 0
phase_offset_left2 = math.pi
phase_offset_right1 = math.pi
phase_offset_right2 = 0

def move_legs(amp_l, amp_r, dir_l=True, dir_r=True):
    current_time = time.ticks_ms()
    cycle_time = (current_time % step_period) / step_period
    phase = cycle_time * 2 * math.pi

    sign_l = 1 if dir_l else -1
    sign_r = 1 if dir_r else -1

    leg.legleft1_A(base_shoulder, base_hip + sign_l * amp_l * math.cos(phase + phase_offset_left1),
                                    base_knee + amplitude_knee * math.sin(phase + phase_offset_left1))
    leg.legleft2_A(base_shoulder, base_hip + sign_l * amp_l * math.cos(phase + phase_offset_left2),
                                    base_knee + amplitude_knee * math.sin(phase + phase_offset_left2))
    leg.legright1_A(base_shoulder, base_hip + sign_r * amp_r * math.cos(phase + phase_offset_right1),
                                     base_knee + amplitude_knee * math.sin(phase + phase_offset_right1))
    leg.legright2_A(base_shoulder, base_hip + sign_r * amp_r * math.cos(phase + phase_offset_right2),
                                     base_knee + amplitude_knee * math.sin(phase + phase_offset_right2))

def walk_forward(): move_legs(10, 10, True, True)
def walk_backward(): move_legs(10, 10, False, False)
def turn_left(): move_legs(10, 10, False, True)
def turn_right(): move_legs(10, 10, True, False)
def standstill():
    leg.legleft1_A(base_shoulder, base_hip, base_knee)
    leg.legleft2_A(base_shoulder, base_hip, base_knee)
    leg.legright1_A(base_shoulder, base_hip, base_knee)
    leg.legright2_A(base_shoulder, base_hip, base_knee)

# ---------------- Async Tasks ----------------
async def read_uart_loop():
    global current_mode
    while True:
        if uart.any():
            data = uart.read()
            if data and len(data) >= 12:
                if data[0] == HEADER1 and data[1] == HEADER2 and data[-2] == FOOTER1 and data[-1] == FOOTER2:
                    data_section = data[3:11]
                    x = data_section[2]
                    y = data_section[1]
                    if y > 200:
                        current_mode = "forward"
                    elif y < 100:
                        current_mode = "backward"
                    elif x > 200:
                        current_mode = "left"
                    elif x < 100:
                        current_mode = "right"
                    else:
                        current_mode = "stop"
        await asyncio.sleep(0.02)

async def read_ultrasonic(sensor):
    trig = sensor['trig']
    echo = sensor['echo']
    name = sensor['name']
    while True:
        trig.value(0)
        time.sleep_us(2)
        trig.value(1)
        time.sleep_us(10)
        trig.value(0)
        try:
            pulse_time = time_pulse_us(echo, 1, 1000000)
            distance = (pulse_time / 2) / 29.1
            global front_distance, back_distance
            if name == 'Ultrasonic1':
                front_distance = distance
            elif name == 'Ultrasonic2':
                back_distance = distance
            if distance < 500:
                print(f"{name} Distance: {distance:.2f} cm")
        except OSError:
            pass
        await asyncio.sleep(0.5)

async def control_loop():
    while True:
        if current_mode == "forward":
            walk_forward()
        elif current_mode == "backward":
            walk_backward()
        elif current_mode == "left":
            turn_left()
        elif current_mode == "right":
            turn_right()
        else:
            standstill()
        print(f"[Mode]: {current_mode}")
        await asyncio.sleep(0.05)

async def obstacle_avoidance_loop():
    global current_mode
    while True:
        if front_distance < 25:
            current_mode = "left"
        elif front_distance >= 25:
            current_mode = "forward"
        await asyncio.sleep(0.7)

async def read_mpu6050():
    while True:
        ax, ay, az = mpu.get_accel()
        gx, gy, gz = mpu.get_gyro()
        print(f"MPU6050 -> Accel: X={ax} Y={ay} Z={az} | Gyro: X={gx} Y={gy} Z={gz}")
        await asyncio.sleep(0.5)

# ---------------- Main ----------------
async def main():
    asyncio.create_task(read_uart_loop())
    asyncio.create_task(read_ultrasonic(sensor1))
    asyncio.create_task(read_ultrasonic(sensor2))
    asyncio.create_task(control_loop())
    asyncio.create_task(obstacle_avoidance_loop())
    asyncio.create_task(read_mpu6050())

    while True:
        await asyncio.sleep(1)

# Run the loop
asyncio.run(main())
