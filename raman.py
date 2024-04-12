import numpy as np
import matplotlib.pyplot as plt

def ry(data):
    """
    Constructing a piecewise-linear waveform of a Rabi frequency pulse to drive a rotation about the y-axis.
    We assume the Aquila parameters that 0.05 microseconds is the minimum timestep
    """
    if "logical_q" and "ancilla" in data:
        angle = data["rotation"]
        name = f"id({data["logical_q"]})_steane({data["q0"]})_ancilla({data["ancilla"]})_op({data["type"]})_angle({angle})"
    else: 
        angle = data["angle"]
        name = f"id({data["id"]})_op({data["op"]})_angle({angle})"
    
    rabi_max = 12.5
    plateau_time = (angle * np.pi - 0.625) / rabi_max

    wf_durations = [0.05, plateau_time, 0.05]
    rabi_wf_values = [0.0, rabi_max, 0.0]

    t = [0]
    waveform_values = [rabi_wf_values[0]]

    # Add the point (0.05, rabi_max)
    t.append(wf_durations[0])
    waveform_values.append(rabi_wf_values[1])

    # Add the point (0.05 + plateau_time, rabi_max)
    t.append(wf_durations[0] + wf_durations[1])
    waveform_values.append(rabi_wf_values[1])

    # Finally add the point (0.1 + plateau_time, 0)
    t.append(sum(wf_durations))
    waveform_values.append(rabi_wf_values[2])

    # Plotting the waveform
    plt.figure(figsize=(10, 4))
    plt.plot(t, waveform_values, label="Waveform")
    plt.xlabel("Time (μs)")
    plt.ylabel("Ω/2π (MHz)")
    plt.title("Piecewise Linear Rabi Pulse for " + name)
    plt.legend()
    plt.grid(True)

    # Saving the figure
    plt.savefig('./gate_pulses/' + name + '.jpg')

    return sum(wf_durations), angle, [rabi_max, 0]

def rz(data):
    """
    Constructing a piecewise-linear waveform of a Rabi frequency pulse to drive a rotation about the x-axis.
    We assume the Aquila parameters that 0.05 microseconds is the minimum timestep
    """
    angle = data["params"]
    if "steane" and "ancilla" in data:
        name = f"id({data["id"]})_steane({data["steane"]})_ancilla({data["ancilla"]})_op({data["op"]})_angle({angle})"
    else: name = f"id({data["id"]})_op({data["op"]})_angle({angle})"
    
    detuning_max = 10
    plateau_time = (angle * np.pi - 0.625) / detuning_max
    
    wf_durations = [0.05, plateau_time, 0.05]
    detuning_wf_values = [0.0, detuning_max, 0.0]

    t = [0]
    waveform_values = [detuning_wf_values[0]]

    # Add the point (0.05, rabi_max)
    t.append(wf_durations[0])
    waveform_values.append(detuning_wf_values[1])

    # Add the point (0.05 + plateau_time, rabi_max)
    t.append(wf_durations[0] + wf_durations[1])
    waveform_values.append(detuning_wf_values[1])

    # Finally add the point (0.1 + plateau_time, 0)
    t.append(sum(wf_durations))
    waveform_values.append(detuning_wf_values[2])

    # Plotting the waveform
    plt.figure(figsize=(10, 4))
    plt.plot(t, waveform_values, label="Waveform")
    plt.xlabel("Time (μs)")
    plt.ylabel("Δ/2π (MHz)")
    plt.title("Piecewise Linear Detuning Pulse for " + name)
    plt.legend()
    plt.grid(True)

    # Saving the figure
    plt.savefig('./gate_pulses/' + name + '.jpg')

    return sum(wf_durations), angle, [0, detuning_max]

def rx(data):
    """
    Constructing a piecewise-linear waveform of a Rabi frequency pulse to drive a rotation about the y-axis.
    We assume the Aquila parameters that 0.05 microseconds is the minimum timestep
    """
    angle = data["params"]
    if "steane" and "ancilla" in data:
        name = f"id({data["id"]})_steane({data["steane"]})_ancilla({data["ancilla"]})_op({data["op"]})_angle({angle})"
    else: name = f"id({data["id"]})_op({data["op"]})_angle({angle})"
    
    # driving a rotation of angle*pi
    rabi_max = 12.5
    plateau_time_rabi = (angle * np.pi - 0.625) / 12.5
    wf_durations_rabi = [0.05, plateau_time_rabi, 0.05]
    rabi_wf_values = [0.0, rabi_max, 0.0]

    # phase shit of pi / 2
    detuning_max = 10
    plateau_time_detuning = (np.pi / 2 - 0.625) / detuning_max
    wf_durations_detuning = [0.05, plateau_time_detuning, 0.05]
    detuning_wf_values = [0.0, detuning_max, 0.0]


    t_rabi = [0]
    t_detuning = [0]
    waveform_values_rabi = [rabi_wf_values[0]]
    waveform_values_detuning = [detuning_wf_values[0]]

    t_rabi.append(wf_durations_rabi[0])
    t_detuning.append(wf_durations_detuning[0])
    waveform_values_rabi.append(rabi_wf_values[1])
    waveform_values_detuning.append(detuning_wf_values[1])

    t_rabi.append(wf_durations_rabi[0] + wf_durations_rabi[1])
    t_detuning.append(wf_durations_detuning[0] + wf_durations_detuning[1])
    waveform_values_rabi.append(rabi_wf_values[1])
    waveform_values_detuning.append(detuning_wf_values[1])

    t_rabi.append(sum(wf_durations_rabi))
    t_detuning.append(sum(wf_durations_detuning))
    waveform_values_rabi.append(rabi_wf_values[2])
    waveform_values_detuning.append(detuning_wf_values[2])

    # Plotting the waveform
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 6))
    ax1.plot(t_rabi, waveform_values_rabi, label="Waveform")
    ax1.xlabel("Time (μs)")
    ax1.ylabel("Ω/2π (MHz)")
    ax1.title("Piecewise Linear RX Rabi Pulse for " + name)
    ax1.legend()
    ax1.grid(True)

    ax2.plot(t_rabi, waveform_values_rabi, label="Waveform")
    ax2.xlabel("Time (μs)")
    ax2.ylabel("Δ/2π (MHz)")
    ax2.title("Piecewise Linear RX Detuning Pulse for " + name)
    ax2.legend()
    ax2.grid(True)

    # Saving the figure
    plt.savefig('./gate_pulses/' + name + '.jpg')

    return sum(wf_durations_rabi), angle, [rabi_max, detuning_max]