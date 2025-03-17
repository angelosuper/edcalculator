#!/bin/bash

# Create output directory
mkdir -p download_package

# Copy and organize files
cp app.py download_package/
cp materials_manager.py download_package/
cp stl_processor.py download_package/
cp -r backend download_package/
cp -r documentation download_package/

# Create ZIP archive
zip -r 3d_print_calculator.zip download_package/

# Cleanup
rm -rf download_package

echo "Project archive created: 3d_print_calculator.zip"
