# Juniper Installation Files

This directory should contain your Juniper installation files (`.tgz` format).

## Instructions

1. Download your Juniper installation files from [Juniper Networks Support Portal](https://support.juniper.net/)
   - You'll need a valid support account
   - Download the appropriate firmware version for your switch model

2. Copy the downloaded files into this directory:
   ```bash
   cp ~/Downloads/jinstall-*.tgz juniper_files/
   ```

3. Run the wizard:
   ```bash
   cd ..
   ./run.sh
   ```

## Supported File Format

- `.tgz` files (compressed Juniper installation packages)
- Example: `jinstall-host-qfx-5-21.4R3.15-signed.tgz`

## Note

⚠️ Do not commit Juniper installation files to version control. They are proprietary and covered by Juniper's licensing terms. The `.gitignore` file is already configured to exclude `.tgz` files from this directory.
