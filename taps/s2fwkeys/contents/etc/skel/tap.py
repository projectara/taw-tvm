#! /usr/bin/env python3

import locale
import dialog
import subprocess
import datetime
from mako.template import Template

public_key_file = "public_keys.c"
public_keys_name_suffix = "s2fvk.projectara.com"

def run_in_shell(cmd, d, pipe_target=None, pipe_flag='a'):
    try:
        pipe = subprocess.check_output(cmd, stderr=subprocess.STDOUT,
                                       shell=True)
        if pipe_target is not None:
            with open(pipe_target, pipe_flag + 'b') as pipe_file:
                pipe_file.write(pipe)
    except subprocess.CalledProcessError as subproc_err:
        d.msgbox('%s (%d): %s\n' % (subproc_err.cmd,
                                        subproc_err.returncode,
                                        subproc_err.output))
        raise subproc_err

locale.setlocale(locale.LC_ALL, '')

tap_dialog = dialog.Dialog(dialog="dialog")
tap_dialog.set_background_title("Generate Stage 2 Firmware Keys")

user_elements = [('Username', 1, 1, '', 1, 20, 10, 0, 0),
                 ('Email Address', 2, 1, '', 2, 20, 30, 0, 0),
                 ('Key-name prefix', 3, 1, '', 3, 20, 10, 0, 0),
                 ('Number of keys', 4, 1, '1', 4, 20, 2, 0, 0),
                 ('Password', 5, 1, '', 5, 20, 10, 0, 1)]
code, user_fields = tap_dialog.mixedform('Please specify profile:',
                                         user_elements)
if code == tap_dialog.OK:
    num_keys = int(user_fields[3])
    keyfile_prefix = user_fields[2] + '-' + datetime.datetime.now().strftime("%Y%m%d")
    confirmation = 'Proceed with the following parameters?\n'
    confirmation +='Username: {0} ({1})\nKeys to generate: {2:d}\nKey prefix: {3}\n'
    confirmation = confirmation.format(user_fields[0], user_fields[1], num_keys,
                                       keyfile_prefix)
    code = tap_dialog.yesno(confirmation, 20, 60)
    if code == tap_dialog.OK:
        for i in range(0, num_keys):
            key_file = keyfile_prefix + '-%.2d' % (i)
            cmd = 'openssl genrsa -aes256 -passout pass:{pw} -out {keyfile}.private.pem 2048'
            cmd = cmd.format(pw=user_fields[4], keyfile=key_file)
            run_in_shell(cmd, tap_dialog)
            cmd = 'openssl rsa -passin pass:{pw} -in {keyfile}.private.pem '
            cmd += '-outform PEM -pubout -out {keyfile}.public.pem'
            cmd = cmd.format(pw=user_fields[4], keyfile=key_file)
            run_in_shell(cmd, tap_dialog)
            with open(public_key_file, 'w') as pkf:
                pkf.write("/* Google Project Ara - Stage 2 Firmware Validation Keys */\n")
                pkf.write("/* Key ID {0} */\n".format(keyfile_prefix))
                pkf.write("/* Automatically generated file ... DO NOT EDIT */\n")
                pkf.write("\n")
            cmd = "./pem2arakeys {0}.public.pem --format rsa2048-sha256 --usage {1}"
            cmd = cmd.format(key_file, public_keys_name_suffix)
            run_in_shell(cmd, tap_dialog, public_key_file)

