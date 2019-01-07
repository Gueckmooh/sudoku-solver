#!/usr/bin/env python2.7
from z3 import *
import sys

N = 3

def to_bool (value):
  result = [False for i in range (N**2)]
  result[value - 1] = True
  return result

def to_value (bool):
  for i in range (len (bool)):
    if bool[i]:
      return i + 1

def read_grid (filename):
  try:
    file = open (filename, "r")
  except IOError:
    print ("Cannot open file ", filename)
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
      columns[i] = columns[i] + [line [i]]
  return columns

def get_squares (grid):
  squares = [[] for i in range (N**2)]
  for j in range (len (grid)):
    line = grid [j]
    for i in range (len (line)):
      squares[N * (j/3) + (i/3)] += [line[i]]
  return squares

filename = "example.txt"

grid = read_grid (filename)
check_grid (grid)
