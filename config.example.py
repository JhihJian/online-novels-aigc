"""
配置文件示例。
使用时请复制为 config.py 并填写您的实际配置。
"""

# ========================
# LLM模型配置
# ========================

# Gemini API配置
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # 您的Gemini API密钥
GEMINI_MODEL = "gemini-pro"  # 使用的模型，默认为gemini-pro
GEMINI_GENERATION_CONFIG = {
    "temperature": 0.7,       # 温度参数，控制随机性
    "top_p": 0.95,            # Top-p采样
    "top_k": 40,              # Top-k采样
    "max_output_tokens": 4096, # 最大输出令牌数
}

# ========================
# 数据存储配置
# ========================

# 默认使用JSON文件存储
STORAGE_TYPE = "json"         # 存储类型: "json" 或 "database"
STORAGE_PATH = "data"         # 存储路径

# 数据库配置（如果使用数据库存储）
# DATABASE_URL = "sqlite:///novel_generator.db"  # SQLite数据库URL
# DATABASE_URL = "postgresql://user:password@localhost/novel_generator"  # PostgreSQL数据库URL

# ========================
# 应用程序配置
# ========================

# 日志配置
LOG_LEVEL = "INFO"            # 日志级别: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "novel_generator.log"  # 日志文件路径

# UI配置
TERMINAL_COLORS_ENABLED = True  # 是否启用终端彩色输出
MAX_OUTPUT_WIDTH = 100          # 终端输出的最大宽度

# ========================
# 系统行为配置
# ========================

# 并发配置
MAX_CONCURRENT_TASKS = 3      # 最大并发任务数

# 缓存配置
ENABLE_CACHE = True           # 是否启用缓存
CACHE_TTL = 3600              # 缓存生存时间（秒）

# 开发模式配置
DEBUG_MODE = False            # 是否启用调试模式

# 系统配置
DEBUG = True

# 数据存储配置
DATA_DIR = "./data"
DB_PATH = "./data/novel.db"  # SQLite数据库路径

# 应用配置
DEFAULT_LANGUAGE = "zh-CN"
MAX_CHAPTER_LENGTH = 3000  # 默认章节字数限制
MAX_CHAPTERS = 50  # 默认最大章节数

# 文本生成配置
TEMPERATURE = 0.7  # 创意度：0.0-1.0
TOP_P = 0.9  # 词汇多样性：0.0-1.0 