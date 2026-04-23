"""
detector.py - 主题检测与智能拆分
基于规则 + 相似度 + LLM 的对话主题识别和多主题拆分
"""

import json
import logging
from encoder import DimensionEncoder

logger = logging.getLogger(__name__)


class TopicDetector:
    """基于关键词 + 语义向量相似度的主题检测"""

    def __init__(self, encoder: DimensionEncoder, topic_registry=None, semantic_matcher=None):
        self.encoder = encoder
        self.topic_keywords = self._build_keyword_map()
        self.topic_registry = topic_registry  # TopicRegistry 实例，可选
        self.semantic_matcher = semantic_matcher  # SemanticTopicMatcher 实例，可选

        # 把 detector 的关键词同步给 registry
        if self.topic_registry:
            self.topic_registry.merge_keywords(self.topic_keywords)

    def _build_keyword_map(self) -> dict[str, list[str]]:
        """从主题树构建关键词映射"""
        return {
            "ai.rag":       ["rag", "检索增强", "向量库", "embedding", "检索", "RAG"],
            "ai.rag.vdb":   ["向量库", "向量数据库", "milvus", "chroma", "qdrant", "pgvector", "faiss", "选型"],
            "ai.rag.emb":   ["embedding", "向量化", "编码器", "sentence-transformer", "bge", "jina"],
            "ai.rag.ret":   ["检索", "召回", "rerank", "重排序", "混合检索", "bm25"],
            "ai.agent":     ["agent", "智能体", "工具调用", "function call"],
            "ai.agent.mem": ["记忆", "memory", "上下文", "回忆", "记忆系统"],
            "ai.agent.tool":["工具", "tool", "skill", "技能"],
            "ai.llm":       ["llm", "大模型", "gpt", "claude", "qwen", "大语言模型"],
            "ai.llm.prompt":["prompt", "提示词", "提示工程"],
            "dev.be":       ["后端", "api", "server", "数据库", "sql", "接口"],
            "dev.fe":       ["前端", "vue", "react", "css", "html"],
            "dev.ops":      ["运维", "docker", "部署", "ci/cd", "k8s", "容器化"],
        }

    def detect(self, text: str, auto_register: bool = False) -> list[str]:
        """
        检测文本涉及的主题，返回主题路径列表（主主题在前）。

        匹配优先级:
        1. 关键词子串匹配（最快）
        2. 语义向量相似度（SemanticTopicMatcher）
        3. TopicRegistry 关键词相似度回退
        4. 动态注册新主题

        参数:
            text: 对话文本
            auto_register: 是否在无匹配时自动注册新主题
        """
        text_lower = text.lower()

        # ── 第一层：关键词子串匹配 ─────────────────────
        scores: dict[str, int] = {}
        for topic, keywords in self.topic_keywords.items():
            for kw in keywords:
                if kw in text_lower:
                    scores[topic] = scores.get(topic, 0) + 1

        if scores:
            sorted_topics = sorted(scores.keys(), key=lambda t: (-scores[t], -len(t)))
            result = []
            for topic in sorted_topics:
                is_child = any(topic.startswith(r + ".") for r in result)
                is_parent = any(r.startswith(topic + ".") for r in result)
                if not is_child and not is_parent:
                    result.append(topic)
            return result

        # ── 第二层：语义向量相似度匹配 ─────────────────
        if self.semantic_matcher:
            semantic_hits = self.semantic_matcher.match(text, top_k=1, threshold=0.35)
            if semantic_hits:
                best = semantic_hits[0]
                topic_path = best["topic"]
                score = best["score"]
                logger.info(f"🧠 语义匹配: {topic_path} (score={score:.3f})")
                return [topic_path]

        # ── 第三层：TopicRegistry 关键词相似度 ─────────
        if self.topic_registry:
            reg_result = self.topic_registry.auto_register(text)
            if reg_result["is_new"] and auto_register:
                # 自动注册了新主题，同步到关键词映射
                new_path = reg_result["path"]
                kws = reg_result.get("keywords", [])
                if kws:
                    self.topic_keywords[new_path] = kws
                # 同步到语义匹配器
                if self.semantic_matcher:
                    self.semantic_matcher.add_topic_vector(new_path, kws)
                logger.info(f"🆕 动态注册新主题: {new_path} (相似度={reg_result['similarity']:.2f})")
                return [new_path]
            elif reg_result["matched"]:
                return [reg_result["path"]]
            elif auto_register:
                # 创建新主题
                new_path = reg_result["path"]
                reg = self.topic_registry.register_topic(
                    topic_path=new_path,
                    keywords=self.topic_registry._extract_keywords(text),
                )
                if reg["keywords"]:
                    self.topic_keywords[new_path] = reg["keywords"]
                # 同步到语义匹配器
                if self.semantic_matcher:
                    self.semantic_matcher.add_topic_vector(new_path, reg["keywords"])
                logger.info(f"🆕 动态注册新主题: {new_path} (相似度={reg_result['similarity']:.2f})")
                return [new_path]

        return []

    def detect_nature(self, text: str) -> str:
        """简单规则判断性质"""
        text_lower = text.lower()

        # 关键词匹配
        if any(w in text_lower for w in ["计划", "打算", "准备", "明天", "接下来"]):
            return "todo"
        if any(w in text_lower for w in ["总结", "回顾", "复盘", "反思", "教训"]):
            return "retro"
        if any(w in text_lower for w in ["笔记", "记录", "学到", "知识点"]):
            return "note"
        if any(w in text_lower for w in ["草稿", "初步", "随便想想", "临时"]):
            return "draft"
        if any(w in text_lower for w in ["完成了", "交付", "成果", "最终版"]):
            return "output"
        if any(w in text_lower for w in ["收藏", "保存", "参考", "链接"]):
            return "archive"
        if "?" in text or "？" in text or any(w in text_lower for w in ["怎么", "什么是", "为什么", "如何"]):
            return "ask"
        if any(w in text_lower for w in ["项目", "任务", "开发", "实现"]):
            return "task"
        if any(w in text_lower for w in ["研究", "调研", "探索", "对比"]):
            return "explore"
        if any(w in text_lower for w in ["配置", "设置", "系统", "环境"]):
            return "config"

        return "chat"  # 默认漫谈

    def detect_knowledge(self, text: str) -> list[str]:
        """检测文本包含的知识类型，返回 code 列表"""
        text_lower = text.lower()
        types = []

        # 规则：条件句式
        if any(w in text_lower for w in ["当……时", "如果……就", "一定要", "必须", "不能", "规则是"]):
            types.append("rule")

        # 教训：失败/踩坑
        if any(w in text_lower for w in ["踩坑", "教训", "失败", "不行", "错误", "问题在于", "因为……所以"]):
            types.append("lesson")

        # 事实：陈述句
        if any(w in text_lower for w in ["是", "等于", "意味着", "事实", "确定", "已知"]):
            # 避免和规则/教训重叠
            if "rule" not in types and "lesson" not in types:
                types.append("fact")

        # 技能：操作/方法
        if any(w in text_lower for w in ["怎么", "如何", "步骤", "方法", "做法", "操作"]):
            types.append("skill")

        # 偏好：比较/选择
        if any(w in text_lower for w in ["更喜欢", "偏好", "比起", "选择", "倾向", "推荐"]):
            types.append("pref")

        # 经历：做过/试过
        if any(w in text_lower for w in ["做过", "试过", "用过", "体验", "经历", "以前"]):
            types.append("exp")

        return types


class TopicSplitter:
    """多主题拆分器 — 接入 LLM 智能拆分一段话里的多个主题"""

    SPLIT_PROMPT = """你是一个对话分析器。请将以下对话内容按主题拆分为独立片段。

可用主题路径：{topics}
可用工具：{tools}
可用性质：draft, log, task, explore, note, output, todo, archive, retro, config, chat, ask
可用知识类型：rule, lesson, fact, skill, pref, exp

对话内容：
{content}

要求：
1. 如果整段话只有一个主题，返回 1 个元素即可
2. 如果包含多个主题（如"RAG 用 Chroma 挺好，另外明天3点开会"），拆成多段
3. 每个片段尽量完整、可独立理解
4. topic 选最匹配的路径，不要猜
5. nature 和 knowledge 是 code 列表

以 JSON 数组返回，每个元素：
{{"content": "片段原文", "topic": "主题路径", "nature": "性质code", "tools": ["工具code"], "knowledge": ["知识type code"]}}
"""

    def __init__(self, encoder: DimensionEncoder, llm_fn=None):
        """
        encoder: DimensionEncoder 实例
        llm_fn: LLM 调用函数，签名 fn(prompt: str) -> str
                 如果为 None，拆分功能不可用，会回退到单片段
        """
        self.encoder = encoder
        self.llm_fn = llm_fn

    def split(self, content: str) -> list[dict]:
        """
        对一段对话进行多主题拆分。

        如果没有 llm_fn，返回单片段（回退到关键词检测）。
        如果有 llm_fn，调用 LLM 拆分并解析结果。
        """
        if not self.llm_fn:
            # 回退：不做拆分，直接返回单片段
            return [{
                "content": content,
                "topic": "",
                "nature": "",
                "tools": [],
                "knowledge": [],
            }]

        prompt = self._build_prompt(content)
        response = self.llm_fn(prompt)
        return self._parse_response(response)

    def _build_prompt(self, content: str) -> str:
        topics = ", ".join(self.encoder.list_topics())
        tools = ", ".join(
            f"{v['code']}({k})" for k, v in self.encoder.registry["tools"].items()
        )
        return self.SPLIT_PROMPT.format(topics=topics, tools=tools, content=content)

    def _parse_response(self, response: str) -> list[dict]:
        """解析 LLM 返回的 JSON"""
        try:
            cleaned = response.strip()
            if cleaned.startswith("```"):
                cleaned = cleaned.split("\n", 1)[1]
            if cleaned.endswith("```"):
                cleaned = cleaned.rsplit("```", 1)[0]
            return json.loads(cleaned.strip())
        except (json.JSONDecodeError, IndexError):
            return [{"content": response, "topic": "", "nature": "chat", "tools": [], "knowledge": []}]
