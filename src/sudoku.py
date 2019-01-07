#!/usr/bin/env python2.7
from z3 import *
import sys

N = 3

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

filename = "test.txt"

print (read_grid (filename))
