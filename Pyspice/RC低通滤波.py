import matplotlib.pyplot as plt
import numpy as np

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *


# 基本参数
R = 1e3
C = 1e-6


# 手算参数
tau_calculated = R * C
fc_calculated = 1 / (2 * np.pi * R * C)


# 创建 RC 低通滤波器
circuit = Circuit("RC Low Pass Filter")


# 添加方波输入源
circuit.PulseVoltageSource(
    "input",
    "vin",
    circuit.gnd,
    initial_value=0@u_V,
    pulsed_value=5@u_V,
    pulse_width=5@u_ms,
    period=10@u_ms
)


# 添加电阻
circuit.R(
    "1",
    "vin",
    "out",
    1@u_kΩ
)


# 添加电容
circuit.C(
    "1",
    "out",
    circuit.gnd,
    1@u_uF
)


# 创建仿真器
simulator = circuit.simulator(
    temperature=25,
    nominal_temperature=25
)


# 瞬态分析
analysis_transient = simulator.transient(
    step_time=10@u_us,
    end_time=50@u_ms
)


# 读取瞬态数据
time = np.array(
    analysis_transient.time
).astype(float)

vin_transient = np.array(
    analysis_transient.nodes["vin"]
).astype(float)

vout_transient = np.array(
    analysis_transient.nodes["out"]
).astype(float)


# 计算仿真时间常数
target_voltage = 5 * (1 - np.exp(-1))

tau_index = np.argmin(
    np.abs(vout_transient - target_voltage)
)

tau_sim = time[tau_index]


# 绘制瞬态波形
plt.figure(figsize=(8, 4))

plt.plot(
    time * 1000,
    vin_transient,
    label="Vin"
)

plt.plot(
    time * 1000,
    vout_transient,
    label="Vout"
)

# 标记时间常数
plt.scatter(
    tau_sim * 1000,
    vout_transient[tau_index],
    marker="o",
    label=f"τ = {tau_sim * 1000:.3f} ms"
)

# 63.2% 电压参考线
plt.axhline(
    target_voltage,
    linestyle="--",
    label=f"63.2% = {target_voltage:.2f} V"
)

plt.xlabel("Time (ms)")
plt.ylabel("Voltage (V)")

plt.title(
    "RC Low Pass Filter Transient Response"
)

plt.grid()
plt.legend()

plt.tight_layout()
plt.show()


# 创建 AC 分析电路
circuit_ac = Circuit("RC Low Pass Filter AC")


# 添加交流输入源
circuit_ac.SinusoidalVoltageSource(
    "input",
    "vin",
    circuit_ac.gnd,
    amplitude=1@u_V,
    frequency=1@u_Hz
)


# 添加电阻
circuit_ac.R(
    "1",
    "vin",
    "out",
    1@u_kΩ
)


# 添加电容
circuit_ac.C(
    "1",
    "out",
    circuit_ac.gnd,
    1@u_uF
)


# 创建 AC 仿真器
simulator_ac = circuit_ac.simulator(
    temperature=25,
    nominal_temperature=25
)


# AC 频率扫描
analysis_ac = simulator_ac.ac(
    start_frequency=10@u_Hz,
    stop_frequency=100000@u_Hz,
    number_of_points=100,
    variation="dec"
)


# 读取频率
frequencies = np.array(
    analysis_ac.frequency
).astype(float)


# 读取输入和输出电压
vin_ac = np.array(
    analysis_ac.nodes["vin"]
)

vout_ac = np.array(
    analysis_ac.nodes["out"]
)


# 计算电压增益
vin_mag = np.abs(vin_ac)
vout_mag = np.abs(vout_ac)

gain = vout_mag / vin_mag


# 转换为 dB
gain_db = 20 * np.log10(gain)


# 寻找仿真截止频率
target_db = -3.01

fc_index = np.argmin(
    np.abs(gain_db - target_db)
)

fc_sim = frequencies[fc_index]


# 计算截止频率误差
fc_error = (
    abs(fc_sim - fc_calculated)
    / fc_calculated
    * 100
)


# 计算时间常数误差
tau_error = (
    abs(tau_sim - tau_calculated)
    / tau_calculated
    * 100
)


# 绘制波特图
plt.figure(figsize=(8, 5))

plt.semilogx(
    frequencies,
    gain_db,
    label="Simulation"
)


# 标记仿真截止频率
plt.scatter(
    fc_sim,
    gain_db[fc_index],
    marker="o",
    label=f"Simulated fc = {fc_sim:.2f} Hz"
)


# -3 dB 参考线
plt.axhline(
    -3.01,
    linestyle="--",
    label="-3.01 dB"
)


# 理论截止频率
plt.axvline(
    fc_calculated,
    linestyle="--",
    label=f"Theoretical fc = {fc_calculated:.2f} Hz"
)


plt.xlabel("Frequency (Hz)")
plt.ylabel("Gain (dB)")

plt.title(
    "RC Low Pass Filter Bode Plot"
)

plt.grid(
    which="both"
)

plt.legend()

plt.tight_layout()
plt.show()


# 输出结果
print()
print("RC低通滤波器实验结果")
print()

print("电路参数")
print(f"R = {R / 1000:.1f} kΩ")
print(f"C = {C * 1e6:.1f} μF")

print()

print("时间常数 τ")
print(f"手算 τ = {tau_calculated * 1000:.3f} ms")
print(f"仿真 τ = {tau_sim * 1000:.3f} ms")
print(f"误差 = {tau_error:.2f} %")

print()

print("截止频率 fc")
print(f"手算 fc = {fc_calculated:.2f} Hz")
print(f"仿真 fc = {fc_sim:.2f} Hz")
print(f"误差 = {fc_error:.2f} %")

print()

print("手算 vs 仿真")
print()

print(
    f"{'参数':<10}"
    f"{'手算':<15}"
    f"{'仿真':<15}"
    f"{'误差':<10}"
)

print("-" * 50)

print(
    f"{'τ':<10}"
    f"{tau_calculated * 1000:.3f} ms      "
    f"{tau_sim * 1000:.3f} ms      "
    f"{tau_error:.2f} %"
)

print(
    f"{'fc':<10}"
    f"{fc_calculated:.2f} Hz       "
    f"{fc_sim:.2f} Hz       "
    f"{fc_error:.2f} %"
)

print()