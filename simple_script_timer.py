#!/usr/bin/env python3
"""
Simple Script Timer (Console Version)
=====================================

A console-based tool to control script/program execution with timer functionality.
This version doesn't require PyQt5 and can be run directly.

Features:
1. Close script/program after x amount of time
2. Run the script/software every x amount of time
3. Start the script/software at x:xx o'clock

Usage:
Run this script and follow the prompts.
"""

import sys
import os
import subprocess
import time
from datetime import datetime, timedelta
import threading
from threading import Timer


class SimpleScriptTimer:
    def __init__(self):
        self.script_path = ""
        self.running_processes = []
        self.timers = []

    def select_script(self):
        """Select a script or program to control"""
        print("\nSelect a script or program to control:")
        script_path = input(
            "Enter full path to script/program (or 'cancel' to quit): "
        ).strip()

        if script_path.lower() == "cancel":
            return False

        if not os.path.exists(script_path):
            print(f"Error: File '{script_path}' not found!")
            return False

        self.script_path = script_path
        print(f"Selected script: {os.path.basename(script_path)}")
        return True

    def run_script(self):
        """Run the selected script"""
        try:
            process = subprocess.Popen([self.script_path])
            self.running_processes.append(process)
            print(f"Script started: {os.path.basename(self.script_path)}")
            return process
        except Exception as e:
            print(f"Error running script: {e}")
            return None

    def close_after_time(self):
        """Run script for specified time then close it"""
        if not self.script_path:
            print("No script selected!")
            return

        try:
            minutes = int(input("Enter duration in minutes: "))
        except ValueError:
            print("Invalid input! Please enter a number.")
            return

        print(f"Running script for {minutes} minutes...")

        # Run the script
        process = self.run_script()
        if not process:
            return

        # Set timer to terminate after specified time
        def stop_script():
            try:
                process.terminate()
                print("Script closed after specified time.")
            except:
                pass

        timer = Timer(minutes * 60, stop_script)
        timer.start()
        self.timers.append(timer)

        # Wait for completion
        try:
            process.wait()
        except:
            pass

        timer.cancel()

    def repeat_every_time(self):
        """Run script every specified interval"""
        if not self.script_path:
            print("No script selected!")
            return

        try:
            minutes = int(input("Enter interval in minutes: "))
        except ValueError:
            print("Invalid input! Please enter a number.")
            return

        print(f"Running script every {minutes} minutes (Ctrl+C to stop)...")

        def run_periodically():
            while True:
                try:
                    process = self.run_script()
                    if process:
                        process.wait()
                    time.sleep(minutes * 60)
                except KeyboardInterrupt:
                    print("\nStopping periodic execution...")
                    break
                except Exception as e:
                    print(f"Error: {e}")
                    break

        thread = threading.Thread(target=run_periodically)
        thread.daemon = True
        thread.start()

        try:
            thread.join()
        except KeyboardInterrupt:
            print("\nPeriodic execution stopped.")

    def start_at_time(self):
        """Run script at a specific time"""
        if not self.script_path:
            print("No script selected!")
            return

        try:
            time_input = input("Enter time (HH:MM format): ").strip()
            time_parts = time_input.split(":")
            hour = int(time_parts[0])
            minute = int(time_parts[1])

            if not (0 <= hour <= 23) or not (0 <= minute <= 59):
                raise ValueError("Invalid time")

        except (ValueError, IndexError):
            print("Invalid time format! Use HH:MM format (e.g., 14:30)")
            return

        repeat_daily = input("Repeat daily? (y/n): ").strip().lower() == "y"

        target_time = datetime.now().replace(
            hour=hour, minute=minute, second=0, microsecond=0
        )
        if target_time <= datetime.now():
            # If time has passed today, schedule for tomorrow
            target_time += timedelta(days=1)

        delay = (target_time - datetime.now()).total_seconds()

        print(f"Scheduled to run script at {target_time.strftime('%Y-%m-%d %H:%M')}")
        if repeat_daily:
            print("Will repeat daily")

        def run_scheduled_script():
            self.run_script()
            if repeat_daily:
                # Schedule the next execution
                next_run = datetime.now().replace(
                    hour=hour, minute=minute, second=0, microsecond=0
                ) + timedelta(days=1)
                delay = (next_run - datetime.now()).total_seconds()
                timer = Timer(delay, run_scheduled_script)
                timer.daemon = True
                timer.start()
                self.timers.append(timer)

        timer = Timer(delay, run_scheduled_script)
        timer.daemon = True
        timer.start()
        self.timers.append(timer)

        print("Timer set. Press Ctrl+C to exit.")

        try:
            # Keep the main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting...")
            for t in self.timers:
                t.cancel()

    def show_menu(self):
        """Display the main menu"""
        print("\n" + "=" * 40)
        print("SCRIPT TIMER MENU")
        print("=" * 40)
        print("1. Close script after x minutes")
        print("2. Run script every x minutes")
        print("3. Start script at specific time")
        print("4. Select script")
        print("5. Exit")
        print("=" * 40)

    def run(self):
        """Main application loop"""
        print("Simple Script Timer")
        print("This version doesn't require PyQt5")

        while True:
            self.show_menu()

            choice = input("Select option (1-5): ").strip()

            if choice == "1":
                self.close_after_time()
            elif choice == "2":
                self.repeat_every_time()
            elif choice == "3":
                self.start_at_time()
            elif choice == "4":
                if not self.select_script():
                    break
            elif choice == "5":
                print("Goodbye!")
                break
            else:
                print("Invalid option. Please try again.")


def main():
    app = SimpleScriptTimer()
    app.run()


if __name__ == "__main__":
    main()
