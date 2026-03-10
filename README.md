# Glint

Glint is a lightweight utility that automatically adjusts your screen brightness based on ambient light captured from your webcam. It bridges the gap for Linux users on desktops or laptops without built-in light sensors, providing a "smart" brightness experience.

## Supported Desktops

Glint is designed to be platform-agnostic but includes native optimizations for:
*   **KDE Plasma**: Uses PowerDevil D-Bus API.
*   **Hyprland / Wayland**: Uses `wl-gammarelay-rs` for software-based dimming. *(Note: Hyprland is still being tested but is currently best at 1.8 multiplier, 30 offset)*
*   **X11 (GNOME, XFCE, etc.)**: Uses `xrandr` for software-based dimming.
*   **Generic**: Uses `brightnessctl` for hardware-level backlight control on any desktop.

## How It Works

1.  **Capture**: It takes a single frame from the default webcam using OpenCV.
2.  **Analyze**: It converts the image to grayscale and calculates the average pixel brightness.
3.  **Adjust**: It calculates a target screen brightness percentage (applying a configurable multiplier and minimum offset).
4.  **Hardware/Software Control**: It first attempts to use desktop-specific APIs (KDE via PowerDevil or Hyprland via `wl-gammarelay`). If those are unavailable, it tries `brightnessctl` (hardware control). Finally, it falls back to `xrandr` (software dimming) for X11 environments, ensuring broad compatibility.

## Prerequisites

*   **Python 3**
*   **OpenCV (python-opencv)**: For image capture and processing.
*   **brightnessctl**: For hardware-level brightness control (generic).
*   **xrandr**: For software-level brightness control on X11 (fallback).
*   **wl-gammarelay-rs**: Required for Hyprland/Wayland software brightness control.
*   **Webcam**: A functional video capture device.

## Installation

### 1. System Dependencies

Install the required utilities.

*   **Debian/Ubuntu:**
    ```bash
    sudo apt install brightnessctl x11-xserver-utils
    ```
*   **Arch Linux:**
    ```bash
    sudo pacman -S brightnessctl xorg-xrandr
    ```
*   **Fedora:**
    ```bash
    sudo dnf install brightnessctl xrandr
    ```

*Note: Ensure your user has permission to control brightness (often requires being in the `video` group for `brightnessctl`).*

### 2. Python Dependencies

Install the required Python packages (it is recommended to use a virtual environment):

```bash
pip install opencv-python
```

## Usage

Run the script manually to adjust brightness once:

```bash
python glint.py
```

### Configuration

You can adjust the behavior by editing the constants at the top of `glint.py`:

*   **`MULTIPLIER`**: Controls sensitivity. Values `> 1` increase brightness more aggressively in light; `< 1` makes it more conservative.
*   **`OFFSET`**: The minimum brightness percentage (prevents the screen from going pitch black).

**Recommended for KDE Plasma:**
*   **`MULTIPLIER`**: `0.6`
*   **`OFFSET`**: `15%` (0.15)

**Recommended for Hyprland (Experimental):**
*   **`MULTIPLIER`**: `1.8`
*   **`OFFSET`**: `30%` (0.30)

## Desktop Integration

A `glint.desktop` file is included to allow launching Glint from your application menu or binding it to a keyboard shortcut.

1.  **Prepare the Script**:
    Make the script executable or ensure you call it with python. You may want to move it to a standard location like `/usr/local/bin/` or keep it in your home directory.

    *If you keep it in the current folder, update the `Exec` line in `glint.desktop` to point to the absolute path of `glint.py` (e.g., `Exec=/usr/bin/python3 /home/user/path/to/glint.py`).*

2.  **Install the Desktop Entry**:
    Copy the desktop file to your local applications folder:

    ```bash
    cp glint.desktop ~/.local/share/applications/
    ```

3.  **Set Icon (Optional)**:
    Place an icon named `glint.png` or `glint.svg` in `~/.local/share/icons/` or update the `Icon=` path in the desktop file.
