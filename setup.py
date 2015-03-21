from cx_Freeze import setup, Executable
import visvis as vv
import os, shutil, sys
import sys

backendAliases = {'qt4': 'pyqt4'}


def copyResources(destPath):   
    """ copyResources(destinationPath)
    
    Copy the visvis resource dir to the specified folder 
    (The folder containing the frozen executable).
    
    """
    # create folder (if required)
    destPath = os.path.join(destPath, 'visvisResources')
    if not os.path.isdir(destPath):
        os.makedirs(destPath)
    # copy files
    path = vv.misc.getResourceDir()
    for file in os.listdir(path):
        if file.startswith('.') or file.startswith('_'):
            continue
        shutil.copy(os.path.join(path,file), os.path.join(destPath,file))
    # copy FreeType library to resource dir
    try:
        ft_filename = 'freetype'
    except Exception:
        ft_filename = None
    if ft_filename and not os.path.isfile(ft_filename):
        # Try harder to get absolute path for the freetype lib
        for dir in ['C:/Python27/Lib/site-packages/visvis/text', '/usr/local/lib/', 
                    '/usr/lib/x86_64-linux-gnu/', '/usr/lib/i386-linux-gnu/']:
            if os.path.isfile(dir+ft_filename):
                ft_filename = dir+ft_filename
                break
    if ft_filename and os.path.isfile(ft_filename):
        fname = os.path.split(ft_filename)[1]
        shutil.copy(ft_filename, os.path.join(destPath,fname))
    else:
        print('Warning: could not copy freetype library.')


def getIncludes(backendName):
    """ getIncludes(backendName)
    
    Get a list of includes to extend the 'includes' list
    with of py2exe or bbfreeze. The list contains:
      * the module of the specified backend 
      * all the functionnames, which are dynamically loaded and therefore
        not included by default.
      * opengl stuff
    
    """
    # init
    includes = []
    backendName = backendAliases.get(backendName, backendName)
    
    # backend
    backendModule = ('C:/Python27/Lib/site-packages/visvis/backends/backend_'+ backendName + '.py','backend_' +backendName+'.py')
    includes.append(backendModule)
    if backendName == 'pyqt4':
        includes.extend([("C:/Python27/Lib/site-packages/PyQt4/sip","sip"),('C:/Python27/Lib/site-packages/PyQt4/sip/PyQt4/QtCore', "PyQt4.QtCore"), ("C:/Python27/Lib/site-packages/PyQt4/sip/PyQt4/QtGui","PyQt4.QtGui"), ("C:/Python27/Lib/site-packages/PyQt4/sip/PyQt4/QtOpenGL","PyQt4.QtOpenGL")])
    elif backendName == 'pyside':
        includes.extend(["PySide.QtCore", "PySide.QtGui", "PySide.QtOpenGL"])
    
    # functions
    for funcName in vv.functions._functionNames:
        includes.append(('C:/Python27/Lib/site-packages/visvis/functions/'+funcName+'.py', funcName+'.py'))
    
    # processing functions
    for funcName in vv.processing._functionNames:
        includes.append(('C:/Python27/Lib/site-packages/visvis/processing/'+funcName+'.py', funcName+'.py'))
    
    # opengl stuff
    arrayModules = [("C:/Python27/Lib/site-packages/OpenGL/arrays/nones.py",'nones.py'), ("C:/Python27/Lib/site-packages/OpenGL/arrays/strings.py",'strings.py'),("C:/Python27/Lib/site-packages/OpenGL/arrays/lists.py",'lists.py'),("C:/Python27/Lib/site-packages/OpenGL/arrays/numbers.py",'numbers.py'),("C:/Python27/Lib/site-packages/OpenGL/arrays/ctypesarrays.py",'cytypesarrays.py'),
        ("C:/Python27/Lib/site-packages/OpenGL/arrays/ctypesparameters.py",'ctypesparameters.py'), ("C:/Python27/Lib/site-packages/OpenGL/arrays/ctypespointers",'ctypespointers.py'), ("C:/Python27/Lib/site-packages/OpenGL/arrays/numpymodule.py",'numpymodule.py'), 
        ("C:/Python27/Lib/site-packages/OpenGL/arrays/formathandler.py","formathandler.py")]
    GLUModules = [("C:/Python27/Lib/site-packages/OpenGL/GLU/glustruct.py",'glustruct.py')]
    for name in arrayModules:
        if name in sys.modules:        
            includes.append(name)
    for name in GLUModules:
        if name in sys.modules:        
            includes.append(name)
    if sys.platform.startswith('win'):
        includes.append(("C:/Python27/Lib/site-packages/OpenGL/platform/win32.py",'win32.py'))
    if sys.platform.startswith('linux'):
        includes.append("OpenGL.platform.glx")
    
    # done
    return includes

def getExcludes(backendName):
    """ getExcludes(backendName)
    
    Get a list of excludes. If using the 'wx' backend, you don't
    want all the qt4 libaries.
    
    backendName is the name of the backend which you do want to use.
    
    """
    
    # init
    excludes = []
    backendName = backendAliases.get(backendName, backendName)
    
    # Neglect pyqt4
    if 'pyqt4' != backendName:
        excludes.extend(["sip", "PyQt4", "PyQt4.QtCore", "PyQt4.QtGui"])
    
    # Neglect PySide
    if 'pyside' != backendName:
        excludes.extend(["PySide", "PySide.QtCore", "PySide.QtGui"])
    
    # Neglect wx
    if 'wx' != backendName:
        excludes.extend(["wx"])
    
    # done
    return excludes
	
# Dependencies are automatically detected, but it might need
# fine tuning.
copyResources('VisTool')
buildOptions = dict(packages = ["os"], include_files = getIncludes('pyqt4'), excludes = [])


base = 'Win32GUI' if sys.platform=='win32' else None
executables = [
    Executable('visualizationTool.py', base=base, targetName = 'VisTool')
]

options = {
    'build_exe': {
        'includes': 'atexit'
    }
}

setup(name='VisTool',
      version = '1.0',
      description = 'Tool for visualization of EMA sensor data in real-time',
      options = dict(build_exe = buildOptions),
      executables = executables)