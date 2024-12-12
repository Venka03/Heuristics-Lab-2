import constraint
class Plane:
   """
   Class representing an aircraft.
   """
   def __init__(self, plane_id, plane_type, restr, tasks_t1, tasks_t2):
       self.id = plane_id  # Aircraft ID
       self.type = plane_type  # Aircraft type (STD/JMB)
       self.restr = restr  # Restriction (True if type 2 tasks must be done before type 1)
       self.tasks_t1 = tasks_t1  # Number of type 1 tasks
       self.tasks_t2 = tasks_t2  # Number of type 2 tasks

   def __repr__(self):
       return f"Plane(id={self.id}, type={self.type}, restr={self.restr}, tasks_t1={self.tasks_t1}, tasks_t2={self.tasks_t2})"


class Slot:
   """
   Class representing a grid slot with row, column, and time properties.
   """
   def __init__(self, row, col, time):
       self.row = row  # Row in the grid
       self.col = col  # Column in the grid
       self.time = time  # Time slot

   def __repr__(self):
       return f"Slot(row={self.row}, col={self.col}, time={self.time})"


def read_maintenance_file(file_path):
   """
   Reads the maintenance file and extracts the problem data.

   :param file_path: Path to the input file
   :return: Parsed data including the number of time slots, grid size, workshops, and aircraft details.
   """
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

def onePlaneSingleSlot(a, b):
    return a != b




if __name__ == '__main__':
    file_path = "maintenance_input.txt"  # Replace with your file path
    data = read_maintenance_file(file_path)
    problem = constraint.Problem()
    sum = 0
    for el in data["aircraft"]:
        sum += el.tasks_t1 + el.tasks_t2
    slots = []
    rows = data["grid_size"][0]
    cols = data["grid_size"][1]
    for i in range(rows):
        for j in range(cols):
            for t in range(sum):
                slots.append(Slot(i, j, t))


    problem.addVariables(slots, data["aircraft"])






    print()


