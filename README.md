# Task Setup for LAMMPS Simulations

## Requirements

- Python version > 3.10

## Setup

- `git clone https://github.com/molee1354/lammps-task-generator.git` into any local directory
- Make adjustments for how the output `.sbatch`, LAMMPS input files, and the directories should be formatted.
  - Make sure the `environment` identifier matches that of the LAMMPS parent files and the dependencies. The program will check that the naming is consistent, but it won't stop the files from generating, which may result in unexpected behavior.
  - If `convert_to_environment` is set to `true`, then the value for gravity provided in the `gravity` field is going to be used to convert the velocities according to the environment. The conversion behavior can be modified in the `./src/sim_setup.py` file.
  - The program will copy the files listed `lammps_input` and the `lammps_dependencies` field from the `./sim_setup/<<Environment>>` directory into the output `task_` directores.
    - **Note**: By default, the program will throw a warning stating that the `discCoords*.data` file has an unexpected name, but this is something that can be ignored.
- The fields under `output_behavior` determine how the `.sbatch` and the `./task_` will behave.
  - `directories` can either be set to `single` or `split`, and it determines whether or not the output files will come in a single directory or a set of them separated into sub-directories based on their angle values.
  - `parallel` determines the number of `.sbatch` files the program will generate.
  - If `progress_tracking` is set to `true`, then there will be an extra `progress.txt` file in the current directory that will show the list of files currently completed by the submitted process.

## Task Generation and Submission

- To generate the LAMMPS task, simply type the `make` command in the current directory. The `Makefile` will set up a temporary virtual Python 3.10 environment and install all the dependencies that allow the program to run.
- The program will check that the necessary dependency files exist, and will throw warnings if that doesn't seem to be the case.
  - **Note**: If the warning appears twice, it means that something is wrong with the current setup of the program.
- After the process is run, the program will show that it has created the `.sbatch` files and the necessary input files for the simulation to run. You can double check to see that the modifications made are correct.
- To submit the jobs, you can submit the jobs manually or run the `submit` command to automatically submit multiple `.sbatch` files at once.
