#Date: 11/03/2025
#Authour: Hasinu Ravishka


from machine import Pin, I2C
import time


gy30_addr = 0x23  
i2c = I2C(0, scl=Pin(17), sda=Pin(16), freq=400_000)  


DARK_THRESHOLD = 50      
BRIGHT_THRESHOLD = 1000  


def Gy_30_Init():
    try:
        i2c.writeto(gy30_addr, bytes([0x01])) 
        i2c.writeto(gy30_addr, bytes([0x07]))  
        i2c.writeto(gy30_addr, bytes([0x10]))  
        print("BH1750 Initialized")
    except Exception as e:
        print(f"Error initializing BH1750: {e}")


def Gy_30():
    try:
        if gy30_addr not in i2c.scan():  # Check if sensor is connected
            print("BH1750 Not Found!")
            return None
        
        gy = i2c.readfrom(gy30_addr, 2)  
        if len(gy) == 2:
            return float((gy[0] << 8) | gy[1]) / 1.2  
        else:
            return None
    except Exception as e:
        print(f"I2C Read Error: {e}")
        return None


def get_stable_light_reading(samples=5, delay=0.1):
    readings = []
    for _ in range(samples):
        lux = Gy_30()
        if lux is not None:
            readings.append(lux)
        time.sleep(delay)  
    return sum(readings) / len(readings) if readings else None  


def robot_light_control():
    Gy_30_Init()
    
    while True:
        lux = get_stable_light_reading()
        
        if lux is None:
            print("Failed to read light sensor")
            continue
        
        print(f"Light Intensity: {lux:.2f} lx")
        
        
        if lux < DARK_THRESHOLD:
            print("⚠️ Too Dark! Turning on robot lights.")
            
        elif lux > BRIGHT_THRESHOLD:
            print("☀️ Too Bright! Avoiding strong light.")
            
        
        
        time.sleep(0.5)  


robot_light_control()

