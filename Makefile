# ============================================================
# Makefile - ROS2 Monitoring System
# Cara pakai: make <perintah>
# ============================================================

.PHONY: help build up down shell rviz gazebo foxglove logs rebuild

# Warna terminal
GREEN  := \033[0;32m
YELLOW := \033[1;33m
CYAN   := \033[0;36m
RESET  := \033[0m

help: ## Tampilkan semua perintah
	@echo ""
	@echo "$(CYAN)╔══════════════════════════════════════════╗$(RESET)"
	@echo "$(CYAN)║      ROS2 Monitoring - Command List      ║$(RESET)"
	@echo "$(CYAN)╚══════════════════════════════════════════╝$(RESET)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-15s$(RESET) %s\n", $$1, $$2}'
	@echo ""

# ── Docker ────────────────────────────────────────────────
build: ## Build Docker image
	@echo "$(YELLOW)Building Docker image...$(RESET)"
	docker compose -f docker/docker-compose.yml build

up: ## Jalankan semua service
	@echo "$(GREEN)Starting all services...$(RESET)"
	docker compose -f docker/docker-compose.yml up -d
	@echo ""
	@echo "$(GREEN)✔ Services ready:$(RESET)"
	@echo "   ✔ Desktop GUI  → http://localhost:6080"
	@echo "   ✔ Foxglove     → https://app.foxglove.dev (connect ws://localhost:8765)"
	@echo "   ✔ File Manager → http://localhost:5000"

down: ## Stop semua service
	docker compose -f docker/docker-compose.yml down

rebuild: ## Rebuild image dari scratch (no cache)
	docker compose -f docker/docker-compose.yml build --no-cache

logs: ## Lihat logs container
	docker compose -f docker/docker-compose.yml logs -f ros-core

# ── Shell ─────────────────────────────────────────────────
shell: ## Masuk ke shell container ROS
	docker exec -it ros_monitoring_system bash

# ── ROS Commands ──────────────────────────────────────────
ros-build: ## Build ROS workspace
	docker exec ros_monitoring_system bash -c \
		"source /opt/ros/humble/setup.bash && \
		 cd /root/ros_ws && \
		 colcon build --symlink-install && \
		 echo 'Build selesai!'"

rviz: ## Launch RViz dengan robot model
	docker exec ros_monitoring_system bash -c \
		"source /opt/ros/humble/setup.bash && \
		 source /root/ros_ws/install/setup.bash && \
		 ros2 launch my_robot display.launch.py"

gazebo: ## Launch Gazebo simulator
	docker exec ros_monitoring_system bash -c \
		"source /opt/ros/humble/setup.bash && \
		 source /root/ros_ws/install/setup.bash && \
		 ros2 launch my_robot gazebo.launch.py"

foxglove: ## Start Foxglove Bridge
	docker exec ros_monitoring_system bash -c \
		"source /opt/ros/humble/setup.bash && \
		 ros2 launch foxglove_bridge foxglove_bridge_launch.xml port:=8765"

topics: ## List semua ROS topics
	docker exec ros_monitoring_system bash -c \
		"source /opt/ros/humble/setup.bash && \
		 source /root/ros_ws/install/setup.bash && \
		 ros2 topic list"

nodes: ## List semua ROS nodes
	docker exec ros_monitoring_system bash -c \
		"source /opt/ros/humble/setup.bash && \
		 ros2 node list"

# ── Browser ───────────────────────────────────────────────
open-gui: ## Buka Desktop GUI di browser
	@xdg-open http://localhost:6080 2>/dev/null || open http://localhost:6080

open-foxglove: ## Buka Foxglove Studio di browser
	@xdg-open https://app.foxglove.dev 2>/dev/null || open https://app.foxglove.dev

open-filemanager: ## Buka File Manager di browser
	@xdg-open http://localhost:5000 2>/dev/null || open http://localhost:5000
