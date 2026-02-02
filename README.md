# Glint

Glint is a lightweight utility that automatically adjusts your screen brightness based on ambient light captured from your webcam. It is designed to be run as a "one-off" command (e.g., triggered by a shortcut or startup script) rather than a background service.

## How It Works

1.  **Capture**: It takes a single frame from the default webcam using OpenCV.
2.  **Analyze**: It converts the image to grayscale and calculates the average pixel brightness.
3.  **Adjust**: It calculates a target screen brightness percentage (applying a configurable multiplier and minimum offset) and applies it using the `brightnessctl` system utility.

## Prerequisites

*   **Python 3**
*   **brightnessctl**: A Linux utility for controlling screen brightness.
*   **Webcam**: A functional video capture device.

## Installation

### 1. System Dependencies

First, install `brightnessctl`.

*   **Debian/Ubuntu:**
    ```bash
    sudo apt install brightnessctl
    ```
*   **Arch Linux:**
    ```bash
    sudo pacman -S brightnessctl
    ```
*   **Fedora:**
    ```bash
    sudo dnf install brightnessctl
    ```

*Note: Ensure your user has permission to control brightness (often requires being in the `video` or `input` group, depending on your distro).*

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
