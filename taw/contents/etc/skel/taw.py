#! /usr/bin/env python3

import locale
import dialog
import subprocess
from datetime import datetime
import os.path
import os
import fnmatch

def isblkdev(path):
    mode = os.stat(path).st_mode
    return os.st.S_ISBLK(mode)

def run_in_shell(cmd, d):
    try:
        subprocess.check_output(' '.join(cmd), stderr=subprocess.STDOUT,
                                shell=True)
    except subprocess.CalledProcessError as subproc_err:
        d.msgbox('{0} ({1}): {2}'.format(subproc_err.cmd,
                                         subproc_err.returncode,
                                         subproc_err.output))
        raise subproc_err

def query_blk_dev(taw_dialog, blk_dev_name):
    code = taw_dialog.OK
    present = False
    while code == taw_dialog.OK and not present:
        code, img = taw_dialog.inputbox('Please specify location of ' +
                                        blk_dev_name + ':')
        present = isblkdev(img)
        if not present:
            taw_dialog.msgbox('Please enter a path to a block device.')
    return (code, img)

def query_hdd_img(taw_dialog, hdd_img_name):
    code = taw_dialog.OK
    present = False
    while code == taw_dialog.OK and not present:
        code, img = taw_dialog.inputbox('Please specify location of ' +
                                        hdd_img_name + ':')
        present = os.path.isfile(img)
        if not present:
            taw_dialog.msgbox('Please enter a path to a QEMU image.')
    return (code, img)

def run_qemu(img_args, taw_dialog):
    args = ['qemu-system-i386', '-m', '1024'] + img_args + ['-enable-kvm',
            '-cpu', 'host', '-virtfs', 'local,path=tashare,mount_tag=tashare,security_model=passthrough,id=host1']
    run_in_shell(args, taw_dialog)

def detect_file_type(top, ext):
    for (path, dirs, files) in os.walk(top):
        for file in files:
            (name, file_ext) = os.path.splitext(file)
            if file_ext == '.' + ext:
                yield path + '/' + file

def detect_disk_writers():
    for dev in os.listdir('/dev/'):
        if fnmatch.fnmatch(dev, 'sr*'):
            yield '/dev/' + dev

def run_xorriso(iso, writer, taw_dialog):
    code = 'retry'
    while code == 'retry':
        try:
            args = ['xorriso', '-as', 'cdrecord', 'dev=' + writer,
                    '-blank=as_needed', '-eject', iso]
            run_in_shell(args, taw_dialog)
            code = taw_dialog.yesno('Was the disk written successfully?')
            if code == taw_dialog.CANCEL:
                code = 'retry'
        except subprocess.CalledProcessError as err:
            code = taw_dialog.yesno('xorriso failed.  Try again?')
            if code == taw_dialog.OK:
                code = 'retry'
            else:
                raise err

locale.setlocale(locale.LC_ALL, '')

taw_dialog = dialog.Dialog(dialog="dialog")
taw_dialog.set_background_title("Trusted Administration Workstation")

taw_choices = [('rundisk', 'Run TVM from live-disk', True),
               ('runhdd', 'Run TVM from installed HDD image', False),
               ('install', '', False)]
code, tag = taw_dialog.radiolist("Select TAW activity to perform:",
                                 choices=taw_choices)
if code == taw_dialog.OK:
    try:
        if tag == 'rundisk':
            (code, img) = query_blk_dev(taw_dialog, 'TVM disk')
            if code == taw_dialog.OK:
                run_qemu(['-cdrom', img], taw_dialog)
            else:
                exit(-1)
        elif tag == 'runhdd':
            (code, img) = query_hdd_img(taw_dialog, 'TVM image')
            if code == taw_dialog.OK:
                run_qemu(['-hda', img], taw_dialog)
            else:
                exit(-1)
        elif tag == 'install':
            (code, img) = query_blk_dev(taw_dialog, 'TVM disk')
            if code == taw_dialog.OK:
                timestamp = datetime.now().strftime('%Y%m%d%H%M%s')
                tvm_img = timestamp + '_hda.qcow2'
                taw_dialog.msgbox('Building TVM image: ' + tvm_img)
                run_in_shell(['qemu-img', 'create', '-f', 'qcow2', tvm_img,
                              '32G'], taw_dialog)
                taw_dialog.msgbox('Running QEMU to install TVM...')
                run_qemu(['-cdrom', img, '-hda', tvm_img], taw_dialog)
            else:
                exit(-1)
        for iso in detect_file_type('tashare', 'iso'):
            code = taw_dialog.yesno('Burn optical disks from ' + iso + '?')
            if code == taw_dialog.OK:
                writers = list(detect_disk_writers())
                choices = [(str(i), dev, True) for (i, dev) in
                           enumerate(writers)]
                (code, tags) = taw_dialog.checklist('Burn to which writers?',
                                                    choices=choices)
                if code == taw_dialog.OK:
                    for i in tags:
                        run_xorriso(iso, writers[int(i)], taw_dialog)
                elif code == taw_dialog.CANCEL:
                    pass
        for pdf in detect_file_type('tashare', 'pdf'):
            copies = ''
            code = taw_dialog.OK
            while not copies.isdigit() and code == taw_dialog.OK:
                code, copies = taw_dialog.inputbox('Print how many copies of ' +
                                                   pdf + '?')
            if code == taw_dialog.OK:
                run_in_shell(['lp', '-n', copies, pdf], taw_dialog)
    finally:
        pass
