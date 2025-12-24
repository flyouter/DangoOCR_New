# DangoOCR New

## 项目描述

DangoOCR New 是基于 PaddlePaddle PP-OCRv5 的本地 OCR 解决方案，专为团子翻译器设计。它提供了高性能的文本识别能力，支持 GPU 加速和多语言识别，能够完全离线运行，保护用户隐私。

**主要优势**:
- 🔒 **完全离线**: 所有处理在本地完成，无需网络连接
- ⚡ **快速识别**: 利用 GPU 加速，处理速度快
- 🌍 **多语言支持**: 覆盖主流语言和特殊语系
- 🎯 **高准确率**: 基于最新的 PP-OCRv5 模型
- 🔧 **易于集成**: 与团子翻译器对接

## 特性

- 🚀 **高性能**: 基于 PP-OCRv5 最新模型，识别准确率高
- 🔧 **GPU 加速**: 支持 NVIDIA CUDA，大幅提升处理速度
- 🌐 **多语言**: 支持中文、英文、日文、韩文、斯拉夫语系等
- 📦 **易部署**: 一键打包，与团子翻译器无缝集成
- 🔌 **API 接口**: 提供 HTTP API，方便集成其他应用
- 🛠️ **可配置**: 支持多种模型切换，满足不同场景需求


## 快速开始

### 1. 环境准备

#### Windows (使用 UV)

```shell
# 创建虚拟环境
uv venv --python 3.12 --seed .venv_win

# 激活虚拟环境
.venv_win\Scripts\activate

# 安装基础依赖
uv pip install -r requirements.txt

# 安装 PaddlePaddle GPU 版本 (根据显卡选择)
# CUDA 12.6 版本 (推荐)
uv pip install paddlepaddle-gpu==3.2.0 -i https://www.paddlepaddle.org.cn/packages/stable/cu126/

# 或 NVIDIA 50 系显卡专用版本
uv pip install https://paddle-qa.bj.bcebos.com/paddle-pipeline/Develop-TagBuild-Training-Windows-Gpu-Cuda12.9-Cudnn9.9-Trt10.5-Mkl-Avx-VS2019-SelfBuiltPypiUse/86d658f56ebf3a5a7b2b33ace48f22d10680d311/paddlepaddle_gpu-3.0.0.dev20250717-cp312-cp312-win_amd64.whl
```

> **注意**:
> 1. 更多安装选项请参考 [PaddleOCR 官方安装文档](https://www.paddleocr.ai/latest/version3.x/installation.html)

### 2. 打包应用

```shell
.\.venv_win\Scripts\python.exe .\startOCR.spec
```

### 3. 部署到团子翻译器

1. 移除团子翻译器根目录下 `ocr` 文件夹中的所有文件
2. 将 `dist/startOCR` 目录下的所有文件复制到团子翻译器的 `ocr` 目录中

## 注意事项

- 由于团子翻译器最新版代码未开源，不知道为啥，本项目启动时会被固定使用 **6666** 端口
- GPU 版本需要正确安装 NVIDIA 驱动
- 模型文件较大，首次启动可能需要较长时间

## 支持的模型

项目内置以下 OCR 模型，可根据需求自动选择或手动指定：

| 模型名称 | 语言支持 | 用途 | 特点 |
|---------|----------|------|------|
| PP-OCRv5_server_det | 通用 | 文本检测 | 高精度检测，适合复杂场景 |
| PP-OCRv5_server_rec | 通用 | 文本识别 | 服务器级识别精度 |
| PP-OCRv5_mobile_rec | 通用 | 文本识别 | 移动端优化，速度快 |
| eslav_PP-OCRv5_mobile_rec | 斯拉夫语系（俄语等） | 文本识别 | 专门优化斯拉夫文字 |
| korean_PP-OCRv5_mobile_rec | 韩文 | 文本识别 | 专门优化韩文字符 |


## 开发

### 项目结构

```
DangoOCR_New/
├── src/                    # 源代码目录
│   └── app.py             # 主应用程序
├── models/                # OCR 模型目录
│   ├── PP-OCRv5_server_det/      # 服务器版文本检测模型
│   ├── PP-OCRv5_server_rec/      # 服务器版文本识别模型
│   ├── PP-OCRv5_mobile_rec/      # 移动端文本识别模型
│   ├── eslav_PP-OCRv5_mobile_rec/ # 斯拉夫语系模型
│   └── korean_PP-OCRv5_mobile_rec/ # 韩文模型
├── docs/                  # 文档目录
│   └── api_sample.md     # API 使用示例
├── ico/                   # 图标资源
│   └── logo.ico          # 应用图标
├── test/                  # 测试目录
├── requirements.txt       # Python 依赖
├── package.py            # 打包脚本
└── README.md             # 项目说明
```


## 许可证

本项目使用GNU LESSER GENERAL PUBLIC LICENSE(LGPL)开源协议

## 致谢

感谢以下项目和开发者的贡献：

- **[PaddlePaddle](https://www.paddlepaddle.org.cn/)** - 优秀的深度学习框架
- **[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR)** - 强大的 OCR 工具库
- **[团子翻译器](https://github.com/PantsuDango/Dango-Translator)团子翻译器开发者** - 提供了优秀的翻译工具
- **所有贡献者** - 感谢每一位为项目做出贡献的开发者