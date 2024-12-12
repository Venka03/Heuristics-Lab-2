import sys
from constraint import Problem


class Plane:
    def __init__(self, pid, ptype, restr, t1, t2):
        self.pid = pid  # Plane ID
        self.ptype = ptype  # "STD" or "JMB"
        self.restr = restr  # "T" or "F"
        self.t1 = t1  # Number of type 1 tasks
        self.t2 = t2  # Number of type 2 tasks

    def __gt__(self, other):
        return self.pid < other.pid

    def __repr__(self):
        return f"plane {self.pid}"


def parse_positions(line):
    # Parses a line of positions like:
    # "STD:(0,1) (1,0) (1,1) ..."
    line = line.strip()
    parts = line.split(":")
    wtype = parts[0].strip().upper()
    coords_str = parts[1].strip()
    coords = []
    for c in coords_str.split():
        c = c.strip("()")
        r, cc = c.split(",")
        coords.append((int(r), int(cc)))
    return wtype, coords


def read_input(filename):
    with open(filename, "r") as f:
        lines = [l.strip() for l in f if l.strip()]

    # Example input format:
    # Line 1: e.g. "Franjas: 4"
    # Line 2: e.g. "5x5"
    # Line 3: e.g. "STD:(0,1) (1,0) ..."
    # Line 4: e.g. "SPC:(0,3) (2,1) ..."
    # Line 5: e.g. "PRK:(0,0) (0,2) ..."
    # Following lines: planes e.g. "1-JMB-T-2-2"

    # Time slots
    _, franja_str = lines[0].split(":")
    n_slots = int(franja_str.strip())

    # Matrix size
    matrix_line = lines[1]  # "5x5"
    rows, cols = matrix_line.split('x')
    n_rows = int(rows)
    n_cols = int(cols)

    # Positions
    wtype_std, std_positions = parse_positions(lines[2])
    wtype_spc, spc_positions = parse_positions(lines[3])
    wtype_prk, prk_positions = parse_positions(lines[4])

    # Planes
    aircraft_lines = lines[5:]
    planes = []
    for al in aircraft_lines:
        parts = al.split('-')
        pid = parts[0]
        ptype = parts[1].strip()  # STD or JMB
        restr = parts[2].strip()  # T or F
        t1 = int(parts[3])
        t2 = int(parts[4])
        planes.append(Plane(pid, ptype, restr, t1, t2))

    return n_slots, n_rows, n_cols, std_positions, spc_positions, prk_positions, planes


def main():

    input_file = "maintenance_input.txt"

    # Read input
    n_slots, n_rows, n_cols, std_positions, spc_positions, prk_positions, planes = read_input(input_file)

    # Domain: all possible positions (STD + SPC + PRK)
    all_positions = std_positions + spc_positions + prk_positions

    problem = Problem()

    # Add variables:
    # For each plane and each slot, we have one variable that must be assigned a position.
    # This inherently ensures constraint 1:
    # "Each aircraft in the fleet must be assigned a single workshop or parking lot in each time slot"
    for plane in planes:
        problem.addVariable(plane, all_positions)

    # Just to illustrate adding a trivial constraint function:
    # Here, constraint 1 is basically ensured by variable definition alone.
    # But if we wanted to explicitly check something (like ensuring they must be assigned somewhere):
    # we can add a dummy constraint that returns True always, since each variable must have a value.
    def trivial_constraint(*args):
        # This constraint does nothing except return True
        return len(args) == len(set(args))

    def adjacent(*args):
        for i in range(len(args)):
            adjust_free = 0
            for j in range(i+1, len(args)):
                if abs(args[i][0] - args[j][0]) + abs(args[i][1] - args[j][1]) != 1:
                    adjust_free += 1
            if adjust == 4:
                return False
        return True

    def jumbo_adjacent(*args):
        """
        Check if there is at least one adjacent pair of planes of type "JMB".

        Args:
            args (tuple): Positions of planes as tuples of (x, y).

        Returns:
            bool: False if at least one adjacent pair exists, True otherwise.
        """

        a_types = [a.ptype for a in planes]
        for i in range(len(args)-1):
            adjust = 0
            for j in range(i + 1, len(args)):
                if a_types[i] == a_types[j] == "JMB":
                    if abs(args[i][0] - args[j][0]) + abs(args[i][1] - args[j][1]) == 1:
                        adjust += 1
            if adjust:
                return False
        return True

    # Add the trivial constraint to all variables of a single timeslot, for example:

    problem.addConstraint(trivial_constraint, planes)
    problem.addConstraint(adjacent, planes)
    #problem.addConstraint(jumbo_adjacent, planes)

    # Solve (this is trivial at this stage, might have many solutions)
    solutions = problem.getSolutions()

    # Print out the number of solutions and one sample solution
    print("Number of solutions:", len(solutions))
    if solutions:
        print("Example solution:")
        for sol in solutions:
            print("Solution:")
            for plane in planes:
                # assign_str = ", ".join(f"{sol[plane]}" for t in range(n_slots))
                assign_str = f"{sol[plane]}"
                print(f"Plane {plane.pid}: {assign_str}")
            print()


if __name__ == "__main__":
    main()