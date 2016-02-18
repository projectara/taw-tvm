#! /usr/bin/env python3

import locale
import dialog
import subprocess
import datetime
from mako.template import Template
from validate_email.validate_email import validate_email
from fnmatch import fnmatch
import os

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
        d.msgbox('{0} ({1}): {2}\n'.format(subproc_err.cmd,
                                           subproc_err.returncode,
                                           subproc_err.output))
        raise subproc_err

def wkhtmltopdf(html, pdf):
    cmd = 'xvfb-run --server-args="-screen 0, 1024x768x24" '
    cmd += 'wkhtmltopdf '
    cmd += '--page-size Letter --orientation landscape '
    cmd += '--page-width 8.5in --page-height 11in '
    cmd += '--margin-bottom 0 --margin-top 0 --margin-right 2.5 '
    cmd += html + ' ' + pdf
    run_in_shell(cmd, tap_dialog)

def generate_dvd_label(label, user, keyfile_prefix, tap_dialog):
    template = Template(filename=label+'.html.template')
    with open(label + '.html', 'w') as dvd_label:
        report = template.render(keyfile_prefix=keyfile_prefix, username=user)
        dvd_label.write(report)
    wkhtmltopdf(label + '.html', label + '.pdf')

def query_parameters(tap_dialog):
    code = tap_dialog.CANCEL
    while code != tap_dialog.OK:
        user_elements = [('Username', 1, 1, '', 1, 20, 10, 0, 0),
                         ('Email Address', 2, 1, '', 2, 20, 30, 0, 0),
                         ('Key-name prefix', 3, 1, '', 3, 20, 10, 0, 0),
                         ('Number of keys', 4, 1, '1', 4, 20, 2, 0, 0),
                         ('Password', 5, 1, '', 5, 20, 10, 0, 1)]
        code, user_fields = tap_dialog.mixedform('Please specify profile:',
                                                 user_elements)
        if code == tap_dialog.OK:
            if not validate_email(user_fields[1]) or user_fields[2].isdigit():
                tap_dialog.msgbox('Invalid parameters')
                code = tap_dialog.CANCEL
                continue
            if not fnmatch(user_fields[1], '*@projectara.com'):
                tap_dialog.msgbox('projectara.com email address required')
                code = tap_dialog.CANCEL
                continue
            keyfile_prefix = user_fields[2] + '-' + \
                datetime.datetime.now().strftime("%Y%m%d")
            confirmation = 'Proceed with the following parameters?\n'
            confirmation +='Username: {0} ({1})\n'
            confirmation += 'Keys to generate: {2}\n'
            confirmation += 'Key prefix: {3}\n'
            confirmation = confirmation.format(user_fields[0], user_fields[1],
                                               user_fields[3], keyfile_prefix)
            code = tap_dialog.yesno(confirmation, 20, 60)
        else:
            return tap_dialog.CANCEL, [], ''
    return code, user_fields, keyfile_prefix

def generate_disk_image(which, label, keyfile_prefix, tap_dialog):
    cmd = 'xorriso -as mkisofs -r -J -o {0}.iso -volid "{1}-{2}" {0}/'
    cmd = cmd.format(which, label, keyfile_prefix)
    run_in_shell(cmd, tap_dialog)

locale.setlocale(locale.LC_ALL, '')

tap_dialog = dialog.Dialog(dialog="dialog")
tap_dialog.set_background_title("Generate Stage 2 Firmware Keys")

run_in_shell('cp -R /media/input_cdrom/* ~', tap_dialog)

code, user_fields, keyfile_prefix = query_parameters(tap_dialog)
if code == tap_dialog.OK:
    os.makedirs('public/', exist_ok=True)
    os.makedirs('private/', exist_ok=True)
    num_keys = int(user_fields[3])
    for i in range(0, num_keys):
        try:
            # Generate key file name
            key_file = keyfile_prefix + '-%.2d' % (i)
            # Generate private key PEM
            tap_dialog.gauge_start(text='Generating private key PEM', percent=0)
            cmd = 'openssl genrsa -aes256 -passout pass:{pw} -out private/{keyfile}.private.pem 2048'
            cmd = cmd.format(pw=user_fields[4], keyfile=key_file)
            run_in_shell(cmd, tap_dialog)
            # Generate public key PEM
            tap_dialog.gauge_update(15, text='Generating public key PEM',
                                    update_text=True)
            cmd = 'openssl rsa -passin pass:{pw} -in private/{keyfile}.private.pem '
            cmd += '-outform PEM -pubout -out public/{keyfile}.public.pem'
            cmd = cmd.format(pw=user_fields[4], keyfile=key_file)
            run_in_shell(cmd, tap_dialog)
            # Generate public key C file
            tap_dialog.gauge_update(30, text='Generating public key C source',
                                    update_text=True)
            with open('public/' + public_key_file, 'w') as pkf:
                pkf.write("/* Google Project Ara - Stage 2 Firmware Validation Keys */\n")
                pkf.write("/* Key ID {0} */\n".format(keyfile_prefix))
                pkf.write("/* Automatically generated file ... DO NOT EDIT */\n")
                pkf.write("\n")
            cmd = "./pem2arakeys public/{0}.public.pem --format rsa2048-sha256 --usage {1}"
            cmd = cmd.format(key_file, public_keys_name_suffix)
            run_in_shell(cmd, tap_dialog, public_key_file)
            # Generate DVD labels from HTML templates
            tap_dialog.gauge_update(50, text='Generating DVD labels',
                                    update_text=True)
            generate_dvd_label('private_key_label', user_fields[0],
                               keyfile_prefix, tap_dialog)
            generate_dvd_label('public_key_label', user_fields[0],
                               keyfile_prefix, tap_dialog)
            #Generate disc image for public keys
            tap_dialog.gauge_update(70, text='Generating public-key disk image',
                                    update_text=True)
            generate_disk_image('public', 'S2FVK', keyfile_prefix, tap_dialog)
            #Generate disc image for private keys
            tap_dialog.gauge_update(80, text='Generating private-key disk image',
                                    update_text=True)
            generate_disk_image('private', 'S2FSK', keyfile_prefix, tap_dialog)
            #Move the disc images and DVD labels to the shared directory
            tap_dialog.gauge_update(90, text='Moving disk images and labels to TAW',
                                    update_text=True)
            cmd = 'mv {0}.iso {1}.iso {0}_key_label.pdf {1}_key_label.pdf /media/user/tashare'
            cmd = cmd.format('public', 'private')
            run_in_shell(cmd, tap_dialog)
            tap_dialog.gauge_update(100, text='Done', update_text=True)
        finally:
            tap_dialog.gauge_stop()
