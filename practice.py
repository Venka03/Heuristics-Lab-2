# Practice II-Part 1
# Import necessary libraries
import sys
from constraint import Problem, ExactSumConstraint, MinSumConstraint, MaxSumConstraint

# Function to read and parse the input file
def read_input(file_path):
    """
    Reads the input file and extracts the data required to model the problem.
    :param file_path: Path to the input file
    :return: Parsed data
    """
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Parse the input file structure
    num_slots = int(lines[0].strip().split(":")[1])
    matrix_size = tuple(map(int, lines[1].strip().split("x")))
    std_positions = parse_positions(lines[2].strip().split(":")[1])
    spc_positions = parse_positions(lines[3].strip().split(":")[1])
    prk_positions = parse_positions(lines[4].strip().split(":")[1])

    aircraft = []
    for line in lines[5:]:
        if line.strip():
            aircraft.append(parse_aircraft(line.strip()))

    return {
        "num_slots": num_slots,
        "matrix_size": matrix_size,
        "std_positions": std_positions,
        "spc_positions": spc_positions,
        "prk_positions": prk_positions,
        "aircraft": aircraft
    }

# Helper function to parse positions from the input
def parse_positions(position_str):
    """
    Parses a string of positions into a list of tuples.
    :param position_str: String of positions
    :return: List of tuples representing positions
    """
    return [tuple(map(int, pos.strip("()").split(","))) for pos in position_str.split()]

# Helper function to parse aircraft data
def parse_aircraft(line):
    """
    Parses a line of aircraft data.
    :param line: Line representing an aircraft's data
    :return: Dictionary with aircraft details
    """
    parts = line.split("-")
    return {
        "id": int(parts[0]),
        "type": parts[1],
        "restrict": parts[2] == "T",
        "t1_tasks": int(parts[3]),
        "t2_tasks": int(parts[4])
    }

# Function to initialize the CSP problem
def initialize_problem():
    """
    Initializes the CSP problem instance.
    :return: A new Problem instance
    """
    return Problem()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python CSPMaintenance.py <path maintenance>")
        sys.exit(1)

    input_path = sys.argv[1]
    data = read_input(input_path)

    # Extract data
    num_slots = data['num_slots']
    locations = data['std_positions'] + data['spc_positions'] + data['prk_positions']
    standard_workshops = data['std_positions']
    specialist_workshops = data['spc_positions']
    task_requirements = {ac['id']: (ac['t2_tasks'], ac['t1_tasks']) for ac in data['aircraft']}
    aircraft_ids = [ac['id'] for ac in data['aircraft']]
    standard_ids = [ac['id'] for ac in data['aircraft'] if ac['type'] == 'STD']
    jumbo_ids = [ac['id'] for ac in data['aircraft'] if ac['type'] == 'JMB']
    specialist_task_aircraft = [ac['id'] for ac in data['aircraft'] if ac['t2_tasks'] > 0]

    time_slots = range(1, num_slots + 1)

    # Initialize problem
    problem = initialize_problem()

    # Debugging: Print parsed data
    print("Number of Slots:", num_slots)
    print("Matrix Size:", data['matrix_size'])
    print("Locations:", locations)
    print("Standard Workshops:", standard_workshops)
    print("Specialist Workshops:", specialist_workshops)
    print("Task Requirements:", task_requirements)
    print("Aircraft IDs:", aircraft_ids)
    print("Jumbo IDs:", jumbo_ids)
    print("Specialist Task Aircraft:", specialist_task_aircraft)

    # Variables: A_{i}_{t}_{x}_{y} = 1 if aircraft i is at (x, y) at time t, otherwise 0
    for i in aircraft_ids:
        for t in time_slots:
            for x, y in locations:
                problem.addVariable(f"A_{i}_{t}_{x}_{y}", [0, 1])

    # Constraints

    # 1. # Unique Assignment Constraint
    # Each aircraft must be assigned to exactly one valid location per time slot.
    for i in aircraft_ids:
        for t in time_slots:
            variables = [f"A_{i}_{t}_{x}_{y}" for x, y in locations]
            problem.addConstraint(ExactSumConstraint(1), variables)
    
    # 4. Task ordering (scheduling of T2 happens before T1 tasks)
    for i, (t2, t1) in task_requirements.items():
        if t2 > 0:
            # Ensure T2 tasks are in specialist workshops
            for t in range(1, t2 + 1):
                variables = [f"A_{i}_{t}_{x}_{y}" for x, y in specialist_workshops]
                problem.addConstraint(lambda *args: sum(args) == 1, variables)

            
            # Force T1 tasks to occur in the next t1 slots at standard workshops
            for t in range(t2 + 1, t2 + t1 + 1):
                problem.addConstraint(lambda *args: sum(args) == 1, [f"A_{i}_{t}_{x}_{y}" for x, y in standard_workshops])


    # 2 
    # For each workshop and time slot, enforce capacity ≤ 2
    workshops = standard_workshops + specialist_workshops
    for (x, y) in workshops:
        for t in time_slots:
            problem.addConstraint(MaxSumConstraint(2), [f"A_{i}_{t}_{x}_{y}" for i in aircraft_ids])


    # 2.1 (7)
    # For each workshop and time slot, ensure at most one jumbo aircraft
    
    '''for (x, y) in workshops:
        for t in time_slots:
            problem.addConstraint(MaxSumConstraint(1), [f"A_{i}_{t}_{x}_{y}" for i in jumbo_ids])'''


    
    # 6
    # Enforce jumbo adjacency constraint
    for (x, y) in locations:
        for t in time_slots:
            jumbo_vars = [f"A_{i}_{t}_{x}_{y}" for i in jumbo_ids]
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                adj_x, adj_y = x+dx, y+dy
                if (adj_x, adj_y) in locations:
                    adj_vars = [f"A_{j}_{t}_{adj_x}_{adj_y}" for j in jumbo_ids]
                    problem.addConstraint(MaxSumConstraint(1), jumbo_vars + adj_vars)

    # 5 Maneuverability (adjacency)
    '''def adjacency_constraint(occupied, *adj_occupied):
        if occupied == 1:
            return any(val == 0 for val in adj_occupied)  # At least one adjacent position must be free
        return True  # If not occupied, no restriction on adjacent positions

    for x, y in locations:
        # Identify adjacent positions
        adj_positions = [(x+dx, y+dy) for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)] if (x+dx, y+dy) in locations]

        for t in time_slots:
            for i in aircraft_ids:
                adj_vars = [f"A_{j}_{t}_{ax}_{ay}" for j in aircraft_ids if j != i for (ax, ay) in adj_positions]
                problem.addConstraint(adjacency_constraint, [f"A_{i}_{t}_{x}_{y}"] + adj_vars)'''

    # 3 Specialist workshop capability
    # Aircraft requiring T2 tasks can only use specialist workshops.
    '''for i in specialist_task_aircraft:
        for t in time_slots:
            for x, y in standard_workshops:
                problem.addConstraint(lambda v: v == 0, [f"A_{i}_{t}_{x}_{y}"])'''


    # Solve the problem and generate the output
    sols = problem.getSolutions()
    l = len(sols)
    solutions = problem.getSolutions()#[:10]  # Limit to first 10 solutions

    # Print the number of solutions found in the required format
    print(f"N. Sol: {l}")

    # Iterate over each solution and print it in the required format
    for sol_idx, solution in enumerate(solutions, start=1):
        print(f"Solución {sol_idx}:")
        
        # Initialize the dictionary to store assignments for each aircraft
        aircraft_assignments = {ac['id']: [] for ac in data['aircraft']}
        
        # Parse the solution to assign each aircraft's positions
        for key, value in solution.items():
            if value == 1:  # If the variable indicates the aircraft is assigned to this position
                parts = key.split("_")
                aircraft_id = int(parts[1])
                time_slot = int(parts[2])
                x, y = map(int, parts[3:])
                location = f"{'STD' if (x, y) in standard_workshops else 'SPC' if (x, y) in specialist_workshops else 'PRK'}({x},{y})"
                aircraft_assignments[aircraft_id].append((time_slot, location))
        
        # Print sorted assignments for each aircraft
        for aircraft_id, assignments in sorted(aircraft_assignments.items()):
            # Sort by time slot to ensure correct order
            sorted_assignments = sorted(assignments, key=lambda x: x[0])
            # Format the locations
            locations_str = ", ".join(location for _, location in sorted_assignments)
            # Get the aircraft details
            aircraft = next(ac for ac in data['aircraft'] if ac['id'] == aircraft_id)
            print(f"{aircraft_id}-{aircraft['type']}-{'T' if aircraft['restrict'] else 'F'}-{aircraft['t1_tasks']}-{aircraft['t2_tasks']}: {locations_str}")




    '''# Solve the problem and generate the output
    #solutions = problem.getSolutions()
    # Solve the problem with a solution limit
    #solutions = problem.getSolutions(limit=10)
    solutions = problem.getSolutions()[:10]  # Limit to first 10 solutions


    # Debugging: Print the number of solutions found
    print(f"Number of solutions: {len(solutions)}")
    # Print the first few solutions for verification
    for idx, solution in enumerate(solutions[:5], start=1):  # Limit to 5 solutions for brevity
        print(f"Solution {idx}: {solution}")

    # Debugging: If no solutions, check constraints
    if len(solutions) == 0:
        print("No solutions found. Consider relaxing constraints or reviewing input data.")
'''