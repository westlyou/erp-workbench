#!/bin/sh
exec gosu nobody:1 odoo -u all  --stop-after-init