#########################################################################
""" wingdbstub.py -- Start debugging Python programs from outside of Wing

Copyright (c) 1999-2018, Archaeopteryx Software, Inc.  All rights reserved.

Written by Stephan R.A. Deibel and John P. Ehresman

Usage:
-----

This file is used to initiate debug in Python code without launching
that code from Wing.  To use it, edit the configuration values below,
start Wing and configure it to listen for outside debug connections,
and then add the following line to your code:

  import wingdbstub

Debugging will start immediately after this import statement is reached.

For details, see Debugging Externally Launched Code in the manual.

"""
#########################################################################

import sys
import os
if sys.version_info >= (3, 7):
  import importlib
else:
  import imp

#------------------------------------------------------------------------
# Required configuration values (some installers set this automatically)

# This should be the full path to your Wing installation.  On OS X, use 
# the full path of the Wing application bundle, for example 
# /Applications/WingIDE.app.  When set to None, the environment variable 
# WINGHOME is used instead.  
WINGHOME="/usr/lib/wingide6"

#------------------------------------------------------------------------
# Optional configuration values:  The named environment variables, if set, 
# will override these settings.

# Set this to 1 to disable all debugging; 0 to enable debugging
# (WINGDB_DISABLED environment variable)
kWingDebugDisabled = 0

# Host:port of the IDE within which to debug: As configured in the IDE
# with the Server Port preference
# (WINGDB_HOSTPORT environment variable)
kWingHostPort = 'localhost:50005'

# Port on which to listen for connection requests, so that the
# IDE can attach or reattach to the debug process after it has started.
# Set this to '-1' to disable listening for connection requests.
# This is only used when the debug process is not attached to
# an IDE or the IDE has dropped its connection. The configured
# port can optionally be added to the IDE's Common Attach Hosts
# preference. Note that a random port is used instead if the given 
# port is already in use.
# (WINGDB_ATTACHPORT environment variable)
kAttachPort = '50015'

# Set this to a filename to log verbose information about the debugger
# internals to a file.  If the file does not exist, it will be created
# as long as its enclosing directory exists and is writeable.  Use 
# "<stderr>" or "<stdout>" to write to stderr or stdout.  Note that 
# "<stderr>" may cause problems on Windows if the debug process is not 
# running in a console.
# (WINGDB_LOGFILE environment variable)
kLogFile = None

# Produce a tremendous amount of logging from the debugger internals.
# Do not set this unless instructed to do so by Wingware support.  It
# will slow the debugger to a crawl.
# (WINGDB_LOGVERYVERBOSE environment variable)
kLogVeryVerbose = 0

# Set this to 1 when debugging embedded scripts in an environment that
# creates and reuses a Python instance across multiple script invocations.  
# It turns off automatic detection of program quit so that the debug session
# can span multiple script invocations.  When this is turned on, you may
# need to call ProgramQuit() on the debugger object to shut down the
# debugger cleanly when your application exits or discards the Python
# instance.  If multiple Python instances are created in the same run,
# only the first one will be able to debug unless it terminates debug
# and the environment variable WINGDB_ACTIVE is unset before importing
# this module in the second or later Python instance.  See the Wing
# manual for details.
# (WINGDB_EMBEDDED environment variable)
kEmbedded = 0

# Path to search for the debug password file and the name of the file
# to use.  The password file contains a security token for all 
# connections to the IDE and must match the wingdebugpw file in the 
# User Settngs directory used by the IDE. '$<winguserprofile>' 
# is replaced by the User Settings directory for the user that
# is running the process.
# (WINGDB_PWFILEPATH environment variable)
kPWFilePath = [os.path.dirname(__file__), '$<winguserprofile>']
kPWFileName = 'wingdebugpw'

# Whether to exit when the debugger fails to run or to connect with the IDE
# By default, execution continues without debug or without connecting to
# the IDE.
# (WINGDB_EXITONFAILURE environment variable)
kExitOnFailure = 0

#------------------------------------------------------------------------
# Find Wing debugger installation location

if sys.hexversion >= 0x03000000:
  def has_key(o, key):
    return key in o
else:
  def has_key(o, key):
    return o.has_key(key)
    
# Check environment:  Must have WINGHOME defined if still == None
if WINGHOME == None:
  if has_key(os.environ, 'WINGHOME'):
    WINGHOME=os.environ['WINGHOME']
  else:
    msg = '\n'.join(["*******************************************************************", 
                     "Error: Could not find Wing installation!  You must set WINGHOME or edit", 
                     "wingdbstub.py where indicated to point it to the location where", 
                     "Wing is installed.\n"])
    sys.stderr.write(msg)
    raise ImportError(msg)

WINGHOME = os.path.expanduser(WINGHOME)
kPWFilePath.append(WINGHOME)

# The user settings dir where per-user settings & patches are located.  Will be
# set from environment if left as None
kUserSettingsDir = None
if kUserSettingsDir is None:
  kUserSettingsDir = os.environ.get('WINGDB_USERSETTINGS')
  
def _FindActualWingHome(winghome):
  """ Find the actual directory to use for winghome.  Needed on OS X
  where the .app directory is the preferred dir to use for WINGHOME and
  .app/Contents/MacOS is accepted for backward compatibility. """
  
  if sys.platform != 'darwin':
    return winghome
  
  app_dir = None
  if os.path.isdir(winghome):
    if winghome.endswith('/'):
      wo_slash = winghome[:-1]
    else:
      wo_slash = winghome
      
    if wo_slash.endswith('.app'):
      app_dir = wo_slash
    elif wo_slash.endswith('.app/Contents/MacOS'):
      app_dir = wo_slash[:-len('/Contents/MacOS')]
    
  if app_dir and os.path.isdir(os.path.join(app_dir, 'Contents', 'Resources')):
    return os.path.join(app_dir, 'Contents', 'Resources')
  
  return winghome
  
def _ImportWingdb(winghome, user_settings=None):
  """ Find & import wingdb module. """
  
  try:
    exec_dict = {}
    execfile(os.path.join(winghome, 'bin', '_patchsupport.py'), exec_dict)
    find_matching = exec_dict['FindMatching']
    dir_list = find_matching('bin', winghome, user_settings)
  except Exception:
    dir_list = []
  dir_list.extend([os.path.join(winghome, 'bin'), os.path.join(winghome, 'src')])
  for path in dir_list:
    try:
      if sys.version_info >= (3, 7):
        import importlib.machinery
        import importlib.util
        
        spec = importlib.machinery.PathFinder.find_spec('wingdb', [path])
        if spec is not None:
          mod = importlib.util.module_from_spec(spec)
          if mod is not None:
            spec.loader.exec_module(mod)
            return mod
      else:
        f, p, d = imp.find_module('wingdb', [path])
        try:
          return imp.load_module('wingdb', f, p, d)
        finally:
          if f is not None:
            f.close()

    except ImportError:
      pass
    
  return None

#------------------------------------------------------------------------
# Set debugger if it hasn't been set -- this is to handle module reloading
# In the reload case, the debugger variable will be set to something
try:
  debugger
except NameError:
  debugger = None
  
# Unset WINGDB_ACTIVE env if it was inherited from another process
# XXX Would be better to be able to call getpid() on dbgtracer but can't access it yet
if 'WINGDB_ACTIVE' in os.environ and os.environ['WINGDB_ACTIVE'] != str(os.getpid()):
  del os.environ['WINGDB_ACTIVE']

# Start debugging if not disabled and this module has never been imported
# before
if (not kWingDebugDisabled and debugger is None
    and not has_key(os.environ, 'WINGDB_DISABLED') and 
    not has_key(os.environ, 'WINGDB_ACTIVE')):

  exit_on_fail = 0
  
  try:
    # Obtain exit if fails value
    exit_on_fail = os.environ.get('WINGDB_EXITONFAILURE', kExitOnFailure)
    
    # Obtain configuration for log file to use, if any
    logfile = os.environ.get('WINGDB_LOGFILE', kLogFile)
    if logfile == '-' or logfile == None or len(logfile.strip()) == 0:
      logfile = None

    very_verbose_log = os.environ.get('WINGDB_LOGVERYVERBOSE', kLogVeryVerbose)
    if type(very_verbose_log) == type('') and very_verbose_log.strip() == '':
      very_verbose_log = 0
      
    # Determine remote host/port where the IDE is running
    hostport = os.environ.get('WINGDB_HOSTPORT', kWingHostPort)
    colonpos = hostport.find(':')
    host = hostport[:colonpos]
    port = int(hostport[colonpos+1:])
  
    # Determine port to listen on locally for attach requests
    attachport = int(os.environ.get('WINGDB_ATTACHPORT', kAttachPort))
  
    # Check if running embedded script
    embedded = int(os.environ.get('WINGDB_EMBEDDED', kEmbedded))
  
    # Obtain debug password file search path
    if has_key(os.environ, 'WINGDB_PWFILEPATH'):
      pwfile_path = os.environ['WINGDB_PWFILEPATH'].split(os.pathsep)
    else:
      pwfile_path = kPWFilePath
    
    # Obtain debug password file name
    if has_key(os.environ, 'WINGDB_PWFILENAME'):
      pwfile_name = os.environ['WINGDB_PWFILENAME']
    else:
      pwfile_name = kPWFileName
    
    # Load wingdb.py
    actual_winghome = _FindActualWingHome(WINGHOME)
    wingdb = _ImportWingdb(actual_winghome, kUserSettingsDir)
    if wingdb == None:
      sys.stdout.write("*******************************************************************\n")
      sys.stdout.write("Error: Cannot find wingdb.py in $(WINGHOME)/bin or $(WINGHOME)/src\n")
      sys.stdout.write("Error: Please check the WINGHOME definition in wingdbstub.py\n")
      sys.exit(2)
    
    # Find the netserver module and create an error stream
    netserver = wingdb.FindNetServerModule(actual_winghome, kUserSettingsDir)
    err = wingdb.CreateErrStream(netserver, logfile, very_verbose_log)
    
    # Start debugging
    debugger = netserver.CNetworkServer(host, port, attachport, err, 
                                        pwfile_path=pwfile_path,
                                        pwfile_name=pwfile_name,
                                        autoquit=not embedded)
    debugger.StartDebug(stophere=0)
    os.environ['WINGDB_ACTIVE'] = str(os.getpid())
    if debugger.ChannelClosed():
      raise ValueError('Not connected')
    
  except:
    if exit_on_fail:
      raise
    else:
      pass

def Ensure(require_connection=1, require_debugger=1):
  """ Ensure the debugger is started and attempt to connect to the IDE if
  not already connected.  Will raise a ValueError if:
  
  * the require_connection arg is true and the debugger is unable to connect
  * the require_debugger arg is true and the debugger cannot be loaded
  
  If SuspendDebug() has been called through the low-level API, calling
  Ensure() resets the suspend count to zero and additional calls to
  ResumeDebug() will be ignored until SuspendDebug() is called again.
  
  Note that a change to the host & port to connect to will only
  be use if a new connection is made.
  
  """
  
  if debugger is None:
    if require_debugger:
      raise ValueError("No debugger")
    return

  hostport = os.environ.get('WINGDB_HOSTPORT', kWingHostPort)
  colonpos = hostport.find(':')
  host = hostport[:colonpos]
  port = int(hostport[colonpos+1:])
  
  resumed = debugger.ResumeDebug()
  while resumed > 0:
    resumed = debugger.ResumeDebug()
  
  debugger.SetClientAddress((host, port))  
  
  if not debugger.DebugActive():
    debugger.StartDebug()
  elif debugger.ChannelClosed():
    debugger.ConnectToClient()
    
  if require_connection and debugger.ChannelClosed():
    raise ValueError('Not connected')
    