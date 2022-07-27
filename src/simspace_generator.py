import os
import yaml
from shutil import copyfile
from pathlib import Path
from platform import platform

class Writer:
    """
    Writing the input files with the necessary parameters
    """
    
    project_root = Path(os.getcwd()).parent.absolute()
        
    def __init__(self, config_file, convert_func) -> None:

        self.setup_paramfile = f"{self.project_root}/{config_file}"

        # a function to convert the input velocities according to the environment
        self.__convert_vel = convert_func

        # fetching the simulation environment parameter settings
        if os.path.exists(self.setup_paramfile):
            with open(self.setup_paramfile, 'r') as file:
                params = yaml.safe_load(file)
        else:
            raise FileNotFoundError(f"\"{self.setup_paramfile}\" was not found. Check to see that it is " \
                    "located correctly or if its name has not changed.")
        
        # setting the input parameters
        self.setup_params = params
        
        # checking that the correct files exist for the directory setup to happen
        self.__check_setupspace()
    
    def __check_setupspace(self):
        """
        Method to check that the necessary input files exist
        """

        # setting and checking source directory
        # source_dir = self.setup_params["sim_setup"]["source_directory"]
        source_dir = f"{self.project_root}/sim_environment/{self.setup_params['sim_setup']['modify']['environment']}"
        if not os.path.exists(source_dir):
            raise FileNotFoundError(f"The input source directory \"{source_dir}\" was not found.")

        necessary_files = [ self.setup_params["sim_setup"]["lammps_input"], *self.setup_params["sim_setup"]["lammps_dependencies"] ]

        warning_files = []
        for input_files in [source_dir, *necessary_files]:
            if self.setup_params["sim_setup"]["modify"]["environment"] not in input_files:
                warning_files.append(f"\t\t{input_files}")

        if len(warning_files) > 0:
            print("\nWARNING:\n\tThe following files did not fully match names " \
                    "and could result unexpected behavior : \n\n" \
                    f"\tEXPECTED : \n\t\t{self.setup_params['sim_setup']['modify']['environment']}\n\n" \
                    "\tUNMATCHING :" \
                    )
            print(*warning_files, sep="\n")
            files_check = input("\nWould you like to continue? [Y/n] : ")

            if files_check.lower() == "n":
                exit()
                # raise FileNotFoundError
            else:
                pass
        

        for target_file in necessary_files:
            if target_file not in os.listdir(source_dir):
                raise FileNotFoundError(f"At least one of the necessary input files " \
                        f"({target_file}) is missing from \"{source_dir}\"!")
        
        return

    def __make_inputFile(self, angle, velocity, input_file):
        """
        Method to edit the the `in.*` LAMMPS input file
        """

        #* Note that the input file already knows about the environment
        # newLines = []
        with open(input_file, 'r') as file:
            input_lines = _Lines(file.readlines())
            oldLines = input_lines.get_lines()
            
            # setting up the job id --> the velocity format is changed here!!!!
            jobID = f"{self.setup_params['sim_setup']['modify']['environment']}_" \
                    f"{self.setup_params['sim_setup']['modify']['identifier']}_V{velocity:3.1f}_A{angle}"

            # Getting the lines and the line numbers for the values to change
            ang_line, ang_idx = input_lines.get_value("angle", angle)
            vel_line, vel_idx = input_lines.get_value("velocity", velocity)
            jid_line, jid_idx = input_lines.get_value("job_id", jobID)
            
            # Replacing the lines with the new lines
            oldLines[ang_idx] = ang_line
            oldLines[vel_idx] = vel_line
            oldLines[jid_idx] = jid_line
            
        return oldLines

    def __make_discFile(self):
        """
        Method to create the discfile"""
        
        # number of atoms and atom types
        atoms = 1
        atom_types = 1

        #setting x,y,z box dimensions
        xlo = 0.0000
        xhi = 0.3210
        ylo = 0.0000
        yhi = 0.8400
        zlo = -0.008075
        zhi = 0.008075
        
        discFileLines = [
            "2D DEM equivalent sim initial grain coords\n\n",
            f"{atoms} atoms\n",
            f"{atom_types} atom types\n",

            # box dims
            f"{xlo} {xhi} xlo xhi\n",
            f"{ylo} {yhi} ylo yhi\n",
            f"{zlo} {zhi} zlo zhi\n\n",
            
            # defining disc atom
            "Atoms\n\n",

            #! the disc id number matters
            "\t100000 1 0.01516 541.702 0.089 0.182 0.0\n" #! set the position here
        ]
        
        return discFileLines


    def __batch_writer(self, files_list, parallel, progress_tracking, filename):
        """
        Method to write out the batch files according to the user inputs.
            - Args:
                - `files_list: list[list[str]]` : the list of input files and their parent directories
                - `**kwargs`: user inputs as defined in the config file
        """
        
        # initializing the dictionary
        commands = { key:"" for key in range(parallel)}
        for idx, (dir,file) in enumerate(files_list):

            # for a windows platform
            if "Windows" in platform():
                if progress_tracking is True:
                    # progress tracking is just writing down the completed files in a separate file.
                    commands[int(idx % parallel)] += f"cd {dir} && lmp -in ./{file} && echo {file} >> {self.project_root}/progress.txt && "

                else:
                    commands[int(idx % parallel)] += f"cd {dir} && lmp -in ./{file} && "

            # for a linux platform
            else:
                if progress_tracking is True:
                    commands[int(idx % parallel)] += f"cd {dir} && lmp_mpi -in ./{file} && echo {file} >> {self.project_root}/progress.txt && "
                else:
                    commands[int(idx % parallel)] += f"cd {dir} && lmp_mpi -in ./{file} && "

            #* If the above doesn't work:
            # command += f"cd {dir} && lmp_mpi -in {dir}/{file} && "

        # for unix based os
        for key in commands:
            # checking for the last two characters of the single command
            if commands[key][-3:-1] == "&&":
                commands[key] = commands[key][:-3]

            if "Windows" in platform():
                with open(f"{self.project_root}/{filename}_{key+1}.bat", 'w') as file:
                    file.writelines(commands[key])
                print(f"Successfully created {filename}_{key+1}.bat!")
            else:
                with open(f"{self.project_root}/{filename}_{key+1}.sbatch", 'w') as file:
                    file.writelines( [
                        "#!/bin/bash\n",
                        f"#SBATCH -o out_{filename}.log\n",
                        "#SBATCH -p standard\n",
                        "#SBATCH -t 120:00:00\n",
                        "#SBATCH -n 32\n",
                        "#SBATCH --mem-per-cpu=200M\n",
                        "echo Running on $SLURM_JOB_NODELIST\n",
                        "module load lammps/8Apr2021/b1\n",
                        "unset SLURM_GTIDS\n",
                    ] )
                    file.writelines(commands[key])
                print(f"Successfully created {filename}_{key+1}.sbatch!")



    def writer(self, **kwargs):
        """
        Method to write out the necessary input files for the task
            - Args:
                - `**kwargs`: is limited to the fields in the `Task_setup.json` file
                    - `directories: str` :
                        - "single": sets up a single directory where all the files are put in 
                        - "split": splits the directories into separate angles and velocities
                    - `parallel: int` : the number of `*.sbatch` files that the program will spawn
                    - `progress_tracking: bool`: sets up a progress tracker if `True` 
                
        """
        #TODO Add split vs single case for output directory (something in the for loop?)
        #TODO 


        # Overriding the parameters set in the *.json file
        for key in kwargs:
            if key in self.setup_params["output_behavior"]:
                self.setup_params["output_behavior"][key] = kwargs[key]
            
        # reading the values from config_file
        dir_behavior, parallel, progress_tracking =  ( 
                i for i in [value for value in self.setup_params["output_behavior"].values()] )

        (environment,identifier,angles,velocities, 
            convert, gravity) = (
                i for i in [value for value in self.setup_params["sim_setup"]["modify"].values()] )   

        # to convert velocities according to the environment
        if convert:
            velocities = [ self.__convert_vel(vel,gravity) for vel in velocities  ]
        
        # separating out the input file and the restart file
        # source_dir = self.setup_params["sim_setup"]["source_directory"]
        source_dir = f"{self.project_root}/sim_environment/{self.setup_params['sim_setup']['modify']['environment']}"
        input_file = f"{source_dir}/{self.setup_params['sim_setup']['lammps_input']}"
        dependencies = [ dep_file for dep_file in self.setup_params["sim_setup"]["lammps_dependencies"] ]
        

        # cycling through the input values to get the things
        inputFile_list = []
        for angle in angles:
            for velocity in velocities:
                
                inputFile_lines = self.__make_inputFile(angle, velocity, input_file)
                # discFile_lines = self.__make_discFile()
                
                # velocity identifier to easily identify files
                #! this is only consistent for single digit numbers!!
                vel_id = f"{velocity:3.1f}"

                # splitting directories into angles if prompted to do so
                if dir_behavior == "split":
                    file_destination = f"{self.project_root}/task_{environment}_{identifier}_A{angle}/iteration_V{vel_id}_A{angle}"
                elif dir_behavior == "single":
                    file_destination = f"{self.project_root}/task_{environment}_{identifier}"
                else:
                    raise Exception(f"The output directories behavior set in {self.setup_paramfile} is invalid!")

                # defining the path, and creating the nested directories if needed to do so 
                #! file destination will not change if "directories" is set to "single"
                Path(file_destination).mkdir(parents=True, exist_ok=True)
                
                # creating the input file
                inputFile_name = f"in.impact_{environment}_{identifier}_V{vel_id}_A{angle}" 

                inputFile_list.append( (file_destination, inputFile_name) )
                with open(f"{file_destination}/{inputFile_name}", 'w') as f:
                    for l in inputFile_lines:
                        f.writelines(l)
                
                # copying the dependencies
                for dep_file in dependencies:
                    try:
                    # if there is a specific disc file within the environment folder, it will copy that
                        copyfile(f"{source_dir}/{dep_file}", f"{file_destination}/{dep_file}")
                    except FileNotFoundError:
                        raise FileNotFoundError(f"At least one of the dependency files were missing ({dep_file})")


        self.__batch_writer(inputFile_list, parallel, progress_tracking, f"{environment}_{identifier}")
        

class _Lines:
    """
    Class to parse the lines of the in.*_parent file"""
    
    def __init__(self, lines):
        """
        `lines: list[str]`"""
        self.lines = lines
        
    def get_lines(self):
        """
        Method to get the input lines"""
        return self.lines

    def get_value(self, param, value):
        """
        Method to replace a specific piece of text with the passed in value
            - Args:
                - `param`: specifies what to quantity to replace
                - `value`: specifies what value to replace
            - Returns: the strings of the input file with the replaced lines"""
        
        # param : keyword
        #* this can be extended in the future to account for more parameters
        conversion = {
            "velocity" : "impVelocity",
            "angle" : "impAngle",
            "job_id" : "JOBID"
        }
        
        target_line = []
        newlineIdx = 0
        for idx, line in enumerate(self.lines):
            words = line.split()

            if conversion[param] in words:

                #* For LAMMPS files, the value always comes last
                # Replacing the value with the input value
                words[-1] = value
                target_line = words
                newlineIdx = idx
                break
        
        newline = ''
        for i, word in enumerate(target_line):
            if i == 0:
                newline += str(word) + "\t\t"
            else: 
                newline += str(word) + " "
        newline+="\n"

        return newline, newlineIdx
