#!/bin/bash

set -euo pipefail

# Define the PHP version to install
PHP_VERSION=${1:-"latest"}

echo "Preparing the build environment for PHP $PHP_VERSION..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Error: Homebrew ('brew') not found." >&2
    echo "Please install Homebrew first." >&2
    exit 1
fi

# Install necessary dependencies
# Includes build tools (autoconf, bison...) and common libraries (openssl, libxml2, oniguruma...)
echo "Installing/updating Homebrew packages..."
brew update
brew install \
    autoconf \
    automake \
    bison \
    freetype \
    gd \
    gettext \
    icu4c \
    krb5 \
    libedit \
    libiconv \
    libjpeg \
    libpng \
    libxml2 \
    libzip \
    pkg-config \
    re2c \
    zlib \
    openssl@3 \
    curl \
    oniguruma

# Set environment variables
# This is the most critical step, telling the compiler where to find these Homebrew-installed libraries
echo "Setting build paths..."

# Get the paths of each package
AUTOCONF_PATH=$(brew --prefix autoconf)
AUTOMAKE_PATH=$(brew --prefix automake)
BISON_PATH=$(brew --prefix bison)
FREETYPE_PATH=$(brew --prefix freetype)
GD_PATH=$(brew --prefix gd)
GETTEXT_PATH=$(brew --prefix gettext)
ICU4C_PATH=$(brew --prefix icu4c)
KRB5_PATH=$(brew --prefix krb5)
LIBEDIT_PATH=$(brew --prefix libedit)
LIBICONV_PATH=$(brew --prefix libiconv)
LIBJPEG_PATH=$(brew --prefix libjpeg)
LIBPNG_PATH=$(brew --prefix libpng)
LIBXML2_PATH=$(brew --prefix libxml2)
LIBZIP_PATH=$(brew --prefix libzip)
RE2C_PATH=$(brew --prefix re2c)
ZLIB_PATH=$(brew --prefix zlib)
OPENSSL_PATH=$(brew --prefix openssl@3)
CURL_PATH=$(brew --prefix curl)
ONIGURUMA_PATH=$(brew --prefix oniguruma)

# Set PKG_CONFIG_PATH so pkg-config can find them
export PKG_CONFIG_PATH="$OPENSSL_PATH/lib/pkgconfig:$CURL_PATH/lib/pkgconfig:$ZLIB_PATH/lib/pkgconfig:$LIBXML2_PATH/lib/pkgconfig:$ICU4C_PATH/lib/pkgconfig:$LIBICONV_PATH/lib/pkgconfig:$ONIGURUMA_PATH/lib/pkgconfig:$LIBZIP_PATH/lib/pkgconfig"
echo "PKG_CONFIG_PATH set to: $PKG_CONFIG_PATH"

# Set build options, forcing the paths for OpenSSL and Iconv
export PHP_CONFIGURE_OPTS="--with-openssl=$OPENSSL_PATH --with-curl=$CURL_PATH --with-zlib=$ZLIB_PATH --with-iconv=$LIBICONV_PATH --with-external-pcre"
echo "PHP_CONFIGURE_OPTS set to: $PHP_CONFIGURE_OPTS"

# Additional compiler flags (to ensure zlib and bzip2 are correctly linked)
export CFLAGS="-I$OPENSSL_PATH/include -I$CURL_PATH/include -I$ZLIB_PATH/include -I$ONIGURUMA_PATH/include -I$LIBXML2_PATH/include -I$ICU4C_PATH/include -I$LIBICONV_PATH/include -I$LIBZIP_PATH/include"
export LDFLAGS="-L$OPENSSL_PATH/lib -L$CURL_PATH/lib -L$ZLIB_PATH/lib -L$ONIGURUMA_PATH/lib -L$LIBXML2_PATH/lib -L$ICU4C_PATH/lib -L$LIBICONV_PATH/lib -L$LIBZIP_PATH/lib"
echo "CFLAGS set to: $CFLAGS"
echo "LDFLAGS set to: $LDFLAGS"

# Prevent PEAR installation
export PHP_WITHOUT_PEAR=yes
echo "PHP_WITHOUT_PEAR set to: $PHP_WITHOUT_PEAR"

# Locate the asdf PHP plugin install script and modify it to use OpenSSL 3
# Check out a specific commit known to work well cause current master have some issues
ASDF_PHP_PLUGIN_DIR="$HOME/.asdf/plugins/php"
if [ ! -d "$ASDF_PHP_PLUGIN_DIR" ]; then
    echo "Error: asdf PHP plugin not found at $ASDF_PHP_PLUGIN_DIR" >&2
    echo "Please install the asdf PHP plugin first. (asdf plugin add php https://github.com/asdf-community/asdf-php.git)" >&2
    exit 1
fi

(cd "$ASDF_PHP_PLUGIN_DIR" && git checkout 09203d1) # Comment out when the plugin is fixed
PLUGIN_INSTALL_SCRIPT="$ASDF_PHP_PLUGIN_DIR/bin/install"

echo "Check and correct the asdf PHP plugin install script..."
if [ -f "$PLUGIN_INSTALL_SCRIPT" ]; then
    sed -i '' 's/openssl@1.1/openssl@3/g' "$PLUGIN_INSTALL_SCRIPT"
    
    echo "Modified the asdf PHP plugin install script to use OpenSSL 3."
else
    echo "Error: asdf PHP plugin install script not found at $PLUGIN_INSTALL_SCRIPT" >&2
    exit 1
fi

# Execute installation
echo "Starting to compile and install PHP $PHP_VERSION (this may take a few minutes)..."

# Remove old failed installation (if any)
asdf uninstall php $PHP_VERSION > /dev/null 2>&1

# Start installation
asdf install php $PHP_VERSION

# 4. Verify the result
if [ $? -eq 0 ]; then
    echo "PHP $PHP_VERSION installed successfully!"
    
    # Switch to the installed version
    asdf set -u php $PHP_VERSION
    echo "Checking version:"
    php -v
else
    echo "Installation failed, please check the error messages above."
fi