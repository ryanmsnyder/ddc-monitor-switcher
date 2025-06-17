#!/usr/bin/env python3
"""
DDC Monitor Input Switcher
Listens for macro pad button presses and switches monitor inputs via DDC commands
Simple version: Always wakes monitor before switching (F23/F24 only)
"""

import evdev
import subprocess
import time
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Configure logging with rotation
log_handler = RotatingFileHandler(
    '/var/log/ddc_switcher.log',
    maxBytes=1024*1024,  # 1MB max file size
    backupCount=3        # Keep 3 backup files
)
console_handler = logging.StreamHandler()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[log_handler, console_handler]
)

class DDCMonitorSwitcher:
    def __init__(self):
        self.bus_number = 2  # Monitor on i2c-2
        self.inputs = {
            'displayport': 15,  # VCP code for DisplayPort
            'usbc': 27,         # VCP code for USB-C
            'hdmi': 17,         # VCP code for HDMI
        }
        self.button_mapping = {
            evdev.ecodes.KEY_F23: 'displayport',  # Button 1 -> DisplayPort
            evdev.ecodes.KEY_F24: 'usbc',         # Button 2 -> USB-C
            evdev.ecodes.KEY_F22: 'hdmi_standby', # Button 3 -> HDMI + Standby
        }
        self.device = None
        self.current_input = None
        
    def find_macro_pad(self):
        """Find and connect to the macro pad device"""
        devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        
        for device in devices:
            # Look for keyboard-like devices (macro pads usually appear as keyboards)
            if evdev.ecodes.EV_KEY in device.capabilities():
                logging.info(f"Found input device: {device.name} at {device.path}")
                # Look for the specific binepad BNK8 device (not the "Keyboard" variant)
                if device.name == "binepad BNK8":
                    return device
                    
        # If no specific macro pad found, list all keyboard devices for manual selection
        keyboard_devices = []
        for device in devices:
            if evdev.ecodes.EV_KEY in device.capabilities():
                keyboard_devices.append(device)
                
        if keyboard_devices:
            logging.info("Available keyboard-like devices:")
            for i, dev in enumerate(keyboard_devices):
                logging.info(f"  {i}: {dev.name} at {dev.path}")
            
            # For now, return the first one (you can modify this logic)
            return keyboard_devices[0] if keyboard_devices else None
            
        return None
    
    def wake_monitor(self):
        """Wake up the monitor from standby/sleep"""
        cmd = [
            'ddcutil', 'setvcp', 'D6', '01',  # Set power state to On
            f'--bus={self.bus_number}', '--noverify'
        ]
        
        try:
            logging.info("Sending wake command to monitor")
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logging.info("Wake command sent successfully")
                return True
            else:
                logging.warning(f"Wake command failed with code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error("Wake command timed out")
            return False
        except Exception as e:
            logging.error(f"Error sending wake command: {e}")
            return False
    
    def switch_input(self, input_name):
        """Switch monitor input using DDC command"""
        if input_name not in self.inputs:
            logging.error(f"Unknown input: {input_name}")
            return False
            
        vcp_code = self.inputs[input_name]
        cmd = [
            'ddcutil', 'setvcp', '60', str(vcp_code), 
            f'--bus={self.bus_number}'
        ]
        
        try:
            logging.info(f"Switching to {input_name} (VCP code: {vcp_code})")
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                logging.info(f"Successfully switched to {input_name}")
                self.current_input = input_name
                return True
            else:
                logging.error(f"Input switch failed with code {result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error("Input switch command timed out")
            return False
        except Exception as e:
            logging.error(f"Error executing input switch: {e}")
            return False
    
    def get_current_input(self):
        """Get current monitor input (optional - for status checking)"""
        cmd = [
            'ddcutil', 'getvcp', '60', 
            f'--bus={self.bus_number}'
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Parse the output to determine current input
                output = result.stdout.lower()
                if 'x0f' in output or '15' in output:
                    return 'displayport'
                elif 'x1b' in output or '27' in output:
                    return 'usbc'
                elif 'x11' in output or '17' in output:
                    return 'hdmi'
            return 'unknown'
        except:
            return 'unknown'
    
    def wake_and_switch(self, input_name):
        """Wake monitor and switch input - simple approach"""
        logging.info(f"Wake and switch to {input_name} requested")
        
        # Step 1: Always send wake command (safe even if already awake)
        self.wake_monitor()
        
        # Step 2: Switch to requested input
        return self.switch_input(input_name)
    
    def switch_to_hdmi_and_standby(self):
        """Switch to HDMI input and then activate standby mode"""
        logging.info("Starting HDMI + Standby sequence")
        
        # Step 1: Switch to HDMI input
        hdmi_cmd = [
            'ddcutil', 'setvcp', '60', '17', 
            f'--bus={self.bus_number}'
        ]
        
        try:
            logging.info("Step 1: Switching to HDMI input")
            hdmi_result = subprocess.run(hdmi_cmd, capture_output=True, text=True, timeout=10)
            
            if hdmi_result.returncode != 0:
                logging.error(f"HDMI switch failed with code {hdmi_result.returncode}")
                return False
            
            logging.info("HDMI switch completed successfully")
            self.current_input = 'hdmi'
            
            # Step 2: Activate standby mode
            standby_cmd = [
                'ddcutil', 'setvcp', 'D6', '02', 
                f'--bus={self.bus_number}', '--noverify'
            ]
            
            logging.info("Step 2: Activating standby mode")
            standby_result = subprocess.run(standby_cmd, capture_output=True, text=True, timeout=10)
            
            if standby_result.returncode == 0:
                logging.info("HDMI + Standby sequence completed successfully")
                return True
            else:
                logging.error(f"Standby command failed with code {standby_result.returncode}")
                return False
                
        except subprocess.TimeoutExpired:
            logging.error("HDMI + Standby command timed out")
            return False
        except Exception as e:
            logging.error(f"Error in HDMI + Standby sequence: {e}")
            return False
    
    def handle_button_press(self, key_event):
        """Handle macro pad button press"""
        # Get both the numeric scancode and string keycode
        scancode = key_event.scancode
        keycode_str = key_event.keycode
        
        logging.info(f"Button press detected - scancode: {scancode}, keycode: {keycode_str}")
        
        # Check if the scancode matches our mapping
        if scancode in self.button_mapping:
            action = self.button_mapping[scancode]
            logging.info(f"Button mapped to: {action}")
            
            # Handle special HDMI + Standby action
            if action == 'hdmi_standby':
                logging.info("Executing HDMI + Standby sequence")
                self.switch_to_hdmi_and_standby()
            else:
                # Handle regular input switching with wake
                logging.info(f"Executing wake and switch to {action}")
                self.wake_and_switch(action)
        else:
            logging.info(f"Scancode {scancode} not found in button mapping")
            logging.info(f"Available mappings: {self.button_mapping}")
    
    def run(self):
        """Main event loop"""
        logging.info("Starting Simple DDC Monitor Switcher...")
        logging.info("Mode: Always wake + switch for F23/F24")
        
        # Find macro pad
        self.device = self.find_macro_pad()
        if not self.device:
            logging.error("No suitable input device found!")
            return
            
        logging.info(f"Using device: {self.device.name}")
        
        # Get initial input state
        self.current_input = self.get_current_input()
        logging.info(f"Current input: {self.current_input}")
        
        try:
            # Main event loop
            for event in self.device.read_loop():
                if event.type == evdev.ecodes.EV_KEY:
                    key_event = evdev.categorize(event)
                    
                    # Only handle key press events (not release)
                    if key_event.keystate == evdev.KeyEvent.key_down:
                        logging.info(f"Key press: {key_event.keycode}")
                        self.handle_button_press(key_event)
                        
        except KeyboardInterrupt:
            logging.info("Shutting down...")
        except Exception as e:
            logging.error(f"Error in main loop: {e}")
        finally:
            if self.device:
                self.device.close()

def main():
    # Check if running as root (needed for DDC commands)
    if Path('/var/log').exists() and not Path('/var/log').is_dir():
        logging.error("Cannot access log directory")
        
    switcher = DDCMonitorSwitcher()
    switcher.run()

if __name__ == "__main__":
    main()
