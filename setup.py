#!/usr/bin/env python

# python setup.py --help
# python setup.py build --help
# python setup.py build -c mingw32
# python setup.py install --skip-build

from distutils.core import setup, Extension

DEBUG = 1
perl = 'perl -MPortable'

import sys, os
from os      import popen, system, access, F_OK
from os.path import isfile, getmtime
from sys     import exit

MULTI_PERL = isfile("MULTI_PERL")
BOOT_FROM_PERL = isfile("BOOT_FROM_PERL")

p = popen(perl + ' ./opts.pl')
perl_ccopts = p.readline()
perl_ldopts = p.readline()
p.close()

ext_name     = "perl"
include_dirs = []
macros       = []
cc_extra     = []

for x in perl_ccopts.split():
    if x[:2] == '-I':
        include_dirs.append(x[2:])

    # XXX This is disabled since distutils does not yet implement
    # define_macros.  Aarghhh!!  So much time wasted on debugging
    # because of this.
    elif 0 and x[:2] == '-D':
        m = split(x[2:], '=', 2)
        if len(m) == 1:
            m.append(None)
        macros.append(tuple(m))
    else:
        cc_extra.append(x)

lib_dirs  = []
libs      = []
ld_extra  = []
o_extra   = []
sym_extra = []

extra_ext = []

# Hack name to get it to compile as C++ file on Windows
svrv_object_c_name = "svrv_object.c"
if sys.platform[:3] == "win":
    import shutil
    svrv_object_c_name = "svrv_object.cpp"
    if os.path.exists(svrv_object_c_name):
        #os.chmod(svrv_object_c_name, 0777)
        os.unlink(svrv_object_c_name)
    shutil.copy("svrv_object.c", svrv_object_c_name)

sources = ['perlmodule.c',
           'lang_lock.c',
           'lang_map.c',
           svrv_object_c_name,
           'try_perlapi.c',
          ]
#o_extra.append('Python-Object/Object.o')

if BOOT_FROM_PERL:
    cc_extra.append("-DBOOT_FROM_PERL")
else:
    for x in perl_ldopts.split():
        if x[:2] == '-L':
            lib_dirs.append(x[2:])
        elif x[:2] == '-l' and sys.platform != 'win32':
            libs.append(x[2:])
        elif x[:1] != '-' and (x[-3:] == '.so' or
                               x[-2:] == '.o'  or
                               x[-2:] == '.a'
                               ):
            o_extra.append(x)
        else:
            ld_extra.append(x)

    p = popen(perl + ' ./objs.pl')
    objs = p.readline()
    for x in objs.split():
        o_extra.append(x)
    p.close()

    if not isfile("perlxsi.c"):
        system(perl + " -MExtUtils::Embed -e xsinit")
    sources.append('perlxsi.c');

    # Try to figure out if we use dlopen on this platform
    p = popen(perl + ' -V:dlsrc')
    dlsrc = p.readline()
    p.close()
    if dlsrc == "dlsrc='dl_dlopen.xs';\n":
        ext_name = "perl2"
        cc_extra.append("-DDL_HACK")
        extra_ext.append(Extension(name = "perl",
                                   sources = ["dlhack.c"],
                                   libraries = ["dl"],
                                   ))
        

if MULTI_PERL:
    cc_extra.append("-DMULTI_PERL")
    sources.append('thrd_ctx.c')

if not isfile("try_perlapi.c") or \
       getmtime("try_perlapi.c") < getmtime("try_perlapi.pl"):
    system(perl + " try_perlapi.pl")

if sys.platform == 'win32':
    libs.append('perl526')
    for x in ['15','16','20','27','36']:
        if access(os.path.join(sys.prefix, 'libs', 'python'+x+'.lib'), \
                  F_OK) == 1 :
            libs.append('python'+x)
    #sym_extra.append('get_thread_ctx')
    sym_extra.append('sv2pyo')
    sym_extra.append('pyo2sv')

if 0: # я привнёс, похоже что зря...
    lib_dirs.append('Python-Object\\blib\\arch\\auto\\Python\\Object')  # Python::Object
    libs.append('Object')  # Python::Object

if DEBUG:
    print("Macros:", macros)
    print("Include: ", include_dirs)
    print("Extra CC: ", cc_extra)
    print("Obj: ", o_extra)
    print("Libs:", libs)
    print("Lib dirs:",  lib_dirs)
    print("Extra LD: ", ld_extra)

ext_modules = []
ext_modules.append(Extension(name = ext_name,
                             sources = sources,
                             define_macros = macros,
                             include_dirs = include_dirs,
                             extra_compile_args = cc_extra,
                             
                             extra_objects =  o_extra,
                             libraries = libs,
                             library_dirs = lib_dirs,
                             extra_link_args = ld_extra,
                             export_symbols = sym_extra,
                             ))
ext_modules.extend(extra_ext)

setup (name        = "pyperl",
       version     = "1.0",
       description = "Embed a perl interpreter",
       url         = "http://www.ActiveState.com",
       author      = "ActiveState",
       author_email= "gisle@ActiveState.com",
       py_modules  = ['perlpickle', 'perlmod'],
       ext_modules = ext_modules,
      )
