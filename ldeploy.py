class RealOSOperations(object):
    def __init__(self):
        import os
        import subprocess
        import shutil
        self.os = os
        self.subprocess = subprocess
        self.shutil = shutil

    def file_exists(self, filename):
        return self.os.path.exists(filename) and self.os.path.isfile(filename)

    def copy(self, source, target):
        self.shutil.copyfile(source, target)

    def changed(self, fname):
        """
        >>> osops = RealOSOperations()
        >>> osops.changed('.gitignore')
        False
        >>> osops.changed('nonexisting')
        True
        """
        if not self.file_exists(fname):
            return True
        command = 'git status --porcelain -u all --'.split() + [fname]
        proc = self.subprocess.Popen(
            command, stdout=self.subprocess.PIPE, stderr=self.subprocess.PIPE)
        results = [output.strip() for output in proc.communicate()]
        return results != ['', '']


class OSOperations(object):
    def __init__(self):
        self.files = {}
        self.changed_gits = []

    def file_exists(self, filename):
        return filename in self.files

    def copy(self, source, target):
        self.files[target] = self.files[source]

    def changed(self, fname):
        return fname in self.changed_gits


class VersionedConfigFile(object):
    """
    >>> cfg = VersionedConfigFile(target='target', saved='saved')
    >>> cfg.target, cfg.saved
    ('target', 'saved')
    """

    def __init__(self, target=None, saved=None):
        self.target = target
        self.saved = saved
        self.osops = OSOperations()

    def _file_exists(self, fname):
        return self.osops.file_exists(fname)

    def target_exists(self):
        """
        >>> cfg = VersionedConfigFile(target='target')
        >>> cfg.target_exists()
        False
        >>> cfg.osops.files = {'target': 'some bytes'}
        >>> cfg.target_exists()
        True
        """
        return self._file_exists(self.target)

    def saved_exists(self):
        """
        >>> cfg = VersionedConfigFile(saved='saved')
        >>> cfg.saved_exists()
        False
        >>> cfg.osops.files = {'saved': 'some bytes'}
        >>> cfg.saved_exists()
        True
        """
        return self._file_exists(self.saved)

    def save(self):
        """
        If the target does not exists, nothing happens:
        >>> cfg = VersionedConfigFile(target='target', saved='saved')
        >>> cfg.save()
        '[target] does not exist'

        If the saved does not exist, but the target does:
        >>> cfg.osops.files = {'target': 'some bytes'}
        >>> cfg.save()
        '[saved] does not exist'

        If both saved and target exists:
        >>> cfg.osops.files = {'target': 'some bytes', 'saved': 'saved bytes'}
        >>> cfg.save()
        '[target] -> [saved] OK'

        And the contents has been overwritten:
        >>> cfg.osops.files['saved']
        'some bytes'

        If the git status is not fine:
        >>> cfg.osops.changed_gits = ['saved']
        >>> cfg.save()
        '[saved] Is out of date according to git'

        """
        if not self.target_exists():
            return '[{0}] does not exist'.format(self.target)
        if not self.saved_exists():
            return '[{0}] does not exist'.format(self.saved)

        if self.osops.changed(self.saved):
            return '[{0}] Is out of date according to git'.format(self.saved)
        self.osops.copy(self.target, self.saved)
        return '[{0}] -> [{1}] OK'.format(self.target, self.saved)


    def restore(self):
        """
        If the target does not exists, the saved will be copied:
        >>> cfg = VersionedConfigFile(target='target', saved='saved')
        >>> cfg.osops.files = {'saved': 'some bytes'}
        >>> cfg.restore()
        '[saved] -> [target] OK'
        >>> cfg.osops.files['target']
        'some bytes'

        Since the target now exists, restore should fail:
        >>> cfg.restore()
        '[target] already exists, was not overwritten'

        And the target's contents won't be changed:
        >>> cfg.osops.files['saved'] = 'new content'
        >>> cfg.restore()
        '[target] already exists, was not overwritten'
        >>> cfg.osops.files['target']
        'some bytes'

        If the saved does not exist, we fail immediately:
        >>> cfg.osops.files = {}
        >>> cfg.restore()
        '[saved] does not exists, so was not copied'
        """
        if not self.saved_exists():
            return '[{0}] does not exists, so was not copied'.format(
                self.saved
            )
        if self.target_exists():
            return '[{0}] already exists, was not overwritten'.format(
                self.target
            )
        self.osops.copy(self.saved, self.target)
        return '[{0}] -> [{1}] OK'.format(self.saved, self.target)



def main():
    import argparse

    parser = argparse.ArgumentParser(description='Save and Restore files')
    parser.add_argument('action', choices=['save', 'restore'])
    args = parser.parse_args()
    configs = [
        VersionedConfigFile(
            target='../kernel/linux-3.10.32/.config',
            saved='./linux/config'),
        VersionedConfigFile(
            target='../xtool/configuration/.config',
            saved='./crosstool-ng/config'),
        VersionedConfigFile(
            target='../br/buildroot-2014.02/.config',
            saved='./buildroot/config'),
    ]

    for config in configs:
        config.osops = RealOSOperations()
        if args.action == 'restore':
            print config.restore()
        elif args.action == 'save':
            print config.save()




if __name__ == "__main__":
    main()
