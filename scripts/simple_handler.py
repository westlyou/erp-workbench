#!bin/python
# -*- encoding: utf-8 -*-
import warnings
import sys
import os
import logging
from pprint import pprint
import os
import subprocess
import tempfile
import shutil
import re
from contextlib import contextmanager
import argparse


# ODOO_CMD : command to start odoo with
# ODOO_PATH: path to ODOO_CMD
# ODOO_CFG : 'openerp_cfg'
# CFG_PATH : path to the configuration 
# odoo will be called executing
# ODOO_PATH/ODOO_CMD -c ODOO_CFG/CFG_PATH * params
ODOO_CMD  = 'odoorunner.py'
ODOO_PATH = '/home/robert/projects/afbschweiz/afbschweiz/bin'
ODOO_CFG  = 'openerp.cfg'
CFG_PATH  =  '/home/robert/projects/afbschweiz/afbschweiz/etc2'
ODOO_START_DIR = '/home/robert/projects/afbschweiz/afbschweiz'
DB_USER = 'robert'
BASE_ADDONS_PATH = '/home/robert/projects/afbschweiz/afbschweiz/parts/odoo/addons'
ADDONS_PATH = '/home/robert/addons'
DATA_DIR = '/home/robert/odoo_projects_data/afbschweiz'
ODOO_ADMIN_PW = 'admin'
DB_PASSWORD = 'odoo'

# path to the site description
SITE_DESCRIPTION = '/home/robert/erp_workbench/sites_list/sites_global/afbs.py'

# SERVER_CONFIG is near the end of the file !!
class bcolors:
    """
    """
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
# ----------------------------------
# find_addon_names
# find the names of an addon
# @addon        : addon to find out names
# an addon can have more than one name when more than one addon has to be
# installed from a folder of addons
# return: list of names
# ----------------------------------
def find_addon_names(addon):
    name = ''
    names = []
    a = addon
    if 'names' in a:
        names = a['names']
    elif 'name' in a:
        name = a['name']
    elif 'group' in a:
        name = a['group']
    elif 'add_path' in a:
        name = a['add_path']
    names = names + [name]
    return [n.strip() for n in names if n]
  
VCS_MSG = """
%supdating %%s from %%s%s
""" % (bcolors.WARNING, bcolors.ENDC)
  
    
class Handler(object):
    def __init__(self, opts):
        # make sure the confi folder exists
        for p_elem in [ADDONS_PATH, CFG_PATH]:
            if not os.path.exists(p_elem):
                parts = []
                for p1 in p_elem.split('/'):
                    if not p1:
                        continue
                    parts.append(p1)
                    pp = '/' + '/'.join(parts)
                    if not os.path.exists(pp):
                        os.makedirs(pp)                   
                    
        # read the site descrition
        if not os.path.exists(SITE_DESCRIPTION):
            print(bcolors.FAIL + '*' * 80)
            print(SITE_DESCRIPTION + 'not accessible' + bcolors.ENDC)
        sd = open(SITE_DESCRIPTION, 'r').read()
        pos = sd.find('{')
        try:
            site_description = eval(sd[pos:])
        except Exception as e:
            print(bcolors.FAIL + '*' * 80)
            print(str(e))
            print('*' * 80 + bcolors.ENDC)
        self.site_name, self.site_description = list(site_description.items())[0]
        self.opts = opts
        
    # ----------------------------------
    # collect_addon_paths
    # go trough the addons in syte.py and collect
    # addon_path info for the actual site. This info
    # is stored in default_values
    def collect_addon_paths(self):
        """
        go trough the addons in syte.py and collect
        addon_path info for the actual site. This info
        return: string with addon path
        """
        addons = self.site_description.get('addons', [])
        base_path = ADDONS_PATH
        apps = []
        for addon in addons:
            if addon.get('add_path'):
                apps.append('%s/%s' % (base_path, addon['add_path']))
    
        return ',' + ','.join(apps)
    
        
    def create_server_config(self):
        """
        create server config file in $odoo_server_data_path$/SITENAME/openerp.conf
        """
        opts = self.opts
        name = self.site_name
        odoo_admin_pw = self.site_description.get('odoo_admin_pw', 'admin')
        addon_paths = self.collect_addon_paths()
        # now copy a template openerp-server.conf
        # since this is a stripped dow version of the real thing, we have to construct
        # a dictionary with all the values
        valDic = {
            'add_path' : addon_paths,
            'db_name' : self.site_name,
            'odoo_admin_pw' : odoo_admin_pw,
            'db_user' : DB_USER,
            'base_addons_path' : BASE_ADDONS_PATH,
            'data_dir' : DATA_DIR,
            'odoo_admin_pw' : ODOO_ADMIN_PW,
            'db_password' : DB_PASSWORD,            
        }
        config_file = SERVER_CONFIG % valDic
        if os.path.exists(CFG_PATH):
            open('%s/%s' % (CFG_PATH, ODOO_CFG), 'w').write(config_file)
        else:
            # should never happen
            print(bcolors.FAIL + 'ERROR: folder %s does not exist' %  CFG_PATH + bcolors.ENDC)
    
    def checkout_sa(self):
        """
        get addons from repository
        @opts   : options as entered by the user
        """
        result = {'failed' : [], 'need_relaod' : []}
        site_addons = []
        site_addons = self.site_description.get('addons', [])
        skip_list   = self.site_description.get('skip', {}).get('addons', [])
        dev_list = []
        #dev_list = _s.get('develop')
        #if dev_list:
            #dev_list = dev_list.get('addons')    
        done = []
        # whether we want to override branches
        #use_branch = opts.use_branch
        
        # restrict list of modules to update 
        only_these_modules = []
        #if opts.module_update:
            #only_these_modules = opts.module_update.split(',')
            
        # if we want to use a branch
        #ubDic = {}
        #if use_branch:
            #for binfo in use_branch.split(','):
                #if binfo:
                    #bl = binfo.split(':')
                    #if len(bl) == 2:
                        #ubDic[bl[0]] = bl[1]
            
        for site_addon in site_addons:
            names = find_addon_names(site_addon)
            
            for name in names:
                if name and name in skip_list:
                    continue
                if only_these_modules:
                    if name and name not in only_these_modules:
                        continue                
                if site_addon:
                    url = site_addon['url']
                    if url in done:
                        # we do not want to chekout things twice
                        # when more than one addon is installed from a folder
                        continue
                    #Updating bae3b03..4bc383f
                    # if the addon is in the project folders addon_path, we assume it is under developement,
                    # and we do not download it
                    target = os.path.normpath(ADDONS_PATH)
                    branch = site_addon.get('branch', 'master')
                    #branch = 'master' #ubDic.get(name, site_addon.get('branch', 'master'))
                    if 'group' in site_addon:
                        target = '%s/%s' % (target, site_addon['group'])
                    target = os.path.normpath(target)
                    if not dev_list or name in dev_list:
                        #if os.path.exists(temp_target % name):
                            #print VCS_MSG_DEVELOP % (name, target)
                        #else:
                            print(VCS_MSG % (name, target))
                            print((target, url))
                            try:
                                if site_addon.get('type') == 'git':
                                    gr = GitRepo(target, url)
                                    gr(branch)
                                #if site_addon.get('type') == 'svn':
                                    #sv = SvnCheckout(target, url)
                                    #sv(branch)
                            except UpdateError as e:
                                result['failed'].append(target)
                                print(VCS_ERROR % target)
                                print(bcolors.WARNING)
                                print(str(e))
                                print(bcolors.ENDC)
                                print(VCS_ERROR_END)
                    done.append(url)
        return result

    def construct_config(self):
        """
        construct config file in the 
        """
        self.create_server_config()
        
    def update(self):
        result = self.checkout_sa()
        if not os.path.exists('%s/%s' % (CFG_PATH,ODOO_CFG)) or self.opts.force:
            self.construct_config()
        print(result)
        
        
def main(opts):
    handler = Handler(opts)
    if opts.update:
        handler.construct_config()
        return
    if opts.force:
        handler.construct_config()
    print('cd %s;%s/%s -c %s/%s' % (ODOO_START_DIR, ODOO_PATH, ODOO_CMD, CFG_PATH, ODOO_CFG))
    
# ----------------------------------------------------------------------------------------------
# git stuff
# ----------------------------------------------------------------------------------------------

SUBPROCESS_ENV = os.environ.copy()
SUBPROCESS_ENV['PYTHONPATH'] = SUBPROCESS_ENV.pop(
    'BUILDOUT_ORIGINAL_PYTHONPATH', '')

logger = logging.getLogger(__name__)


class UpdateError(subprocess.CalledProcessError):
    """Specific class for errors occurring during updates of existing repos.
    """


class CloneError(subprocess.CalledProcessError):
    """Class to easily signal errors in initial cloning.
    """


def wrap_check_call(exc_cls, call_fn):

    def wrapped_check_call(*args, **kwargs):
        """Variant on subprocess.check_* that raises %s.""" % exc_cls
        try:
            return call_fn(*args, **kwargs)
        except subprocess.CalledProcessError as e:
            up_exc = exc_cls(e.returncode, e.cmd)
            output = getattr(e, 'output', None)
            if output is not None:
                up_exc.output = output
            raise up_exc

    return wrapped_check_call


class BaseRepo(object):
    """The common interface that all repository classes implement.

    :param target_dir: the local directory which will serve as a working tree
    :param offline: if ``True``, the repository instance will perform no
                    network operation, and will fail instead if a non
                    available revision is required.
    :param clear_locks: Some VCS systems can leave locks after some failures
                        and provide a separate way to break them. If ``True``,
                        the repo
                        will break any locks prior to operations (mostly useful
                        for automated agents, such as CI robots)
    :param clear_retry: if ``True`` failed updates by calling the instance are
                        cleared (see :meth:`clear_target`) and retried once.
                        This is intended for brittle VCSes from CI robots.

    Other options depend on the concrete repository class.

    Repository instances are **callable**. For each of them::

        repo(rev)

    will take all the steps necessary so that its local directory is a clone of
    the remote source, at the specified revision. If needed and possible
    The revision format depends on the
    concrete class, but it is passed as a :class:`str`.
    """

    def __init__(self, target_dir, url, clear_retry=False,
                 offline=False, clear_locks=False, **options):

        self.target_dir = target_dir
        self.url = isinstance(url, str) and url.strip() or url
        self.clear_retry = clear_retry
        self.offline = offline
        self.clear_locks = clear_locks

        # additional options that may depend on the VCS subclass
        self.options = options

    def clear_target(self):
        """Entirely remove the target directory."""
        shutil.rmtree(self.target_dir)

    def clean(self):
        """Remove unwanted untracked files.

        This default implementation removes Python object files and
        (resulting) empty directories.
        Subclasses are supposed to implement better vcs-specific behaviours.
        It is important for release-related options that this cleaning does not
        appear as a local modification.
        """
        utils.clean_object_files(self.target_dir)

    def revert(self, revision):
        """Revert any local changes, including pending merges."""
        raise NotImplementedError

    def __call__(self, revision):
        """Create if needed from remote source, and put it at wanted revision.
        """
        if self.options.get('clean'):
            self.clean()

        try:
            self.get_update(revision)
        except UpdateError:
            if self.offline or not self.clear_retry:
                raise
            logger.warn("Update of %s failed, removing and re-cloning "
                        "according to the clear-retry option. ", self)
            self.clear_target()
            self.get_update(revision)
        return self  # nicer in particular for tests

    def get_update(self, revision):
        """Make it so that the target directory is at the prescribed revision.

        The target directory need not to be initialized: this method will
        "clone" it from the remote source (whatever that means in the
        considered VCS).

        This method can fail under various circumstances, for instance if the
        wanted revision does not exist locally and offline mode has been
        selected.

        :raises CloneError: if initial cloning fails
        :raises UpdateError: if update of existing repository fails

        Must be implemented in concrete subclasses
        """
        raise NotImplementedError

    def __str__(self):
        return "%s at %r (remote=%r)" % (
            self.__class__.__name__, self.target_dir, self.url)

    @classmethod
    def is_versioned(cls, path):
        """True if path exists and is versioned under this vcs.

        Common implementation based on vcs_control_dir class attribute.
        """
        return os.path.exists(os.path.join(path, cls.vcs_control_dir))

    def uncommitted_changes(self):
        """True if we have uncommitted changes.

        Must be implemented by concrete subclasses
        """
        raise NotImplementedError

    def is_local_fixed_revision(self, revspec):
        """True if revspec is a locally available fixed revision.

        The concept of a fixed revision depends on the concrete VCS in use.
        It means that retrieving revspec at any point in the future

        1. is guaranteed to work
        2. always yields the same result

        In practice, for most VCSes, these cannot be totally guaranteed, but
        each VCS defines those cases whose breaking is considered to be a
        very bad practice.

        In Mercurial, removing a commit from a public repository is possible,
        but very bad.
        In Git, removing a commit from a public repository is normal workflow,
        but removing a tag is very bad.

        The name stresses that only locally available ones will be recognized
        due to the promise that this method does not query any remote repo.
        """
        raise NotImplementedError

    def parents(self, pip_compatible=False):
        """Return universal identifier for parent nodes, aka current revisions.

        There might be more than one with some VCSes (ex: pending merge in hg).

        :param pip_compatible: if ``True``, only `pip compatible
                               <http://pip.readthedocs.org/en/latest/
                               reference/pip_install.html#vcs-support>`_
                               revision specifications are returned, depending
                               on the VCS type.
        """
        raise NotImplementedError

    def archive(self, target_path):
        raise NotImplementedError
    import subprocess
    
class UserError(Exception):
    """Errors made by a user
    """

    def __str__(self):
        return " ".join(map(str, self.args))

class UpdateError(subprocess.CalledProcessError):
    """Specific class for errors occurring during updates of existing repos.
    """


class CloneError(subprocess.CalledProcessError):
    """Class to easily signal errors in initial cloning.
    """

logger = logging.getLogger(__name__)


MAJOR_VERSION_RE = re.compile(r'(\d+)[.](saas~|)(\d*)(\w*)')


class WorkingDirectoryKeeper(object):
    """A context manager to get back the working directory as it was before.

    If you want to stack working directory keepers, you need a new instance
    for each stage.
    """

    active = False

    def __enter__(self):
        if self.active:
            raise RuntimeError("Already in a working directory keeper !")
        self.wd = os.getcwd()
        self.active = True

    def __exit__(self, *exc_args):
        os.chdir(self.wd)
        self.active = False
    
working_directory_keeper = WorkingDirectoryKeeper()


@contextmanager
def use_or_open(provided, path, *open_args):
    """A context manager to use an open file if not None or open one.

    Useful for code that should be unit-testable, but work on a default file if
    None is passed.
    """
    if provided is not None:
        yield provided
    else:
        with open(path, *open_args) as f:
            yield f


def major_version(version_string):
    """The least common denominator of OpenERP versions : two numbers.

    OpenERP version numbers are a bit hard to compare if we consider nightly
    releases, bzr versions etc. It's almost impossible to compare them without
    an a priori knowledge of release dates and revisions.

    Here are some examples::

       >>> major_version('1.2.3-foo.bar')
       (1, 2)
       >>> major_version('6.1-20121003-233130')
       (6, 1)
       >>> major_version('7.0alpha')
       (7, 0)

    Beware, the packaging script does funny things, such as labeling current
    nightlies as 6.2-date-time whereas version_info is (7, 0, 0, ALPHA)
    We can in recipe code check for >= (6, 2), that's not a big issue.

    Regarding OpenERP saas releases (e.g. 7.saas~1) that are short-lived stable
    versions between two "X.0" LTS releases, the 'saas~' argument before the
    minor version number is stripped. For instance::

       >>> major_version('7.saas~3')
       (7, 3)

    """

    m = MAJOR_VERSION_RE.match(version_string)

    if m is None:
        raise ValueError("Unparseable version string: %r" % version_string)

    major = int(m.group(1))
    minor = m.group(3)

    try:
        return major, int(minor)
    except TypeError:
        raise ValueError(
            "Unrecognized second version segment in %r" % version_string)


def is_object_file(filename):
    """True if given filename is a python object file."""
    return filename.endswith('.pyc') or filename.endswith('.pyo')


def clean_object_files(directory):
    """Recursively remove object files in given directory.

    Also remove resulting empty directories.
    """
    dirs_to_remove = []
    for dirpath, dirnames, filenames in os.walk(directory, topdown=False):
        to_delete = [os.path.join(dirpath, f)
                     for f in filenames if is_object_file(f)]
        if not dirnames and len(to_delete) == len(filenames):
            dirs_to_remove.append(dirpath)
        for p in to_delete:
            try:
                os.unlink(p)
            except:
                logger.exception("Error attempting to unlink %r. "
                                 "Proceeding anyway.", p)
    for d in dirs_to_remove:
        try:
            os.rmdir(d)
        except:
            logger.exception("Error attempting to rmdir %r",
                             "Proceeding anyway.", p)


def check_output(*popenargs, **kwargs):
    r"""Backport of subprocess.check_output from python 2.7.

    Example (this doctest would be more readable with ELLIPSIS, but
    that's good enough for today):

    >>> out = check_output(["ls", "-l", "/dev/null"])
    >>> out.startswith('crw-rw-rw')
    True

    The stdout argument is not allowed as it is used internally.
    To capture standard error in the result, use stderr=STDOUT.

    >>> os.environ['LANG'] = 'C'  # for uniformity of error msg
    >>> err = check_output(["/bin/sh", "-c",
    ...               "ls -l non_existent_file ; exit 0"],
    ...              stderr=subprocess.STDOUT)
    >>> err.strip().endswith("No such file or directory")
    True
    """

    if sys.version >= (2, 7):
        return subprocess.check_output(*popenargs, **kwargs)
    if 'stdout' in kwargs:
        raise ValueError('stdout argument not allowed, it will be overridden.')

    process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
    output, unused_err = process.communicate()
    retcode = process.poll()
    if retcode:
        cmd = kwargs.get("args")
        if cmd is None:
            cmd = popenargs[0]
        # in python 2.6, CalledProcessError.__init__ does not have output kwarg
        exc = subprocess.CalledProcessError(retcode, cmd)
        exc.output = output
        print('*' * 80)
        print(os.getcwd())
        raise exc
    return output

INLINE_COMMENT_REGEXP = re.compile(r'\s;|^;')


def option_splitlines(opt_val):
    r"""Split a multiline option value.

    This function performs stripping of whitespaces and allows comments as
    `ConfigParser <http://docs.python.org/2/library/configparser.html>`_ would
    do. Namely:

    * a line starting with a hash is a comment. This is already taken care of
      by ``zc.buildout`` parsing of the configuration file.

      :mod:`ConfigParser` does not apply this rule to the case where the hash
      is after some leading whitespace (e.g, line-continuation
      indentation) as in this example::

          [foo]
          bar = line1
            line2
          # this is a comment
            # this is not a comment, and will appear in 'bar' value

      Therefore this function does not have to perform anything with respect to
      hash-comments.

    * everything after a semicolon following a whitespace is a comment::

          [foo]
          bar = line1
                line2 ;this is a comment

    :param basestring opt_val: the raw option value
    :returns: tuple of strings

    doctests (less readable than examples above, but more authoritative)::

        >>> option_splitlines('line1\n  line2 ;this is a comment\n  line3')
        ('line1', 'line2', 'line3')
        >>> option_splitlines('l1\n; inline comment from beginning\n  line3')
        ('l1', 'line3')
        >>> option_splitlines('l1\n; inline comment from beginning\n  line3')
        ('l1', 'line3')
        >>> option_splitlines('l1\n  ; disappears after stripping \n  line3')
        ('l1', 'line3')
        >>> option_splitlines('line1\n\n')
        ('line1',)
        >>> option_splitlines('')
        ()

    The return value is guaranteed not to be a single string::

        >>> option_splitlines('single')
        ('single',)

    For convenience, ``None`` is accepted::

        >>> option_splitlines(None)
        ()

    """
    if opt_val is None:
        return ()

    lines = opt_val.splitlines()
    return tuple(l for l in (option_strip(line) for line in lines)
                 if l)


def option_strip(opt_val):
    """Same as :func:`option_splitlines` for a single line.

    >>> option_strip("   hey, we have ; a comment")
    'hey, we have'
    >>> option_strip(None) is None
    True
    """
    if opt_val is not None:
        return INLINE_COMMENT_REGEXP.split(opt_val, 1)[0].strip()


def total_seconds(td):
    """Uniformity backport of :meth:`datetime.timedelta.total_seconds``

    :param td: a :class:`datetime.timedelta` instance
    :returns: the number of seconds in ``tdelta``

    The implementation for Python < 2.7 is taken from the
    `standard library documentation
    <https://docs.python.org/2.7/library/datetime.html>`_
    """
    if sys.version_info >= (2, 7):
        return td.total_seconds()

    return ((td.microseconds +
             (td.seconds + td.days * 24 * 3600) * 1e6) / 10**6)

logger = logging.getLogger(__name__)

BUILDOUT_ORIGIN = 'origin'


def ishex(s):
    """True iff given string is a valid hexadecimal number.

    >>> ishex('deadbeef')
    True
    >>> ishex('01bn78')
    False
    """
    try:
        int(s, 16)
    except ValueError:
        return False
    return True


class GitRepo(BaseRepo):
    """Represent a Git clone tied to a reference branch/commit/tag."""

    vcs_control_dir = '.git'

    vcs_official_name = 'Git'

    _git_version = None

    def __init__(self, *args, **kwargs):
        super(GitRepo, self).__init__(*args, **kwargs)
        depth = self.options.pop('depth', None)
        if depth is not None and depth != 'None':
            # 'None' as a str can be used as an explicit per-repo override
            # of a global setting
            invalid = UserError("Invalid depth value %r for Git repository "
                                "at %r" % (depth, self.target_dir))
            try:
                depth = int(depth)
            except ValueError:
                raise invalid
            if depth <= 0:
                raise invalid
            self.options['depth'] = depth

    @property
    def git_version(self):
        cls = self.__class__
        version = cls._git_version
        if version is not None:
            return version

        return cls.init_git_version(utils.check_output(
            ['git', '--version']))

    @classmethod
    def init_git_version(cls, v_str):
        r"""Parse git version string and store the resulting tuple on self.

        :returns: the parsed version tuple

        Only the first 3 digits are kept. This is good enough for the few
        version dependent cases we need, and coarse enough to avoid
        more complicated parsing.

        Some real-life examples::

          >>> GitRepo.init_git_version('git version 1.8.5.3')
          (1, 8, 5)
          >>> GitRepo.init_git_version('git version 1.7.2.5')
          (1, 7, 2)

        Seen on MacOSX (not on MacPorts)::

          >>> GitRepo.init_git_version('git version 1.8.5.2 (Apple Git-48)')
          (1, 8, 5)

        Seen on Windows (Tortoise Git)::

          >>> GitRepo.init_git_version('git version 1.8.4.msysgit.0')
          (1, 8, 4)

        A compiled version::

          >>> GitRepo.init_git_version('git version 2.0.3.2.g996b0fd')
          (2, 0, 3)

        Rewrapped by `hub <https://hub.github.com/>`_, it has two lines:

          >>> GitRepo.init_git_version('git version 1.7.9\nhub version 1.11.0')
          (1, 7, 9)

        This one does not exist, allowing us to prove that this method
        actually governs the :attr:`git_version` property

          >>> GitRepo.init_git_version('git version 0.0.666')
          (0, 0, 666)
          >>> GitRepo('', '').git_version
          (0, 0, 666)

        Expected exceptions::

          >>> try: GitRepo.init_git_version('invalid')
          ... except ValueError: pass

        After playing with it, we must reset it so that tests can run with
        the proper detected one, if needed::

          >>> GitRepo.init_git_version(None)

        """
        if v_str is None:
            cls._git_version = None
            return

        v_str = v_str.strip()
        try:
            version = cls._git_version = tuple(
                int(x) for x in v_str.split()[2].split('.')[:3])
        except:
            raise ValueError("Could not parse git version output %r. Please "
                             "report this" % v_str)
        return version

    def log_call(self, cmd, callwith=subprocess.check_call,
                 log_level=logging.INFO, **kw):
            """Wrap a subprocess call with logging

            :param meth: the calling method to use.
            """
            logger.log(log_level, "%s> call %r", self.target_dir, cmd)
            return callwith(cmd, **kw)

    def clean(self):
        if not os.path.isdir(self.target_dir):
            return
        with working_directory_keeper:
            os.chdir(self.target_dir)
            subprocess.check_call(['git', 'clean', '-fdqx'])

    def parents(self, pip_compatible=False):
        """Return full hash of parent nodes.

        :param pip_compatible: ignored, all Git revspecs are pip compatible
        """
        with working_directory_keeper:
            os.chdir(self.target_dir)
            p = subprocess.Popen(['git', 'rev-parse', '--verify', 'HEAD'],
                                 stdout=subprocess.PIPE, env=SUBPROCESS_ENV)
            return p.communicate()[0].split()

    def uncommitted_changes(self):
        """True if we have uncommitted changes."""
        with working_directory_keeper:
            os.chdir(self.target_dir)
            p = subprocess.Popen(['git', 'status', '--short'],
                                 stdout=subprocess.PIPE, env=SUBPROCESS_ENV)
            out = p.communicate()[0]
            return bool(out.strip())

    def get_current_remote_fetch(self):
        with working_directory_keeper:
            os.chdir(self.target_dir)
            for line in self.log_call(['git', 'remote', '-v'],
                                      callwith=check_output).splitlines():
                if (line.endswith('(fetch)')
                        and line.startswith(BUILDOUT_ORIGIN)):
                    return line[len(BUILDOUT_ORIGIN):-7].strip()

    def offline_update(self, revision):
        target_dir = self.target_dir

        # TODO what if remote repo is actually local fs ?
        # GR, redux: git has a two notions of local repos, which
        # differ at least for shallow clones : path or file://
        if not os.path.exists(target_dir):
            # TODO case of local url ?
            raise UserError("git repository %s does not exist; cannot clone "
                            "it from %s (offline mode)" % (target_dir,
                                                           self.url))

        current_url = self.get_current_remote_fetch()
        if current_url != self.url:
            raise UserError("Existing Git repository at %r fetches from %r "
                            "which is different from the specified %r. "
                            "Cannot update adresses in offline mode." % (
                                self.target_dir, current_url, self.url))
        self.log_call(['git', 'checkout', revision],
                      callwith=update_check_call,
                      cwd=self.target_dir)

    def is_local_fixed_revision(self, refspec):
        """In Git, tags only are reproductible refspec."""
        tags = (t.strip()
                for t in self.log_call(['git', 'tag'],
                                       callwith=check_output,
                                       cwd=self.target_dir).splitlines())
        return refspec in tags

    def has_commit(self, sha):
        """Return true if repo has specified commit"""
        try:
            objtype = check_output(['git', 'cat-file', '-t', sha],
                                   cwd=self.target_dir,
                                   stderr=subprocess.PIPE).strip()
        except subprocess.CalledProcessError:
            return False

        return objtype == 'commit'

    def fetch_remote_sha(self, sha):
        """Fetch a precise SHA from remote if necessary.

        SHA pinning is suboptimal, can't be guaranteed to work (see the
        warnings emitted in code for explanations). Still, many users
        people depend on it, for not having enough privileges to add tags.
        """
        logger.warn("%s: pointing to a remote commit directly by its SHA "
                    "is unsafe because it can become unreachable "
                    "due to history rewrites (squash, rebase) in the remote "
                    "branch. "
                    "Please consider using tags if you can.", self.target_dir)
        branch = self.options.get('branch')
        if not self.has_commit(sha):
            fetch_cmd = ['git', 'fetch', BUILDOUT_ORIGIN]
            if branch is None:
                logger.info("%s: SHA pinning without remote "
                            "branch indication. "
                            "Now performing a fetch with no argument, hoping "
                            "it'll retrieve the commit %r. Please consider "
                            "adding a branch indication for more efficiency "
                            "and possibly reliability.", self.target_dir, sha)
            else:
                fetch_cmd.append(branch)
            self.log_call(fetch_cmd, callwith=update_check_call)

        self.log_call(['git', 'checkout', sha])

    def query_remote_ref(self, remote, ref):
        """Query remote repo about given ref.

        :return: ``('tag', sha)`` if ref is a tag in remote
                 ``('branch', sha)`` if ref is branch (aka "head") in remote
                 ``(None, ref)`` if ref does not exist in remote. This happens
                 notably if ref if a commit sha (they can't be queried)
        """
        out = self.log_call(['git', 'ls-remote', remote, ref],
                            cwd=self.target_dir,
                            callwith=check_output).strip()
        for sha, fullref in (l.split() for l in out.splitlines()):
            if fullref == 'refs/heads/' + ref:
                return 'branch', sha
            elif fullref == 'refs/tags/' + ref:
                return 'tag', sha
            elif fullref == ref and ref == 'HEAD':
                return 'HEAD', sha
        return None, ref

    dangerous_revisions = ('FETCH_HEAD', 'ORIG_HEAD', 'MERGE_HEAD',
                           'CHERRY_PICK_HEAD', 'REVERT_HEAD')

    def get_update(self, revision):
        """Make it so that the target directory is at the prescribed revision.

        Special case: if the 'merge' option is True,
        merge revision into current branch.
        """
        if revision in self.dangerous_revisions:
            logger.warn("%s> use of %r as revision in the recipe may "
                        "interfere with the Git subcommands issued "
                        "by the recipe in unspecified ways. It is in "
                        "particular not guaranteed to provide "
                        "consistent results on subsequent runs, new versions "
                        "of the recipe etc. "
                        "You should use them for exceptional and "
                        "timebound operations only, backed "
                        "with good knowledge of the recipe internals. "
                        "If you get a related error below, that won't be "
                        "a recipe bug.",
                        self.target_dir, revision)

        if self.options.get('merge'):
            return self.merge(revision)

        if self.offline:
            return self.offline_update(revision)

        target_dir = self.target_dir
        url = self.url

        with working_directory_keeper:
            is_new = not os.path.exists(target_dir)
            if is_new:
                self.log_call(['git', 'init', target_dir])

            os.chdir(target_dir)
            self.log_call(['git', 'remote', 'add' if is_new else 'set-url',
                           BUILDOUT_ORIGIN, url],
                          log_level=logging.DEBUG)

            rtype, sha = self.query_remote_ref(BUILDOUT_ORIGIN, revision)
            if rtype is None and ishex(revision):
                return self.fetch_remote_sha(revision)

            fetch_cmd = ['git', 'fetch']
            depth = self.options.get('depth')
            if depth is not None:
                fetch_cmd.extend(('--depth', str(depth)))
            if rtype == 'tag':
                fetch_refspec = '+refs/tags/%s:refs/tags/%s' % (revision,
                                                                revision)
            else:
                fetch_refspec = revision
            fetch_cmd.extend((BUILDOUT_ORIGIN, fetch_refspec))
            self.log_call(fetch_cmd, callwith=update_check_call)

            if rtype == 'tag':
                self.log_call(['git', 'checkout', revision])
            elif rtype in ('branch', 'HEAD'):
                self.update_fetched_branch(revision)
            else:
                raise NotImplementedError(
                    "Unknown remote reference type %r" % rtype)

    def update_fetched_branch(self, branch):
        # TODO: check what happens when there are local changes
        # TODO: what about the 'clean' option
        # setup remote tracking branch, in all cases
        # it's necessary with Git 1.7.10, not with 1.9.3 and shoud not
        # harm
        self.log_call(['git', 'update-ref', '/'.join((
            'refs', 'remotes', BUILDOUT_ORIGIN, branch)), 'FETCH_HEAD'])
        if self.options.get('depth') or branch == 'HEAD':
            # doing it the other way does not work, at least
            # not on Git 1.7
            self.log_call(['git', 'checkout', 'FETCH_HEAD'],
                          callwith=update_check_call)
            if branch != 'HEAD':
                self.log_call(['git', 'branch', '-f', branch],
                              callwith=update_check_call)
            return

        if not self._is_a_branch(branch):
            self.log_call(['git', 'checkout', '-b', branch, 'FETCH_HEAD'])
        else:
            # switch, then fast-forward
            self.log_call(['git', 'checkout', branch])
            try:
                self.log_call(['git', 'merge', '--ff-only', 'FETCH_HEAD'],
                              callwith=update_check_call)
            except UpdateError:
                if not self.clear_retry:
                    raise
                else:
                    # users are willing to wipe the entire repo
                    # to get this update done ! Let's try something less
                    # harsh first that works if previous latest commit
                    # is not an ancestor of remote latest
                    # note: fetch has already been done
                    logger.warn("Fast-forward merge failed for "
                                "repo %s, "
                                "but clear-retry option is active: "
                                "trying a reset in case that's a "
                                "simple fast-forward issue.", self)
                    self.log_call(['git', 'reset', '--hard', 'FETCH_HEAD'],
                                  callwith=update_check_call)

    def merge(self, revision):
        """Merge revision into current branch"""
        with working_directory_keeper:
            if not self.is_versioned(self.target_dir):
                raise RuntimeError("Cannot merge into non existent "
                                   "or non git local directory %s" %
                                   self.target_dir)
            os.chdir(self.target_dir)
            cmd = ['git', 'pull', self.url, revision]
            if self.git_version >= (1, 7, 8):
                # --edit and --no-edit appear with Git 1.7.8
                # see Documentation/RelNotes/1.7.8.txt of Git
                # (https://git.kernel.org/cgit/git/git.git/tree)
                cmd.insert(2, '--no-edit')

            self.log_call(cmd)

    def archive(self, target_path):
        # TODO: does this work with merge-ins?
        revision = self.parents()[0]
        if not os.path.exists(target_path):
            os.makedirs(target_path)
        with working_directory_keeper:
            os.chdir(self.target_dir)
            target_tar = tempfile.NamedTemporaryFile(
                prefix=os.path.split(self.target_dir)[1] + '.tar')
            target_tar.file.close()
            subprocess.check_call(['git', 'archive', revision,
                                   '-o', target_tar.name])
            subprocess.check_call(['tar', '-x', '-f', target_tar.name,
                                   '-C', target_path])
            os.unlink(target_tar.name)

    def revert(self, revision):
        with working_directory_keeper:
            os.chdir(self.target_dir)
            subprocess.check_call(['git', 'checkout', revision])
            if self._is_a_branch(revision):
                self.log_call(['git', 'reset', '--hard',
                              BUILDOUT_ORIGIN + '/' + revision],
                              callwith=update_check_call)
            else:
                self.log_call(['git', 'reset', '--hard', revision])

    def _is_a_branch(self, revision):
        # if this fails, we have a seriously corrupted repo
        branches = update_check_output(["git", "branch"])
        branches = branches.split()
        return revision in branches

update_check_call = wrap_check_call(UpdateError, subprocess.check_call)
clone_check_call = wrap_check_call(CloneError, subprocess.check_call)
update_check_output = wrap_check_call(UpdateError, check_output)
clone_check_output = wrap_check_call(CloneError, check_output)
    
# ----------------------------------------------------------------------------------------------
# end git stuff
# ----------------------------------------------------------------------------------------------

SERVER_CONFIG = """[options]
addons_path = %(base_addons_path)s,%(add_path)s
without_demo = all
data_dir = %(data_dir)s
auto_reload = False
db_name = %(db_name)s
admin_passwd = %(odoo_admin_pw)s
db_user = %(db_user)s
db_password = %(db_password)s
dbfilter = %(db_name)s
listdb = False
db_maxconn = 64
limit_memory_soft = 2147483648
limit_memory_hard = 2684354560
limit_request = 8192
limit_time_cpu = 60
limit_time_real = 120
log_handler = ':INFO'
log_level = info
; log_db = False
max_cron_threads = 2
workers = 4
log_db = False
logrotate = True
syslog = False
"""


if __name__ == '__main__':
    usage = "simple_handler.py is a tool to create and maintain local odoo developement environment\n"
    
    parent_parser = argparse.ArgumentParser(usage=usage, add_help=False)
    parent_parser.add_argument(
        "-f", "--force",
        action="store_true", dest="force", default=False,
        help = 'force recreation of %s/%s' % (CFG_PATH, ODOO_CFG)
    )
    parent_parser.add_argument(
        "-u", "--update",
        action="store_true", dest="update", default=False,
        help = 'update all addons in %s/%s' % (CFG_PATH, ODOO_CFG)
    )

    opts = parent_parser.parse_args()
    main(opts)
