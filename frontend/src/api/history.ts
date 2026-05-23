const API_BASE_URL = "http://127.0.0.1:8000";

export type HistoryRecord = {
  id: number;
  text: string;
  mode: "normal" | "office" | "study";
  created_at: string;
};

type HistoryListResponse = {
  data: HistoryRecord[];
};

export async function fetchHistory() {
  const response = await fetch(`${API_BASE_URL}/api/history`);
  if (!response.ok) {
    throw new Error("获取历史记录失败。");
  }

  const result = (await response.json()) as HistoryListResponse;
  return result.data;
}

export async function saveHistory(text: string, mode: HistoryRecord["mode"]) {
  const response = await fetch(`${API_BASE_URL}/api/history`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ text, mode }),
  });

  if (!response.ok) {
    throw new Error("保存历史记录失败。");
  }
}
