# Hardware Setup Guide

This guide walks you through the complete hardware setup for the DDC Monitor Input Switcher project.

## 📦 Parts List

### Required Components

| Component | Purpose | Notes |
|-----------|---------|-------|
| **Raspberry Pi Zero W** | Main controller | WiFi required for SSH access |
| **Micro SD Card** | Storage (16GB+) | Class 10 recommended |
| **Mini HDMI Cable** | Pi to monitor connection | For DDC/CI communication |
| **Micro USB OTG Adapter** | Macro pad connection | Enables USB host mode |
| **Programmable Macro Pad** | Input control | QMK/VIA compatible |
| **Micro USB Power Adapter** | Pi power supply | 5V, 1A minimum rating |
| **DDC/CI Compatible Monitor** | Display device | Most modern monitors work |

### Tested Hardware

- **Monitor**: Dell U2720Q (confirmed working)
- **Macro Pad**: Binepad BNK8 (confirmed working)
- **Pi**: Raspberry Pi Zero W v1.1

## 🔌 Physical Connections

### Connection Diagram

```
[Computer 1] ──(DisplayPort)──┐
                               ├── [Monitor] ──(Mini HDMI)── [Pi Zero W] ──(Micro USB Power)── [Power Adapter/USB Charger]
[Computer 2] ──(USB-C)────────┘                                    │
                                                                    │
[Macro Pad] ──(USB)── [OTG Adapter] ──(Micro USB Data)─────────────┘
```

### Step-by-Step Connections

1. **Connect Computers to Monitor**
   - Computer 1 → Monitor DisplayPort
   - Computer 2 → Monitor USB-C port

2. **Connect Pi to Monitor**
   - Pi Zero W Mini HDMI → Monitor HDMI port
   - This connection enables DDC/CI communication

3. **Connect Macro Pad to Pi**
   - Macro Pad USB → OTG Adapter
   - OTG Adapter → Pi Zero W micro USB port

4. **Power the Pi**
   - Pi Zero W micro USB power port → USB power adapter (5V, 1A minimum)
   - Use dedicated power supply, not computer USB port
   - Keep power cable separate from data cable

## ⚙️ Raspberry Pi Configuration

### 1. Initial Setup

```bash
# Update the system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install i2c-tools python3-evdev git vim -y
```

### 2. Enable I2C Interface

```bash
# Method 1: Using raspi-config (recommended)
sudo raspi-config
# Navigate to: Interface Options > I2C > Enable > Finish

# Method 2: Manual configuration
echo 'dtparam=i2c_arm=on' | sudo tee -a /boot/firmware/config.txt
```

### 3. Enable USB OTG Host Mode

Add these lines to `/boot/firmware/config.txt`:

```bash
sudo nano /boot/firmware/config.txt

# Add at the end of the file:
dtoverlay=dwc2
```

Add to `/boot/firmware/cmdline.txt` (add after `rootwait`):

```bash
sudo nano /boot/firmware/cmdline.txt

# Add: modules-load=dwc2
# Example result:
# ... rootwait modules-load=dwc2 quiet init=/usr/lib/...
```

### 4. Reboot and Verify

```bash
sudo reboot

# After reboot, verify I2C is enabled
lsmod | grep i2c

# Verify USB OTG is working
lsmod | grep dwc2

# Check I2C buses
sudo i2cdetect -l
```

## 🖥️ Monitor Configuration

### 1. Identify Your Monitor's I2C Bus

```bash
# List all I2C buses
sudo i2cdetect -l

# Typical output:
# i2c-1   i2c       bcm2835 (i2c@7e804000)                 I2C adapter
# i2c-2   i2c       vc4                                     I2C adapter  <- Usually this one
```

### 2. Test DDC Communication

```bash
# Detect monitors on I2C bus (replace 2 with your bus number)
sudo ddcutil detect --bus=2

# Expected output should show your monitor details
```

### 3. Find Input VCP Codes

```bash
# Get monitor capabilities
sudo ddcutil capabilities --bus=2

# Look for input source codes in the output
# Common codes:
# DisplayPort: 15 (0x0f)
# HDMI-1: 17 (0x11) 
# HDMI-2: 18 (0x12)
# USB-C: 27 (0x1b)
```

### 4. Test Input Switching

```bash
# Test switching to different inputs
sudo ddcutil setvcp 60 15 --bus=2  # DisplayPort
sudo ddcutil setvcp 60 27 --bus=2  # USB-C

# Verify current input
sudo ddcutil getvcp 60 --bus=2
```

## 🎮 Macro Pad Setup

### 1. Install VIA (Recommended)

1. Download VIA from [usevia.app](https://usevia.app)
2. Connect your macro pad to your computer
3. Open VIA and authorize the device
4. Program buttons:
   - **Button 1**: F23
   - **Button 2**: F24

### 2. Alternative: QMK Configuration

If your macro pad isn't VIA-compatible:

```c
// In your QMK keymap
const uint16_t PROGMEM keymaps[][MATRIX_ROWS][MATRIX_COLS] = {
    [0] = LAYOUT(
        KC_F23,  // Button 1
        KC_F24   // Button 2
    ),
};
```

### 3. Verify Macro Pad Programming

Connect the macro pad to your Pi and test:

```bash
# Install evtest
sudo apt install evtest

# Test button presses
sudo evtest
# Select your macro pad device
# Press buttons to verify F23/F24 codes
```

## 🔍 Troubleshooting Hardware Issues

### I2C Not Working

```bash
# Check if I2C is enabled
sudo raspi-config nonint get_i2c
# Should return 0 (enabled)

# Check loaded modules
lsmod | grep i2c_dev

# If not loaded, add to /etc/modules
echo 'i2c-dev' | sudo tee -a /etc/modules
```

### USB OTG Not Working

```bash
# Check if dwc2 module is loaded
lsmod | grep dwc2

# If not loaded, check config files
grep -n dwc2 /boot/firmware/config.txt
grep -n dwc2 /boot/firmware/cmdline.txt

# Check USB devices
lsusb
```

### Monitor Not Detected

```bash
# Try different I2C buses
for bus in 0 1 2 3; do
    echo "Testing bus $bus:"
    sudo ddcutil detect --bus=$bus
done

# Check HDMI connection
# The Pi must be connected via HDMI for DDC to work
```

### Macro Pad Not Detected

```bash
# List input devices
ls -la /dev/input/event*

# Check with evtest
sudo evtest
# Look for your macro pad in the device list

# Check USB devices
lsusb
```

## 🔧 Hardware Tips

### Power Considerations

- **Pi Zero W Power**: ~500mA typical
- **Macro Pad Power**: Usually powered via USB
- **Total Power**: Plan for 1A minimum power supply

### Cable Management

- Use short, high-quality cables to minimize interference
- Keep power and data cables separated
- Consider a case or mounting solution for the Pi

### Monitor Compatibility

Most modern monitors support DDC/CI, but some have it disabled by default:

- **Dell**: Usually enabled by default
- **ASUS**: Check OSD settings for "DDC/CI"
- **LG**: Look for "Deep Color" or "HDMI Ultra HD Deep Color"
- **Samsung**: Check for "Input Signal Plus" or similar

### Performance Notes

- DDC commands can take 1-2 seconds to execute
- Some monitors have faster switching between certain inputs
- The Pi Zero W is sufficient for this application

## 📐 Physical Installation

### Mounting Options

1. **Desktop Setup**: Pi Zero case with heat dissipation
2. **Monitor Mount**: VESA-compatible case attached to monitor
3. **Under-desk**: Adhesive mount or small enclosure

### Cable Routing

- Route cables to avoid strain on Pi Zero connectors
- Use cable management for clean installation
- Consider strain relief for frequently moved cables

## ✅ Final Verification

Before proceeding to software installation:

- [ ] Pi Zero W boots successfully
- [ ] I2C interface is enabled and working
- [ ] USB OTG host mode is functional
- [ ] Monitor is detected via DDC
- [ ] Manual DDC input switching works
- [ ] Macro pad is detected and programmed
- [ ] All cables are secure and properly routed

Once all hardware is confirmed working, proceed to the software installation in the main [README.md](../README.md).
