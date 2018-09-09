import yaml
from io import StringIO
from pprint import pformat
from scripts.bcolors import bcolors
import os

"""this module provides functionality to read and write yaml files
"""

def check_and_update_base_defaults(base_path, user_home, act_user, yaml_files, results={}):
    """resad a list of yaml files and construct python files that can be imported

    Arguments:
        base_path {string} -- path where erp-workbench is installed
        user_home {string} -- users home directory
        act_user {string} -- name of the sctual user
        yaml_files {list of tuples} -- tuples with (
            path to the yaml file, path to the datafile to be constructed)

    Keyword Arguments:
        results {dict} -- dictionary with the data loaded (default: {{}})

    Returns:
        boolean -- flag telling whether the data had to be constructed 
    """

    must_restart = False
    for yaml_data in yaml_files:
        # we have to construct a yaml file with its variable replaced
        yaml_file_path, data_file_path = yaml_data
        vals = {
            'USER_HOME' : user_home, 
            'BASE_PATH' : base_path,
            'ACT_USER'  : act_user,
        }
        if os.path.exists(yaml_file_path):
            # compare file dates
            # check if folder exists:
            if not os.path.exists(os.path.dirname(data_file_path)):
                print(bcolors.FAIL)
                print('*' * 80)
                print('folder %s does not exist' % os.path.dirname(data_file_path))
                print(bcolors.ENDC)
                raise ValueError
            if os.path.exists(data_file_path) and  \
                os.path.getmtime(data_file_path) >= os.path.getmtime(yaml_file_path):
                continue
            with open(yaml_file_path) as f:
                raw_yaml_data = f.read()
            # it can be hard to find an error when varibale are not well define
            # so check the content line by line
            counter = -1
            for line in raw_yaml_data.split('\n'):
                counter += 1
                if line.strip().startswith('#'):
                    continue
                try:
                    line % vals
                except Exception:
                    print(bcolors.FAIL)
                    print('*' * 80)
                    print('file %s' % yaml_file_path)
                    print('line %s: %s has a problem' % (counter, line))
                    print(bcolors.ENDC)
                    raise
            try:
                raw_yaml_data = raw_yaml_data % vals
                yaml_data = yaml.load(StringIO(raw_yaml_data))
                with open(data_file_path, 'w') as f:
                    f.write(pformat(yaml_data))
            except Exception as e:
                print(str(e))
            must_restart = True
            results[yaml_file_path] = yaml_data
        else:
            print(bcolors.WARNING)
            print('*' * 80)
            print('%s does not exist', yaml_file)
            print(bcolors.ENDC)
            continue

    return must_restart
    