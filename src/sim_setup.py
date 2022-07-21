import math
from simspace_generator import Writer

"""
Function `convert_vel()` to convert an input velocity to
the appropriate environment.
    - Args:
        - `velocity: float` -> the input velocity to be converted (Earth velocity)
            - the values of the velocities will be directly read from the `Task_setup.yaml` file

        - `gravity: float` -> the gravity at the target environment
            - the value for gravity is also directly read from the `Task_setup.yaml` file

    - Returns:
        - `converted_velocity` -> the converted velocity value

## Units must be CONSISTENT!!
"""
def convert_vel( 

    # add arguments here as necesary
        
    #   Format:
    #   [input_name]: [input_type]
    #   Example:
    #   particle_count: int,
        velocity: float,
        gravity: float ) -> float:
    """
    Syntax for using special functions:

        - square root of x --> math.sqrt( x )
        - x to the power of n --> x**n
        - logarithms
            - log base N of B --> math.log(N,B)
            - ln B --> math.log(math.e,B)
    """

    # Function operations start here
    # converted_velocity = velocity * (gravity/gravity) * 0.5
    converted_velocity = math.sqrt(velocity) *(gravity/gravity)

    return converted_velocity

def main():
    Writer("Task_setup.yaml", convert_vel).writer()

if __name__ == "__main__":
    main()
