#!/usr/bin/env python2.7
from z3 import *
import sys

N = 3

def pretty_print (grid):
  for line in grid:
    print line


def to_bool (value):
  result = [False for i in range (N**2)]
  if value != 0:
    result[value - 1] = True
  return result

def to_value (bool):
  for i in range (len (bool)):
    if bool[i]:
      return i + 1
  return 0

def apply_on_grid (function, grid):
  for line in grid:
    for i in range (len (line)):
      line[i] = function (line[i])

def read_grid (filename):
  try:
    file = open (filename, "r")
  except IOError:
    print "Cannot open file", filename
    sys.exit (1)
  grid = []
  lines = file.readlines ()
  for line in lines:
    if line == '':
      print "The file must have", N, "lines"
      sys.exit (2)
    line = line.split (" ")
    T = [int(x) for x in line]
    if grid == []:
      grid = [T]
    else:
      grid = grid + [T]
  return grid

def check_grid (grid):
  assert len (grid) == N**2
  for line in grid:
    assert len (line) == N**2
    for value in line:
      assert value >= 0 and value <= 9

def get_lines (grid):
  return grid

def get_columns (grid):
  columns = [[] for i in range (N**2)]
  for line in grid:
    for i in range (len (line)):
      columns[i].insert (len(columns[i]), line [i])
  return columns

def get_squares (grid):
  squares = [[] for i in range (N**2)]
  for j in range (len (grid)):
    line = grid [j]
    for i in range (len (line)):
      squares[N * (j/3) + (i/3)] += [line[i]]
  return squares

def generate_z3_grid ():
  grid = [ [ [Int ("x_%d_%d_%d" % (i, j, k)) for k in range (N**2)
  ] for j in range (N**2)]
  for i in range (N**2)]
  return grid

def retreive_grid (z3_model, z3_grid):
  grid = [[0 for i in range (N**2)] for j in range (N**2)]
  for i in range (N**2):
    for j in range (N**2):
      for k in range (N**2):
        v = z3_grid [i][j][k]
        if z3_model [v].as_long () == 1:
          # print z3_model [v]
          grid [i][j] = k + 1
          # print k
  return grid


# filename = "example.txt"
filename = "/home/brignone/Documents/Cours/M2/SAT-SMT-solving/sudoku-solver/src/example.txt"

grid = read_grid (filename)
check_grid (grid)
z3_grid = generate_z3_grid ()

solver = Solver ()

for i in z3_grid:
  for j in i:
    for k in j:
      val = k >= 0
      # print val
      solver.add (val)

# Add default values to z3
for i in range (N**2):
  for j in range (N**2):
    val = grid [i][j]
    if val != 0:
      val = z3_grid[i][j][val-1] == 1
      # print val
      solver.add (val)

# Each cell should have exactly one value
for i in z3_grid:
  for j in i:
    val = Sum ([x for x in j]) == 1
    # print val
    solver.add (val)

for i in get_lines (z3_grid):
  for j in range (N**2):
    l = []
    for v in range (N**2):
      l.insert (len (l), i[v][j])
    val = Sum (l) == 1
    # print val
    solver.add (val)

for i in get_columns (z3_grid):
  for j in range (N**2):
    l = []
    for v in range (N**2):
      l.insert (len (l), i[v][j])
    val = Sum (l) == 1
    # print val
    solver.add (val)

for i in get_squares (z3_grid):
  for j in range (N**2):
    l = []
    for v in range (N**2):
      l.insert (len (l), i[v][j])
    val = Sum (l) == 1
    # print val
    solver.add (val)

if solver.check () == sat:
  model = solver.model ()
  grid = retreive_grid (model, z3_grid)
  pretty_print (grid)
else:
  print "unsat"


# a = Bool ('a')
# b = Bool ('b')

# solver.add (Or (a, b))
