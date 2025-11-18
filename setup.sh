#!/bin/bash
# Setup script for Juniper USB Wizard

echo "==================================="
echo "Juniper USB Wizard - Setup"
echo "==================================="
echo ""

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed."
    echo "Please install pip3 and try again."
    exit 1
fi

echo "✓ pip3 found"

# Check if dosfstools is installed
if ! command -v mkfs.vfat &> /dev/null; then
    echo "⚠ Warning: mkfs.vfat not found (part of dosfstools package)"
    echo ""
    echo "Would you like to install it now? (requires sudo)"
    read -p "Install dosfstools? [y/N]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v apt-get &> /dev/null; then
            sudo apt-get install -y dosfstools
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y dosfstools
        elif command -v yum &> /dev/null; then
            sudo yum install -y dosfstools
        else
            echo "Could not determine package manager. Please install dosfstools manually."
            exit 1
        fi
    else
        echo "Skipping dosfstools installation. The wizard will not work without it."
    fi
else
    echo "✓ mkfs.vfat found"
fi

echo ""
echo "Creating virtual environment..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "Error: Failed to create virtual environment."
    exit 1
fi

echo "✓ Virtual environment created"

echo ""
echo "Installing Python dependencies..."
venv/bin/pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "Error: Failed to install dependencies."
    exit 1
fi

echo ""
echo "Making scripts executable..."
chmod +x juniper_wizard.py
chmod +x run.sh

echo ""
echo "==================================="
echo "✓ Setup complete!"
echo "==================================="
echo ""
echo "To run the wizard:"
echo "  ./run.sh"
echo ""
echo "Make sure to run 'sudo -v' first to cache your sudo credentials."
