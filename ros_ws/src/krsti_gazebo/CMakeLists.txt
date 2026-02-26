cmake_minimum_required(VERSION 3.5)
project(krsti_gazebo)

find_package(ament_cmake REQUIRED)

install(DIRECTORY worlds launch
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
