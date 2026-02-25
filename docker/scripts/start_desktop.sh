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

echo "=== Configuring VirtualGL Backend ==="
export VGL_REFRESHRATE=60
export DISPLAY=:1

# Auto-detect GPU and set appropriate VirtualGL backend
if [ -d /proc/driver/nvidia ] || [ -c /dev/nvidia0 ] 2>/dev/null; then
    echo ">>> NVIDIA GPU detected, using EGL backend"
    export VGL_DISPLAY=egl
elif ls /dev/dri/card* 2>/dev/null | grep -q card; then
    DRI_CARD=$(ls /dev/dri/card* 2>/dev/null | head -1)
    echo ">>> AMD/Intel GPU detected, using DRI backend: $DRI_CARD"
    export VGL_DISPLAY=$DRI_CARD
else
    echo ">>> No GPU detected, using software rendering (Mesa llvmpipe)"
    export LIBGL_ALWAYS_SOFTWARE=1
    export GALLIUM_DRIVER=llvmpipe
    export VGL_DISPLAY=egl
fi

# Persist environment variables for all processes
echo "DISPLAY=:1" >> /etc/environment
echo "VGL_DISPLAY=${VGL_DISPLAY}" >> /etc/environment
echo "VGL_REFRESHRATE=60" >> /etc/environment
[ -n "$LIBGL_ALWAYS_SOFTWARE" ] && echo "LIBGL_ALWAYS_SOFTWARE=1" >> /etc/environment
[ -n "$GALLIUM_DRIVER" ] && echo "GALLIUM_DRIVER=${GALLIUM_DRIVER}" >> /etc/environment

echo "=== Display Ready! ==="
echo ">>> Access Gazebo at http://localhost:6080"