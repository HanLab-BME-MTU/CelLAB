# -*- mode: python ; coding: utf-8 -*-
"""
CelLAB Lite — PyInstaller spec file.

Build command:
    pyinstaller cellab.spec

Output:
    dist/CelLAB/CelLAB.exe
"""

import os
import sys

from PyInstaller.utils.hooks import collect_submodules, collect_data_files, collect_all

block_cipher = None
base_dir = os.path.dirname(os.path.abspath(SPEC))

# Nuclear option: collect everything from skimage
skimage_datas, skimage_binaries, skimage_imports = collect_all('skimage')

a = Analysis(
    ['cellab_launcher.py'],
    pathex=[base_dir],
    binaries=[
        *skimage_binaries,
    ],
    datas=[
        *skimage_datas,
        # Frontend
        ('frontend', 'frontend'),
        # Backend modules (released only)
        ('backend/cornealia', 'backend/cornealia'),
        ('backend/shared_modules', 'backend/shared_modules'),
        ('backend/cellintella', 'backend/cellintella'),
        # Root files
        ('app.py', '.'),
        ('backend/project_manager.py', '.'),
        ('backend/cellade_manager.py', '.'),
        ('modules.json', '.'),
        ('cellab.ico', '.'),
    ],
    hiddenimports=[
        *skimage_imports,
        # Web/GUI
        'flask',
        'webview',
        # Core scientific
        'numpy',
        'pandas',
        'matplotlib',
        'matplotlib.backends.backend_agg',
        'matplotlib.backends.backend_svg',
        # SciPy
        'scipy',
        'scipy.signal',
        'scipy.optimize',
        'scipy.ndimage',
        'scipy.spatial',
        'scipy.stats',
        # OpenCV
        'cv2',
        # scikit-image (collected via collect_all above)
        # scikit-fuzzy
        'skfuzzy',
        # scikit-learn
        'sklearn',
        'sklearn.cluster',
        # PIL / Pillow
        'PIL',
        'PIL.Image',
        'PIL.ImageDraw',
        # Stats / plotting
        'statsmodels',
        'statsmodels.nonparametric',
        'statsmodels.nonparametric.smoothers_lowess',
        'seaborn',
        # Utilities
        'tqdm',
        'psutil',
        'networkx',
        'markdown',
        'shapely',
        'shapely.geometry',
        'imageio',
        'joblib',
        'requests',
        # File formats
        'tifffile',
        # Standard lib that PyInstaller may miss
        'tkinter',
        'tkinter.filedialog',
        'csv',
        'sqlite3',
        'hashlib',
        'uuid',
        'platform',
        'concurrent',
        'concurrent.futures',
        'multiprocessing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # Heavy packages not needed for Lite
        'easyocr',
        'torch',
        'torchvision',
        'llama_cpp',
        'sentence_transformers',
        'chromadb',
        'trackpy',
        'cupy',
        'cupyx',
        'numba',
        # Dev tools
        'IPython',
        'jupyter',
        'notebook',
        'pytest',
    ],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CelLAB',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,       # Debug: show console to see errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon='cellab.ico' if sys.platform == 'win32' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CelLAB',
)
