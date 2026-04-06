import os
import re

BUILD_VOLUME = 250

def parse_delay_input(delay_str):
    delay_str = delay_str.strip().lower()
    minutes = seconds = 0
    if 'm' in delay_str:
        minutes = int(delay_str.strip('m').replace('s',''))
    elif 's' in delay_str:
        seconds = int(delay_str.strip('s').replace('m',''))
    return minutes, seconds

def extract_bounds(lines):
    min_x = min_y = None
    max_x = max_y = 0
    max_z = 0
    for line in lines:
        if line.startswith(";"):
            continue
        match_x = re.search(r"X([-+]?[0-9]*\.?[0-9]+)", line)
        match_y = re.search(r"Y([-+]?[0-9]*\.?[0-9]+)", line)
        match_z = re.search(r"Z([-+]?[0-9]*\.?[0-9]+)", line)
        if match_x:
            x = float(match_x.group(1))
            max_x = max(max_x, x)
            min_x = x if min_x is None else min(min_x, x)
        if match_y:
            y = float(match_y.group(1))
            max_y = max(max_y, y)
            min_y = y if min_y is None else min(min_y, y)
        if match_z:
            z = float(match_z.group(1))
            max_z = max(max_z, z)
    return min_x or 0, max_x, min_y or 0, max_y, max_z

def modify_gcode(filepath, delay_min, delay_sec, copies, object_height):
    try:
        with open(filepath, "r") as f:
            lines = f.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False

    min_x, max_x, min_y, max_y, max_z = extract_bounds(lines)
    final_z = max(object_height - 17.97, 5 if object_height < 22.97 else object_height - 17.97)
    push_y = max(min_y - 10, 0)
    push_x_start = min(max_x + 10, BUILD_VOLUME - 30)
    push_x_end = min(push_x_start + 30, BUILD_VOLUME - 1)
    total_delay = delay_min * 60 + delay_sec
    delay_gcode = [f"; Cooldown delay {delay_min}m {delay_sec}s\n", f"G4 S{total_delay}\n"] if total_delay > 0 else []

    push_gcode = [
        "; --- PushTerm push-off sequence ---\n",
        "G90 ; Ensure absolute positioning\n",
        f"G1 Z{final_z:.2f} F3000 ; Move bed to proper height\n",
        f"G1 Y{push_y:.2f} F6000 ; Move Y to safe zone\n",
        f"G1 X{push_x_start:.2f} Y{push_y:.2f} F6000 ; Move to push start\n",
        "G4 S1 ; Small pause\n",
        f"G1 X{push_x_end:.2f} Y{push_y:.2f} F3000 ; Push off\n",
        "G4 S1 ; Pause after push\n",
        "G28 X Y ; Rehome X and Y\n",
        ";pushoff_added\n"
    ]

    insert_idx = next((i for i in reversed(range(len(lines))) if any(cmd in lines[i] for cmd in ("M104","M107","M140","G28"))), len(lines)-1)

    modified_lines = []
    inserted = False
    for copy in range(copies):
        if copy > 0:
            modified_lines.append(f"\n; --- Copy {copy+1} Start ---\n")
        for i, line in enumerate(lines):
            if i == insert_idx and not inserted:
                modified_lines.extend(delay_gcode)
                modified_lines.extend(push_gcode)
                inserted = True
            modified_lines.append(line)

    output_path = os.path.splitext(filepath)[0] + "_modified.gcode"
    try:
        with open(output_path, "w") as f:
            f.writelines(modified_lines)
        print(f"Modified G-code saved as: {output_path}")
        return True
    except Exception as e:
        print(f"Error saving file: {e}")
        return False