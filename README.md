# 智能中文网络小说生成系统

基于大语言模型的中文网络小说自动生成系统，支持世界观构建、角色创建、剧情设计和章节写作。现已集成 agno 代理框架，提供更高效的 AI 代理交互。

## 项目结构

```
novel_generator/
├── agents/                # LLM代理模块
│   ├── __init__.py
│   ├── world_builder_agent.py
│   ├── character_creator_agent.py
│   ├── plot_designer_agent.py
│   └── content_creator_agent.py
├── llm/                   # LLM接口模块
│   ├── __init__.py
│   ├── base.py
│   └── gemini.py
├── models/                # 数据模型模块
│   ├── __init__.py
│   ├── world.py
│   ├── character.py
│   └── plot.py
├── storage/               # 数据存储模块
│   ├── __init__.py
│   └── json_storage.py
├── tools/                 # 工具模块
│   ├── __init__.py
│   ├── world_tools.py
│   ├── character_tools.py
│   └── plot_tools.py
└── __init__.py            # 主包初始化文件
main.py                    # 主程序入口点
config.example.py          # 配置文件示例
requirements.txt           # 项目依赖
TROUBLESHOOTING.md         # 问题排查指南
```

## 主要功能

### 1. 数据模型

- **世界模型**：定义小说世界的结构和属性，包括历史、文化、地理、政治、经济等方面
- **角色模型**：定义小说角色的结构和属性，包括外貌、性格、背景、能力、关系等
- **剧情模型**：定义小说剧情的结构和属性，包括标题、背景、主线、转折点、章节等

### 2. 数据存储

- **JSON存储**：使用JSON文件存储世界、角色、剧情和章节数据
- **文本导出**：支持将生成的章节内容导出为文本文件

### 3. LLM代理

所有代理现已集成 agno 框架，提供更高效的 AI 代理交互：

- **世界构建代理**：与LLM交互生成丰富、一致的世界观
- **角色创建代理**：与LLM交互生成立体、深刻的角色
- **剧情设计代理**：与LLM交互生成引人入胜的剧情大纲
- **内容创建代理**：与LLM交互生成具体章节和场景内容

### 4. 工具模块

- **世界工具**：提供世界查询和修改功能，支持按路径获取世界观特定部分
- **角色工具**：提供角色查询和修改功能，支持按路径获取角色特定属性
- **剧情工具**：提供剧情查询和修改功能，支持获取特定章节信息

### 5. LLM接口

- **基类接口**：定义与LLM交互的标准接口
- **Gemini实现**：Google Gemini API的具体实现，支持最新的模型版本

### 6. 主程序

- **命令行界面**：提供创建和管理世界、角色、剧情的交互式界面
- **章节预览**：在生成章节后提供内容预览功能
- **多角色选择**：支持为剧情选择多个角色
- **文件导出**：自动将生成的章节导出为文本文件

## 使用方法

1. 克隆项目并安装依赖：

```bash
git clone https://github.com/your-username/novel-generator.git
cd novel-generator
pip install -r requirements.txt
```

2. 创建配置文件：

```bash
cp config.example.py config.py
```

3. 编辑配置文件，设置您的Gemini API密钥：

```python
GEMINI_API_KEY = "your-api-key-here"
GEMINI_MODEL = "gemini-1.5-pro"  # 使用最新的Gemini模型
```

4. 运行主程序：

```bash
python main.py
```

5. 界面操作流程：
   - 创建或选择世界观
   - 在世界观中创建角色
   - 选择多个角色创建剧情
   - 生成具体章节内容

## 代理框架集成

本项目现已集成 agno 代理框架，相比于传统的LLM调用方式，提供以下优势：

- **工具注册机制**：简化代理功能的定义和调用
- **状态管理**：更好地管理代理的状态和上下文
- **异步支持**：通过异步API提高性能
- **一致的接口**：所有代理使用统一的接口，便于扩展和维护

## 后续开发计划

1. 实现更丰富的用户界面，支持Web界面
2. 添加对多种LLM的支持，包括本地部署的模型
3. 增加数据库存储后端
4. 添加批量生成和导出功能
5. 实现更复杂的剧情规划和角色关系管理
6. 优化生成质量，增加风格调整功能
7. 添加角色对话生成功能
8. 支持用户手动编辑和修改自动生成的内容

## 故障排除

如果您在使用过程中遇到问题，请参考 `TROUBLESHOOTING.md` 文件，其中包含常见问题的解决方案。

## 贡献指南

欢迎贡献代码、报告问题或提出建议。请遵循以下步骤：

1. Fork本项目
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个Pull Request

## 许可证

[MIT](LICENSE) 