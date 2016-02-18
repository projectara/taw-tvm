#! /usr/bin/env python3

import locale
import dialog
import subprocess
from datetime import datetime
import glob
import re
import os.path
import os
import fnmatch
import psutil

def isblkdev(path):
    mode = os.stat(path).st_mode
    return os.st.S_ISBLK(mode)

def run_in_shell(cmd, d):
    try:
        return subprocess.check_output(' '.join(cmd), stderr=subprocess.STDOUT,
                                       shell=True)
    except subprocess.CalledProcessError as subproc_err:
        d.msgbox('{0} ({1}): {2}'.format(subproc_err.cmd,
                                         subproc_err.returncode,
                                         subproc_err.output))
        raise subproc_err

dev_pattern = ['sd*', 'sr*']

def enumerate_blk_devs(taw_dialog, fstype='iso9660'):
    i = 0
    for pattern in dev_pattern:
        for disk in glob.glob('/sys/block/' + pattern):
            dev = '/dev/' + os.path.basename(disk)
            cmd = 'blkid -s LABEL -o value ' + dev
            try:
                label = run_in_shell([cmd], taw_dialog)
                if label == '':
                    label = 'UNKNOWN' + str(i)
                    i += 1
                yield (str(label), dev)
            except subprocess.CalledProcessError as err:
                if err.returncode == 2:
                    continue

def query_blk_dev(taw_dialog, blk_dev_name):
    code = taw_dialog.OK
    present = False
    img = ''
    while code == taw_dialog.OK and not present:
        choices = list(enumerate_blk_devs(taw_dialog))
        code, label = taw_dialog.menu('Please specify location of ' +
                                      blk_dev_name + ':', choices=choices)
        if code == taw_dialog.OK:
            choices = dict(choices)
            present = isblkdev(choices[label])
            if present:
                img = choices[label]
            else:
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

def run_in_shell_retry(args, taw_dialog):
    code = 'retry'
    while code == 'retry':
        try:
            run_in_shell(args, taw_dialog)
            code = taw_dialog.yesno('Did {0} succeed?'.format(args[0]))
            if code == taw_dialog.CANCEL:
                code = 'retry'
        except subprocess.CalledProcessError as err:
            code = taw_dialog.yesno('{0} failed.  Try again?'.format(args[0]))
            if code == taw_dialog.OK:
                code = 'retry'
            else:
                raise err

def burn_iso(iso, taw_dialog):
    writers = list(detect_disk_writers())
    choices = [(str(i), dev, True) for (i, dev) in
               enumerate(writers)]
    if len(choices) > 0:
        (code, tags) = taw_dialog.checklist('Burn to which writers?',
                                            choices=choices)
        if code == taw_dialog.OK:
            for i in tags:
                run_xorriso(iso, writers[int(i)], taw_dialog)
        return code
    else:
        return taw_dialog.yesno('No disk writers found.  Continue anyway?')

def run_xorriso(iso, writer, taw_dialog):
    args = ['xorriso', '-as', 'cdrecord', 'dev=' + writer,
            '-blank=as_needed', '-eject', iso]
    run_in_shell_retry(args, taw_dialog)

def print_pdf(pdf, copies, taw_dialog):
    run_in_shell_retry(['lp', '-n', copies, pdf], taw_dialog)

def run_qemu(img_args, taw_dialog):
    args = ['qemu-system-i386', '-m', '2048'] + img_args + ['-enable-kvm',
            '-cpu', 'host', '-virtfs', 'local,path=tashare,mount_tag=tashare,security_model=passthrough,id=host1']
    run_in_shell_retry(args, taw_dialog)

def burn_hdd_image(image, taw_dialog):
    basename, ext = os.path.splitext(image)
    args = ['xorriso', '-dev', basename + '.iso', '-commit_eject', 'all',
            '-volid', basename, '-add', image]
    run_in_shell(args, taw_dialog)
    return burn_iso(basename + '.iso', taw_dialog)

locale.setlocale(locale.LC_ALL, '')

taw_dialog = dialog.Dialog(dialog="dialog")
taw_dialog.set_background_title("Trusted Administration Workstation")

taw_choices = [('rundisk', 'Run TVM from live-disk'),
               ('runhdd', 'Run TVM from installed HDD image'),
               ('install', 'Install TVM to HDD image')]
code, tag = taw_dialog.menu("Select TAW activity to perform:",
                            choices=taw_choices)
if code == taw_dialog.OK:
    try:
        if tag == 'rundisk':
            (code, img) = query_blk_dev(taw_dialog, 'TVM disk')
            (indisk_code, indisk_img) = query_blk_dev(taw_dialog,
                                                      'TVM data input disk')
            if code == taw_dialog.OK and indisk_code == taw_dialog.OK:
                run_qemu(['-cdrom', img, '-drive',
                         'file={0},index=1,media=disk'.format(indisk_img)],
                         taw_dialog)
            else:
                exit(-1)
        elif tag == 'runhdd':
            (code, img) = query_hdd_img(taw_dialog, 'TVM image')
            (indisk_code, indisk_img) = query_blk_dev(taw_dialog,
                                                      'TVM data input disk')
            if code == taw_dialog.OK and indisk_code == taw_dialog.OK:
                run_qemu(['-hda', img, '-cdrom', indisk_img], taw_dialog)
            else:
                exit(-1)
        elif tag == 'install':
            (code, img) = query_blk_dev(taw_dialog, 'TVM disk')
            (indisk_code, indisk_img) = query_blk_dev(taw_dialog,
                                                      'TVM data input disk')
            if code == taw_dialog.OK and indisk_code == taw_dialog.OK:
                timestamp = datetime.now().strftime('%Y%m%d%H%M%s')
                tvm_img = timestamp + '_hda.qcow2'
                taw_dialog.msgbox('Building TVM image: ' + tvm_img)
                run_in_shell(['qemu-img', 'create', '-f', 'qcow2', tvm_img,
                              '32G'], taw_dialog)
                code = burn_hdd_image(tvm_img, taw_dialog)
                if code != taw_dialog.OK:
                    exit(-1)
                taw_dialog.msgbox('Running QEMU to install TVM...')
                run_qemu(['-cdrom', img, '-hda', tvm_img, '-drive',
                         'file={0},index=1,media=disk'.format(indisk_img)],
                         taw_dialog)
            else:
                exit(-1)
        for pdf in detect_file_type('tashare', 'pdf'):
            copies = ''
            code = taw_dialog.OK
            while not copies.isdigit() and code == taw_dialog.OK:
                code, copies = taw_dialog.inputbox('Print how many copies of ' +
                                                   pdf + '?')
            if code == taw_dialog.OK and int(copies) > 0:
                print_pdf(pdf, copies, taw_dialog)
        for iso in detect_file_type('tashare', 'iso'):
            code = taw_dialog.yesno('Burn optical disks from ' + iso + '?')
            if code == taw_dialog.OK:
                burn_iso(iso, taw_dialog)
    finally:
        pass
