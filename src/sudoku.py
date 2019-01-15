#!/usr/bin/env python2.7
from z3 import *
import sys
import getopt
import textwrap
import re

verbose = False
pretty = False
output = None
filename = None
use_unsat_core = False
N = None

def vprint (message):
  if verbose:
    sys.stdout.write (message)

def pretty_string (grid, core=[]):
  out = ''
  for i in range (N**2):
    for j in range (N**2):
      if (i, j) in set (core):
        out += " \033[0;31m%d\033[0m " % grid [i][j]
      else:
        out += " %d " % grid [i][j]
      if (j % N == 2) and (j != (N**2 - 1)):
        out += "|"
    out += "\n"
    if (i % N == 2) and (i != (N**2 - 1)):
      for k in range (N):
        out += "-" * 3 * N
        if k != N - 1:
          out += "+"
      out += "\n"
  return out

def less_pretty_string (grid):
  out = "%d\n" % (N)
  for i in grid:
    for v in i:
      out += "%d " % (v)
    out += "\n"
  return out

def read_grid (filename):
  global N
  vprint ("Reading grid from %s\n" % (filename))
  try:
    file = open (filename, "r")
  except IOError:
    sys.stderr.write ("Could not open file %s...\n" % (filename))
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
  if verbose:
    gstr = pretty_string (grid)
    print "Grid red from file:"
    sys.stdout.write (re.sub ('0', ' ', gstr))
  return grid

def read_grid_from_command ():
  vprint ("Reading grid from command line...\n")
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
  if verbose:
    gstr = pretty_string (grid)
    print "Grid red from command line:"
    sys.stdout.write (re.sub ('0', ' ', gstr))
  return grid

def check_grid (grid):
  vprint ("Checking wether the grid is correct or not...\n")
  assert len (grid) == N**2
  for line in grid:
    assert len (line) == N**2
    for value in line:
      assert value >= 0 and value <= 9
  vprint ("Grid is correct !\n")

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
      squares[N * (j/N) + (i/N)] += [line[i]]
  return squares

def generate_z3_grid ():
  vprint ("Generation of the grid of Z3 variables...\n")
  grid = [ [ [Int ("x_%d_%d_%d" % (i, j, k)) for k in range (N**2)
  ] for j in range (N**2)]
  for i in range (N**2)]
  return grid

def retreive_grid (z3_model, z3_grid):
  vprint ("Retreiving grid from Z3 variables...\n")
  grid = [[0 for i in range (N**2)] for j in range (N**2)]
  for i in range (N**2):
    for j in range (N**2):
      for k in range (N**2):
        v = z3_grid [i][j][k]
        if z3_model [v].as_long () == 1:
          grid [i][j] = k + 1
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
    if subject == "pretty":
      message = textwrap.dedent ("""\
      If the pretty option is given the output will be a table with
      pipes and dashes to separate each squares.
      Otherwise the output will of the same kind than the input format.\
      """)
      print message
      sys.exit (retval)
    else:
      sys.stderr.write ("Unknown subject for the help command.\n")
      sys.exit (1)
  if retval == 0:
    message = textwrap.dedent ("""\
    Usage: %s [options]...
    Mandatory arguments to long options are mandatory
    for short options too.
    Options:
      -h, --help               Display this information.
      --help-topic=<topic>     Display the help about the given topic.
                               Available topics are: format, pretty..
      -v, --verbose            Display more information during execution.
      -p, --pretty             Prints the output the pretty way.
      -f, --file <file>        Use the sudoku as input.
      -o, --output <file>      Write the result in the <file> output file.
      -u, --unsat-core         Use unsat core to see what is wrong.\
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
optlist, args = getopt.getopt (args, "hvpf:o:u",[
  'help', 'verbose', 'file=', 'pretty', "output=", "help-topic=", "unsat-core"
])
for o, a in optlist:
  if o in ('-h', '--help'):
    usage (0)
  elif o in ('--help-topic'):
    usage (0, a)
  elif o in ('-v', '--verbose'):
    verbose = True
  elif o in ('-p', '--pretty'):
    pretty = True
  elif o in ('-f', '--file'):
    filename = a
  elif o in ('-o', '--output'):
    output = a
  elif o in ('-u', '--unsat-core'):
    use_unsat_core = True

grid = None
if filename != None:
  grid = read_grid (filename)
else:
  grid = read_grid_from_command ()

check_grid (grid)
z3_grid = generate_z3_grid ()

vprint ("Creating solver\n")
solver = Solver ()
solver.set (unsat_core = True)

# Each variables should have a positive value
vprint ("Asserting that each Z3 variables should be positive..\n")
for i in z3_grid:
  for j in i:
    for k in j:
      val = k >= 0
      if use_unsat_core:
        solver.assert_and_track (val, "pos")
      else:
        solver.add (val)


sat_core = []
core_name_id = 0

# Add default values to z3
vprint ("Seting the default values for the sudoku grid..\n")
for i in range (N**2):
  for j in range (N**2):
    v = grid [i][j]
    if v != 0:
      val = z3_grid[i][j][v-1] == 1
      if use_unsat_core:
        core_name = "init_val_%d" % (core_name_id)
        core_name_id+=1
        sat_core.insert (len (sat_core), (core_name, i, j))
        solver.assert_and_track (val, core_name)
      else:
        solver.add (val)


# Each cell should have exactly one value
vprint ("Asserting that there must be exactly one value per cell..\n")
for i in z3_grid:
  for j in i:
    val = Sum ([x for x in j]) == 1
    solver.add (val)

# There must be only one iteration of each values in 1..N**2 per line
vprint ("Asserting that there must be only one iteration of each values in "
        "1..%d per line..\n" % (N**2))
for i in get_lines (z3_grid):
  for j in range (N**2):
    l = []
    for v in range (N**2):
      l.insert (len (l), i[v][j])
    val = Sum (l) == 1
    solver.add (val)

# There must be only one iteration of each values in 1..N**2 per columns
vprint ("Asserting that there must be only one iteration of each values in "
        "1..%d per columns..\n" % (N**2))
for i in get_columns (z3_grid):
  for j in range (N**2):
    l = []
    for v in range (N**2):
      l.insert (len (l), i[v][j])
    val = Sum (l) == 1
    solver.add (val)

# There must be only one iteration of each values in 1..N**2 per square
vprint ("Asserting that there must be only one iteration of each values in "
        "1..%d per square..\n" % (N**2))
for i in get_squares (z3_grid):
  for j in range (N**2):
    l = []
    for v in range (N**2):
      l.insert (len (l), i[v][j])
    val = Sum (l) == 1
    solver.add (val)

result_grid = None
vprint ("Checking wether the instance is satifiable..\n")
if solver.check () == sat:
  vprint ("It is !\n")
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
  vprint ("It is not..\n")
  print "unsat"
  if use_unsat_core:
    core = solver.unsat_core ()
    core_list = []
    for c in core:
      if c.decl().name() != "pos":
        for n, i, j in sat_core:
          if n == c.decl().name():
            core_list.insert (len (core_list), (i, j))
    string = pretty_string (grid, core_list)
    print "Here is the unsat core:"
    sys.stdout.write (re.sub ('0', ' ', string))
