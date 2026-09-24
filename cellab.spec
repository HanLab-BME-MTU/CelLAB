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
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(SPEC)))  # parent of packaging/

# Nuclear option: collect everything from packages with deep submodules
skimage_datas, skimage_binaries, skimage_imports = collect_all('skimage')
sm_datas, sm_binaries, sm_imports = collect_all('statsmodels')

a = Analysis(
    [os.path.join(base_dir, 'packaging', 'cellab_launcher.py')],
    pathex=[base_dir],
    binaries=[
        *skimage_binaries,
        *sm_binaries,
    ],
    datas=[
        *skimage_datas,
        *sm_datas,
        # Frontend
        (os.path.join(base_dir, 'frontend'), 'frontend'),
        # Backend modules (released only)
        (os.path.join(base_dir, 'backend', 'cornealia'), os.path.join('backend', 'cornealia')),
        (os.path.join(base_dir, 'backend', 'shared_modules'), os.path.join('backend', 'shared_modules')),
        (os.path.join(base_dir, 'backend', 'orchestrators'), os.path.join('backend', 'orchestrators')),
        (os.path.join(base_dir, 'backend', 'cellintella', '*.py'), os.path.join('backend', 'cellintella')),
        # Root files
        (os.path.join(base_dir, 'cellab.py'), '.'),
        (os.path.join(base_dir, 'backend', 'project_manager.py'), '.'),
        (os.path.join(base_dir, 'backend', 'cellade_manager.py'), '.'),
        (os.path.join(base_dir, 'modules.lab.json'), '.'),
        (os.path.join(base_dir, 'packaging', 'cellab.ico'), '.'),
    ],
    hiddenimports=[
        *skimage_imports,
        *sm_imports,
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
        # OCR
        'easyocr',
        'torch',
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
        # Heavy packages not needed for standard version
        'llama_cpp',
        'sentence_transformers',
        'chromadb',
        'trackpy',
        'cupy',
        'cupyx',
        'numba',
        'torchvision',
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
    name='CelLAB_Win64',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,       # Debug: show console to see errors
    disable_windowed_traceback=False,
    argv_emulation=False,
    icon=os.path.join(base_dir, 'packaging', 'cellab.ico') if sys.platform == 'win32' else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CelLAB_Win64',
)
