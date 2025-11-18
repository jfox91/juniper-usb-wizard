# Juniper USB Wizard
[jin-usb-wizard](https://github.com/user-attachments/assets/8e4dccc1-2903-4b43-b87a-3b0a1543ffd3)
A terminal-based tool to properly format USB drives and copy Juniper installation files for use with Juniper switches.

## Features!


- **Interactive TUI** - Easy-to-use terminal interface
- **Safety checks** - Warns when selecting drives larger than 10GB
- **Proper formatting** - Ensures FAT32 formatting for Juniper compatibility
- **Bundled files** - All Juniper files are included in the project
- **Progress tracking** - Clear feedback during format and copy operations

## Requirements

- Linux operating system
- Python 3.8 or higher
- sudo access (required for formatting drives)
- `mkfs.vfat` utility (usually part of `dosfstools` package)

## Installation

### Quick Install (One Command)

```bash
cd ~ && git clone https://github.com/jfox91/juniper-usb-wizard.git && cd juniper-usb-wizard && ./setup.sh
```

### Step-by-Step Install

1. Clone or download this repository:
   ```bash
   cd ~
   git clone https://github.com/jfox91/juniper-usb-wizard.git
   # OR download the ZIP from GitHub and extract it
   ```

2. Navigate to the directory:
   ```bash
   cd juniper-usb-wizard
   ```

3. Run the setup script (it will handle everything automatically):
   ```bash
   ./setup.sh
   ```

   The setup script will automatically:
   - Detect your Linux package manager (apt, dnf, yum, pacman)
   - Install Python 3 if missing (prompts first)
   - Install pip3 if missing
   - Install python3-venv if missing
   - Install dosfstools (mkfs.vfat) if missing (prompts first)
   - Create a virtual environment
   - Install all Python dependencies
   - Make scripts executable

   **No manual dependency installation needed!** Just run `./setup.sh` and answer the prompts.

## Usage

1. Connect your USB drive to your computer

2. Run the wizard:
   ```bash
   ./run.sh
   ```

3. Follow the on-screen prompts:
   - Select the Juniper file you want to install
   - Select the USB drive
   - Confirm the operation (pay attention to warnings!)
   - Wait for the process to complete

4. When done, safely remove the USB drive and use it with your Juniper switch

## Adding Juniper Files

**Important:** This repository does not include Juniper installation files. You must provide your own.

To add Juniper installation files:

1. Download your Juniper installation `.tgz` files from Juniper Networks
2. Place them in the `juniper_files/` directory
3. The files will automatically appear in the selection menu when you run the wizard

Example:
```bash
cp ~/Downloads/jinstall-*.tgz juniper_files/
```

## Safety Features

- **Drive size warning**: Displays a warning when selecting drives larger than 10GB
- **Confirmation screen**: Shows all details before proceeding
- **System drive exclusion**: Automatically excludes your main system drive from the list
- **sudo requirement**: Ensures proper permissions for drive operations

## Troubleshooting

**"pip3 not installed" or "python3-venv not found"**
- Simply run `./setup.sh` - it will automatically detect and offer to install missing dependencies
- If the setup script doesn't work, manually install: `sudo apt-get install python3 python3-pip python3-venv dosfstools`

**"No USB drives found"**
- Ensure your USB drive is connected
- Try running `lsblk` to see if the system detects it
- Make sure the drive isn't your system drive (those are automatically excluded)

**Permission errors**
- The script requires sudo access. Run: `sudo -v` before starting
- Ensure you're in the sudoers group

**"Failed to format" or "device busy"**
- The drive might be mounted. The wizard will try to unmount it automatically
- If that fails, manually unmount: `sudo umount /dev/sdX*`
- Make sure no file manager windows are open with the USB drive

**Setup script fails on minimal systems**
- Some minimal Linux installs don't have basic tools. Install: `sudo apt-get install git python3 python3-pip python3-venv dosfstools`

## How It Works

1. **Unmounts** the drive if currently mounted
2. **Formats** the drive as FAT32 with the label "JUNIPER"
3. **Mounts** the freshly formatted drive temporarily
4. **Copies** the selected Juniper file without extraction
5. **Syncs** data to ensure everything is written
6. **Unmounts** and cleans up

## Warning

⚠️ **This tool will erase ALL data on the selected USB drive!** ⚠️

Always double-check you've selected the correct drive before proceeding.

## License

MIT License - Feel free to use and modify as needed.
