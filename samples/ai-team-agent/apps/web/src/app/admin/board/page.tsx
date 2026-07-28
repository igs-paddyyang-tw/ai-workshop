"use client";
import useSWR, { mutate } from "swr";
import { fetcher, api } from "@/lib/api";

const statusColumns = [
  { key: "queued", label: "Queued", color: "border-blue-500" },
  { key: "claimed", label: "Claimed", color: "border-yellow-500" },
  { key: "executing", label: "Executing", color: "border-cyan-500" },
  { key: "blocked", label: "Blocked", color: "border-red-500" },
  { key: "completed", label: "Completed", color: "border-green-500" },
];

const priorityStyle: Record<number, { icon: string; border: string }> = {
  1: { icon: "🔴", border: "border-l-red-500" },
  2: { icon: "🟠", border: "border-l-orange-500" },
  3: { icon: "🔵", border: "border-l-blue-500" },
  4: { icon: "⚪", border: "border-l-slate-500" },
};

interface Task {
  id: string;
  title: string;
  status: string;
  priority: number;
  assignee?: string;
  created_at?: string;
  blocked_reason?: string;
}

export default function BoardPage() {
  const { data: board } = useSWR("/api/board", fetcher, { refreshInterval: 5000 });

  // /api/board returns { columns: { pending: [...], assigned: [...], ... } }
  const columns = board?.columns || board || {};

  async function handleComplete(id: string) {
    await api.patch(`/api/tasks/${id}/complete`, {});
    mutate("/api/board");
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Task Board</h2>
      <p className="text-sm text-slate-400">Kanban 看板 — 即時更新（5s）</p>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
        {statusColumns.map((col) => {
          const tasks: Task[] = Array.isArray(columns[col.key]) ? columns[col.key] : [];
          return (
            <div key={col.key} className="bg-slate-900 border border-slate-800 rounded-lg min-h-[300px] flex flex-col">
              {/* Column Header */}
              <div className={`px-4 py-3 border-b border-slate-800 border-t-2 ${col.color} flex justify-between items-center`}>
                <h3 className="text-sm font-medium uppercase tracking-wide">{col.label}</h3>
                <span className="text-xs bg-slate-800 px-2 py-0.5 rounded-full">{tasks.length}</span>
              </div>

              {/* Cards */}
              <div className="p-2 flex-1 space-y-2 overflow-y-auto max-h-[500px]">
                {tasks.length === 0 && (
                  <p className="text-slate-600 text-xs text-center py-4">空</p>
                )}
                {tasks.map((task) => {
                  const p = priorityStyle[task.priority] || priorityStyle[3];
                  return (
                    <div
                      key={task.id}
                      className={`bg-slate-950 border border-slate-800 rounded p-3 border-l-2 ${p.border} hover:border-slate-600 transition-colors`}
                    >
                      <div className="flex items-start justify-between gap-2">
                        <span className="text-sm text-slate-200 leading-tight">{task.title}</span>
                        <span className="text-xs flex-shrink-0">{p.icon}</span>
                      </div>
                      <div className="flex items-center justify-between mt-2">
                        <span className="text-xs text-cyan-400">{task.assignee || "—"}</span>
                        {col.key === "assigned" && (
                          <button
                            onClick={() => handleComplete(task.id)}
                            className="text-xs px-2 py-0.5 bg-green-900/50 text-green-400 rounded hover:bg-green-900"
                          >
                            ✓ Done
                          </button>
                        )}
                      </div>
                      {task.blocked_reason && (
                        <div className="text-xs text-red-400 mt-1">🚫 {task.blocked_reason}</div>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
