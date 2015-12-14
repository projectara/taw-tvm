#!/usr/bin/python
#
# Copyright (c) 2015 Google Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
# this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
# contributors may be used to endorse or promote products derived from this
# software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
# OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import difflib
import sys

timestamp_lines = ['-@ffe 30313531\n', '-@fff 30313731\n', '-@fff 30303731\n']

def timestamp_diff(line):
    timestamp_plus_prefix = line.startswith('+@ffe') or line.startswith('+@fff')
    return line in timestamp_lines or timestamp_plus_prefix

def distinct_diff_lines(diff):
    for line in [l for l in diff if l[0] in '+-']:
        if line != '+++ \n' and line != '--- \n':
            if not timestamp_diff(line):
                yield line

def main(drop_bootrom, reproduced_bootrom):
    with open(drop_bootrom) as f_drop:
        with open(reproduced_bootrom) as f_reproduced:
            drop_lines = f_drop.readlines()
            reproduced_lines = f_reproduced.readlines()
            diff = difflib.unified_diff(drop_lines, reproduced_lines)
            differences = [l for l in distinct_diff_lines(diff)]
            for diff_line in differences:
                print diff_line
            return sum(1 for _ in differences)

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
