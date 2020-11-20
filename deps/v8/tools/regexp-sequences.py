#!/usr/bin/env python
# Copyright 2019 the V8 project authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""
python %prog trace-file

Parses output generated by v8 with flag --trace-regexp-bytecodes and generates
a list of the most common sequences.
"""

from __future__ import print_function

import sys
import re
import collections

def parse(file, seqlen):
  # example:
  # pc = 00, sp = 0, curpos = 0, curchar = 0000000a ..., bc = PUSH_BT, 02, 00, 00, 00, e8, 00, 00, 00 .......
  rx = re.compile(r'pc = (?P<pc>[0-9a-f]+), sp = (?P<sp>\d+), '
                  r'curpos = (?P<curpos>\d+), curchar = (?P<char_hex>[0-9a-f]+) '
                  r'(:?\.|\()(?P<char>\.|\w)(:?\.|\)), bc = (?P<bc>\w+), .*')
  total = 0
  bc_cnt = [None] * seqlen
  for i in range(seqlen):
    bc_cnt[i] = {}
  last = [None] * seqlen
  with open(file) as f:
    l = f.readline()
    while l:
      l = l.strip()
      if l.startswith("Start bytecode interpreter"):
        for i in range(seqlen):
          last[i] = collections.deque(maxlen=i+1)

      match = rx.search(l)
      if match:
        total += 1
        bc = match.group('bc')
        for i in range(seqlen):
          last[i].append(bc)
          key = ' --> '.join(last[i])
          bc_cnt[i][key] = bc_cnt[i].get(key,0) + 1

      l = f.readline()
  return bc_cnt, total

def print_most_common(d, seqlen, total):
  sorted_d = sorted(d.items(), key=lambda kv: kv[1], reverse=True)
  for (k,v) in sorted_d:
    if v*100/total < 1.0:
      return
    print("{}: {} ({} %)".format(k,v,(v*100/total)))

def main(argv):
  max_seq = 7
  bc_cnt, total = parse(argv[1],max_seq)
  for i in range(max_seq):
    print()
    print("Most common of length {}".format(i+1))
    print()
    print_most_common(bc_cnt[i], i, total)

if __name__ == '__main__':
  main(sys.argv)