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

import os
from os.path import join, expanduser, abspath, isdir, islink
import itertools

__all__ = ['tree']


class Error(Exception):
    pass

class NotExistsError(Error):
    pass


START   = u'├'
BLANK   = u'│'
END     = u'└'
LINE    = u'─'

DIR, FILE, LINK = TYPES = range(3)

def ensure_unicode(s):
    if isinstance(s, unicode):
        return s
    else:
        for enc in ('utf8', 'cp932'):
            try:
                return s.decode(enc)
            except:
                pass
        return s.decode('utf8', 'ignore')


def file_filter(name):
    return not name.startswith('.')

def link_filter(name):
    return not name.startswith('.')

def dir_filter(name):
    return not name.startswith('.')


filter_funcs = {
    DIR     : dir_filter,
    FILE    : file_filter,
    LINK    : link_filter,
}



def filters((type, name)):
    return filter_funcs[type](name)

def get_item(root, name):
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
        if item.endswith(BLANK) and len(self) > 0 and self[-1].split('\n')[-1] == item:
            return
        list.append(self, item)

    def __unicode__(self):
        return '\n'.join(ensure_unicode(x) for x in self)


class DirTree(object):
    _defaults = {
        'tab'       : 3,
        'indent'    : 1,
        'dense'     : False,
    }

    def __init__(self, path, **kws):
        self.path = path
        paras = DirTree._defaults
        paras.update(**kws)
        for k, v in paras.iteritems():
            setattr(self, k, v)

    def render(self, path, padding=''):
        rslt = Lines()
        indented = ' ' * self.indent

        items = list(filter(filters, (get_item(path, x) for x in os.listdir(path))))

        for i, (type, name) in enumerate(items):
            last = (i == (len(items) - 1))
            prefix = '%s%s ' % ((last and END or START), LINE * self.tab)
            rslt.append(indented + padding + '%s[%s]' % (prefix, ensure_unicode(name)))
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

        return unicode(rslt)

    def tree(self):
        path = expanduser(self.path)
        path = abspath(path)
        if not os.path.exists(path):
            raise NotExistsError, path

        rslt = []
        rslt.append(path)
        if not self.dense:
            rslt.append('')
        rslt.append(self.render(ensure_unicode(path).encode('utf8')))
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
    print tree(args.path)

