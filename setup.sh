#!/bin/bash

# Detect the platform (similar to $OSTYPE)
OS="`uname`"
case $OS in
  'Linux')
    OS='Linux'
    PACKAGE_COMMAND='python setup.py bdist'
    ;;
  'WindowsNT')
    OS='Windows'
    PACKAGE_COMMAND='python setup.py bdist_msi'
    ;;
  'Darwin') 
    OS='Mac'
    # Define each command separately
    BUILD_COMMAND='python setup.py bdist_mac'
    INSTALL_CREATE_DMG='npm install -g appdmg'
    CREATE_DMG_COMMAND='appdmg setup.json build/CTViewer.dmg'
    ;;
  *) 
    OS='Unknown'
    PACKAGE_COMMAND='echo "Unknown OS."'
    ;;
esac

echo "Detected OS: $OS"

# Run the package commands for macOS
if [ "$OS" = "Mac" ]; then
    echo "Building .app with: $BUILD_COMMAND"
    $BUILD_COMMAND
    if [ $? -eq 0 ]; then
        echo "Installing appdmg with: $INSTALL_CREATE_DMG"
        $INSTALL_CREATE_DMG
        if [ $? -eq 0 ]; then
            echo "Creating .dmg with: $CREATE_DMG_COMMAND"
            $CREATE_DMG_COMMAND
        else
            echo "Failed to install appdmg"
        fi
    else
        echo "Failed to build .app"
    fi
else
    echo "Running package command: $PACKAGE_COMMAND"
    $PACKAGE_COMMAND
fi
