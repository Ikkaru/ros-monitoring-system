# =========================================================
# Dependency image
# ROS 2 Humble Desktop + Foxglove Bridge + Gazebo Sim
# Base: Ubuntu 22.04 (Jammy)
# =========================================================

# ROS 2 Image
FROM osrf/ros:humble-desktop

# Ignore interactive prompts during package installation
ARG DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble

# Install tools & depemdencies
RUN apt-get update && apt-get install -y \
    # Hardware acceleration & Display
    wget \
    libgl1 \
    libglu1-mesa \
    libegl1 \
    libgles2 \
    mesa-utils-extra \
    # Window Manager
    openbox \
    # noVNC dependencies
    python3-websockify \
    novnc \
    && rm -rf /var/lib/apt/lists/* \
    \
    # Install VirtualGL
    && wget https://github.com/VirtualGL/virtualgl/releases/download/3.1/virtualgl_3.1_amd64.deb \
    && apt-get update && apt-get install -y ./virtualgl_3.1_amd64.deb \
    && rm virtualgl_3.1_amd64.deb \
    \
    # Install TurboVNC
    && wget https://github.com/TurboVNC/turbovnc/releases/download/3.1/turbovnc_3.1_amd64.deb \
    && apt-get update && apt-get install -y ./turbovnc_3.1_amd64.deb \
    && rm turbovnc_3.1_amd64.deb \
    \
    # ROS Packages
    && apt-get update && apt-get install -y \
    # ROS 2 tools
    ros-${ROS_DISTRO}-foxglove-bridge \
    ros-${ROS_DISTRO}-joint-state-publisher-gui \
    # Gazebo
    ros-${ROS_DISTRO}-ros-gz \
    ros-${ROS_DISTRO}-ros-gz-bridge \
    # Navigation and Control
    ros-${ROS_DISTRO}-nav2-bringup \
    ros-${ROS_DISTRO}-slam-toolbox \
    # Webserver
    python3-flask \
    ssl-cert \
    # Clean up 
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Set VirtualGL EGL backend via environment (no vglserver_config needed in container)
ENV VGL_DISPLAY=egl
ENV VGL_REFRESHRATE=60

# Workspace setup
ENV ROS_WS=/root/ros_ws
WORKDIR ${ROS_WS}

# Copy all ROS worsspace from host
COPY ros_ws/ ${ROS_WS}/

# Build ROS workspace
RUN /bin/bash -c "source /opt/ros/${ROS_DISTRO}/setup.bash && \
    cd ${ROS_WS} && \
    colcon build --symlink-install --cmake-args -DCMAKE_BUILD_TYPE=Release"

# Source ROS setup files and set ROS_DOMAIN_ID in .bashrc for interactive shells
RUN echo "source /opt/ros/${ROS_DISTRO}/setup.bash" >> ~/.bashrc && \
    echo "source ${ROS_WS}/install/setup.bash" >> ~/.bashrc && \
    echo "export ROS_DOMAIN_ID=0" >> ~/.bashrc

COPY docker/scripts/start_desktop.sh /start_desktop.sh
RUN chmod +x /start_desktop.sh

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]