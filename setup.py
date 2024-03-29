#Copyright ReportLab Europe Ltd. 2000-2012
#see license.txt for license details
__version__=''' $Id: setup.py 3963 2012-09-27 16:14:06Z rgbecker $ '''
import os, sys, glob, ConfigParser, shutil
platform = sys.platform
pjoin = os.path.join
abspath = os.path.abspath
isfile = os.path.isfile
isdir = os.path.isdir
dirname = os.path.dirname
if __name__=='__main__':
    pkgDir=dirname(sys.argv[0])
else:
    pkgDir=dirname(__file__)
if not pkgDir:
    pkgDir=os.getcwd()
elif not os.path.isabs(pkgDir):
    pkgDir=os.path.abspath(pkgDir)
try:
    os.chdir(pkgDir)
except:
    print '!!!!! warning could not change directory to %r' % pkgDir
daily=os.environ.get('RL_EXE_DAILY','')

import distutils
from distutils.core import setup, Extension
from distutils import sysconfig

# from Zope - App.Common.package_home
def package_home(globals_dict):
    __name__=globals_dict['__name__']
    m=sys.modules[__name__]
    r=os.path.split(m.__path__[0])[0]
    return r

package_path = pjoin(package_home(distutils.__dict__), 'site-packages', 'reportlab')

def get_version():
    if daily: return 'daily'
    #determine Version
    HERE = pkgDir
    if os.getcwd()!=HERE:
        if __name__=='__main__':
            HERE=os.path.dirname(sys.argv[0])
        else:
            HERE=os.path.dirname(__file__)

    #first try source
    FN = pjoin(HERE,'src','reportlab','__init__')
    try:
        for l in open(pjoin(FN+'.py'),'r').readlines():
            if l.startswith('Version'):
                exec l.strip()
                return Version
    except:
        pass

    #don't have source, try import
    import imp
    for desc in ('.pyc', 'rb', 2), ('.pyo', 'rb', 2):
        try:
            fn = FN+desc[0]
            f = open(fn,desc[1])
            m = imp.load_module('reportlab',f,fn,desc)
            return m.Version
        except:
            pass
    raise ValueError('Cannot determine ReportLab Version')

class config:
    def __init__(self):
        try:
            self.parser = ConfigParser.RawConfigParser()
            self.parser.read(pjoin(pkgDir,'setup.cfg'))
        except:
            self.parser = None

    def __call__(self,sect,name,default=None):
        try:
            return self.parser.get(sect,name)
        except:
            return default
config = config()

#this code from /FBot's PIL setup.py
def aDir(P, d, x=None):
    if d and os.path.isdir(d) and d not in P:
        if x is None:
            P.append(d)
        else:
            P.insert(x, d)

class inc_lib_dirs:
    L = None
    I = None
    def __call__(self):
        if self.L is None:
            L = []
            I = []
            if platform == "cygwin":
                aDir(L, os.path.join("/usr/lib", "python%s" % sys.version[:3], "config"))
            elif platform == "darwin":
                # attempt to make sure we pick freetype2 over other versions
                aDir(I, "/sw/include/freetype2")
                aDir(I, "/sw/lib/freetype2/include")
                # fink installation directories
                aDir(L, "/sw/lib")
                aDir(I, "/sw/include")
                # darwin ports installation directories
                aDir(L, "/opt/local/lib")
                aDir(I, "/opt/local/include")
            prefix = sysconfig.get_config_var("prefix")
            if prefix:
                aDir(L, pjoin(prefix, "lib"))
                aDir(I, pjoin(prefix, "include"))
            aDir(I, "/usr/local/include")
            aDir(L, "/usr/local/lib")
            aDir(I, "/usr/include")
            aDir(L, "/usr/lib")
            aDir(I, "/usr/include/freetype2")
            self.L=L
            self.I=I
        return self.I,self.L
inc_lib_dirs=inc_lib_dirs()

def getVersionFromCCode(fn):
    import re
    tag = re.search(r'^#define\s+VERSION\s+"([^"]*)"',open(fn,'r').read(),re.M)
    return tag and tag.group(1) or ''

class _rl_dir_info:
    def __init__(self,cn):
        self.cn=cn
    def __call__(self,dir):
        import stat
        fn = pjoin(dir,self.cn)
        try:
            return getVersionFromCCode(fn),os.stat(fn)[stat.ST_MTIME]
        except:
            return None

def _cmp_rl_ccode_dirs(a,b):
    return cmp(_rl_dir_info(b),_rl_dir_info(a))

def _find_rl_ccode(dn='rl_accel',cn='_rl_accel.c'):
    '''locate where the accelerator code lives'''
    _ = []
    for x in [
            pjoin('src','rl_addons',dn),
            pjoin('rl_addons',dn),
            pjoin('..','rl_addons',dn),
            pjoin('..','..','rl_addons',dn),
            dn,
            pjoin('..',dn),
            pjoin('..','..',dn),
            ] \
            + glob.glob(pjoin(dn+'-*',dn))\
            + glob.glob(pjoin('..',dn+'-*',dn))\
            + glob.glob(pjoin('..','..',dn+'-*',dn))\
            :
        fn = pjoin(pkgDir,x,cn)
        if isfile(fn):
            _.append(x)
    if _:
        _ = filter(_rl_dir_info(cn),_)
        if len(_):
            _.sort(_cmp_rl_ccode_dirs)
            return abspath(_[0])
    return None


def BIGENDIAN(macname,value=None):
    'define a macro if bigendian'
    return sys.byteorder=='big' and [(macname,value)] or []

def pfxJoin(pfx,*N):
    R=[]
    for n in N:
        R.append(os.path.join(pfx,n))
    return R

INFOLINES=[]
def infoline(t):
    print t
    INFOLINES.append(t)

reportlab_files= [
        'fonts/00readme.txt',
        'fonts/bitstream-vera-license.txt',
        'fonts/DarkGarden-copying-gpl.txt',
        'fonts/DarkGarden-copying.txt',
        'fonts/DarkGarden-readme.txt',
        'fonts/DarkGarden.sfd',
        'fonts/DarkGardenMK.afm',
        'fonts/DarkGardenMK.pfb',
        'fonts/Vera.ttf',
        'fonts/VeraBd.ttf',
        'fonts/VeraBI.ttf',
        'fonts/VeraIt.ttf',
        'fonts/_abi____.pfb',
        'fonts/_ab_____.pfb',
        'fonts/_ai_____.pfb',
        'fonts/_a______.pfb',
        'fonts/cobo____.pfb',
        'fonts/cob_____.pfb',
        'fonts/com_____.pfb',
        'fonts/coo_____.pfb',
        'fonts/_ebi____.pfb',
        'fonts/_eb_____.pfb',
        'fonts/_ei_____.pfb',
        'fonts/_er_____.pfb',
        'fonts/sy______.pfb',
        'fonts/zd______.pfb',
        'fonts/zx______.pfb',
        'fonts/zy______.pfb',
        ]

def get_fonts(PACKAGE_DIR, reportlab_files):
    import sys, os, os.path, urllib2, zipfile, StringIO
    rl_dir = PACKAGE_DIR['reportlab']
    if not [x for x in reportlab_files if not os.path.isfile(pjoin(rl_dir,x))]:
        infoline("Standard T1 font curves already downloaded")
        return
    try:
        infoline("Downloading standard T1 font curves")

        remotehandle = urllib2.urlopen("http://www.reportlab.com/ftp/pfbfer-20070710.zip")
        zipdata = StringIO.StringIO(remotehandle.read())
        remotehandle.close()
        archive = zipfile.ZipFile(zipdata)
        dst = pjoin(rl_dir, 'fonts')

        for name in archive.namelist():
            if not name.endswith('/'):
                outfile = open(os.path.join(dst, name), 'wb')
                outfile.write(archive.read(name))
                outfile.close()
        xitmsg = "Finished download of standard T1 font curves"
    except:
        xitmsg = "Failed to download standard T1 font curves"
    reportlab_files = [x for x in reportlab_files if os.path.isfile(pjoin(rl_dir,x))]
    infoline(xitmsg)

def main():
    #test to see if we've a special command
    if 'tests' in sys.argv or 'tests-preinstall' in sys.argv:
        if len(sys.argv)!=2:
            raise ValueError('tests commands may only be used alone')
        cmd = sys.argv[-1]
        PYTHONPATH=[pkgDir]
        if cmd=='tests-preinstall':
            PYTHONPATH.insert(0,pjoin(pkgDir,'src'))
        os.environ['PYTHONPATH']=os.pathsep.join(PYTHONPATH)
        os.chdir(pjoin(pkgDir,'tests'))
        os.system("%s runAll.py" % sys.executable)
        return

    SPECIAL_PACKAGE_DATA = {}
    RL_ACCEL = _find_rl_ccode('rl_accel','_rl_accel.c')
    LIBRARIES=[]
    EXT_MODULES = []
    if not RL_ACCEL:
        infoline( '***************************************************')
        infoline( '*No rl_accel code found, you can obtain it at     *')
        infoline( '*http://www.reportlab.org/downloads.html#_rl_accel*')
        infoline( '***************************************************')
    else:
        infoline( '################################################')
        infoline( '#Attempting install of _rl_accel, sgmlop & pyHnj')
        infoline( '#extensions from %r'%RL_ACCEL)
        infoline( '################################################')
        fn = pjoin(RL_ACCEL,'hyphen.mashed')
        SPECIAL_PACKAGE_DATA = {fn: pjoin('lib','hyphen.mashed')}
        EXT_MODULES += [
                    Extension( '_rl_accel',
                                [pjoin(RL_ACCEL,'_rl_accel.c')],
                                include_dirs=[],
                            define_macros=[],
                            library_dirs=[],
                            libraries=[], # libraries to link against
                            ),
                    Extension( 'sgmlop',
                            [pjoin(RL_ACCEL,'sgmlop.c')],
                            include_dirs=[],
                            define_macros=[],
                            library_dirs=[],
                            libraries=[], # libraries to link against
                            ),
                    Extension( 'pyHnj',
                            [pjoin(RL_ACCEL,'pyHnjmodule.c'),
                             pjoin(RL_ACCEL,'hyphen.c'),
                             pjoin(RL_ACCEL,'hnjalloc.c')],
                            include_dirs=[],
                            define_macros=[],
                            library_dirs=[],
                            libraries=[], # libraries to link against
                            ),
                    ]
    RENDERPM = _find_rl_ccode('renderPM','_renderPM.c')
    if not RENDERPM:
        infoline( '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
        infoline( '!No rl_accel code found, you can obtain it at     !')
        infoline( '!http://www.reportlab.org/downloads.html          !')
        infoline( '!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
    else:
        infoline( '################################################')
        infoline( '#Attempting install of _renderPM')
        infoline( '#extensions from %r'%RENDERPM)
        LIBART_DIR=pjoin(RENDERPM,'libart_lgpl')
        GT1_DIR=pjoin(RENDERPM,'gt1')
        MACROS=[('ROBIN_DEBUG',None)]
        MACROS=[]
        def libart_version():
            K = ('LIBART_MAJOR_VERSION','LIBART_MINOR_VERSION','LIBART_MICRO_VERSION')
            D = {}
            for l in open(pjoin(LIBART_DIR,'configure.in'),'r').readlines():
                l = l.strip().split('=')
                if len(l)>1 and l[0].strip() in K:
                    D[l[0].strip()] = l[1].strip()
                    if len(D)==3: break
            return (sys.platform == 'win32' and '\\"%s\\"' or '"%s"') % '.'.join(map(lambda k,D=D: D.get(k,'?'),K))
        LIBART_VERSION = libart_version()
        SOURCES=[pjoin(RENDERPM,'_renderPM.c'),
                    pjoin(LIBART_DIR,'art_vpath_bpath.c'),
                    pjoin(LIBART_DIR,'art_rgb_pixbuf_affine.c'),
                    pjoin(LIBART_DIR,'art_rgb_svp.c'),
                    pjoin(LIBART_DIR,'art_svp.c'),
                    pjoin(LIBART_DIR,'art_svp_vpath.c'),
                    pjoin(LIBART_DIR,'art_svp_vpath_stroke.c'),
                    pjoin(LIBART_DIR,'art_svp_ops.c'),
                    pjoin(LIBART_DIR,'art_vpath.c'),
                    pjoin(LIBART_DIR,'art_vpath_dash.c'),
                    pjoin(LIBART_DIR,'art_affine.c'),
                    pjoin(LIBART_DIR,'art_rect.c'),
                    pjoin(LIBART_DIR,'art_rgb_affine.c'),
                    pjoin(LIBART_DIR,'art_rgb_affine_private.c'),
                    pjoin(LIBART_DIR,'art_rgb.c'),
                    pjoin(LIBART_DIR,'art_rgb_rgba_affine.c'),
                    pjoin(LIBART_DIR,'art_svp_intersect.c'),
                    pjoin(LIBART_DIR,'art_svp_render_aa.c'),
                    pjoin(LIBART_DIR,'art_misc.c'),
                    pjoin(GT1_DIR,'gt1-parset1.c'),
                    pjoin(GT1_DIR,'gt1-dict.c'),
                    pjoin(GT1_DIR,'gt1-namecontext.c'),
                    pjoin(GT1_DIR,'gt1-region.c'),
                    ]

        if platform=='win32':
            FT_LIB=os.environ.get('FT_LIB','')
            if not FT_LIB: FT_LIB=config('FREETYPE','lib','')
            if FT_LIB and not os.path.isfile(FT_LIB):
                infoline('# freetype lib %r not found' % FT_LIB)
                FT_LIB=[]
            if FT_LIB:
                FT_INC_DIR=os.environ.get('FT_INC','')
                if not FT_INC_DIR: FT_INC_DIR=config('FREETYPE','inc')
                FT_MACROS = [('RENDERPM_FT',None)]
                FT_LIB_DIR = [dirname(FT_LIB)]
                FT_INC_DIR = [FT_INC_DIR or pjoin(dirname(FT_LIB_DIR[0]),'include')]
                FT_LIB_PATH = FT_LIB
                FT_LIB = [os.path.splitext(os.path.basename(FT_LIB))[0]]                
                if isdir(FT_INC_DIR[0]):                   
                    infoline('# installing with freetype %r' % FT_LIB_PATH)
                else:
                    infoline('# freetype2 include folder %r not found' % FT_INC_DIR[0])
                    FT_LIB=FT_LIB_DIR=FT_INC_DIR=FT_MACROS=[]
            else:
                FT_LIB=FT_LIB_DIR=FT_INC_DIR=FT_MACROS=[]
        else:
            FT_LIB_DIR=config('FREETYPE','lib')
            FT_INC_DIR=config('FREETYPE','inc')
            I,L=inc_lib_dirs()
            ftv = None
            for d in I:
                if isfile(pjoin(d, "ft2build.h")):
                    ftv = 21
                    FT_INC_DIR=[d,pjoin(d, "freetype2")]
                    break
                d = pjoin(d, "freetype2")
                if isfile(pjoin(d, "ft2build.h")):
                    ftv = 21
                    FT_INC_DIR=[d]
                    break
                if isdir(pjoin(d, "freetype")):
                    ftv = 20
                    FT_INC_DIR=[d]
                    break
            if ftv:
                FT_LIB=['freetype']
                FT_LIB_DIR=L
                FT_MACROS = [('RENDERPM_FT',None)]
                infoline('# installing with freetype version %d' % ftv)
            else:
                FT_LIB=FT_LIB_DIR=FT_INC_DIR=FT_MACROS=[]
        if not FT_LIB:
            infoline('# installing without freetype no ttf, sorry!')
            infoline('# You need to install a static library version of the freetype2 software')
            infoline('# If you need truetype support in renderPM')
            infoline('# You may need to edit setup.cfg (win32)')
            infoline('# or edit this file to access the library if it is installed')
        EXT_MODULES +=  [Extension( '_renderPM',
                                        SOURCES,
                                        include_dirs=[RENDERPM,LIBART_DIR,GT1_DIR]+FT_INC_DIR,
                                        define_macros=FT_MACROS+[('LIBART_COMPILATION',None)]+MACROS+[('LIBART_VERSION',LIBART_VERSION)],
                                        library_dirs=[]+FT_LIB_DIR,

                                        # libraries to link against
                                        libraries=FT_LIB,
                                        #extra_objects=['gt1.lib','libart.lib',],
                                        #extra_compile_args=['/Z7'],
                                        extra_link_args=[]
                                        ),
                            ]
        infoline('################################################')

    #copy some special case files into place so package_data will treat them properly
    PACKAGE_DIR = {'reportlab': pjoin('src','reportlab')}
    for fn,dst in SPECIAL_PACKAGE_DATA.iteritems():
        shutil.copyfile(fn,pjoin(PACKAGE_DIR['reportlab'],dst))
        reportlab_files.append(dst)
    get_fonts(PACKAGE_DIR, reportlab_files)
    try:
        setup(
            name="reportlab",
            version=get_version(),
            license="BSD license (see license.txt for details), Copyright (c) 2000-2012, ReportLab Inc.",
            description="The Reportlab Toolkit",
            long_description="""The ReportLab Toolkit. An Open Source Python library for generating PDFs and graphics.""",

            author="Andy Robinson, Robin Becker, the ReportLab team and the community",
            author_email="reportlab-users@lists2.reportlab.com",
            url="http://www.reportlab.com/",
            packages=[
                    'reportlab',
                    'reportlab.graphics.charts',
                    'reportlab.graphics.samples',
                    'reportlab.graphics.widgets',
                    'reportlab.graphics.barcode',
                    'reportlab.graphics',
                    'reportlab.lib',
                    'reportlab.pdfbase',
                    'reportlab.pdfgen',
                    'reportlab.platypus',
                    ],
            # Ideally we'd have this but PIL via easy_install doesn't seem stable
            #install_requires=[
            #        'PIL',
            #],
            package_dir = PACKAGE_DIR,
            package_data = {'reportlab': reportlab_files},
            ext_modules =   EXT_MODULES,
            )
        print
        print '########## SUMMARY INFO #########'
        print '\n'.join(INFOLINES)
    finally:
        for dst in SPECIAL_PACKAGE_DATA.itervalues():
            os.remove(pjoin(PACKAGE_DIR['reportlab'],dst))
            reportlab_files.remove(dst)


if __name__=='__main__':
    main()
