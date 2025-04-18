import machine
import time
import uasyncio as asyncio

# --- Wing Servo Setup ---
wing_left = machine.PWM(machine.Pin(18))
wing_right = machine.PWM(machine.Pin(19))
wing_left.freq(50)
wing_right.freq(50)

def set_servo_angle(servo, angle):
    duty = int((angle / 180.0 * 2 + 0.5) / 20 * 65535)
    servo.duty_u16(duty)

def open_wings():
    set_servo_angle(wing_left, 60)     # Open position
    set_servo_angle(wing_right, 120)   # Mirrored open

def close_wings():
    set_servo_angle(wing_left, 120)    # Closed position
    set_servo_angle(wing_right, 60)    # Mirrored closed

async def flap_wings(duration=5, interval=0.3):
    print("⚠️ Wing response activated")
    end_time = time.ticks_add(time.ticks_ms(), int(duration * 1000))
    while time.ticks_diff(end_time, time.ticks_ms()) > 0:
        open_wings()
        await asyncio.sleep(interval)
        close_wings()
        await asyncio.sleep(interval)
    print("✅ Wing flapping complete")