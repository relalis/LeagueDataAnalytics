#!/bin/bash

# Change these variables according to your setup
SOURCE_DIR="$(PWD)"
APP_DIR="$(PWD)/LDA.app"
APP_NAME="LDA"
INFO_PLIST_PATH="$APP_DIR/Contents/Info.plist"

# Create the .app structure if it doesn't exist
mkdir -p "$APP_DIR/Contents/MacOS"
mkdir -p "$APP_DIR/Contents/Resources"

find "$SOURCE_DIR" -name "*.py" -exec cp {} "$APP_DIR/Contents/MacOS" \;

cat > "$INFO_PLIST_PATH" << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" 
"http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
	<key>CFBundleDevelopmentRegion</key>
	<string>en</string>
	<key>CFBundleExecutable</key>
	<string>main.py</string>
	<key>CFBundleIconFile</key>
	<string>AppIcon.icns</string>
	<key>CFBundleIdentifier</key>
	<string>com.example.$APP_NAME</string>
	<key>CFBundleInfoDictionaryVersion</key>
	<string>6.0</string>
	<key>CFBundleName</key>
	<string>$APP_NAME</string>
	<key>CFBundlePackageType</key>
	<string>APPL</string>
	<key>CFBundleShortVersionString</key>
	<string>1.0</string>
	<key>CFBundleSignature</key>
	<string>????</string>
	<key>CFBundleVersion</key>
	<string>1</string>
	<key>LSMinimumSystemVersion</key>
	<string>10.10</string>
	<key>NSPrincipalClass</key>
	<string>NSApplication</string>
	<key>NSMainNibFile</key>
	<string>MainMenu</string>
</dict>
</plist>
EOF

echo "Info.plist file generated."
