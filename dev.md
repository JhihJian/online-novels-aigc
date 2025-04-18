goal: implement a agent to write chinese online novels using agno and gemini api


为了实现使用 Agno 代理编写在线中文小说的目标,该程序应实现以下能力
世界观与设定：
构建清晰且富有吸引力的世界观，包括详细的背景设定、独特的种族、势力划分、以及完整的力量体系。
确保世界观的逻辑一致性，避免出现前后矛盾。
人物塑造：
塑造鲜明且具有深度的角色，每个角色都应有独特的性格、动机和成长轨迹。
避免角色过于脸谱化，注重人物内心的复杂性和矛盾性。
确保人物前后性格发展逻辑一致。
情节推进：
设计紧凑且具有吸引力的情节，设置足够的悬念和冲突，保持读者的阅读兴趣。
合理安排剧情节奏，避免过于平淡或过于激烈的剧情。
在主线剧情中，合理的穿插支线剧情，丰富小说内容。
文笔与风格：
使用流畅且具有感染力的文笔，注意语言的准确性和生动性。
根据小说类型，调整合适的写作风格，例如：玄幻小说的恢弘大气，或者都市小说的轻松幽默。
避免出现语法错误。
创新与特色：
在遵循网络小说创作规律的基础上，融入独特的创意和元素，避免内容过于同质化。
挖掘新的题材和角度，为读者带来新鲜感。
读者互动：
在创作过程中要考虑读者的反馈，合理的调整写作内容。
要考虑读者的爽点。




网络小说生成器的功能逻辑大体上应该是这样的：

首先是作家agent的工作流程
1. 用户提供一段描述，agent通过描述丰富创建世界观，调用工具将创建的世界观存储起来，并支持通过工具查询
2. 生成剧情大纲，和主要角色设定，调用工具将剧情大纲和人物设定存储起来，并支持通过工具查询
3. 依据大纲，生成小说内容

更详细的说就是

世界观构建与管理：

详细的世界观属性：
除了基本的地理、历史、种族、势力、力量体系外，还应包括文化、宗教、经济、科技等更详细的属性。
这些属性可以通过结构化的数据（例如 JSON 或 XML）存储，以便于代理进行查询和推理。
世界观的动态演化：
世界观不是静态的，而是随着剧情的推进而不断演化的。
代理应能够根据剧情发展，动态地更新世界观信息。
世界观的冲突与矛盾：
世界观内部应存在一定的冲突和矛盾，例如不同势力之间的争斗、不同文化之间的冲突等。
这些冲突和矛盾可以为剧情提供丰富的素材。
2. 剧情大纲和人物设定：

详细的剧情大纲：
剧情大纲应包括主要情节、转折点、高潮、结局等。
可以使用流程图或时间线等可视化工具，展示剧情的结构和发展。
多维度的人物设定：
人物设定不仅包括外貌、性格、背景，还应包括人物的动机、目标、价值观等。
人物关系图谱可以帮助代理理解人物之间的互动。
人物的成长与变化：
人物在剧情中应有成长和变化，例如性格的转变、能力的提升等。
代理应能够跟踪人物的成长轨迹，确保人物的转变是合理的。
3. 小说内容生成：

情节驱动的生成：
小说内容生成应以剧情大纲为基础，确保情节的连贯性和逻辑性。
代理应能够根据当前情节，选择合适的场景、人物和对话。
文笔风格控制：
代理应能够根据小说类型和读者喜好，调整文笔风格。
可以使用预定义的文笔风格模板，或者根据用户反馈动态调整。
读者互动与反馈：
在小说生成过程中，应考虑读者的反馈，例如评论、投票、打赏等。
代理应能够根据读者反馈，调整小说内容和情节走向。
创新元素的融入：
代理应该有能力，根据用户给出的主题，或者读者喜好，生成一些创新元素。