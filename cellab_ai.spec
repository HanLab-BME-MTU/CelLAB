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
llama_datas, llama_binaries, llama_imports = collect_all('llama_cpp')

a = Analysis(
    [os.path.join(base_dir, 'packaging', 'cellab_launcher.py')],
    pathex=[base_dir],
    binaries=[
        *skimage_binaries,
        *sm_binaries,
        *llama_binaries,
		# VC++ runtime DLLs for llama.cpp portability
	    (r'C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Redist\MSVC\14.51.36231\x64\Microsoft.VC145.CRT\msvcp140.dll', '.'),
		(r'C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Redist\MSVC\14.51.36231\x64\Microsoft.VC145.CRT\vcruntime140.dll', '.'),
		(r'C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Redist\MSVC\14.51.36231\x64\Microsoft.VC145.CRT\vcruntime140_1.dll', '.'),
		(r'C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Redist\MSVC\14.51.36231\x64\Microsoft.VC145.OpenMP\vcomp140.dll', '.'),
	],
    datas=[
        *skimage_datas,
        *sm_datas,
        *llama_datas,
        # Frontend
        (os.path.join(base_dir, 'frontend'), 'frontend'),
        # Backend modules (released only)
        (os.path.join(base_dir, 'backend', 'cornealia'), os.path.join('backend', 'cornealia')),
        (os.path.join(base_dir, 'backend', 'shared_modules'), os.path.join('backend', 'shared_modules')),
        (os.path.join(base_dir, 'backend', 'orchestrators'), os.path.join('backend', 'orchestrators')),
        (os.path.join(base_dir, 'backend', 'cellintella'), os.path.join('backend', 'cellintella')),
        (os.path.join(base_dir, 'docs'), 'docs'),
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
        *llama_imports,
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
        # AI assistant
        'llama_cpp',
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
        # Heavy packages not needed
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
    name='CelLAB_AI_Win64',
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
    name='CelLAB_AI_Win64',
)
