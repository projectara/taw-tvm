#! /usr/bin/env python3
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

import locale
import dialog
import subprocess

def run_in_shell(cmd, d):
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as subproc_err:
        d.msgbox('{0} ({1}): {2}\n'.format(subproc_err.cmd,
                                           subproc_err.returncode,
                                           subproc_err.output))
        raise subproc_err

locale.setlocale(locale.LC_ALL, '')

tap_dialog = dialog.Dialog(dialog="dialog")
tap_dialog.set_background_title("Reproduce ES3 bootrom")

run_in_shell('cp -R /media/input_cdrom/* ~', tap_dialog)

code, tag = tap_dialog.radiolist("Select revision of bootrom to build:",
                                 choices=[('es2tsb', 'ES2 flashable bootrom',
                                           False),
                                          ('es3tsb', 'ES3 bootrom, most recent',
                                           False),
                                          ('Toshiba_Drop',
                                           'ES3 bootrom as delivered to Toshiba',
                                           True)])
if code == tap_dialog.OK:
    try:
        tap_dialog.gauge_start(text='Building bootrom prerequisites', percent=0)
        run_in_shell('./bootrom_setup.sh', tap_dialog)
        tap_dialog.gauge_update(33, text='Building bootrom...',
                                update_text=True)
        if tag == 'Toshiba_Drop':
            run_in_shell('./build_bootrom.sh', tap_dialog)
            tap_dialog.gauge_update(66, text='Generating ISO...', update_text=True)
            run_in_shell('./deliver_iso.sh', tap_dialog)
            tap_dialog.gauge_update(100, text='ISO and report delivered',
                                    update_text=True)
        else:
            run_in_shell(['./bootrom-tools/scripts/makeboot', '-' + tag],
                         tap_dialog)
            tap_dialog.gauge_update(100, text='Bootrom rebuilt from up-to-date \
                                    source', update_text=True)
        tap_dialog.msgbox('Bootrom successfully rebuilt and delivered to \
                           Trusted Administration Workstation')
    finally:
        tap_dialog.gauge_stop()