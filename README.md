# 智能中文网络小说生成系统

基于大语言模型的中文网络小说自动生成系统，支持世界观构建、角色创建、剧情设计和章节写作。

## 项目结构

```
novel_generator/
├── agents/                # LLM代理模块
│   ├── __init__.py
│   ├── world_builder_agent.py
│   ├── character_creator_agent.py
│   ├── plot_designer_agent.py
│   └── chapter_writer_agent.py
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
```

## 实现功能

### 1. 数据模型

- **世界模型**：定义小说世界的结构和属性
- **角色模型**：定义小说角色的结构和属性
- **剧情模型**：定义小说剧情的结构和属性

### 2. 数据存储

- **JSON存储**：使用JSON文件存储世界、角色和剧情数据

### 3. LLM代理

- **世界构建代理**：与LLM交互生成世界观
- **角色创建代理**：与LLM交互生成角色
- **剧情设计代理**：与LLM交互生成剧情
- **章节写作代理**：与LLM交互生成章节内容

### 4. 工具模块

- **世界工具**：提供世界查询和修改功能
- **角色工具**：提供角色查询和修改功能
- **剧情工具**：提供剧情查询和修改功能

### 5. LLM接口

- **基类接口**：定义与LLM交互的标准接口
- **Gemini实现**：Google Gemini API的具体实现

### 6. 主程序

- **命令行界面**：提供创建和管理世界、角色、剧情的功能

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
```

4. 运行主程序：

```bash
python main.py
```

## 后续开发计划

1. 实现更丰富的用户界面，支持Web界面
2. 添加对多种LLM的支持，包括本地部署的模型
3. 增加数据库存储后端
4. 添加批量生成和导出功能
5. 实现更复杂的剧情规划和角色关系管理
6. 优化生成质量，增加风格调整功能

## 贡献指南

欢迎贡献代码、报告问题或提出建议。请遵循以下步骤：

1. Fork本项目
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 打开一个Pull Request

## 许可证

[MIT](LICENSE) 