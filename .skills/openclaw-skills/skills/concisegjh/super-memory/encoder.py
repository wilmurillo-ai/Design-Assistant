"""
encoder.py - 维度编码器
负责将维度值编码为 memory_id，查注册表
"""

import json
import hashlib
from datetime import datetime
from pathlib import Path

REGISTRY_PATH = Path(__file__).parent / "registry" / "dimensions.json"


class DimensionEncoder:
    def __init__(self, registry_path: str = None):
        path = Path(registry_path) if registry_path else REGISTRY_PATH
        with open(path, "r", encoding="utf-8") as f:
            self.registry = json.load(f)
        # 建反向索引：code → id
        self._nature_by_code = {}
        for nid, info in self.registry["natures"].items():
            self._nature_by_code[info["code"]] = nid

    # ── 时间编码 ──────────────────────────────────────────

    def encode_time(self, ts: float = None, precision: str = "second") -> str:
        """生成时间编码
        precision: 'second' → T20260411.213742
                   'minute' → T20260411.2137
        """
        dt = datetime.fromtimestamp(ts) if ts else datetime.now()
        if precision == "minute":
            return f"T{dt.strftime('%Y%m%d.%H%M')}"
        return f"T{dt.strftime('%Y%m%d.%H%M%S')}"

    # ── 人物编码 ──────────────────────────────────────────

    def encode_person(self, person_id: str) -> str:
        """直接用注册表里的 ID，如 P01"""
        if person_id not in self.registry["persons"]:
            raise ValueError(f"未注册的人物 ID: {person_id}，请先在 dimensions.json 中注册")
        return person_id

    def get_person_by_code(self, code: str) -> str:
        """通过 code 查 person_id"""
        for pid, info in self.registry["persons"].items():
            if info["code"] == code:
                return pid
        raise ValueError(f"未找到 code={code} 的人物")

    # ── 主题编码 ──────────────────────────────────────────

    def encode_topic(self, topic_path: str) -> str:
        """主题路径直接作为编码，如 ai.rag.vdb"""
        parts = topic_path.split(".")
        node = self.registry["topics"]
        for p in parts:
            if p not in node:
                raise ValueError(f"未注册的主题路径: {topic_path}，请先在 dimensions.json 中注册")
            if "children" in node[p]:
                node = node[p]["children"]
            elif p != parts[-1]:
                raise ValueError(f"主题路径不完整: {topic_path}")
        return topic_path

    def list_topics(self, prefix: str = "") -> list:
        """列出所有主题路径"""
        results = []
        self._walk_topics(self.registry["topics"], prefix, results)
        return results

    def _walk_topics(self, node, path, results):
        for key, val in node.items():
            full = f"{path}.{key}" if path else key
            if "children" in val:
                self._walk_topics(val["children"], full, results)
            else:
                results.append(full)

    # ── 性质编码 ──────────────────────────────────────────

    def encode_nature(self, nature_code: str) -> str:
        """通过 code（如 'explore'）查找 D 编码"""
        if nature_code in self._nature_by_code:
            return self._nature_by_code[nature_code]
        # 也支持直接传 D 编码
        if nature_code in self.registry["natures"]:
            return nature_code
        raise ValueError(f"未注册的性质: {nature_code}")

    # ── 知识类型编码 ──────────────────────────────────────

    def encode_knowledge(self, knowledge_code: str) -> str:
        """通过 code（如 'rule'）查找 K 编码"""
        for kid, info in self.registry["knowledge_types"].items():
            if info["code"] == knowledge_code:
                return kid
        # 也支持直接传 K 编码
        if knowledge_code in self.registry["knowledge_types"]:
            return knowledge_code
        raise ValueError(f"未注册的知识类型: {knowledge_code}")

    # ── 重要度编码 ──────────────────────────────────────────

    VALID_IMPORTANCE = ("high", "medium", "low")

    def encode_importance(self, level: str) -> str:
        """校验并返回 importance 值"""
        if level not in self.VALID_IMPORTANCE:
            raise ValueError(f"未注册的重要度: {level}，可选: {self.VALID_IMPORTANCE}")
        return level

    # ── 工具编码 ──────────────────────────────────────────

    def encode_tool(self, tool_id: str) -> str:
        """直接用注册表里的工具 ID，如 t_lc"""
        if tool_id not in self.registry["tools"]:
            raise ValueError(f"未注册的工具 ID: {tool_id}，请先在 dimensions.json 中注册")
        return tool_id

    def get_tool_by_code(self, code: str) -> str:
        """通过 code 查 tool_id"""
        for tid, info in self.registry["tools"].items():
            if info["code"] == code:
                return tid
        raise ValueError(f"未找到 code={code} 的工具")

    # ── Memory ID 生成 ────────────────────────────────────

    def generate_memory_id(
        self,
        time_id: str,
        person_id: str,
        topic_codes: list[str],
        nature_id: str,
        tool_ids: list[str] = None,
    ) -> str:
        """组合维度生成唯一 memory_id
        格式: T20260411.213742_P01_rag.vdb_D04_lc.ch
        """
        # 主题取主主题（第一个）
        primary_topic = topic_codes[0] if topic_codes else "none"
        # 短化：去掉顶层前缀 ai./dev./life.
        for prefix in ("ai.", "dev.", "life."):
            if primary_topic.startswith(prefix):
                primary_topic = primary_topic[len(prefix):]
                break

        # 工具缩写（取前两个）
        tool_part = ""
        if tool_ids:
            tool_codes = []
            for tid in tool_ids[:2]:
                info = self.registry["tools"].get(tid, {})
                tool_codes.append(info.get("code", tid))
            tool_part = "." + "+".join(tool_codes)

        raw = f"{time_id}_{person_id}_{primary_topic}_{nature_id}{tool_part}"

        # 如果组合太长，末尾加 hash 短码保证唯一
        if len(raw) > 64:
            h = hashlib.sha256(raw.encode()).hexdigest()[:6]
            raw = f"{raw[:58]}_{h}"

        return raw

    @staticmethod
    def content_hash(content: str) -> str:
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    enc = DimensionEncoder()
    print("=== 性质列表 ===")
    for nid, info in enc.registry["natures"].items():
        print(f"  {nid} ({info['code']:8s}) → {info['name']}  {info['desc']}")

    print("\n=== 主题树 ===")
    for t in enc.list_topics():
        print(f"  {t}")

    print("\n=== 示例编码 ===")
    tid = enc.encode_time(precision="second")
    mid = enc.generate_memory_id(
        time_id=tid,
        person_id="P01",
        topic_codes=["ai.rag.vdb"],
        nature_id=enc.encode_nature("explore"),
        tool_ids=["t_ch", "t_lc"],
    )
    print(f"  memory_id = {mid}")
