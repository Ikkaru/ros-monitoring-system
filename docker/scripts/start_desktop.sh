#!/bin/bash
set -e

echo "=== Configuring GPU Backend ==="

# Detect environment: WSLg or Linux native
if grep -qi microsoft /proc/version 2>/dev/null; then
    echo ">>> Running inside WSLg (WSL2) — X11 via WSLg XServer (DISPLAY=${DISPLAY})"
else
    echo ">>> Running on Linux native — X11 via host display (DISPLAY=${DISPLAY})"
fi

# GPU detection & rendering backend
if [ -c /dev/dxg ] 2>/dev/null; then
    # WSLg: GPU via D3D12 translation layer (Windows driver stub)
    # /dev/dxg dan /usr/lib/wsl/lib di-mount via docker-compose.wslg.yml
    echo ">>> WSLg GPU detected via /dev/dxg — using D3D12 (NVIDIA/AMD/Intel)"
elif [ -d /proc/driver/nvidia ] || [ -c /dev/nvidia0 ] 2>/dev/null; then
    # NVIDIA Linux native: Container Toolkit handles GPU passthrough
    echo ">>> NVIDIA GPU detected — using NVIDIA runtime"
elif ls /dev/dri/card* 2>/dev/null | grep -q card; then
    # AMD / Intel Linux native: DRI device passed through via docker-compose.ogpu.yml
    echo ">>> AMD/Intel GPU detected via /dev/dri"
else
    # No GPU: fallback ke software rendering Mesa llvmpipe
    echo ">>> No GPU detected — falling back to software rendering (Mesa llvmpipe)"
    export LIBGL_ALWAYS_SOFTWARE=1
    export GALLIUM_DRIVER=llvmpipe
fi

echo "=== GPU config ready! ==="