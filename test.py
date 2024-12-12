import constraint

problem = constraint.Problem()
problem.addVariable('a', [1, 2, 3, 4]) # var name and domain

problem.addVariable('b', [1, 2, 3, 4]) # var name and domain

problem.addVariable('c', [1, 2, 3, 4]) # var name and domain

def le(x, y):
    return x <= y

def gt(x, y):
    return x > y

problem.addConstraint(le, ['a', 'b']) # pass function as parameter and array of variables to be used
problem.addConstraint(gt, ['b', 'c'])

solutions = problem.getSolutions()
print(solutions)  # better not to do so

for isolution in solutions:
    print(f"{'a'}: {isolution['a']} / {'b'}: {isolution['b']} / {'c'}: {isolution['c']} ")
