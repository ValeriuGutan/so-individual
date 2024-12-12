import os
import platform
import subprocess
import shutil

def build_application():
    system = platform.system().lower()
    os.makedirs('dist', exist_ok=True)
    
    app_name = "InvoiceManager"

    if system == 'darwin':  
        separator = ':'
        extra_args = [
            '--osx-bundle-identifier', 'com.yourcompany.invoicemanager'
        ]
    elif system == 'windows':
        separator = ';'
        extra_args = []
    else:
        raise SystemError(f"Unsupported system: {system}")
    
    cmd = [
        'pyinstaller',
        '--name', app_name,
        '--windowed',
        '--clean',
        '--noconfirm',
        '--onedir',
        '--hidden-import=PyQt6.QtCore',
        '--hidden-import=PyQt6.QtWidgets',
        '--hidden-import=PyQt6.QtGui',
        '--exclude-module=PyQt6.QtBluetooth',
        '--exclude-module=PyQt6.QtDBus',
        '--exclude-module=PyQt6.Qt3D',
        '--exclude-module=PyQt6.QtWebEngine',
        '--exclude-module=PyQt6.QtWebView',
        '--exclude-module=PyQt6.QtQuick',
        '--collect-submodules=PyQt6.QtCore',
        '--collect-submodules=PyQt6.QtWidgets',
        '--collect-submodules=PyQt6.QtGui',
        *extra_args,
        os.path.join('frontend', 'run.py')
    ]
    

    try:
        subprocess.run(cmd, check=True)

        if system == 'darwin':
            app_path = os.path.join('dist', f'{app_name}.app')

            with open(os.path.join('dist', 'run_debug.sh'), 'w') as f:
                f.write(f'''#!/bin/bash
cd "{os.path.dirname(app_path)}"
"{app_path}/Contents/MacOS/{app_name}"
''')
            
            os.chmod(os.path.join('dist', 'run_debug.sh'), 0o755)

            with open(os.path.join('dist', 'run.sh'), 'w') as f:
                f.write(f'''#!/bin/bash
cd "{os.path.dirname(app_path)}"
open "{app_path}"
''')
            os.chmod(os.path.join('dist', 'run.sh'), 0o755)
        else:
            app_path = os.path.join('dist', app_name)
            
        print(f"Build completed successfully: {app_path}")
        print("To run normally: ./dist/run.sh")
        print("To run with debug output: ./dist/run_debug.sh")
        
    except subprocess.CalledProcessError as e:
        print(f"Error during build: {e}")
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise

if __name__ == "__main__":
    build_application() 