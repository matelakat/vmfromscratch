class RealOSOperations(object):
    def __init__(self):
        import os
        self.os = os

    def file_exists(self, filename):
        return self.os.path.exists(filename) and self.os.path.isfile(filename)

    def copy(self, source, target):
        self.files[target] = self.files[source]


class OSOperations(object):
    def __init__(self):
        self.files = {}

    def file_exists(self, filename):
        return filename in self.files

    def copy(self, source, target):
        self.files[target] = self.files[source]


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

    def restore(self):
        """
        If the target does not exists, the saved will be copied:
        >>> cfg = VersionedConfigFile(target='target', saved='saved')
        >>> cfg.osops.files = {'saved': 'some bytes'}
        >>> cfg.restore()
        'OK'
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
        return 'OK'



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




if __name__ == "__main__":
    main()
