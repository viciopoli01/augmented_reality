
**NOTE:** If you want to develop software that does not use
ROS, check out [this template](https://github.com/duckietown/template-basic).


## How to use it

Run the following commands:

```
dts devel build -f --arch arm32v7 -H DUCKIEBOT_NAME.local    
docker -H DUCKIEBOT_NAME.local run -it --rm -v /data:/data --privileged --network=host duckietown/augmented_reality:v1-arm32v7 /bin/bash
roslaunch augmented_reality augmented_reality.launch map_file:=calibration_pattern robot_name:=DUCKIEBOT_NAME
roslaunch augmented_reality augmented_reality.launch map_file:=intersection_4way robot_name:=DUCKIEBOT_NAME
roslaunch augmented_reality augmented_reality.launch map_file:=lane robot_name:=DUCKIEBOT_NAME
roslaunch augmented_reality augmented_reality.launch map_file:=hub robot_name:=DUCKIEBOT_NAME
```