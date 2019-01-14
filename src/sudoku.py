#!/usr/bin/env python2.7
from z3 import *
import sys
import getopt
import textwrap

verbose = False
pretty = False
output = None
filename = None
N = 3

def pretty_string (grid):
  out = ''
  for i in range (N**2):
    for j in range (N**2):
      out += " %d " % grid [i][j]
      if (j % 3 == 2) and (j != (N**2 - 1)):
        out += "|"
    out += "\n"
    if (i % 3 == 2) and (i != (N**2 - 1)):
      for k in range (N):
        out += "-" * 3 * N
        if k != N - 1:
          out += "+"
      out += "\n"
  return out

def less_pretty_string (grid):
  out = ''
  for i in grid:
    for v in i:
      out += "%d " % (v)
    out += "\n"
  return out

def read_grid (filename):
  try:
    file = open (filename, "r")
  except IOError:
    sys.stderr.write ("Could not open file %s\n" % (filename))
    sys.exit (1)
  grid = []
  lines = file.readlines ()
  file.close ()
  N = int (lines[0][0])
  for line in lines[1:]:
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

def read_grid_from_command ():
  N = int (raw_input ("Give the size of the grid (for 9x9 grid give 3 (3**2 = 9)): "))
  lines = []
  print "Give the %d lines of the grid" % (N**2)
  grid = []
  for i in range (N**2):
    l = raw_input ()
    lines.insert (len (lines), l)
  for line in lines:
    line = line.split ()
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

def usage (retval, subject=None):
  prgname = sys.argv[0]
  if subject != None:
    if subject == "format":
      message = textwrap.dedent ("""\
      The input format is the following:
        On the first line there must be written the N value
        which is the size of the grid. With N=3 for 9x9 grid
        format (3**2 = 9).

        On the following lines there is the values of each lines
        of the grid with 0 where the value is unknown.

      For example:
        3
        3 0 7 6 0 0 0 0 2
        0 6 0 0 0 8 7 0 5
        5 0 2 0 0 0 0 0 0
        1 0 0 8 6 5 0 7 9
        0 0 0 2 0 3 0 0 0
        8 3 0 7 4 9 0 0 6
        0 0 0 0 0 0 4 0 1
        6 0 8 1 0 0 0 5 0
        7 0 0 0 0 6 2 0 8

      For the following grid:
        3     7 | 6       |       2
           6    |       8 | 7     5
        5     2 |         |
       ---------+---------+---------
        1       | 8  6  5 |    7  9
                | 2     3 |
        8  3    | 7  4  9 |       6
       ---------+---------+---------
                |         | 4     1
        6     8 | 1       |    5
        7       |       6 | 2     8
      """)
      print message
      sys.exit (retval)
    else:
      sys.stderr.write ("Unknown subject for the help command.")
      sys.exit (1)
  if retval == 0:
    message = textwrap.dedent ("""\
    Usage: %s [options]...
    Mandatory arguments to long options are mandatory
    for short options too.
    Options:
      -h, --help               Display this information.
      --help=<subject>         Display the help about the given subject.
                               Available subjects are: format..
      -v, --verbose            Display more information during execution.
      -p, --pretty             Prints the output the pretty way.
      -f, --file <file>        Use the sudoku as input.
      -o, --output <file>      Write the result in the <file> output file.\
    """ % prgname)
    print message
    sys.exit (retval)
  else:
    message = textwrap.dedent ("""\
    Try '%s --help' for more information.\
    """ % (prgname))
    print message
    sys.exit (retval)


# Command line arguments parsing

args = sys.argv[1:]
optlist, args = getopt.getopt (args, "hvpf:o:",[
  'help=', 'verbose', 'file=', 'pretty', "output="
])
for o, a in optlist:
  if o in ('-h', '--help'):
    if a != '':
      usage (0, a)
    else:
      usage (0)
  elif o in ('-v', '--verbose'):
    verbose = True
  elif o in ('-p', '--pretty'):
    pretty = True
  elif o in ('-f', '--file'):
    filename = a
  elif o in ('-o', '--output'):
    output = a

# filename = "/home/brignone/Documents/Cours/M2/SAT-SMT-solving/sudoku-solver/src/example.txt"

grid = None
if filename != None:
  grid = read_grid (filename)
else:
  grid = read_grid_from_command ()

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

result_grid = None
if solver.check () == sat:
  model = solver.model ()
  result_grid = retreive_grid (model, z3_grid)
  grid_str = ''

  # Is this pretty ?
  if pretty:
    grid_str = pretty_string (result_grid)
  else:
    grid_str = less_pretty_string (result_grid)

  # Do I write it in file ?
  if output != None:
    try:
      file = open (output, "w")
    except IOError:
      sys.stderr.write ("Could not open %s\n" % (output))
      sys.exit (1)
    file.write (grid_str)
    file.close ()
  else:
    sys.stdout.write (grid_str)

else:
  print "unsat"
