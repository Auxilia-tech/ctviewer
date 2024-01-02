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
    PACKAGE_COMMAND='python setup.py bdist_dmg'
    ;;
  *) 
    ;;
esac

echo "Detected OS: $OS"
echo "Running package command: $PACKAGE_COMMAND"

# Run the package command
$PACKAGE_COMMAND
