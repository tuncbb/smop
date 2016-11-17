# SMOP -- Simple Matlab/Octave to Python compiler
# Copyright 2011-2016 Victor Leikehman

import tarfile
import sys
import traceback
from os.path import basename, splitext

import lexer
import options
import parse
import resolve
import backend
import version


def print_header(fp):
    print >> fp, "# Autogenerated with SMOP " + version.__version__
    # print >> fp, "from __future__ import division"
    print >> fp, "from smop.core import *"
    if options.link:
        print >> fp, "from %s import *" % options.link
    print >> fp, "#", options.filename


def main():
    if not options.filelist and not options.archive:
        options.parser.print_help()
        return
    if options.archive:
        tar = tarfile.open(options.archive)
        options.filelist += tar.getnames()
    else:
        tar = None
    if options.output == "-":
        fp = sys.stdout
    elif options.output:
        fp = open(options.output, "w")
    else:
        fp = None
    for i, options.filename in enumerate(options.filelist):
        try:
            if options.verbose:
                print i, options.filename
            if not options.filename.endswith(".m"):
                if options.verbose:
                    print("\tIgnored: '%s' (unexpected file type)" %
                          options.filename)
                continue
            if basename(options.filename) in options.xfiles:
                if options.verbose and "a3" in options.debug:
                    print "\tExcluded: '%s'" % options.filename
                continue
            if tar:
                buf = tar.extractfile(options.filename).read()
            else:
                buf = open(options.filename).read()
            buf = buf.replace("\r\n", "\n")
            buf = buf.decode("ascii", errors="ignore")
            stmt_list = parse.parse(buf if buf[-1] == '\n' else buf + '\n')
            #assert None not in stmt_list
            if not stmt_list:
                continue
            if not options.no_resolve:
                G = resolve.resolve(stmt_list)
            if not options.no_backend:
                s = backend.backend(stmt_list)
            if not options.output:
                f = splitext(basename(options.filename))[0] + ".py"
                with open(f, "w") as fp:
                    fp.write(s)
            else:
                fp.write(s)

        except:
            print 40*"="
            traceback.print_exc()
            if not options.ignore_errors:
                return
            options.ignore_errors -= 1


if __name__ == "__main__":
    main()
