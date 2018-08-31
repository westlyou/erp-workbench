UPDATE_SCRIPT_TEMPLATE = """#!/bin/bash
# create a link, do not bail out if it exists
(ln -s %(upgrade_folder)s migrations)
# install the openlib
(cd migrations/openupgradelib; ./setup.py install)
# now do the upgrade
%(upgrade_line)s
echo 'all well ..............'
"""