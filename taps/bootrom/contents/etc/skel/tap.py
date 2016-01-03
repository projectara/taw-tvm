#! /usr/bin/env python3

import locale
import dialog
import subprocess

def run_in_shell(cmd, d):
    try:
        subprocess.check_output(cmd, stderr=subprocess.STDOUT, shell=True)
    except subprocess.CalledProcessError as subproc_err:
        d.msgbox('%s (%d): %s\n'.format(subproc_err.cmd,
                                        subproc_err.returncode,
                                        subproc_err.output))
        raise subproc_err

locale.setlocale(locale.LC_ALL, '')

tap_dialog = dialog.Dialog(dialog="dialog")
tap_dialog.set_background_title("Reproduce ES3 bootrom")

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