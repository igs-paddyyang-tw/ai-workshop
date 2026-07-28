"use client";
import useSWR, { mutate } from "swr";
import { fetcher, api } from "@/lib/api";
import { useState } from "react";

const priorityLabel: Record<number, { icon: string; color: string }> = {
  1: { icon: "🔴", color: "text-red-400" },
  2: { icon: "🟠", color: "text-orange-400" },
  3: { icon: "🔵", color: "text-blue-400" },
  4: { icon: "⚪", color: "text-slate-400" },
};

export default function QueuePage() {
  const { data: queue } = useSWR("/api/admin/queue", fetcher, { refreshInterval: 5000 });
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [batchAgent, setBatchAgent] = useState("");

  async function setPriority(id: string, priority: number) {
    await api.patch(`/api/admin/queue/${id}/priority?priority=${priority}`, {});
    mutate("/api/admin/queue");
  }

  function toggleSelect(id: string) {
    setSelected((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }

  function selectAll() {
    if (!queue) return;
    if (selected.size === queue.length) {
      setSelected(new Set());
    } else {
      setSelected(new Set(queue.map((i: any) => i.id)));
    }
  }

  async function batchAssign() {
    if (!batchAgent || selected.size === 0) return;
    await api.post("/api/admin/queue/batch", {
      action: "assign",
      issue_ids: Array.from(selected),
      params: { agent: batchAgent },
    });
    setSelected(new Set());
    setBatchAgent("");
    mutate("/api/admin/queue");
  }

  async function batchCancel() {
    if (selected.size === 0) return;
    if (!confirm(`確定取消 ${selected.size} 個任務？`)) return;
    await api.post("/api/admin/queue/batch", {
      action: "cancel",
      issue_ids: Array.from(selected),
    });
    setSelected(new Set());
    mutate("/api/admin/queue");
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Queue</h2>
      <p className="text-slate-400 text-sm">{queue?.length || 0} pending items</p>

      {/* Batch Actions */}
      {selected.size > 0 && (
        <div className="flex items-center gap-3 bg-slate-800/50 border border-slate-700 rounded-lg px-4 py-2">
          <span className="text-sm text-cyan-400">{selected.size} selected</span>
          <input
            placeholder="Agent name..."
            value={batchAgent}
            onChange={(e) => setBatchAgent(e.target.value)}
            className="px-2 py-1 bg-slate-800 border border-slate-700 rounded text-xs w-36"
          />
          <button
            onClick={batchAssign}
            disabled={!batchAgent}
            className="px-3 py-1 text-xs bg-cyan-900 hover:bg-cyan-800 text-cyan-300 rounded border border-cyan-700 disabled:opacity-50"
          >
            指派
          </button>
          <button
            onClick={batchCancel}
            className="px-3 py-1 text-xs bg-red-900 hover:bg-red-800 text-red-300 rounded border border-red-700"
          >
            取消
          </button>
          <button
            onClick={() => setSelected(new Set())}
            className="px-3 py-1 text-xs text-slate-400 hover:text-slate-200"
          >
            清除選取
          </button>
        </div>
      )}

      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-left text-slate-400">
              <th className="px-4 py-3 w-8">
                <input
                  type="checkbox"
                  checked={queue?.length > 0 && selected.size === queue?.length}
                  onChange={selectAll}
                  className="rounded bg-slate-700 border-slate-600"
                />
              </th>
              <th className="px-4 py-3">Priority</th>
              <th className="px-4 py-3">Title</th>
              <th className="px-4 py-3">Assignee</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {(!queue || queue.length === 0) && (
              <tr><td colSpan={5} className="px-4 py-8 text-center text-slate-500">佇列為空 ✨</td></tr>
            )}
            {queue?.map((item: any) => {
              const p = priorityLabel[item.priority] || priorityLabel[3];
              return (
                <tr key={item.id} className={`hover:bg-slate-800/30 ${selected.has(item.id) ? "bg-slate-800/20" : ""}`}>
                  <td className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selected.has(item.id)}
                      onChange={() => toggleSelect(item.id)}
                      className="rounded bg-slate-700 border-slate-600"
                    />
                  </td>
                  <td className="px-4 py-3">
                    <span className={p.color}>{p.icon} P{item.priority}</span>
                  </td>
                  <td className="px-4 py-3 text-slate-200">{item.title}</td>
                  <td className="px-4 py-3 text-slate-400">{item.assignee || "—"}</td>
                  <td className="px-4 py-3">
                    <select
                      className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs"
                      value={item.priority}
                      onChange={(e) => setPriority(item.id, Number(e.target.value))}
                    >
                      <option value={1}>P1 Urgent</option>
                      <option value={2}>P2 High</option>
                      <option value={3}>P3 Normal</option>
                      <option value={4}>P4 Low</option>
                    </select>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
