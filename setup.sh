#!/bin/bash
# Setup script for Juniper USB Wizard

set -e  # Exit on error

echo "==================================="
echo "Juniper USB Wizard - Setup"
echo "==================================="
echo ""

# Detect package manager
if command -v apt-get &> /dev/null; then
    PKG_MANAGER="apt"
elif command -v dnf &> /dev/null; then
    PKG_MANAGER="dnf"
elif command -v yum &> /dev/null; then
    PKG_MANAGER="yum"
elif command -v pacman &> /dev/null; then
    PKG_MANAGER="pacman"
else
    PKG_MANAGER="unknown"
fi

echo "Detected package manager: $PKG_MANAGER"
echo ""

# Function to install packages
install_package() {
    local package=$1
    echo "Installing $package..."

    case $PKG_MANAGER in
        apt)
            sudo apt-get update -qq
            sudo apt-get install -y $package
            ;;
        dnf)
            sudo dnf install -y $package
            ;;
        yum)
            sudo yum install -y $package
            ;;
        pacman)
            sudo pacman -S --noconfirm $package
            ;;
        *)
            echo "❌ Unknown package manager. Please install $package manually."
            return 1
            ;;
    esac
}

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed."
    echo ""
    read -p "Install Python 3? [y/N]: " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        case $PKG_MANAGER in
            apt) install_package "python3 python3-pip python3-venv" ;;
            dnf|yum) install_package "python3 python3-pip" ;;
            pacman) install_package "python python-pip" ;;
            *)
                echo "Please install Python 3 manually and run this script again."
                exit 1
                ;;
        esac
    else
        echo "Python 3 is required. Exiting."
        exit 1
    fi
fi

echo "✓ Python 3 found: $(python3 --version)"

# Check if pip3 is installed
if ! command -v pip3 &> /dev/null && ! python3 -m pip --version &> /dev/null; then
    echo "⚠ pip3 not found. Installing..."
    case $PKG_MANAGER in
        apt) install_package "python3-pip" ;;
        dnf|yum) install_package "python3-pip" ;;
        pacman) install_package "python-pip" ;;
        *)
            echo "❌ Could not install pip3. Please install it manually."
            exit 1
            ;;
    esac
fi

echo "✓ pip3 found"

# Check if python3-venv is available
echo "Checking for venv module..."
if ! python3 -m venv --help &> /dev/null; then
    echo "⚠ python3-venv not found. Installing..."
    case $PKG_MANAGER in
        apt) install_package "python3-venv" ;;
        dnf|yum)
            echo "✓ venv should be included with Python 3"
            ;;
        pacman)
            echo "✓ venv should be included with Python 3"
            ;;
        *)
            echo "❌ Could not install python3-venv. Please install it manually."
            exit 1
            ;;
    esac
fi

echo "✓ venv module available"

# Check if dosfstools is installed
if ! command -v mkfs.vfat &> /dev/null; then
    echo "⚠ mkfs.vfat not found (part of dosfstools package)"
    echo ""
    read -p "Install dosfstools? [Y/n]: " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Nn]$ ]]; then
        install_package "dosfstools"
    else
        echo "⚠ Warning: The wizard will not work without dosfstools!"
    fi
else
    echo "✓ mkfs.vfat found"
fi

echo ""
echo "Creating virtual environment..."
python3 -m venv venv

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
