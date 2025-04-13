import machine
import time
import uasyncio as asyncio
import leg
import math
from machine import Pin, time_pulse_us

# UART 初始化
uart = machine.UART(1, baudrate=115200, tx=machine.Pin(4), rx=machine.Pin(5))

# 帧常量
HEADER1 = 0xFF
HEADER2 = 0xAA
FOOTER1 = 0xBF
FOOTER2 = 0xC0

# 全局状态
current_mode = "stop"

# ------------------------------
# 超声波传感器配置（根据实际接线修改引脚）
sensor1 = {
    'trig': Pin(16, Pin.OUT),
    'echo': Pin(17, Pin.IN),
    'name': 'Ultrasonic1'
}

sensor2 = {
    'trig': Pin(14, Pin.OUT),
    'echo': Pin(15, Pin.IN),
    'name': 'Ultrasonic2'
}

# ------------------------------
# 异步读取超声波传感器数据
async def read_ultrasonic(sensor):
    trig_pin = sensor['trig']
    echo_pin = sensor['echo']
    name = sensor['name']
    while True:
        # 发出触发脉冲
        trig_pin.value(0)
        time.sleep_us(2)
        trig_pin.value(1)
        time.sleep_us(10)
        trig_pin.value(0)
        try:
            pulse_time = time_pulse_us(echo_pin, 1, 1000000)
            # 计算距离（cm）：距离 = (脉冲时长/2) / 29.1
            distance = (pulse_time / 2) / 29.1
            if distance < 500:
                print(f"{name} Distance: {distance:.2f} cm")
        except OSError as e:
            print(f"{name} Ultrasonic Read Error:", e)
        await asyncio.sleep(0.5)

# ---------------- 参数 ----------------
step_period = 1000
base_hip = 160
base_knee = 120
base_shoulder = 90
amplitude_knee = 10
phase_offset_left1 = 0
phase_offset_left2 = math.pi
phase_offset_right1 = math.pi
phase_offset_right2 = 0

# ---------------- 运动函数 ----------------
def move_legs(amp_l, amp_r, dir_l=True, dir_r=True):
    current_time = time.ticks_ms()
    cycle_time = (current_time % step_period) / step_period
    phase = cycle_time * 2 * math.pi

    sign_l = 1 if dir_l else -1
    hip_left1 = base_hip + sign_l * amp_l * math.cos(phase + phase_offset_left1)
    knee_left1 = base_knee + amplitude_knee * math.sin(phase + phase_offset_left1)
    hip_left2 = base_hip + sign_l * amp_l * math.cos(phase + phase_offset_left2)
    knee_left2 = base_knee + amplitude_knee * math.sin(phase + phase_offset_left2)

    sign_r = 1 if dir_r else -1
    hip_right1 = base_hip + sign_r * amp_r * math.cos(phase + phase_offset_right1)
    knee_right1 = base_knee + amplitude_knee * math.sin(phase + phase_offset_right1)
    hip_right2 = base_hip + sign_r * amp_r * math.cos(phase + phase_offset_right2)
    knee_right2 = base_knee + amplitude_knee * math.sin(phase + phase_offset_right2)

    leg.legleft1_A(base_shoulder, hip_left1, knee_left1)
    leg.legleft2_A(base_shoulder, hip_left2, knee_left2)
    leg.legright1_A(base_shoulder, hip_right1, knee_right1)
    leg.legright2_A(base_shoulder, hip_right2, knee_right2)

def walk_forward():
    move_legs(10, 10, dir_l=True, dir_r=True)

def walk_backward():
    move_legs(10, 10, dir_l=False, dir_r=False)

def turn_left():
    move_legs(10, 10, dir_l=False, dir_r=True)

def turn_right():
    move_legs(10, 10, dir_l=True, dir_r=False)

def standstill():
    leg.legleft1_A(base_shoulder, base_hip, base_knee)
    leg.legleft2_A(base_shoulder, base_hip, base_knee)
    leg.legright1_A(base_shoulder, base_hip, base_knee)
    leg.legright2_A(base_shoulder, base_hip, base_knee)

# ---------------- 异步UART读取任务 ----------------
async def read_uart_loop():
    global current_mode

    while True:
        if uart.any():
            data = uart.read()
            if data and len(data) >= 12:
                if data[0] == HEADER1 and data[1] == HEADER2 and data[-2] == FOOTER1 and data[-1] == FOOTER2:
                    mode = data[2]
                    data_section = data[3:11]  # 取中间8字节

                    if len(data_section) == 8:
                        print("Mode:", mode)
                        print("Joystick data:", ', '.join(str(b) for b in data_section))

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
        await asyncio.sleep(0.02)  # 异步延迟10ms

# ---------------- 异步运动控制任务 ----------------
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
        print(current_mode)
        await asyncio.sleep(0.05)  # 控制节奏

# ---------------- 主入口 ----------------
async def main():
    asyncio.create_task(read_uart_loop())
    asyncio.create_task(control_loop())
    # 可在这里加其他任务，如超声波
    asyncio.create_task(read_ultrasonic(sensor1))
    asyncio.create_task(read_ultrasonic(sensor2))

    while True:
        
        await asyncio.sleep(0)

# 启动事件循环
asyncio.run(main())

