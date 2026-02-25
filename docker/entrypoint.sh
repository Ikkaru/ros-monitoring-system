#!/bin/bash
set -e

# Source ROS
source /opt/ros/humble/setup.bash

# === Start Desktop (TurboVNC + noVNC + VirtualGL) ===
echo "[INFO] Starting desktop environment..."
/start_desktop.sh

# Auto build workspace jika belum di-build
if [ ! -f "/root/ros_ws/install/setup.bash" ]; then
    echo "[INFO] Workspace belum di-build, memulai build otomatis..."
    cd /root/ros_ws && colcon build --symlink-install
    echo "[INFO] Build selesai!"
fi

# Source workspace
source /root/ros_ws/install/setup.bash 2>/dev/null || true

# Run foxglove bridge on background
if [ "${START_FOXGLOVE}" = "true" ]; then
    echo "[INFO] Starting Foxglove Bridge on port 8765..."
    ros2 launch foxglove_bridge foxglove_bridge_launch.xml \
        port:=8765 &
fi

# Run webserver file manager on background
if [ "${START_FILEMANAGER}" = "true" ]; then
    echo "[INFO] Starting File Manager on port 5000..."
    python3 /root/file_manager/app.py &
fi

# I write this because its cool 
echo "========================================="
echo " ROS2 Monitoring System Container Ready"
echo "========================================="
echo " → Desktop GUI  : http://localhost:6080"
echo " → Foxglove     : ws://localhost:8765"
echo " → File Manager : http://localhost:5000"
echo "========================================="

# Keep the container running
tail -f /dev/null