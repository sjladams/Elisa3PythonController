from nodes import Nodes
import json

if __name__ == "__main__":
    with open('mapper.json') as json_file:
        mapper = json.load(json_file)

    active_robots = list(mapper.keys())

    # Init phase
    nodes = Nodes(active_robots)

    # Set Leds
    nodes.set_leds(green=0, blue=0, red=10)

    # Move Robots
    nodes.move(step_size=0.1, theta=0.)

    # Pull Odometry measure
    nodes.print_position_measures()


