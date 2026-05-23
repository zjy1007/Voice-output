const API_BASE_URL = "http://127.0.0.1:8000";

type HotwordListResponse = {
  data: string[];
};

export async function fetchHotwords() {
  const response = await fetch(`${API_BASE_URL}/api/hotwords`);
  if (!response.ok) {
    throw new Error("获取热词失败。");
  }

  const result = (await response.json()) as HotwordListResponse;
  return result.data;
}

export async function createHotword(word: string) {
  const response = await fetch(`${API_BASE_URL}/api/hotwords`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ word }),
  });

  if (!response.ok) {
    throw new Error("添加热词失败。");
  }
}
