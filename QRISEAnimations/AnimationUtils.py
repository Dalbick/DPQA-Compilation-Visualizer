import numpy as np
import os
import shutil
import imageio

import matplotlib.pyplot as plt
import matplotlib
from matplotlib.animation import FuncAnimation, writers
import matplotlib.animation as animation
import matplotlib.colors as mcolors
from matplotlib.colors import to_rgba, to_hex
import warnings
warnings.filterwarnings('ignore')


def multiple_shuttle_animation(atoms1, atoms2, shuttle_time,
                               distance, include_reverse=True,
                               stop_time=0, standby_atoms=[],
                               path='./', name='shuttle_animation.mp4'):
    if standby_atoms is None:
        standby_atoms = []
    fps = 30  # Frames per second
    shuttle_frames = int(fps * shuttle_time)  # Number of frames for shuttling
    stop_frames = int(fps * stop_time)  # Number of frames to stop

    if include_reverse:
        # Total frames for the entire animation including reverse shuttle
        total_frames = 2 * shuttle_frames + stop_frames
    else:
        # Total frames if not including reverse
        total_frames = shuttle_frames + stop_frames

    # Prepare figure and axis
    fig, ax = plt.subplots()
    ax.set_xlim(min([atom[0] for atom in atoms1 + atoms2 + standby_atoms]) - 5,
                max([atom[0] for atom in atoms1 + atoms2 + standby_atoms]) + 5)
    ax.set_ylim(min([atom[1] for atom in atoms1 + atoms2 + standby_atoms]) - 5,
                max([atom[1] for atom in atoms1 + atoms2 + standby_atoms]) + 5)

    # Plotting the standby atoms
    for atom in standby_atoms:
        ax.plot(atom[0], atom[1], 'bo')  # Standby atoms as green dots

    # Adjusted target positions considering the distance parameter
    adjusted_atoms2 = []
    for start_pos, end_pos in zip(atoms1, atoms2):
        direction_vector = (end_pos - start_pos).astype(np.float64)
        norm = np.linalg.norm(direction_vector)
        if norm != 0:
            direction_vector /= norm
        adjusted_end_pos = end_pos - direction_vector * distance
        adjusted_atoms2.append(adjusted_end_pos)

    # Plotting the target positions
    for atom2 in atoms2:
        ax.plot(atom2[0], atom2[1], 'bo')  # Target positions as red dots

    # Creating a list to hold the atom markers
    atom_markers = [ax.plot([], [], 'bo')[0] for _ in atoms1]  # Start positions as blue dots

    # Animation update function
    def update(frame):
        if include_reverse:
            if frame <= shuttle_frames:
                t = frame / shuttle_frames # Shuttle forward
            elif frame <= shuttle_frames + stop_frames:
                t = 1 # Stop phase
            else:
                t = (total_frames - frame) / shuttle_frames # Reverse shuttle
        else:
            if frame <= shuttle_frames:
                t = frame / shuttle_frames # Shuttle forward
            else:
                t = 1 # Stop phase

        for marker, start_pos, end_pos in zip(atom_markers, atoms1, adjusted_atoms2):
            current_pos = (1 - t) * start_pos + t * end_pos
            marker.set_data(current_pos[0], current_pos[1])
        return atom_markers

    # Initialize function
    def init():
        for marker in atom_markers:
            marker.set_data([], [])
        return atom_markers

    # Create the animation
    ani = FuncAnimation(fig, update, frames=total_frames, init_func=init, blit=True, repeat=False)

    # Ensure the path exists
    if not os.path.exists(path):
        os.makedirs(path)

    filepath = os.path.join(path, name)
    ani.save(filepath, fps=fps, extra_args=['-vcodec', 'libx264'])
    plt.close(fig)


def gates_animation(atoms, pulse_duration, standby_atoms=[], path='./', name='gates_animation.mp4'):
    # Desired frames per second in the final video
    fps = 30

    # Total frames for the whole animation cycle (back and forth)
    total_frames = int(pulse_duration * fps)

    initial_color_rgba = to_rgba('blue')
    final_color_rgba = to_rgba('red')
    standby_color = 'blue'  # Color for standby atoms

    fig, ax = plt.subplots()
    active_scat = ax.scatter([], [], color=initial_color_rgba)  # Active atoms
    standby_scat = ax.scatter([], [], color=standby_color)  # Standby atoms

    # Combine all atoms for setting plot limits
    all_atoms = np.vstack(atoms + standby_atoms)
    ax.set_xlim(all_atoms[:, 0].min() - 5, all_atoms[:, 0].max() + 5)
    ax.set_ylim(all_atoms[:, 1].min() - 5, all_atoms[:, 1].max() + 5)

    def interpolate_color(start_color, end_color, fraction):
        color = [start + (end - start) * fraction for start, end in zip(start_color, end_color)]
        return to_hex(color)

    def init():
        active_scat.set_offsets(np.vstack(atoms))
        if len(standby_atoms) != 0:
            standby_scat.set_offsets(np.vstack(standby_atoms))
        return active_scat, standby_scat

    def update(frame):
        fraction = (frame % (total_frames // 2)) / (total_frames // 2)
        if frame < total_frames // 2:
            color = interpolate_color(initial_color_rgba, final_color_rgba, fraction)
        else:
            color = interpolate_color(final_color_rgba, initial_color_rgba, fraction)
        active_scat.set_color(color)
        # Standby atoms color does not change
        return active_scat, standby_scat

    ani = animation.FuncAnimation(fig, update, frames=range(total_frames), init_func=init, blit=True,
                                  interval=1000 / fps)

    # Ensure the path exists
    if not os.path.exists(path):
        os.makedirs(path)

    filepath = os.path.join(path, name)
    ani.save(filepath, fps=fps, extra_args=['-vcodec', 'libx264'])
    plt.close(fig)

