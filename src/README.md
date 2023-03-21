# Elisa3PythonController

## Description
This is a python API for the Elisa3-robots (see https://www.gctronic.com/doc/index.php/Elisa-3) build on ROS and the modified Elisa3_npde_cpp package (https://github.com/sjladams/elisa3_node_cpp)

## Test instruction
### Remarks
If something is not working your first hypothesis should be: robot is defect :)

### Code structure
- catkin_ws
  - src
        - elisa3_node_cpp (https://github.com/sjladams/elisa3_node_cpp)
        - Elisa3PythonController
    
### Preperation
- update robot addresses in 'catkin_ws/src/elisa3_node_cpp/config/robots.yaml'
- update information on robots in 'carkin_ws/src/Elisa3PythonController/src/mapper.json'

### Launch
- from 'catkin_ws' run 'roslaunch elisa3_node_cpp elisa3_swarm.launch'



