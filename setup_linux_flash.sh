#!/bin/bash
# setup_linux_flash.sh — one-time setup to enable firmware flashing on Linux
#
# Run this ONCE after cloning the repo.
# Requires sudo for udev rules.

set -e
TOOLS_DIR="$(cd "$(dirname "$0")/cpu/br28/tools" && pwd)"

echo "=== Step 1: Fix execute permissions on bundled Linux tools ==="
chmod +x "$TOOLS_DIR/isd_download" "$TOOLS_DIR/fw_add" "$TOOLS_DIR/run_jtag.sh"
echo "  isd_download, fw_add, run_jtag.sh -> executable"

echo ""
echo "=== Step 2: USB udev rule for Jieli devices (requires sudo) ==="
RULE_FILE="/etc/udev/rules.d/99-jieli.rules"
if [ -f "$RULE_FILE" ] && grep -q "4c4a" "$RULE_FILE" 2>/dev/null; then
    echo "  udev rule already present, skipping."
else
    sudo tee "$RULE_FILE" > /dev/null << 'EOF'
# Jieli BR28/AC701N in forced-download / uboot mode
SUBSYSTEM=="usb", ATTR{idVendor}=="4c4a", MODE="0666", GROUP="plugdev"
SUBSYSTEM=="block", SUBSYSTEMS=="usb", ATTRS{idVendor}=="4c4a", MODE="0660", GROUP="plugdev"
SUBSYSTEM=="scsi_generic", SUBSYSTEMS=="usb", ATTRS{idVendor}=="4c4a", MODE="0660", GROUP="plugdev"
EOF
    sudo udevadm control --reload-rules
    sudo udevadm trigger
    echo "  Written: $RULE_FILE"
fi

# Make sure current user is in plugdev group
if ! groups | grep -qw plugdev; then
    echo "  WARNING: user $(whoami) is not in the 'plugdev' group."
    echo "  Fix: sudo usermod -aG plugdev $(whoami)  then log out and back in."
fi

echo ""
echo "=== Step 3: ulimit check ==="
NOFILE=$(ulimit -n)
if [ "$NOFILE" -lt 8096 ]; then
    echo "  WARNING: ulimit -n is $NOFILE (too low, may cause link failures)"
    echo "  Fix: ulimit -n 8096  (add to ~/.bashrc for persistence)"
else
    echo "  ulimit -n = $NOFILE (OK)"
fi

echo ""
echo "=== Setup complete ==="
echo "  To flash: plug in the IC in forced-download mode, then run:  make"
echo "  The IC should appear as USB device 4c4a:3442 (BR28UBOOT1.00)."
echo "  isd_download will detect it automatically."
