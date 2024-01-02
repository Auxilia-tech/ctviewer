import sys
from cx_Freeze import setup, Executable

# Les dépendances sont automatiquement détectées, mais il peut être nécessaire de les ajuster.
build_exe_options = {
    "packages": ["vedo", "vtkmodules"],  # Include vedo and any other necessary packages
    "excludes": ["tkinter", "unittest"],
}

# base="Win32GUI" devrait être utilisé uniquement avec l’app Windows GUI
base = "Win32GUI" if sys.platform == "win32" else None

executables = Executable("main.py",
                         base=base,
                         target_name="CTViewer",
                         icon='icons/logo.ico')

setup(
    name="CTViewer",
    version="0.5",
    description="Auxilia CTViewer !",
    options={"build_exe": build_exe_options},
    executables=[executables],
)
