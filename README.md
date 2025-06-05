# DDC Monitor Input Switcher

Automated monitor input switcher using Raspberry Pi Zero W and DDC/CI commands. Switch between computer inputs via programmable macro pad button presses, eliminating the need for monitor's physical buttons.

## 🎯 Project Overview

This project creates a seamless way to switch between multiple computers connected to a single monitor using:
- **Raspberry Pi Zero W** as the main controller
- **DDC/CI protocol** for monitor communication
- **Programmable macro pad** for instant input switching
- **Systemd service** for reliable auto-start functionality

## ✨ Features

- **One-button switching** between DisplayPort and USB-C inputs
- **Automatic startup** on Pi boot
- **Smart switching** - skips unnecessary commands if already on target input
- **Comprehensive logging** with automatic rotation
- **Reliable operation** with automatic service restart on failure

## 🔧 Hardware Requirements

- Raspberry Pi Zero W
- DDC/CI compatible monitor (tested with Dell U2720Q)
- Programmable macro pad (QMK/VIA compatible)
- Micro USB OTG adapter
- Mini HDMI cable
- Two computers (one on DisplayPort, one on USB-C)

## 🚀 Quick Start

### 1. Hardware Setup
See [docs/hardware-setup.md](docs/hardware-setup.md) for detailed hardware configuration.

### 2. Software Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/ddc-monitor-switcher.git
cd ddc-monitor-switcher

# Install dependencies
sudo apt update
sudo apt install python3-evdev i2c-tools

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options > I2C > Enable

# Copy the script to your home directory
cp ddc_switcher.py /home/pi/
chmod +x /home/pi/ddc_switcher.py
```

### 3. Configure Your Monitor

```bash
# Find your monitor's I2C bus
sudo i2cdetect -l

# Test DDC communication (replace X with your bus number)
sudo ddcutil detect --bus=X

# Test input switching
sudo ddcutil setvcp 60 15 --bus=X  # DisplayPort
sudo ddcutil setvcp 60 27 --bus=X  # USB-C
```

### 4. Program Your Macro Pad

Using VIA or QMK, program your macro pad buttons to:
- **Button 1**: F23
- **Button 2**: F24

### 5. Install as System Service

```bash
# Copy service file
sudo cp ddc-switcher.service /etc/systemd/system/

# Enable and start the service
sudo systemctl daemon-reload
sudo systemctl enable ddc-switcher.service
sudo systemctl start ddc-switcher.service

# Check service status
sudo systemctl status ddc-switcher.service
```

## 🎮 Usage

Once installed and running:
- **Press Button 1 (F23)**: Switch to DisplayPort
- **Press Button 2 (F24)**: Switch to USB-C

The system automatically:
- Detects which input is currently active
- Skips switching if already on the target input
- Logs all activity for troubleshooting

## 📊 Monitoring

```bash
# View service status
sudo systemctl status ddc-switcher.service

# View real-time logs
sudo journalctl -u ddc-switcher.service -f

# View log files
tail -f /var/log/ddc_switcher.log
```

## 🔧 Configuration

### Monitor Input Codes
Edit `ddc_switcher.py` to modify input codes for your specific monitor:

```python
self.inputs = {
    'displayport': 15,  # VCP code for DisplayPort
    'usbc': 27,         # VCP code for USB-C
    # Add other inputs as needed:
    # 'hdmi1': 17,      # HDMI-1
    # 'hdmi2': 18,      # HDMI-2
}
```

### Button Mapping
Modify button assignments:

```python
self.button_mapping = {
    evdev.ecodes.KEY_F23: 'displayport',
    evdev.ecodes.KEY_F24: 'usbc',
    # Add more buttons:
    # evdev.ecodes.KEY_F13: 'hdmi1',
}
```

## 🛠️ Troubleshooting

### Service Not Starting
```bash
# Check service logs
sudo journalctl -u ddc-switcher.service -n 50

# Test script manually
sudo python3 /home/pi/ddc_switcher.py
```

### Macro Pad Not Detected
```bash
# List input devices
ls /dev/input/event*

# Test with evtest
sudo evtest
```

### DDC Commands Failing
```bash
# Check I2C bus
sudo i2cdetect -l

# Test DDC communication
sudo ddcutil detect

# Check monitor capabilities
sudo ddcutil capabilities
```

## 📁 Project Structure

```
ddc-monitor-switcher/
├── README.md                 # This file
├── ddc_switcher.py          # Main Python script
├── ddc-switcher.service     # Systemd service file
├── docs/
│   ├── hardware-setup.md    # Detailed hardware guide
│   └── troubleshooting.md   # Common issues and solutions
├── LICENSE                  # MIT License
└── .gitignore              # Git ignore file
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [ddcutil](http://www.ddcutil.com/) for DDC/CI communication
- [evdev](https://python-evdev.readthedocs.io/) for input device handling
- [QMK](https://qmk.fm/) and [VIA](https://www.caniusevia.com/) for macro pad programming

## 💡 Related Projects

- Looking for wireless switching? Consider adding MQTT integration
- Want multiple monitors? The script can be extended for multiple DDC buses
- Need different input types? Check your monitor's VCP codes with `ddcutil capabilities`
