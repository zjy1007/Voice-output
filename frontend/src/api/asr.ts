export type TranscribeResponse = {
  code: number;
  message: string;
  data: {
    filename?: string;
    mode: string;
    raw_text: string;
    optimized_text: string;
  };
};

const API_BASE_URL = "http://127.0.0.1:8000";

type ApiErrorResponse = {
  detail?: string;
};

export async function transcribeAudio(audioBlob: Blob, mode = "normal") {
  const formData = new FormData();
  formData.append("file", audioBlob, "recording.webm");
  formData.append("mode", mode);

  const response = await fetch(`${API_BASE_URL}/api/asr/transcribe`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    let message = "上传音频失败，请确认后端服务已启动。";
    try {
      const errorData = (await response.json()) as ApiErrorResponse;
      if (errorData.detail) {
        message = errorData.detail;
      }
    } catch {
      // Keep the default message when the backend does not return JSON.
    }
    throw new Error(message);
  }

  return (await response.json()) as TranscribeResponse;
}
