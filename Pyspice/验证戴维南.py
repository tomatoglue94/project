from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *


# 电路参数
Vs = 12
R1 = 2000
R2 = 4000
RL = 1000


# 理论计算
Voc_theory = Vs * R2 / (R1 + R2)

Isc_theory = Vs / R1

Rth_theory = R1 * R2 / (R1 + R2)

Vth_theory = Voc_theory

R_parallel = R2 * RL / (R2 + RL)

VL_theory = Vs * R_parallel / (R1 + R_parallel)

IL_theory = VL_theory / RL

VL_th_theory = Vth_theory * RL / (Rth_theory + RL)

IL_th_theory = VL_th_theory / RL


# 仿真开路电压
circuit_voc = Circuit("Thevenin Voc")

circuit_voc.V(
    "1",
    "vin",
    circuit_voc.gnd,
    12@u_V
)

circuit_voc.R(
    "1",
    "vin",
    "a",
    2@u_kΩ
)

circuit_voc.R(
    "2",
    "a",
    circuit_voc.gnd,
    4@u_kΩ
)

simulator_voc = circuit_voc.simulator(
    temperature=25,
    nominal_temperature=25
)

analysis_voc = simulator_voc.operating_point()

Voc_sim = float(
    analysis_voc.nodes["a"][0]
)


# 仿真短路电流
circuit_isc = Circuit("Thevenin Isc")

circuit_isc.V(
    "1",
    "vin",
    circuit_isc.gnd,
    12@u_V
)

circuit_isc.R(
    "1",
    "vin",
    "a",
    2@u_kΩ
)

circuit_isc.R(
    "2",
    "a",
    circuit_isc.gnd,
    4@u_kΩ
)

circuit_isc.R(
    "short",
    "a",
    circuit_isc.gnd,
    1e-9@u_Ω
)

simulator_isc = circuit_isc.simulator(
    temperature=25,
    nominal_temperature=25
)

analysis_isc = simulator_isc.operating_point()

Va_isc = float(
    analysis_isc.nodes["a"][0]
)

Vvin_isc = float(
    analysis_isc.nodes["vin"][0]
)

Isc_sim = (
    Vvin_isc - Va_isc
) / R1


# 仿真原电路接负载
circuit_load = Circuit("Original Circuit With Load")

circuit_load.V(
    "1",
    "vin",
    circuit_load.gnd,
    12@u_V
)

circuit_load.R(
    "1",
    "vin",
    "a",
    2@u_kΩ
)

circuit_load.R(
    "2",
    "a",
    circuit_load.gnd,
    4@u_kΩ
)

circuit_load.R(
    "load",
    "a",
    circuit_load.gnd,
    1@u_kΩ
)

simulator_load = circuit_load.simulator(
    temperature=25,
    nominal_temperature=25
)

analysis_load = simulator_load.operating_point()

VL_sim_original = float(
    analysis_load.nodes["a"][0]
)

IL_sim_original = (
    VL_sim_original / RL
)


# 仿真戴维南等效电路
circuit_th = Circuit("Thevenin Equivalent")

circuit_th.V(
    "th",
    "th_source",
    circuit_th.gnd,
    Vth_theory@u_V
)

circuit_th.R(
    "th",
    "th_source",
    "a",
    Rth_theory@u_Ω
)

circuit_th.R(
    "load",
    "a",
    circuit_th.gnd,
    RL@u_Ω
)

simulator_th = circuit_th.simulator(
    temperature=25,
    nominal_temperature=25
)

analysis_th = simulator_th.operating_point()

VL_sim_th = float(
    analysis_th.nodes["a"][0]
)

IL_sim_th = (
    VL_sim_th / RL
)


# 计算误差
Voc_error = (
    abs(Voc_sim - Voc_theory)
    / Voc_theory
    * 100
)

Isc_error = (
    abs(Isc_sim - Isc_theory)
    / Isc_theory
    * 100
)

VL_error = (
    abs(VL_sim_original - VL_theory)
    / VL_theory
    * 100
)

IL_error = (
    abs(IL_sim_original - IL_theory)
    / IL_theory
    * 100
)

VL_th_error = (
    abs(VL_sim_th - VL_th_theory)
    / VL_th_theory
    * 100
)

IL_th_error = (
    abs(IL_sim_th - IL_th_theory)
    / IL_th_theory
    * 100
)


# 输出结果
print()
print("戴维南定理验证实验")
print()

print("电路参数")
print(f"Vs = {Vs:.2f} V")
print(f"R1 = {R1 / 1000:.2f} kΩ")
print(f"R2 = {R2 / 1000:.2f} kΩ")
print(f"RL = {RL / 1000:.2f} kΩ")

print()

print("开路电压 Voc")
print(f"理论值 = {Voc_theory:.3f} V")
print(f"仿真值 = {Voc_sim:.3f} V")
print(f"误差 = {Voc_error:.2f} %")

print()

print("短路电流 Isc")
print(f"理论值 = {Isc_theory * 1000:.3f} mA")
print(f"仿真值 = {Isc_sim * 1000:.3f} mA")
print(f"误差 = {Isc_error:.2f} %")

print()

print("戴维南等效参数")
print(f"Vth = {Vth_theory:.3f} V")
print(f"Rth = {Rth_theory / 1000:.3f} kΩ")

print()

print("原电路接 RL")
print(f"理论 VL = {VL_theory:.3f} V")
print(f"仿真 VL = {VL_sim_original:.3f} V")
print(f"VL 误差 = {VL_error:.2f} %")

print()

print(f"理论 IL = {IL_theory * 1000:.3f} mA")
print(f"仿真 IL = {IL_sim_original * 1000:.3f} mA")
print(f"IL 误差 = {IL_error:.2f} %")

print()

print("戴维南等效电路接 RL")
print(f"理论 VL = {VL_th_theory:.3f} V")
print(f"仿真 VL = {VL_sim_th:.3f} V")
print(f"VL 误差 = {VL_th_error:.2f} %")

print()

print(f"理论 IL = {IL_th_theory * 1000:.3f} mA")
print(f"仿真 IL = {IL_sim_th * 1000:.3f} mA")
print(f"IL 误差 = {IL_th_error:.2f} %")

print()

# Markdown 表格
print("Markdown 表格")
print()

print("| 参数 | 理论值 | 仿真值 | 相对误差 |")
print("|:---|---:|---:|---:|")
print(
    f"| $V_{{oc}}$ | {Voc_theory:.3f} V | "
    f"{Voc_sim:.3f} V | {Voc_error:.2f}% |"
)
print(
    f"| $I_{{sc}}$ | {Isc_theory * 1000:.3f} mA | "
    f"{Isc_sim * 1000:.3f} mA | {Isc_error:.2f}% |"
)

print()

print("| 参数 | 原电路手算 | 原电路仿真 | 戴维南等效仿真 |")
print("|:---|---:|---:|---:|")
print(
    f"| $V_L$ | {VL_theory:.3f} V | "
    f"{VL_sim_original:.3f} V | {VL_sim_th:.3f} V |"
)
print(
    f"| $I_L$ | {IL_theory * 1000:.3f} mA | "
    f"{IL_sim_original * 1000:.3f} mA | "
    f"{IL_sim_th * 1000:.3f} mA |"
)