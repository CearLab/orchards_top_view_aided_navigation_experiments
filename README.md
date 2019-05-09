# orchards_top_view_aided_navigation_experiments
This repository concentrates the experiments related to the research thesis titled ***Navigation in Orchards with Aiding Top-View Imagery*** which was submitted to the Senate of the Technion - Israel Institute of Technology in May 2019.

**Author:** Omer Shalev

**Advisor:** Assistant Professor Amir Degani

## Installation
The experiments were tested on Ubuntu 16.04 with ROS Kinetic.

Follow the instructions below to install all dependencies:
```
# Create catkin workspace
mkdir -p ~/orchards_ws/src
cd ~/orchards_ws
catkin_init_workspace

# Clone dependencies
git clone https://github.com/CearLab/orchards_top_view_aided_navigation_core
git clone https://github.com/CearLab/nelder_mead
git clone https://github.com/CearLab/astar
git clone https://github.com/CearLab/navigation -b narrow-amcl-angular-range

# Clone this repository
git clone https://github.com/CearLab/orchards_top_view_aided_navigation_experiments

# Build
catkin_make
```

Global configuration is in the [config file](framework/config.py). Pointers to the data is configured in [data_pointers](content/data_pointers) (see [Lavi-April](content/data_pointers/lavi_april_18) for reference).

## How to run an experiment
All experiments have an associated runner model under [runners](content/runners/). Experiment configuration is done in the runner file.

Below are the runners related to the main experiments and methods presented in the work:
1. [Canopies Extraction](content/runners/contours_drawer.py)
2. [Trunks Approximation and Semantic Labeling](content/runners/trunks_detection.py)
3. [Canopy-based AMCL](content/runners/amcl_simulation.py)
4. [Canopy-based ICP](content/runners/icp_simulation.py)
5. [UGV Periodic State Update](content/runners/global_ekf_updates.py)
6. [Semantic Global Path Planning](content/runners/path_planning.py)
7. [Path Update](content/runners/trajectory_update.py)
