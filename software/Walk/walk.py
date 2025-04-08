import leg
import math , time

print(leg.legleft1_A(90,160,120))
print(leg.legleft2_A(90,160,120))
print(leg.legright1_A(90,160,120))
print(leg.legright2_A(90,160,120))

# 步态控制参数
step_period = 1000  # 步态周期（毫秒）

# 相位偏移 (对角步态)
phase_offset_left1 = 0       # 左前腿
phase_offset_left2 = math.pi  # 左后腿
phase_offset_right1 = math.pi # 右前腿
phase_offset_right2 = 0       # 右后腿

# 基础角度和振幅
base_hip = 160      # 臀部角度基础值
base_knee = 120     # 膝关节角度基础值
amplitude_hip = 10  # 臀部角度振幅
amplitude_knee = 10 # 膝关节角度振幅

# 主循环
while True:
    # 计算当前时间和归一化周期时间 (0~1)
    current_time = time.ticks_ms()
    cycle_time = (current_time % step_period) / step_period
    phase = cycle_time * 2 * math.pi
    
    # 计算各腿的当前角度
    hip_left1 = base_hip + amplitude_hip * math.cos(phase + phase_offset_left1)
    knee_left1 = base_knee + amplitude_knee * math.sin(phase + phase_offset_left1)

    hip_left2 = base_hip + amplitude_hip * math.cos(phase + phase_offset_left2)
    knee_left2 = base_knee + amplitude_knee * math.sin(phase + phase_offset_left2)

    hip_right1 = base_hip + amplitude_hip * math.cos(phase + phase_offset_right1)
    knee_right1 = base_knee + amplitude_knee * math.sin(phase + phase_offset_right1)

    hip_right2 = base_hip + amplitude_hip * math.cos(phase + phase_offset_right2)
    knee_right2 = base_knee + amplitude_knee * math.sin(phase + phase_offset_right2)
    
    # 调用各腿的运动函数
    leg.legleft1_A(90,hip_left1, knee_left1)
    leg.legleft2_A(90,hip_left2, knee_left2)
    leg.legright1_A(90,hip_right1, knee_right1)
    leg.legright2_A(90,hip_right2, knee_right2)
    
    # 控制步态刷新率（约50Hz）
    time.sleep(0.1)
