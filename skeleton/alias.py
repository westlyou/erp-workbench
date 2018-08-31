import platform
import sys
import os
import time
from optparse import OptionParser
import re

ALIASESS = """%(marker)s
alias  %(urname)s="cd %(ur)s"
alias  %(urname)sa="cd %(ur)s/%(proname)s_addons"
alias  %(urname)shome="cd %(urhome)s"
"""
PROS = """# projects
alias  pro="cd %(prohome)s/%(prn)s" """

def cleanData(data):
    # remove superfluous newlines
    while data.find('\n\n\n') > -1:
        data = data.replace('\n\n\n', '\n\n')
    return data

def collect_aliases(alias_path, aDic):
    try:
        data = open(alias_path, 'r').read().split('\n')
    except:
        return
    running = ''
    pattern = r'# +(\w+)[ ]*$'
    apat = r'alias +(\w+)=.*'
    regex = re.compile(pattern)
    areg  = re.compile(apat)
    counter = 0
    for line in data:
        counter += 1
        if not line:
            continue
        m = regex.search(line)
        ma = areg.search(line)
        if m:
            running = m.groups()[0]
            counter = -1
        elif ma:
            if not running:
                continue
            add_str = ''
            if counter:
                add_str = str(counter)
            aDic[running + add_str] = ma.groups()[0]


def find_alias(aDic, candidate):
    keys = aDic.keys()
    keyr = aDic.values()
    if candidate in keys:
        return ''
    for i in range(len(candidate)-4):
        if not candidate[:4+i] in keyr:
            return candidate[:4+i]
    raise ValueError('could not construct alias')

def delete_alias(alias_path, candidate):
    try:
        data = open(alias_path, 'r').read().split('\n')
    except:
        return
    pattern = r'# +(\w+)[ ]*$'
    regex = re.compile(pattern)
    f = open(alias_path, 'w')
    started = False
    for line in data:
        if not line and started:
            started = False
            continue
        m = regex.search(line)
        if m:
            if m.groups()[0] == candidate:
                started = True
        if started:
            # skip line
            continue
        else:
            f.write('%s\n' % line.strip())
    f.close()

def main():
    usage = "alias.py -h for help on usage"
    parser = OptionParser(usage=usage)

    parser.add_option(
        "-n", "--name",
        action="store", dest="name", default='',
        help="name of the projects, default autodetected"
    )

    parser.add_option(
        "-p", "--projects",
        action="store", dest="projects", default='/projects',
        help="home of the projects, default /projects"
    )

    parser.add_option(
        "-f", "--fullpath",
        action="store", dest="fullpath", default='',
        help="full path to the project"
    )

    parser.add_option(
        "-F", "--force",
        action="store_true", dest="force", default=False,
        help="force overwrite of alias"
    )

    (opts, args) = parser.parse_args()

    projects = opts.projects
    prn = projects
    if prn.startswith('/'):
        prn = prn[1:]
    
    home = os.path.expanduser("~")
    #alias_script = "bash_aliases"

    # assuming we are running tis script in PROJECTNAME/PROJECTNAME
    if opts.fullpath:
        ur = opts.fullpath
    else:
        ur = os.path.realpath(__file__)
        ur = os.path.split(ur)[0]

    urhome = os.path.split(ur)[0]
    prohome = ur.split("/")
    if not opts.name:
        proname = prohome[-1]
    else:
        proname = opts.name
    MARKER = '# %s' % proname.strip()
    # go up the folder hierarchy and search the projects home
    i=0
    for item in prohome:
        if item == prn:
            prohome = "/".join(prohome[:i])
            print prohome
            break
        i += 1

    # where do we want to add our aliases?
    alias_script = "bash_aliases"
    try:
        dist = open("/etc/lsb-release").readline()
        dist = dist.split("=")
        print dist[1]
        if dist[1].strip("\n") == "LinuxMint":
            alias_script = "bashrc"
        elif dist[1].strip("\n") == "Ubuntu":
            alias_script = "bash_aliases"
    except:
        print 'could not determine linux distribution'
        pass
    
    alias_path = '%s/.%s' % (home, alias_script)
    if opts.force:
        delete_alias(alias_path, proname)
        
    try:
        data = open(alias_path, 'r').read()
    except:
        data = ''

    # get rid of superfluous newlines
    data = cleanData(data)
    aDict = {}
    collect_aliases(alias_path, aDict)
    PRO = PROS % {'prohome' : prohome, 'prn' : prn}
    alias_name = find_alias(aDict, proname)
    if not alias_name:
        return

    ALIASES = ALIASESS % {
        'home' : home,
        'marker' : MARKER,
        'projects' : platform.processor() == 'x86_64' and ('%s/' % prn) or '',
        'ur' : ur,
        'urname' : alias_name,
        'urhome' : urhome,
        'proname' : proname
    }

    newdata = ''
    started = False
    profound = False
    for line in data.split('\n'):
        if line.find('alias pro="') > -1:
            profound = True
        # if we find the marker for this project
        # we keep on reading till we find a newline
        if not started:
            if line.strip()== MARKER:
                started = True
            else:
                newdata += ('%s\n' % line)
        else:
            if not line:
                started = False
    newdata += ALIASES
    if not profound:
        newdata += PRO % {'prohome' : prohome}
    #print newdata
    f = open('%s/.%s' % (home, alias_script), 'w')
    f.write(newdata)
    f.close()

if __name__=='__main__':
    #import pudb;pu.db
    main()
