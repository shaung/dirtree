# -*- coding: utf-8 -*-

"""
    dirtree
    ~~~~~~~

    print
     ├─── the
     │     ├─── folders
     │     ├─── and
     │     └─── files
     └─── as
           ├─── a
           └─── tree

"""

from __future__ import print_function, unicode_literals

import sys
import os
from os.path import join, expanduser, abspath, isdir, islink
from fnmatch import fnmatch, fnmatchcase

try:
    unicode
except:
    unicode = str

__all__ = ['tree', 'Error', 'NotExistsError', 'NotDirectoryError']


class Error(Exception):
    pass

class NotExistsError(Error):
    pass

class NotDirectoryError(Error):
    pass


START   = '├'
BLANK   = '│'
END     = '└'
LINE    = '─'

DIR, FILE, LINK = TYPES = range(3)

def is_hidden(path, name):
    if os.name == 'posix':
        return name.startswith('.')
    elif os.name == 'nt':
        # TODO: check the file attribute on windows
        return False
    else:
        return False

def get_type_name_tuple(root, name):
    path = join(root, name)
    if islink(path):
        type = LINK
    elif isdir(path):
        type = DIR
    else:
        type = FILE
    return type, name


class Lines(list):
    def append(self, item):
        item = item.rstrip()
        try:
            if item.endswith(BLANK) and self[-1].split('\n')[-1] == item:
                return
        except IndexError:
            pass
        list.append(self, item)


class DirTree(object):
    _defaults = {
        'tab'       : 3,
        'indent'    : 1,
        'dense'     : False,
        'encodings' : (sys.getfilesystemencoding() or sys.getdefaultencoding(), 'utf8', 'cp932', 'sjis', 'eucjp'),
        'gitignore' : False,
        'hgignore'  : False,
        'include'   : '*',
        'exclude'   : '',
        'all_files' : False,
        'case_sensitive': False,
    }

    def __init__(self, path, **kws):
        self.path = path
        paras = DirTree._defaults
        for k, v in paras.items():
            setattr(self, k, kws.get(k, v))

    def ensure_unicode(self, s, encs=None):
        if isinstance(s, unicode):
            return s
        else:
            for enc in encs or self.encodings:
                try:
                    return s.decode(enc)
                except:
                    pass
            return s.decode('utf8', 'ignore')

    def _filter(self, path, type, name):
        name = self.ensure_unicode(name)

        if not self.all_files and is_hidden(path, name):
            return False

        _fnmatch = fnmatchcase if self.case_sensitive else fnmatch

        if type == DIR:
            pass
        else:
            if self.include and not _fnmatch(name, self.include):
                return False
            if self.exclude and _fnmatch(name, self.exclude):
                return False

            if type == FILE:
                pass
            elif type == LINK:
                pass
            else:
                return False

        return True

    def render(self, path, padding=''):
        rslt = Lines()
        indented = ' ' * self.indent

        _filter = lambda args: self._filter(path, *args)

        items = list(filter(_filter, (get_type_name_tuple(path, name) for name in os.listdir(path))))

        for i, (type, name) in enumerate(items):
            last = (i == (len(items) - 1))
            prefix = '%s%s' % ((last and END or START), LINE * self.tab)
            rslt.append(indented + padding + '%s %s' % (prefix, self.ensure_unicode(name)))
            if type == DIR:
                dirpath = join(path, name)
                lead = (last and ' ' or BLANK) + ' ' * (self.tab + 2)
                if not self.dense:
                    rslt.append(indented + padding + lead)
                subrslt = self.render(dirpath, padding=(padding+lead+indented[:-1]))
                if subrslt:
                    rslt.append(subrslt)
            if not self.dense:
                rslt.append(indented + padding + ((not last) and BLANK or ''))

        return '\n'.join(self.ensure_unicode(x) for x in rslt)

    def tree(self):
        path = expanduser(self.path)
        path = abspath(path)
        if not os.path.exists(path):
            raise NotExistsError(path)
        if not isdir(path):
            raise NotDirectoryError

        rslt = []
        rslt.append(path)
        if not self.dense:
            rslt.append('')
        rslt.append(self.render(self.ensure_unicode(path).encode('utf8')))
        return '\n'.join(rslt)


def tree(path, *args, **kws):
    t = DirTree(path, *args, **kws)
    return t.tree()


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Print the tree structure of specified directory.')
    parser.add_argument('path', metavar='path', type=str, 
                       help='the root directory')
    args = parser.parse_args()
    path = args.path
    print (tree(args.path))

