#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  doc_gen.py
#
#  Copyright 2017 Ian Ichung'wah Karanja <karanjaichungwa@gmail.com>
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
#  MA 02110-1301, USA.
#

import os
import pydoc as pd


def write_docs(fn, doc):
    f = open(fn, 'w')
    f.write(doc)
    f.close()


def gen_docs_module(m):
    d = pd.HTMLDoc()
    doc = d.docmodule(m)

    _dir = m.__name__
    os.mkdir(_dir)

    fn = '{}/{}.html'.format(_dir, m.__name__)
    write_docs(fn, doc)

    for item in dir(m):
        if eval("type(m.{})".format(item)) == type(m):
            sub_mod = eval("m.{}".format(item))
            doc = d.docmodule(sub_mod)

            fn = '{}/{}.html'.format(_dir, sub_mod.__name__)
            write_docs(fn, doc)



def main(args):
    import wx
    gen_docs_module(wx)

if __name__ == '__main__':
    import sys
    sys.exit(main(sys.argv))
