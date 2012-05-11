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


def render(path, padding='', tab=3, indent=1, dense=False):
    rslt = Lines()
    indented = ' '*indent

    items = list(filter(filters, (get_item(path, x) for x in os.listdir(path))))

    for i, (type, name) in enumerate(items):
        last = (i == (len(items) - 1))
        prefix = '%s%s ' % ((last and END or START), LINE * tab)
        rslt.append(indented + padding + '%s[%s]' % (prefix, ensure_unicode(name)))
        if type == DIR:
            dirpath = join(path, name)
            lead = last and (' ' * 6) or (BLANK + ' ' * 5)
            rslt.append(indented + padding + lead)
            subrslt = render(dirpath, padding=(padding+lead), tab=tab, indent=indent, dense=dense)
            if subrslt:
                rslt.append(subrslt)
        if not dense:
            rslt.append(indented + padding + ((not last) and BLANK or ''))

    return unicode(rslt)


def tree(path, dense=False):
    path = expanduser(path)
    path = abspath(path)

    rslt = []
    rslt.append(path)
    rslt.append('')
    rslt.append(render(ensure_unicode(path).encode('utf8'), dense=dense))
    return '\n'.join(rslt)

if __name__ == '__main__':
    print tree('../')

