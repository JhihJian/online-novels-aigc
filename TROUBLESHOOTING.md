# 故障排除指南

本文档提供了运行智能中文网络小说生成系统时可能遇到的常见问题及其解决方案。

## 1. "models/gemini-pro is not found" 错误

### 问题描述

当运行程序时，出现类似以下错误：

```
google.api_core.exceptions.NotFound: 404 models/gemini-pro is not found for API version v1beta, or is not supported for generateContent.
```

### 解决方案

这个错误通常是因为 Google Gemini API 的模型名称变更导致的。Google 会定期更新他们的模型，有时会弃用旧模型。

1. **更新 config.py 中的模型名称**:
   
   打开 `config.py` 文件，找到 `GEMINI_MODEL` 设置，将其更改为最新可用的模型名称：
   
   ```python
   GEMINI_MODEL = "gemini-1.5-pro"  # 或其他可用的 Gemini 模型
   ```

2. **检查可用模型**:
   
   运行程序时，系统会自动列出可用的模型。请注意控制台输出中的 "可用模型" 信息，选择一个适合的模型。

3. **确认 API 密钥有效**:
   
   确保您的 `GEMINI_API_KEY` 设置正确，并且有权访问 Gemini API。

## 2. API 密钥相关问题

### 问题描述

出现类似下面的错误：

```
API key not valid
```

### 解决方案

1. **获取新的 API 密钥**:
   
   访问 [Google AI Studio](https://makersuite.google.com/app/apikey) 获取新的 API 密钥。

2. **正确设置 API 密钥**:
   
   在 `config.py` 文件中设置您的 API 密钥：
   
   ```python
   GEMINI_API_KEY = "YOUR_ACTUAL_API_KEY_HERE"
   ```

3. **检查地区限制**:
   
   确认您所在地区支持 Gemini API。某些地区可能有限制。

## 3. 导入错误

### 问题描述

出现类似以下错误：

```
ImportError: cannot import name 'X' from 'Y'
```

### 解决方案

1. **确保安装了所有依赖**:
   
   运行以下命令重新安装所有依赖：
   
   ```bash
   pip install -r requirements.txt
   ```

2. **检查项目结构**:
   
   确保项目文件结构完整，所有必要的文件都存在。

3. **更新 Google Generative AI 库**:
   
   更新到最新版本的库：
   
   ```bash
   pip install --upgrade google-generativeai
   ```

## 4. 数据存储问题

### 问题描述

无法保存或加载数据，出现权限错误或找不到目录。

### 解决方案

1. **检查数据目录**:
   
   确保 `config.py` 中的 `DATA_DIR` 设置正确，且程序有权限访问该目录：
   
   ```python
   DATA_DIR = "./data"  # 或您希望存储数据的其他路径
   ```

2. **手动创建目录**:
   
   如果系统无法自动创建目录，请手动创建：
   
   ```bash
   mkdir -p data/worlds data/characters data/plots data/novels
   ```

3. **检查文件权限**:
   
   确保当前用户对数据目录有读写权限。

## 联系支持

如果您遇到的问题未在本文档中列出，请提交 GitHub issue 或联系项目维护者获取支持。 