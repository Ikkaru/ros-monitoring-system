#!/bin/bash
set -e

echo "=== Starting TurboVNC Server ==="
/opt/TurboVNC/bin/vncserver :1 \
    -geometry 1920x1080 \
    -depth 24 \
    -rfbport 5901 \
    -noxstartup \
    -securitytypes none
sleep 2

echo "=== Starting Window Manager ==="
DISPLAY=:1 openbox &
sleep 1

echo "=== Starting noVNC Proxy ==="
websockify --web /usr/share/novnc \
    0.0.0.0:6080 \
    localhost:5901 &

echo "=== Configuring VirtualGL EGL Backend ==="
export VGL_DISPLAY=egl
export VGL_REFRESHRATE=60
export DISPLAY=:1

# Persist environment variables for all processes
echo "DISPLAY=:1" >> /etc/environment
echo "VGL_DISPLAY=egl" >> /etc/environment
echo "VGL_REFRESHRATE=60" >> /etc/environment

echo "=== Display Ready! ==="
echo ">>> Access Gazebo at http://localhost:6080"