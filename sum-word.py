import constraint
"""

script to solve the following sum-word brain teaser:

  S E N D
+ M O R E
---------
M O N E Y
  a b c d


  meaning D + E = Y
  domain: 0...9
  a, b, c, d stands for ten, in sense if D + E >= 10, then d = 1

"""

def sumWordConstraint(a, b, c, post, pre=0):
    return pre + a + b == c + 10*post


if __name__ == '__main__':
    problem = constraint.Problem()

    problem.addVariables("SENDMORY", range(10))
    problem.addVariables("abcd", range(2))

    problem.addConstraint(sumWordConstraint, ('D', 'E', 'Y', 'd'))
    problem.addConstraint(sumWordConstraint, ('N', 'R', 'E', 'c', 'd'))
    problem.addConstraint(sumWordConstraint, ('E', 'O', 'N', 'b', 'c'))
    problem.addConstraint(sumWordConstraint, ('S', 'M', 'O', 'a', 'b'))
    problem.addConstraint(constraint.AllDifferentConstraint(), "SENDMORE")
    problem.addConstraint(lambda x, y: x==y, ('M', 'a'))

    solutions = problem.getSolutions()
    print(f"Amount of solutions: {len(solutions)}")  # better not to do so
    print(solutions)

