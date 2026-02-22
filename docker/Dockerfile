# =========================================================
# Dependency image
# ROS 2 Humble Desktop Full + Foxglove Bridge
# Base: Ubuntu 22.04 (Jammy)
# =========================================================

# ROS 2 Image
FROM osrf/ros:humble-desktop-full

# Ignore interactive prompts during package installation
ARG DEBIAN_FRONTEND=noninteractive
ENV ROS_DISTRO=humble

# Install tools & depemdencies
RUN apt-get update && apt-get install -y \
    # ROS 2 tools
    ros-${ROS_DISTRO}-foxglove-bridge \
    ros-${ROS_DISTRO}-joint-state-publisher-gui \
    ros-${ROS_DISTRO}-gazebo-ros2-control \
    # Navigation and Control
    ros-${ROS_DISTRO}-nav2-bringup \
    ros-${ROS_DISTRO}-slam-toolbox \
    # Webserver
    python3-flask \
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

# Set entrypoint
COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]