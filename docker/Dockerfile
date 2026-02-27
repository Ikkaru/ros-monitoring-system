# =========================================================
# Dependency image
# ROS 2 Jazzy Desktop + Foxglove Bridge + Gazebo Sim
# Base: Ubuntu 24.04 (Noble)
# =========================================================

# ROS 2 Image
FROM osrf/ros:jazzy-desktop

# Ignore interactive prompts during package installation
ARG DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=jazzy

# Install tools & depemdencies
RUN apt-get update && apt-get install -y \
    # Hardware acceleration & Display (NVIDIA, AMD, Intel, Software)
    libgl1 \
    libglu1-mesa \
    libegl1 \
    libgles2 \
    # AMD/Intel GPU support via Mesa
    libdrm2 \
    libdrm-amdgpu1 \
    libdrm-intel1 \
    mesa-vulkan-drivers \
    libvulkan1 \
    mesa-utils \
    mesa-utils-extra \
    libgl1-mesa-dri \
    # ROS Packages
    && apt-get update && apt-get install -y \
    # ROS 2 tools
    ros-${ROS_DISTRO}-foxglove-bridge \
    ros-${ROS_DISTRO}-ros2-control \
    ros-${ROS_DISTRO}-ros2-controllers \
    ros-${ROS_DISTRO}-joint-state-publisher-gui \
    ros-${ROS_DISTRO}-gz-ros2-control \
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