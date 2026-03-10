#!/usr/bin/env python3
import cv2
import subprocess
import os
import shutil
import argparse

try:
    from PyQt6.QtCore import QSettings
    HAS_QT = True
except ImportError:
    HAS_QT = False

def run_glint(multiplier, offset):
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return

    # Throw away frames to allow the camera's auto-exposure to stabilize
    # Increased to 20 frames (approx 0.7s at 30fps)
    for _ in range(20):
        cap.read()

    brightness_samples = []
    # Capture 10 frames to average out noise/flicker
    for _ in range(10):
        ret, frame = cap.read()
        if ret:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness_samples.append(gray.mean())

    cap.release()

    if brightness_samples:
        avg_brightness = sum(brightness_samples) / len(brightness_samples)

        # Calculate percentage with Multiplier and Offset
        # Formula: (Raw % * Multiplier) + Offset
        raw_percentage = (avg_brightness / 255) * 100
        final_percentage = int((raw_percentage * multiplier) + offset)

        # Constrain to 0-100 range
        final_percentage = max(0, min(100, final_percentage))
        
        print(f"Target Brightness: {final_percentage}% (Multiplier: {multiplier}, Offset: {offset})")

        brightness_set = False

        # Try KDE PowerDevil (Wayland/X11 compliant for KDE)
        if os.environ.get("XDG_CURRENT_DESKTOP") == "KDE" and shutil.which("busctl"):
            try:
                # Get Max Brightness
                cmd_max = [
                    "busctl", "--user", "call", 
                    "org.kde.Solid.PowerManagement", 
                    "/org/kde/Solid/PowerManagement/Actions/BrightnessControl", 
                    "org.kde.Solid.PowerManagement.Actions.BrightnessControl", 
                    "brightnessMax"
                ]
                res = subprocess.check_output(cmd_max, stderr=subprocess.DEVNULL).decode().strip()
                # Output format: "i 10000"
                parts = res.split()
                if len(parts) >= 2 and parts[0] == "i":
                    max_val = int(parts[1])
                    target_val = int((final_percentage / 100.0) * max_val)
                    
                    # Set Brightness
                    cmd_set = [
                        "busctl", "--user", "call", 
                        "org.kde.Solid.PowerManagement", 
                        "/org/kde/Solid/PowerManagement/Actions/BrightnessControl", 
                        "org.kde.Solid.PowerManagement.Actions.BrightnessControl", 
                        "setBrightness", "i", str(target_val)
                    ]
                    subprocess.run(cmd_set, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    print(f"Set KDE brightness to {target_val} (Max: {max_val})")
                    brightness_set = True
            except Exception as e:
                print(f"KDE PowerDevil control failed: {e}")

        # Try Hyprland (via wl-gammarelay)
        if os.environ.get("XDG_CURRENT_DESKTOP") == "Hyprland" and shutil.which("busctl"):
            try:
                target_val = final_percentage / 100.0
                cmd_set = [
                    "busctl", "--user", "set-property", 
                    "rs.wl-gammarelay", 
                    "/", 
                    "rs.wl.gammarelay", 
                    "Brightness", "d", str(target_val)
                ]
                subprocess.run(cmd_set, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"Set Hyprland brightness to {target_val} (via wl-gammarelay)")
                brightness_set = True
            except Exception as e:
                # If wl-gammarelay isn't running, we'll fall through to other methods
                pass

        if not brightness_set:
            # Try brightnessctl first (hardware backlight)
            try:
                # Check if a backlight device exists first to avoid controlling LEDs
                check = subprocess.run(["brightnessctl", "-c", "backlight", "info"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if check.returncode == 0:
                    subprocess.run(["brightnessctl", "-c", "backlight", "set", f"{final_percentage}%"], check=True)
                    brightness_set = True
                else:
                    raise FileNotFoundError("No backlight device found")
            except (subprocess.CalledProcessError, FileNotFoundError):
                pass # Fall through to xrandr
        
        if not brightness_set:
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
                
        return {
            "raw_brightness": raw_percentage,
            "target_brightness": final_percentage
        }
    else:
        print("Error: Failed to capture frame.")
        return None

def main():
    # --- CONFIGURATION ---
    DEFAULT_MULTIPLIER = 1.0
    DEFAULT_OFFSET = 15
    
    if HAS_QT:
        try:
            settings = QSettings("Glint", "GlintTray")
            # QSettings.value returns the stored type or a variant.
            # We explicitly cast to ensure safety.
            saved_mult = settings.value("multiplier")
            saved_offset = settings.value("offset")
            
            if saved_mult is not None:
                DEFAULT_MULTIPLIER = float(saved_mult)
            
            if saved_offset is not None:
                DEFAULT_OFFSET = int(saved_offset)
            
            # print(f"Loaded config from QSettings: Mult={DEFAULT_MULTIPLIER}, Offset={DEFAULT_OFFSET}")
        except Exception as e:
            print(f"Warning: Could not load QSettings: {e}")
            
    # ---------------------

    parser = argparse.ArgumentParser(description="Adjust screen brightness based on webcam light levels.")
    parser.add_argument("-m", "--multiplier", type=float, default=DEFAULT_MULTIPLIER,
                        help=f"Sensitivity multiplier (default: {DEFAULT_MULTIPLIER})")
    parser.add_argument("-o", "--offset", type=int, default=DEFAULT_OFFSET,
                        help=f"Minimum brightness percentage (default: {DEFAULT_OFFSET})")
    args = parser.parse_args()

    run_glint(args.multiplier, args.offset)

if __name__ == "__main__":
    main()
