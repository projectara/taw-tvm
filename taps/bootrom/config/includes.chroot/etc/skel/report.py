#!/usr/bin/python
#
#  Copyright (c) 2015-2016 Google Inc.
#  All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are met:
#  1. Redistributions of source code must retain the above copyright notice,
#  this list of conditions and the following disclaimer.
#  2. Redistributions in binary form must reproduce the above copyright notice,
#  this list of conditions and the following disclaimer in the documentation
#  and/or other materials provided with the distribution.
#  3. Neither the name of the copyright holder nor the names of its
#  contributors may be used to endorse or promote products derived from this
#  software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
#  AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
#  THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
#  PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
#  CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
#  EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
#  PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS;
#  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
#  WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
#  OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
#  ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Basic plan for how to build a Bootrom report:
# 1) Get the name of the delivery tarball (by regex matching)
# 2) Get the version (by command-line)
# 3) Pass the appropriate variables to Mako with the template (command-line?  hard-coded?)
# 4) Output Mako's resulting HTML

from mako.template import Template
import glob
import os.path
import sys
import tarfile

def render_report(template_file, git_hash):
    drop_files = glob.glob('*.es3-bootrom-delivery.sha256')
    drop_name = os.path.splitext(drop_files[0])[0]
    with open(drop_name + '.sha256') as sha_file:
        sha_sum = sha_file.readlines()[0].split(' ')[0]
    archive = tarfile.open(drop_name + '.tar.gz', mode='r:gz')
    template = Template(filename=template_file)
    print(template.render(git_hash=git_hash, delivery_files_name=drop_name, top_marking="GOOGLE CONFIDENTIAL RESTRICTED", tar_contents=archive.getnames(), sha_sum=sha_sum))

if __name__ == '__main__':
    render_report(sys.argv[1], sys.argv[2])
