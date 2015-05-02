"""
This is a setup.py script generated by py2applet

Usage:
    python setup.py py2app
"""

from setuptools import setup

APP = ['MolDesigner.py']
DATA_FILES = [('', ['images'])]
OPTIONS = {
	'argv_emulation': True,
	'optimize': 2,
	'iconfile':'images/icon.icns',
	'includes': ['wx', 'OpenGL.GL', 'OpenGL.GLU', 'OpenGL.GLUT', 'numpy', 'PIL.Image']
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
)
