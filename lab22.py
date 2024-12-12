import constraint

# Define the Plane class
class Plane:
   def __init__(self, plane_id, plane_type, restr, tasks_t1, tasks_t2):
       self.id = plane_id
       self.type = plane_type
       self.restr = restr  # Restriction: True if type 2 tasks must be done before type 1
       self.tasks_t1 = tasks_t1  # Number of type 1 tasks
       self.tasks_t2 = tasks_t2  # Number of type 2 tasks

   def __repr__(self):
       return f"Plane(id={self.id}, type={self.type}, restr={self.restr}, tasks_t1={self.tasks_t1}, tasks_t2={self.tasks_t2})"

# Define the Slot class
class Slot:
   def __init__(self, row, col, time):
       self.row = row
       self.col = col
       self.time = time

   def __repr__(self):
       return f"Slot(row={self.row}, col={self.col}, time={self.time})"

# Function to read the input file
def read_maintenance_file(file_path):
   with open(file_path, 'r') as file:
       lines = file.readlines()

   # Parse the number of time slots
   time_slots = int(lines[0].split(":")[1].strip())

   # Parse the grid size
   grid_size = tuple(map(int, lines[1].split("x")))

   # Parse the standard workshop positions
   STD_positions = [
       Slot(*map(int, coord.strip("()").split(",")), time=None) for coord in lines[2].split(":")[1].strip().split()
   ]

   # Parse the specialist workshop positions
   SPC_positions = [
       Slot(*map(int, coord.strip("()").split(",")), time=None) for coord in lines[3].split(":")[1].strip().split()
   ]

   # Parse the parking positions
   PRK_positions = [
       Slot(*map(int, coord.strip("()").split(",")), time=None) for coord in lines[4].split(":")[1].strip().split()
   ]

   # Parse the aircraft data
   aircraft = []
   for line in lines[5:]:
       if line.strip():
           parts = line.split("-")
           plane_id = int(parts[0].strip())
           plane_type = parts[1].strip()
           restr = parts[2].strip() == "T"
           t1_tasks = int(parts[3].strip())
           t2_tasks = int(parts[4].strip())
           aircraft.append(Plane(plane_id, plane_type, restr, t1_tasks, t2_tasks))

   return {
       "time_slots": time_slots,
       "grid_size": grid_size,
       "STD_positions": STD_positions,
       "SPC_positions": SPC_positions,
       "PRK_positions": PRK_positions,
       "aircraft": aircraft
   }

# Load data from file
file_path = "maintenance_input.txt"  # Replace with your file path
data = read_maintenance_file(file_path)

# Create a CSP object
problem = constraint.Problem()

# Extract valid positions (combine STD, SPC, and PRK)
valid_positions = data["STD_positions"] + data["SPC_positions"] + data["PRK_positions"]

# Add variables for each aircraft and each time slot
for plane in data["aircraft"]:
   for t in range(data["time_slots"]):
       # Variable name: PlaneID_TimeSlot
       variable_name = f"P{plane.id}_T{t}"
       # The domain is all valid positions in the grid
       problem.addVariable(variable_name, [(pos.row, pos.col, t) for pos in valid_positions])
"""
# Constraint 1: Single location assignment per time slot
def single_location_constraint(*assignments ):
   # Ensure all aircraft have unique assignments in the same time slot
   return len(assignments) == len(set(assignments))

# Apply the constraint for each time slot
for t in range(data["time_slots"]):
   variables_at_time_t = [f"P{plane.id}_T{t}" for plane in data["aircraft"]]
   problem.addConstraint(single_location_constraint, variables_at_time_t)
"""
# Solve the problem
solutions = problem.getSolutions()

# Display results
print(f"Number of solutions: {len(solutions)}")
if solutions:
   print("Example solution:")
   for key, value in solutions[0].items():
       print(f"{key}: {value}")
