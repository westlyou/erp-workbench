workon %(projectname)s
cd %(inner)s
git clone -b v%(erp_version)s  https://gitlab.com/flectra-hq/flectra.git
cd flectra
git checkout tags/v1.2.0
python setup.py install
cd %(inner)s
