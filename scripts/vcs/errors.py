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
