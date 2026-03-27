#!/bin/bash

# -----------------------------------------------------------------------------
# pyenv_install_python_with_tkinter.sh
#
# A universal script to install a specific Python version using pyenv,
# automatically handling tkinter dependencies on macOS (Homebrew)
# and major Linux distributions.
#
# Usage: ./pyenv_install_python_with_tkinter.sh <python_version>
# Example: ./pyenv_install_python_with_tkinter.sh 3.14.0
# -----------------------------------------------------------------------------

# --- Safety and Checks ---
# -e: Exit immediately if a command exits with a non-zero status.
# -u: Treat unset variables as an error when substituting.
# -o pipefail: The return value of a pipeline is the status of
#              the last command to exit with a non-zero status.
set -euo pipefail

# 1. Check if Python version is provided
if [ -z "${1:-}" ]; then
    echo "Error: No Python version specified." >&2
    echo "Usage: $0 <python_version>" >&2
    exit 1
fi
PYTHON_VERSION="$1"

# 2. Check if pyenv is installed
if ! command -v pyenv > /dev/null; then
    echo "Error: 'pyenv' command not found." >&2
    echo "Please install pyenv first." >&2
    exit 1
fi

# 3. Detect Operating System
OS_TYPE=$(uname)

# --- Platform-Specific Setup ---

if [ "$OS_TYPE" = "Darwin" ]; then
    # --- macOS (using Homebrew) ---
    echo "Detected macOS (Darwin)."
    
    if ! command -v brew > /dev/null; then
        echo "Error: Homebrew ('brew') not found." >&2
        echo "Please install Homebrew first." >&2
        exit 1
    fi
    
    brew update
    echo "Installing/updating tcl-tk and other build dependencies..."
    # Install tcl-tk and other pyenv-recommended dependencies
    brew install tcl-tk openssl readline sqlite3 xz zlib bzip2
    
    # Dynamically get the Homebrew-installed tcl-tk path (for Intel & Apple Silicon)
    TCL_TK_PATH=$(brew --prefix tcl-tk)
    
    echo "Setting compile-time environment variables for tcl-tk..."
    export LDFLAGS="-L${TCL_TK_PATH}/lib"
    export CPPFLAGS="-I${TCL_TK_PATH}/include"
    export PKG_CONFIG_PATH="${TCL_TK_PATH}/lib/pkgconfig"
    
    # Note: pyenv's build-system will usually find other brew dependencies
    # automatically, but setting this ensures tcl-tk is found.
    
elif [ "$OS_TYPE" = "Linux" ]; then
    # --- Linux ---
    echo "Detected Linux."
    
    # Check for sudo permissions
    SUDO_CMD=""
    if [ "$(id -u)" -ne 0 ]; then
        if command -v sudo > /dev/null; then
            SUDO_CMD="sudo"
            echo "Sudo permissions are required to install system dependencies..."
        else
            echo "Error: This script requires root privileges or 'sudo' to install dependencies." >&2
            exit 1
        fi
    fi

    echo "Detecting package manager and installing 'tk-dev' and related dependencies..."
    
    # General dependencies recommended by pyenv wiki (for building Python)
    # We add tcl/tk *dev* packages to this list.
    
    if command -v apt-get > /dev/null; then
        # Debian / Ubuntu
        $SUDO_CMD apt-get update
        $SUDO_CMD apt-get install -y make build-essential libssl-dev zlib1g-dev \
            libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
            libncursesw5-dev xz-utils libxml2-dev libxmlsec1-dev \
            libffi-dev liblzma-dev tcl-dev tk-dev
            
    elif command -v dnf > /dev/null; then
        # Fedora / RHEL (newer)
        $SUDO_CMD dnf install -y make gcc zlib-devel bzip2 bzip2-devel \
            readline-devel sqlite sqlite-devel openssl-devel \
            libffi-devel xz-devel libuuid-devel gdbm-libs \
            libxml2-devel libxmlsec1-devel tk-devel tcl-devel
            
    elif command -v yum > /dev/null; then
        # CentOS / RHEL (older)
        $SUDO_CMD yum install -y make gcc zlib-devel bzip2 bzip2-devel \
            readline-devel sqlite sqlite-devel openssl-devel \
            libffi-devel xz-devel libuuid-devel gdbm-libs \
            libxml2-devel libxmlsec1-devel tk-devel tcl-devel
            
    elif command -v pacman > /dev/null; then
        # Arch Linux
        $SUDO_CMD pacman -Syu --noconfirm --needed base-devel openssl zlib \
            bzip2 readline sqlite xz libffi tk tcl
            
    else
        echo "Warning: Could not identify package manager." >&2
        echo "Please manually install Python build dependencies, 'tk-dev', and 'tcl-dev'."
        # We continue anyway, just in case they are already installed.
    fi
    
    # On Linux, if installed via system package manager,
    # libs and headers are in standard paths (e.g., /usr/lib, /usr/include).
    # pyenv's build script finds these automatically, so we *do not*
    # need to set LDFLAGS and CPPFLAGS as we do for Homebrew on macOS.

else
    echo "Warning: Unknown operating system '$OS_TYPE'."
    echo "Attempting to install without platform-specific dependencies."
fi

# --- Execute Installation ---
echo ""
echo "==== Ready to install Python ${PYTHON_VERSION} ===="

# We pass the environment variables explicitly to the pyenv command
# to ensure they are set for this command's environment.
# ${VAR:-} is a safety mechanism for `set -u` (use empty string if unset).
env \
    LDFLAGS="${LDFLAGS:-}" \
    CPPFLAGS="${CPPFLAGS:-}" \
    PKG_CONFIG_PATH="${PKG_CONFIG_PATH:-}" \
    pyenv install "$PYTHON_VERSION"

echo ""
echo "==== Python ${PYTHON_VERSION} installation complete ===="

# Verify that tkinter was installed successfully
echo "Verifying tkinter for ${PYTHON_VERSION}..."
TEMP_PYTHON_PATH=$(pyenv root)/versions/${PYTHON_VERSION}/bin/python
if [ ! -f "$TEMP_PYTHON_PATH" ]; then
    echo "Error: Could not find the newly installed Python executable." >&2
    exit 1
fi

if "$TEMP_PYTHON_PATH" -c "import tkinter; print('tkinter OK')" ; then
    echo "Success! Tkinter module is working in ${PYTHON_VERSION}."
else
    echo "Error: Tkinter module failed to install correctly in ${PYTHON_VERSION}." >&2
fi