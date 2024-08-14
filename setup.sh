#!/bin/sh

# =============================================================================
# ctviewer Package Builder Script
# =============================================================================
# This script automates the process of building a Debian package for the 
# ctviewer application using PyInstaller and fpm. The PyInstaller configuration
# is dynamically generated within this script, so no separate .spec file is 
# needed.
# =============================================================================

# Define the version of the application
VERSION="0.1.0"

# Get the vedo fonts directory path
VEDO_FONTSDIR=$(python3 -c 'from vedo import installdir; import os; print(os.path.join(installdir, "fonts"))')

# Step 1: Create the executable for the application using PyInstaller
echo "Building the ctviewer executable..."

pyinstaller --name ctviewer \
--onefile \
--exclude-module PyQt5 \
--icon=icons/logo.ico \
--hidden-import=vtkmodules \
--hidden-import=vtkmodules.all \
--hidden-import=vtkmodules.util \
--hidden-import=vtkmodules.util.numpy_support \
--hidden-import=vtkmodules.qt.QVTKRenderWindowInteractor \
--add-data "config.json:." \
--add-data "$VEDO_FONTSDIR:vedo/fonts" \
--log-level WARN \
--optimize 2 \
ctviewer/main.py

# Step 2: Set up the directory structure for the Debian package
echo "Setting up the directory structure..."
mkdir -p dist/opt/ctviewer
mkdir -p dist/usr/share/applications
mkdir -p dist/usr/share/icons/hicolor/scalable/apps

# Step 3: Copy the necessary files to the package directory
cp dist/ctviewer dist/opt/ctviewer/ctviewer && rm -rf dist/ctviewer
cp icons/logo.png dist/usr/share/icons/hicolor/scalable/apps/ctviewer.png

# Step 4: Create a .desktop file for the application
cat << EOF > dist/usr/share/applications/ctviewer.desktop
[Desktop Entry]
Name=CtViewer
Path=/opt/ctviewer
Exec=/opt/ctviewer/ctviewer
Icon=ctviewer
Type=Application
Categories=Graphics;
EOF

# Step 5: Set appropriate permissions
find dist/opt/ctviewer -type f -exec chmod 644 {} +
find dist/opt/ctviewer -type d -exec chmod 755 {} +
find dist/usr/share -type f -exec chmod 644 {} +
chmod +x dist/opt/ctviewer/ctviewer

# Step 6: Build the Debian package using fpm
echo "Building the .deb package..."
fpm \
  -C dist \
  -s dir -t deb \
  -p ctviewer-${VERSION}.deb \
  -n ctviewer \
  -v "${VERSION}" \
  --license "MIT" \
  --architecture all \
  --depends bash --depends lolcat \
  --description "Application for rendering 3D CT images and DICOS files" \
  --url "https://auxilia-tech.com" \
  --maintainer "AUXILIA"

# Step 7: Clean up build artifacts
echo "Cleaning up..."
rm -rf build
rm -rf dist

# Step 8: Check and delete the .spec file if it was generated
SPEC_FILE="ctviewer.spec"
if [ -f "$SPEC_FILE" ]; then
  rm -f "$SPEC_FILE"
fi

echo "Package creation complete: ctviewer-${VERSION}.deb"