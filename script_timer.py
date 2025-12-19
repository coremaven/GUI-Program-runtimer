#!/usr/bin/env python3
"""
Script Timer Application
========================

A GUI application to control script/program execution with three timer functions:
1. Close script/program after x amount of time
2. Run the script/software every x amount of time
3. Start the script/software at x:xx o'clock

Requirements:
- Python 3.6+
- PyQt5 (install with: pip install PyQt5)

Usage:
1. Run this script
2. Select a script or program to control
3. Configure one of the three functions:
   - Close after time: Runs script for x minutes then closes it
   - Run every x time: Repeats script execution every x minutes
   - Start at specific time: Runs script at specified time (and optionally daily)
"""

import sys
import os
import subprocess
from datetime import datetime, time
import threading
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QFileDialog,
    QLabel,
    QSpinBox,
    QGroupBox,
    QTimeEdit,
    QCheckBox,
    QMessageBox,
    QGridLayout,
)
from PyQt5.QtCore import QTimer, QTime, pyqtSignal
from PyQt5.QtGui import QFont


class ScriptTimer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Script Timer")
        self.setGeometry(100, 100, 500, 400)

        # Variables to store script info and timers
        self.script_path = ""
        self.timer = QTimer()
        self.schedule_timer = QTimer()
        self.running_processes = []

        # Setup UI
        self.init_ui()

        # Connect signals
        self.timer.timeout.connect(self.check_processes)

    def init_ui(self):
        # Main widget and layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)

        # Script selection section
        script_group = QGroupBox("Script Selection")
        script_layout = QVBoxLayout()

        self.script_label = QLabel("No script selected")
        self.script_label.setWordWrap(True)
        self.script_label.setFont(QFont("Arial", 10))

        select_button = QPushButton("Select Script")
        select_button.clicked.connect(self.select_script)

        script_layout.addWidget(self.script_label)
        script_layout.addWidget(select_button)
        script_group.setLayout(script_layout)

        # Functions section
        functions_group = QGroupBox("Functions")
        functions_layout = QVBoxLayout()

        # Function 1: Close after time
        close_group = QGroupBox("Close after time")
        close_layout = QGridLayout()

        self.close_time_spin = QSpinBox()
        self.close_time_spin.setRange(1, 10000)
        self.close_time_spin.setValue(10)
        self.close_time_spin.setSuffix(" minutes")

        self.close_button = QPushButton("Start Close Timer")
        self.close_button.clicked.connect(self.start_close_timer)

        close_layout.addWidget(QLabel("Duration:"), 0, 0)
        close_layout.addWidget(self.close_time_spin, 0, 1)
        close_layout.addWidget(self.close_button, 1, 0, 1, 2)
        close_group.setLayout(close_layout)

        # Function 2: Run every x time
        repeat_group = QGroupBox("Run every x time")
        repeat_layout = QGridLayout()

        self.repeat_time_spin = QSpinBox()
        self.repeat_time_spin.setRange(1, 10000)
        self.repeat_time_spin.setValue(30)
        self.repeat_time_spin.setSuffix(" minutes")

        self.repeat_button = QPushButton("Start Repeat Timer")
        self.repeat_button.clicked.connect(self.start_repeat_timer)

        repeat_layout.addWidget(QLabel("Interval:"), 0, 0)
        repeat_layout.addWidget(self.repeat_time_spin, 0, 1)
        repeat_layout.addWidget(self.repeat_button, 1, 0, 1, 2)
        repeat_group.setLayout(repeat_layout)

        # Function 3: Start at specific time
        schedule_group = QGroupBox("Start at specific time")
        schedule_layout = QGridLayout()

        self.time_edit = QTimeEdit()
        self.time_edit.setDisplayFormat("HH:mm")
        self.time_edit.setTime(QTime.currentTime())

        self.schedule_button = QPushButton("Start Schedule Timer")
        self.schedule_button.clicked.connect(self.start_schedule_timer)

        self.schedule_checkbox = QCheckBox("Repeat daily")

        schedule_layout.addWidget(QLabel("Time:"), 0, 0)
        schedule_layout.addWidget(self.time_edit, 0, 1)
        schedule_layout.addWidget(self.schedule_checkbox, 1, 0, 1, 2)
        schedule_layout.addWidget(self.schedule_button, 2, 0, 1, 2)
        schedule_group.setLayout(schedule_layout)

        functions_layout.addWidget(close_group)
        functions_layout.addWidget(repeat_group)
        functions_layout.addWidget(schedule_group)
        functions_group.setLayout(functions_layout)

        # Status section
        self.status_label = QLabel("Ready")
        self.status_label.setFont(QFont("Arial", 10))
        self.status_label.setStyleSheet("color: blue")

        # Stop button
        self.stop_button = QPushButton("Stop All")
        self.stop_button.clicked.connect(self.stop_all)
        self.stop_button.setEnabled(False)

        # Add all sections to main layout
        main_layout.addWidget(script_group)
        main_layout.addWidget(functions_group)
        main_layout.addWidget(self.status_label)
        main_layout.addWidget(self.stop_button)

    def select_script(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(
            self, "Select Script/Program", "", "All Files (*)", options=options
        )
        if file_name:
            self.script_path = file_name
            self.script_label.setText(f"Selected script: {os.path.basename(file_name)}")
            self.status_label.setText(f"Script selected: {os.path.basename(file_name)}")

    def start_close_timer(self):
        if not self.script_path:
            QMessageBox.warning(self, "No Script", "Please select a script first!")
            return

        interval = (
            self.close_time_spin.value() * 60000
        )  # Convert minutes to milliseconds
        self.timer.start(interval)
        self.close_button.setText("Stop Close Timer")
        self.close_button.clicked.disconnect()
        self.close_button.clicked.connect(self.stop_close_timer)
        self.stop_button.setEnabled(True)

        # Run the script
        self.run_script()
        self.status_label.setText(
            f"Running script for {self.close_time_spin.value()} minutes"
        )

    def stop_close_timer(self):
        self.timer.stop()
        self.close_button.setText("Start Close Timer")
        self.close_button.clicked.disconnect()
        self.close_button.clicked.connect(self.start_close_timer)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Close timer stopped")

    def start_repeat_timer(self):
        if not self.script_path:
            QMessageBox.warning(self, "No Script", "Please select a script first!")
            return

        interval = (
            self.repeat_time_spin.value() * 60000
        )  # Convert minutes to milliseconds
        self.timer.start(interval)
        self.repeat_button.setText("Stop Repeat Timer")
        self.repeat_button.clicked.disconnect()
        self.repeat_button.clicked.connect(self.stop_repeat_timer)
        self.stop_button.setEnabled(True)

        # Run the script
        self.run_script()
        self.status_label.setText(
            f"Script will repeat every {self.repeat_time_spin.value()} minutes"
        )

    def stop_repeat_timer(self):
        self.timer.stop()
        self.repeat_button.setText("Start Repeat Timer")
        self.repeat_button.clicked.disconnect()
        self.repeat_button.clicked.connect(self.start_repeat_timer)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Repeat timer stopped")

    def start_schedule_timer(self):
        if not self.script_path:
            QMessageBox.warning(self, "No Script", "Please select a script first!")
            return

        scheduled_time = self.time_edit.time()
        today = QTime.currentTime()

        # Calculate time difference
        if scheduled_time <= today:
            # If scheduled time has passed today, schedule for tomorrow
            tomorrow = QTime(0, 0, 0)
            time_diff = today.msecsTo(tomorrow) + scheduled_time.msecsSinceStartOfDay()
        else:
            time_diff = today.msecsTo(scheduled_time)

        self.schedule_timer.singleShot(time_diff, self.run_scheduled_script)

        self.schedule_button.setText("Stop Schedule Timer")
        self.schedule_button.clicked.disconnect()
        self.schedule_button.clicked.connect(self.stop_schedule_timer)
        self.stop_button.setEnabled(True)

        if self.schedule_checkbox.isChecked():
            self.schedule_timer.timeout.connect(self.run_scheduled_script)
            self.schedule_timer.start(24 * 60 * 60 * 1000)  # 24 hours in milliseconds
            self.status_label.setText(
                f"Script scheduled to run daily at {scheduled_time.toString()}"
            )
        else:
            self.status_label.setText(
                f"Script scheduled to run once at {scheduled_time.toString()}"
            )

    def stop_schedule_timer(self):
        self.schedule_timer.stop()
        self.schedule_button.setText("Start Schedule Timer")
        self.schedule_button.clicked.disconnect()
        self.schedule_button.clicked.connect(self.start_schedule_timer)
        self.stop_button.setEnabled(False)
        self.status_label.setText("Schedule timer stopped")

    def run_script(self):
        try:
            process = subprocess.Popen([self.script_path])
            self.running_processes.append(process)
            self.status_label.setText(
                f"Script started: {os.path.basename(self.script_path)}"
            )
        except Exception as e:
            self.status_label.setText(f"Error running script: {str(e)}")

    def run_scheduled_script(self):
        try:
            process = subprocess.Popen([self.script_path])
            self.running_processes.append(process)
            self.status_label.setText(
                f"Script scheduled started: {os.path.basename(self.script_path)}"
            )
        except Exception as e:
            self.status_label.setText(f"Error running scheduled script: {str(e)}")

    def check_processes(self):
        # Check if any processes have finished
        for process in self.running_processes[:]:
            if process.poll() is not None:  # Process has finished
                self.running_processes.remove(process)
                self.status_label.setText("Script completed execution")

    def stop_all(self):
        # Kill all running processes
        for process in self.running_processes:
            try:
                process.terminate()
            except:
                pass
        self.running_processes.clear()

        # Stop all timers
        self.timer.stop()
        self.schedule_timer.stop()

        # Reset buttons
        self.close_button.setText("Start Close Timer")
        self.close_button.clicked.disconnect()
        self.close_button.clicked.connect(self.start_close_timer)

        self.repeat_button.setText("Start Repeat Timer")
        self.repeat_button.clicked.disconnect()
        self.repeat_button.clicked.connect(self.start_repeat_timer)

        self.schedule_button.setText("Start Schedule Timer")
        self.schedule_button.clicked.disconnect()
        self.schedule_button.clicked.connect(self.start_schedule_timer)

        self.stop_button.setEnabled(False)
        self.status_label.setText("All timers stopped")


def main():
    app = QApplication(sys.argv)
    window = ScriptTimer()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
