#!/usr/bin/env python3
import sys
import os
import glint
from PyQt6.QtWidgets import (QApplication, QSystemTrayIcon, QMenu, QWidget, 
                             QVBoxLayout, QLabel, QSlider, QPushButton)
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import Qt, QSettings

class GlintConfigWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Glint Settings")
        
        # Resolve icon path relative to script
        script_dir = os.path.dirname(os.path.realpath(__file__))
        self.icon_path = os.path.join(script_dir, "icon.png")
        self.setWindowIcon(QIcon(self.icon_path))
        
        self.settings = QSettings("Glint", "GlintTray")
        
        self.resize(300, 200)

        # Layout
        layout = QVBoxLayout()
        
        # Load saved settings
        saved_mult = float(self.settings.value("multiplier", 1.2))
        slider_mult_val = int(saved_mult * 10)
        
        saved_offset = int(self.settings.value("offset", 10))
        
        # Multiplier Slider
        self.lbl_mult = QLabel(f"Multiplier: {saved_mult}")
        layout.addWidget(self.lbl_mult)
        
        self.slider_mult = QSlider(Qt.Orientation.Horizontal)
        self.slider_mult.setMinimum(5)   # 0.5
        self.slider_mult.setMaximum(30)  # 3.0
        self.slider_mult.setValue(slider_mult_val)
        self.slider_mult.valueChanged.connect(self.update_mult_label)
        self.slider_mult.valueChanged.connect(self.save_settings)
        layout.addWidget(self.slider_mult)
        
        # Offset Slider
        self.lbl_offset = QLabel(f"Offset: {saved_offset}%")
        layout.addWidget(self.lbl_offset)
        
        self.slider_offset = QSlider(Qt.Orientation.Horizontal)
        self.slider_offset.setMinimum(0)
        self.slider_offset.setMaximum(100)
        self.slider_offset.setValue(saved_offset)
        self.slider_offset.valueChanged.connect(self.update_offset_label)
        self.slider_offset.valueChanged.connect(self.save_settings)
        layout.addWidget(self.slider_offset)
        
        # Run Button
        self.btn_run = QPushButton("Adjust Brightness Now")
        self.btn_run.clicked.connect(self.run_glint)
        layout.addWidget(self.btn_run)
        
        self.setLayout(layout)

    def save_settings(self):
        mult = self.slider_mult.value() / 10.0
        offset = self.slider_offset.value()
        self.settings.setValue("multiplier", mult)
        self.settings.setValue("offset", offset)

    def update_mult_label(self, value):
        self.lbl_mult.setText(f"Multiplier: {value / 10.0}")

    def update_offset_label(self, value):
        self.lbl_offset.setText(f"Offset: {value}%")

    def run_glint(self):
        mult = self.slider_mult.value() / 10.0
        offset = self.slider_offset.value()
        
        self.btn_run.setText("Adjusting...")
        self.btn_run.setEnabled(False)
        QApplication.processEvents() # Update UI
        
        try:
            glint.run_glint(mult, offset)
        except Exception as e:
            print(f"Error running glint: {e}")
        finally:
            self.btn_run.setText("Adjust Brightness Now")
            self.btn_run.setEnabled(True)

class GlintTrayApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        script_dir = os.path.dirname(os.path.realpath(__file__))
        icon_path = os.path.join(script_dir, "icon.png")
        
        self.window = GlintConfigWindow()
        
        self.tray_icon = QSystemTrayIcon(QIcon(icon_path), self.app)
        self.tray_icon.setToolTip("Glint Brightness Control")
        
        # Context Menu
        self.menu = QMenu()
        self.action_show = self.menu.addAction("Settings")
        self.action_show.triggered.connect(self.show_window)
        self.action_run = self.menu.addAction("Run Now")
        self.action_run.triggered.connect(self.window.run_glint)
        self.menu.addSeparator()
        self.action_quit = self.menu.addAction("Quit")
        self.action_quit.triggered.connect(self.app.quit)
        
        self.tray_icon.setContextMenu(self.menu)
        
        # Click handler
        self.tray_icon.activated.connect(self.on_tray_click)
        
        self.tray_icon.show()
        
    def show_window(self):
        self.window.show()
        self.window.activateWindow()

    def on_tray_click(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            if self.window.isVisible():
                self.window.hide()
            else:
                self.show_window()

    def run(self):
        sys.exit(self.app.exec())

if __name__ == "__main__":
    GlintTrayApp().run()
