"""TaskGraph — 任務依賴圖解析與拓撲排序。

用於將複合任務拆解為有向無環圖（DAG），決定執行順序與並行機會。

Workshop 03 程式碼閱讀重點：
  - resolve_dependencies(): 判斷哪些任務可並行、哪些要等
  - topological_sort(): DAG 拓撲排序（Kahn's Algorithm）
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TaskNode:
    """任務圖中的節點。"""

    id: str
    title: str
    skill: str = ""
    depends_on: list[str] = field(default_factory=list)
    status: str = "pending"  # pending | ready | running | completed | failed
    assignee: str = ""
    result: dict = field(default_factory=dict)


class TaskGraph:
    """有向無環任務圖 — 支援依賴解析與並行調度。

    使用方式:
        graph = TaskGraph()
        graph.add_node(TaskNode(id="fetch", title="抓新聞", skill="news_scraper"))
        graph.add_node(TaskNode(id="analyze", title="分析", skill="llm_analyze", depends_on=["fetch"]))
        graph.add_node(TaskNode(id="render", title="渲染", skill="report_template", depends_on=["analyze"]))

        order = graph.topological_sort()
        # → ["fetch", "analyze", "render"]

        ready = graph.resolve_dependencies()
        # → ["fetch"] (只有無依賴的先執行)
    """

    def __init__(self) -> None:
        self._nodes: dict[str, TaskNode] = {}

    def add_node(self, node: TaskNode) -> None:
        """新增任務節點。"""
        self._nodes[node.id] = node

    def get_node(self, node_id: str) -> TaskNode | None:
        """取得節點。"""
        return self._nodes.get(node_id)

    @property
    def nodes(self) -> list[TaskNode]:
        """所有節點。"""
        return list(self._nodes.values())

    # ─── 核心方法 ────────────────────────────────────────

    def resolve_dependencies(self) -> list[str]:
        """解析當前可執行的任務（所有依賴已完成 + 自身狀態為 pending）。

        Returns:
            可立即執行的 task_id 列表（這些可以並行啟動）。
        """
        ready: list[str] = []
        for node in self._nodes.values():
            if node.status != "pending":
                continue
            # 檢查所有依賴是否已完成
            deps_satisfied = all(
                self._nodes[dep_id].status == "completed"
                for dep_id in node.depends_on
                if dep_id in self._nodes
            )
            if deps_satisfied:
                ready.append(node.id)
        return ready

    def topological_sort(self) -> list[str]:
        """Kahn's Algorithm — 拓撲排序。

        Returns:
            按依賴順序排列的 task_id 列表。

        Raises:
            ValueError: 若圖中有循環依賴。
        """
        # 計算每個節點的入度（被多少節點依賴）
        in_degree: dict[str, int] = {nid: 0 for nid in self._nodes}
        for node in self._nodes.values():
            for dep_id in node.depends_on:
                if dep_id in self._nodes:
                    in_degree[node.id] += 1  # 此節點等待 dep_id，入度+1

        # 入度為 0 的節點先入隊
        queue: list[str] = [nid for nid, deg in in_degree.items() if deg == 0]
        result: list[str] = []

        while queue:
            current = queue.pop(0)
            result.append(current)

            # 移除 current 的出邊：找所有依賴 current 的節點
            for node in self._nodes.values():
                if current in node.depends_on:
                    in_degree[node.id] -= 1
                    if in_degree[node.id] == 0:
                        queue.append(node.id)

        if len(result) != len(self._nodes):
            raise ValueError("TaskGraph 有循環依賴，無法排序")

        return result

    # ─── 輔助方法 ────────────────────────────────────────

    def mark_completed(self, node_id: str, result: dict | None = None) -> None:
        """標記節點已完成。"""
        node = self._nodes.get(node_id)
        if node:
            node.status = "completed"
            node.result = result or {}

    def mark_failed(self, node_id: str, error: str = "") -> None:
        """標記節點失敗。"""
        node = self._nodes.get(node_id)
        if node:
            node.status = "failed"
            node.result = {"error": error}

    def mark_running(self, node_id: str, assignee: str = "") -> None:
        """標記節點執行中。"""
        node = self._nodes.get(node_id)
        if node:
            node.status = "running"
            node.assignee = assignee

    def get_execution_plan(self) -> list[list[str]]:
        """取得分層執行計畫（每層可並行）。

        Returns:
            二維列表，每個子列表中的任務可同時執行。
            例如: [["fetch"], ["analyze", "summarize"], ["render"]]
        """
        layers: list[list[str]] = []
        completed: set[str] = set()
        remaining = set(self._nodes.keys())

        while remaining:
            # 找出本輪可執行的（依賴都在 completed 中）
            layer: list[str] = []
            for nid in remaining:
                node = self._nodes[nid]
                deps_done = all(d in completed for d in node.depends_on if d in self._nodes)
                if deps_done:
                    layer.append(nid)

            if not layer:
                raise ValueError("TaskGraph 有循環依賴")

            layers.append(sorted(layer))
            completed.update(layer)
            remaining -= set(layer)

        return layers

    def to_dict(self) -> dict:
        """序列化為 dict。"""
        return {
            "nodes": [
                {
                    "id": n.id,
                    "title": n.title,
                    "skill": n.skill,
                    "depends_on": n.depends_on,
                    "status": n.status,
                    "assignee": n.assignee,
                }
                for n in self._nodes.values()
            ]
        }
