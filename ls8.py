"""Main."""

import sys
from cpu import *

if len(sys.argv) != 2:
  print('Invalid input.')
  sys.exit(1)

if len(sys.argv) == 2:
  print(f'Running: {sys.argv[0]}')
  print(f'With program: {sys.argv[1]}')
  cpu = CPU()
  cpu.load(sys.argv[1])
  cpu.run()