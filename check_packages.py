import os
import logging
import argparse
import subprocess
from glob import iglob

# setup a command line parser with options
parser = argparse.ArgumentParser(description='Searches all virtualenvs on a drive and checks for specific packages.')
parser.add_argument('-l', '--log_level', type=int, default=1, choices=range(0, 4), metavar="[0-3]",
                    help='Level of messages to log (0 = error, 1 = warning, 2 = info, 3 = debug) (warning default).')
parser.add_argument('-d', '--drive', action='append', default=[], metavar="[A-Z]",
                    help='Drive(s) to check. Repeat argument to check multiple drives. Defaults to just C:')
parser.add_argument('-p', '--package', action='append', default=[],
                    help='Additional package names to check. Repeat argument to check multiple. Prefix ! to negate.')
parser.add_argument('-pl', '--package_list', type=str, default='',
                    help='File containing nothing but a list of package names to check. (bar comments and empty lines)')
parser.add_argument('-pm', '--python_marker', type=str, default='Scripts/python.exe',
                    help='Contents of a folder identifying it as a virtualenv.')
args = parser.parse_args()

# setup logging
log_levels = {0: logging.ERROR, 1: logging.WARNING, 2: logging.INFO, 3: logging.DEBUG}
logger = logging.getLogger('check_packages')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(log_levels[args.log_level])
logger.addHandler(ch)
logger.debug('log_level : {log_level}'.format(log_level=args.log_level))

# list of drives to check, check C: by default
check_drives = args.drive
if not check_drives:
    check_drives = ['C']
logger.debug('check_drives : {c}'.format(c=check_drives))

# If a folder has this in it, it's likely a virtualenv
python_marker = args.python_marker
logger.debug('python_marker : {c}'.format(c=python_marker))

# default pip location in virtualenv
pip = 'Scripts/pip.exe'

# list of packages to find in any virtualenv
if args.package_list != '':
    if not os.path.isfile(args.package_list):
        logger.error('Package list not found: {p}'.format(p=args.package_list))
        exit(1)
    with open(args.package_list, 'r') as pl:
        check_packages = {line for line in pl.read().splitlines() if len(line.strip()) > 0 and line.strip()[0] != '#'}
else:
    # default list in case no list was provided
    # from http://www.nbu.gov.sk/skcsirt-sa-20170909-pypi/
    check_packages = {
        'acqusition',
        'apidev-coop',
        'bzip',
        'crypt',
        'django-server',
        'pwd',
        'setup-tools',
        'telnet',
        'urlib3',
        'urllib'
    }

# add individually specified packages or exceptions
for p in args.package:
    if p[0] == '!':
        if p[1:] in check_packages:
            check_packages.remove(p[1:])
        else:
            logger.warning('Trying to remove package from checklist, which is not on the list: {p}'.format(p=p))
    else:
        check_packages.add(p)
logger.debug('check_packages : {c}'.format(c=check_packages))

count_unable = 0
count_found = 0

for check_drive in check_drives:
    for python_path in iglob('{drive}:/**/{marker}'.format(drive=check_drive, marker=python_marker), recursive=True):
        ve_path = os.path.normpath(python_path[0:-len(python_marker)])
        pip_path = os.path.normpath(os.path.join(ve_path, pip))

        if not os.path.isfile(pip_path):
            count_unable += 1
            logger.warning('Cannot find {pip} in {path}, check manually!'.format(pip=pip, path=ve_path))
        else:
            logger.info('Running "pip freeze" in {v}'.format(v=ve_path))
            try:
                process = subprocess.run([pip_path, 'freeze'], stdout=subprocess.PIPE, cwd=ve_path)
                packages = process.stdout.decode('utf-8').splitlines()
                if process.returncode != 0:
                    count_unable += 1
                    logger.error('Error running "pip freeze" in {v}, returned {e}'.format(
                        v=ve_path, e=process.returncode))
            except Exception as e:
                count_unable += 1
                logger.error('Exception running "pip freeze" in {v}: {e}'.format(v=ve_path, e=e))

            for p in packages:
                logger.info('Package {p} in {v}'.format(p=p, v=ve_path))
            found = [p for p in packages if p.split('==')[0] in check_packages]
            if len(found) > 0:
                for p in found:
                    count_found += 1
                    logger.warning('Found package {p} in {v}'.format(p=p, v=ve_path))
            else:
                logger.info('None of check_packages found in {v}'.format(v=ve_path))

if count_found > 0:
    print('{n} packages matching the criteria were found.'.format(n=count_found))
else:
    print('No packages matching the criteria found.')
if count_unable > 0:
    print('In {n} locations, "pip freeze" could not be successfully executed.'.format(n=count_unable))
else:
    print('All found virtual environments checked.')
if count_found + count_unable > 0:
    exit(2)
