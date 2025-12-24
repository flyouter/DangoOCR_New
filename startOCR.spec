# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files
from PyInstaller.utils.hooks import collect_all
from PyInstaller.utils.hooks import copy_metadata
from PyInstaller.utils.hooks import collect_dynamic_libs

# ============ 必需的 CUDA DLL 列表（小写，便于匹配）============
REQUIRED_CUDA_DLLS = {
    'cublaslt64_12.dll',
    'cublas64_12.dll',
    'cudnn_cnn64_9.dll',
    'cudnn_engines_precompiled64_9.dll',
    'cudnn_engines_runtime_compiled64_9.dll',
    'cudnn_graph64_9.dll',
    'cudnn_heuristic64_9.dll',
    'cudnn_ops64_9.dll',
    'cudnn64_9.dll',
}

# ============ 初始化 ============
datas = [('models', 'models')]
binaries = []
hiddenimports = []

# 1. 收集 paddle 所有内容
tmp_ret = collect_all('paddle')
datas += tmp_ret[0]
binaries += tmp_ret[1]
hiddenimports += tmp_ret[2]

# 2. 收集 paddlex 数据
datas += collect_data_files('paddlex')

# 3. 收集 metadata
metadata_pkgs = [
    'aistudio-sdk', 'chardet', 'colorlog', 'filelock', 'imagesize', 'modelscope',
    'numpy', 'opencv-contrib-python', 'packaging', 'pandas', 'pillow', 'prettytable',
    'pyclipper', 'pydantic', 'pypdfium2', 'python-bidi', 'PyYAML', 'py-cpuinfo',
    'requests', 'ruamel.yaml', 'shapely', 'tqdm', 'ujson'
]
for pkg in metadata_pkgs:
    datas += copy_metadata(pkg)

# 4. 关键：收集 nvidia DLL，并过滤
nvidia_binaries = collect_dynamic_libs('nvidia')  # 收集所有 nvidia-* 包中的 DLL
filtered_nvidia_binaries = []
for bin_path, dest_dir in nvidia_binaries:
    dll_name = os.path.basename(bin_path).lower()
    if dll_name in REQUIRED_CUDA_DLLS:
        filtered_nvidia_binaries.append((bin_path, dest_dir))

binaries += filtered_nvidia_binaries

# ============ 构建 Analysis ============
a = Analysis(
    ['src\\app.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='startOCR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['ico\\logo.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='startOCR',
)