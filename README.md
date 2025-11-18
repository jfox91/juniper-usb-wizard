# Juniper USB Wizard

A terminal-based tool to properly format USB drives and copy Juniper installation files for use with Juniper switches.

## Features

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

3. Run the setup script (it will handle everything):
   ```bash
   ./setup.sh
   ```

   The setup script will:
   - Check for Python 3 and pip
   - Prompt to install dosfstools if needed
   - Create a virtual environment
   - Install all Python dependencies
   - Make scripts executable

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

**"No USB drives found"**
- Ensure your USB drive is connected
- Try running `lsblk` to see if the system detects it

**Permission errors**
- The script requires sudo access. Run: `sudo -v` before starting
- Ensure you're in the sudoers group

**Format fails**
- Make sure `dosfstools` is installed
- Check that the drive isn't mounted elsewhere: `sudo umount /dev/sdX`

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
