import paddlex
import importlib.metadata
import argparse
import subprocess
import sys
import os

parser = argparse.ArgumentParser()
parser.add_argument('--file', required=True, help='Your main Python file, e.g., main.py.')
parser.add_argument('--nvidia', action='store_true', help='Include NVIDIA CUDA dependencies (Linux only).')
# parser.add_argument('--onefile', action='store_true', help='Create a single-file executable.')
parser.add_argument('--name', type=str, help='Name for the executable (sets --name for PyInstaller).')
parser.add_argument('--icon', type=str, help='Path to .ico file for the executable icon.')

args = parser.parse_args()
main_file = args.file

# 构建基础命令
cmd = ["pyinstaller"]

# 添加 --name（如果提供）
if args.name:
    cmd += ["--name", args.name]

# 添加 --onefile
# if args.onefile:
#     cmd += ["--onefile"]

# 添加主文件
cmd += [main_file]

# 添加图标（如果提供）
if args.icon:
    if not os.path.exists(args.icon):
        print(f"Error: Icon file not found: {args.icon}")
        sys.exit(1)
    cmd += ["--icon", args.icon]

# 必要的依赖收集
cmd += [
    "--collect-data", "paddlex",
    "--collect-all", "paddle"
]

# NVIDIA 支持（仅 Linux 有效）
if args.nvidia:
    cmd += ["--collect-binaries", "nvidia"]

# 复制元数据
user_deps = [dist.metadata["Name"] for dist in importlib.metadata.distributions()]
deps_all = list(paddlex.utils.deps.BASE_DEP_SPECS.keys())
deps_need = [dep for dep in user_deps if dep in deps_all]
for dep in deps_need:
    cmd += ["--copy-metadata", dep]

print("PyInstaller command:", " ".join(cmd))

try:
    result = subprocess.run(cmd, check=True)
except subprocess.CalledProcessError as e:
    print("PyInstaller failed:", e)
    sys.exit(1)