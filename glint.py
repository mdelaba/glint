#!/usr/bin/env python3
import cv2
import subprocess

# --- CONFIGURATION ---
# Multiplier: >1 increases sensitivity, <1 decreases it.
MULTIPLIER = 1.2 
# Offset: The minimum brightness % you ever want (e.g., 10% so the screen isn't black)
OFFSET = 10      
# ---------------------

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("Error: Could not open camera.")
    exit(1)

ret, frame = cap.read()
cap.release()

if ret:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = gray.mean()

    # Calculate percentage with Multiplier and Offset
    # Formula: (Raw % * Multiplier) + Offset
    raw_percentage = (avg_brightness / 255) * 100
    final_percentage = int((raw_percentage * MULTIPLIER) + OFFSET)

    # Constrain to 0-100 range
    final_percentage = max(0, min(100, final_percentage))
    
    print(f"Target Brightness: {final_percentage}%")

    # Try brightnessctl first (hardware backlight)
    try:
        # Check if a backlight device exists first to avoid controlling LEDs
        check = subprocess.run(["brightnessctl", "-c", "backlight", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if check.returncode == 0:
            subprocess.run(["brightnessctl", "-c", "backlight", "set", f"{final_percentage}%"], check=True)
        else:
            raise FileNotFoundError("No backlight device found")
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Fallback to xrandr (software brightness)
        try:
            # Find the connected monitor
            xrandr_out = subprocess.check_output(["xrandr"]).decode("utf-8")
            for line in xrandr_out.splitlines():
                if " connected" in line:
                    monitor = line.split()[0]
                    # xrandr brightness is 0.0 to 1.0
                    brightness_float = final_percentage / 100.0
                    print(f"Using xrandr fallback for monitor {monitor}...")
                    subprocess.run(["xrandr", "--output", monitor, "--brightness", str(brightness_float)])
                    break # Only set the first connected monitor
        except Exception as e:
            print(f"Failed to set brightness: {e}")
else:
    print("Error: Failed to capture frame.")
