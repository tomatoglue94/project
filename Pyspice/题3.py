import numpy as np
import matplotlib.pyplot as plt

from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *


# 创建电路
circuit = Circuit("NMOS Common Source Amplifier")

# 电源
circuit.V(
    "DD",
    "vdd",
    circuit.gnd,
    5 @ u_V
)

# 输入信号：10 mV，1 kHz
circuit.SinusoidalVoltageSource(
    "in",
    "vin",
    circuit.gnd,
    amplitude=10 @ u_mV,
    frequency=1 @ u_kHz
)

# 输入耦合电容
# Cb1 足够大，这里取 10 uF
circuit.C(
    "b1",
    "vin",
    "g",
    10 @ u_uF
)

# 栅极分压电阻
circuit.R(
    "g1",
    "vdd",
    "g",
    60 @ u_kΩ
)

circuit.R(
    "g2",
    "g",
    circuit.gnd,
    40 @ u_kΩ
)

# 漏极电阻
circuit.R(
    "d",
    "vdd",
    "out",
    2 @ u_kΩ
)

# NMOS 模型
# 题目中的 K = 0.8 mA/V^2
# SPICE Level-1 中 KP = 2K
circuit.model(
    "NMOS_MODEL",
    "NMOS",
    LEVEL=1,
    VTO=1,
    KP=1.6e-3,
    LAMBDA=0.02
)

# 创建 NMOS
# 端口顺序：D、G、S、B
circuit.MOSFET(
    "M1",
    "out",
    "g",
    circuit.gnd,
    circuit.gnd,
    model="NMOS_MODEL"
)

# 创建仿真器
simulator = circuit.simulator(
    temperature=25,
    nominal_temperature=25
)

# 直流工作点分析
dc_analysis = simulator.operating_point()

Vg_sim = float(
    np.asarray(dc_analysis.nodes["g"]).flatten()[0]
)

Vd_sim = float(
    np.asarray(dc_analysis.nodes["out"]).flatten()[0]
)

Vs_sim = 0.0

Vgs_sim = Vg_sim - Vs_sim
Vds_sim = Vd_sim - Vs_sim

# 由漏极电阻计算仿真漏极电流
Id_sim = (5.0 - Vd_sim) / 2000


# 手算参数
VDD_value = 5.0
Rg1 = 60e3
Rg2 = 40e3
Rd = 2e3

K = 0.8e-3
Vth = 1.0
lam = 0.02

# 手算栅极电压
Vg_hand = VDD_value * Rg2 / (Rg1 + Rg2)

# 源极接地
Vgs_hand = Vg_hand

# 按题目给出的公式计算 ID
Id_hand = K * (Vgs_hand - Vth) ** 2

# 手算 VDS
Vds_hand = VDD_value - Id_hand * Rd

# 判断是否处于饱和区
saturation_hand = Vds_hand >= (Vgs_hand - Vth)

# 手算 gm
gm_hand = 2 * K * (Vgs_hand - Vth)

# 根据 lambda 计算输出电阻
ro_hand = 1 / (lam * Id_hand)

# 手算电压增益
parallel_resistance = (
    Rd * ro_hand
    / (Rd + ro_hand)
)

Av_hand = -gm_hand * parallel_resistance


# 计算仿真 gm
# SPICE Level-1 模型考虑了 lambda
gm_sim = (
    2
    * K
    * (Vgs_sim - Vth)
    * (1 + lam * Vds_sim)
)

# 仿真输出电阻
ro_sim = 1 / (lam * Id_sim)

# 根据仿真工作点计算理论增益
parallel_resistance_sim = (
    Rd * ro_sim
    / (Rd + ro_sim)
)

Av_sim_theory = -gm_sim * parallel_resistance_sim


# 瞬态分析
transient_analysis = simulator.transient(
    step_time=1 @ u_us,
    end_time=10 @ u_ms
)

time = np.asarray(
    transient_analysis.time
).flatten()

vin = np.asarray(
    transient_analysis["vin"]
).flatten()

vout = np.asarray(
    transient_analysis["out"]
).flatten()


# 测量实际仿真增益
# 只取后 5 ms，避开开始阶段的暂态过程
mask = time >= 5e-3

vin_measure = vin[mask]
vout_measure = vout[mask]

vin_pp = np.ptp(vin_measure)
vout_pp = np.ptp(vout_measure)

Av_measured = vout_pp / vin_pp


# 输出直流工作点
print()
print("直流工作点")
print(f"VGS 手算 = {Vgs_hand:.4f} V")
print(f"VGS 仿真 = {Vgs_sim:.4f} V")

print(f"ID 手算 = {Id_hand * 1000:.4f} mA")
print(f"ID 仿真 = {Id_sim * 1000:.4f} mA")

print(f"VDS 手算 = {Vds_hand:.4f} V")
print(f"VDS 仿真 = {Vds_sim:.4f} V")


# 输出饱和区判断
print()
print("饱和区判断")
print(f"VGS - Vth = {Vgs_hand - Vth:.4f} V")
print(f"VDS = {Vds_hand:.4f} V")

if saturation_hand:
    print("手算判断：NMOS 工作在饱和区")
else:
    print("手算判断：NMOS 不在饱和区")


# 输出小信号参数
print()
print("小信号参数")
print(f"gm 手算 = {gm_hand * 1000:.4f} mS")
print(f"gm 仿真 = {gm_sim * 1000:.4f} mS")

print(f"ro 手算 = {ro_hand / 1000:.4f} kΩ")
print(f"ro 仿真 = {ro_sim / 1000:.4f} kΩ")

print(f"Av 手算 = {Av_hand:.4f}")
print(f"Av 仿真理论值 = {Av_sim_theory:.4f}")
print(f"Av 波形测量值 = {-Av_measured:.4f}")


# 输出手算与仿真对比表
print()
print("手算 vs 仿真")

print(
    f"{'参数':<10}"
    f"{'手算':>15}"
    f"{'仿真':>15}"
)

print(
    f"{'VGS':<10}"
    f"{Vgs_hand:>15.4f}"
    f"{Vgs_sim:>15.4f} V"
)

print(
    f"{'ID':<10}"
    f"{Id_hand * 1000:>15.4f}"
    f"{Id_sim * 1000:>15.4f} mA"
)

print(
    f"{'VDS':<10}"
    f"{Vds_hand:>15.4f}"
    f"{Vds_sim:>15.4f} V"
)

print(
    f"{'gm':<10}"
    f"{gm_hand * 1000:>15.4f}"
    f"{gm_sim * 1000:>15.4f} mS"
)

print(
    f"{'Av':<10}"
    f"{Av_hand:>15.4f}"
    f"{-Av_measured:>15.4f}"
)


# 绘制输入输出波形
plt.figure(figsize=(10, 5))

plt.plot(
    time * 1000,
    vin * 1000,
    label="Input vi"
)

plt.plot(
    time * 1000,
    vout * 1000,
    label="Output vo"
)

plt.xlabel("Time (ms)")
plt.ylabel("Voltage (mV)")
plt.title("NMOS Common-Source Amplifier")

plt.legend()
plt.grid()

plt.tight_layout()
plt.show()