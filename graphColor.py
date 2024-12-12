import constraint


# return a list of adjacent vertices to the given vertex
def adjacent(vertex) -> list:
    return {'a': ['b', 'c', 'e'],
                'b': ['a', 'e', 'd'],
                'c': ['a', 'e'],
                'd': ['b'],
                'e': ['a', 'b', 'c']}[vertex]  # the definition of graph we have


# verify that two adjacent vertices are coloured with different colors
def constraintColor(vertex, *neighbors) -> bool:
    for i_neighbor in neighbors:
        if vertex == i_neighbor:
            return False
    
    # at this point, the vertex is meant to be coloured with diff colors
    return True

if __name__ == "__main__":

    # create csp task
    task = constraint.Problem()

    # crete the variables
    task.addVariables("abcde", range(3))
    vertices = ['a', 'b', 'c', 'd', 'e']

    
    for i_vertex in vertices:
        task.addConstraint(constraintColor, [i_vertex, *adjacent(i_vertex)])
    
    solutions = task.getSolutions()
    print(f"Amount of solutions: {len(solutions)}")  # better not to do so

    for i_solution in solutions:
        for i_vertex in vertices:
            print(f"{i_vertex}: {i_solution[i_vertex]}")
        print()