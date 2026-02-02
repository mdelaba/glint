import cv2
import subprocess

# --- CONFIGURATION ---
# Multiplier: >1 increases sensitivity, <1 decreases it.
MULTIPLIER = 1.2 
# Offset: The minimum brightness % you ever want (e.g., 10% so the screen isn't black)
OFFSET = 10      
# ---------------------

cap = cv2.VideoCapture(0)
ret, frame = cap.read()
cap.release()

if ret:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    avg_brightness = gray.mean()

    # Calculate percentage with Multiplier and Offset
    # Formula: (Raw % * Multiplier) + Offset
    raw_percentage = (avg_brightness / 255) * 100
    final_percentage = int((raw_percentage * MULTIPLIER) + OFFSET)

    # Constrain to 0-100 range so brightnessctl doesn't error out
    final_percentage = max(0, min(100, final_percentage))

    subprocess.run(["brightnessctl", "set", f"{final_percentage}%"])
