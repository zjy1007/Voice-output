import { useEffect, useState } from "react";
import "./styles.css";
import { transcribeAudio } from "./api/asr";
import { fetchHistory, saveHistory, type HistoryRecord } from "./api/history";
import { createHotword, fetchHotwords } from "./api/hotword";
import { useRecorder } from "./hooks/useRecorder";

type TextMode = "normal" | "office" | "study";

function App() {
  const {
    audioBlob,
    audioUrl,
    errorMessage,
    isRecording,
    startRecording,
    status,
    stopRecording,
  } = useRecorder();
  const [transcript, setTranscript] = useState("");
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploadError, setUploadError] = useState("");
  const [isUploading, setIsUploading] = useState(false);
  const [mode, setMode] = useState<TextMode>("normal");
  const [hotwordInput, setHotwordInput] = useState("");
  const [hotwords, setHotwords] = useState<string[]>([]);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [actionMessage, setActionMessage] = useState("");

  useEffect(() => {
    void refreshHotwords();
    void refreshHistory();
  }, []);

  const statusText = {
    idle: "等待录音",
    recording: "正在录音",
    finished: "录音结束",
    error: "录音出错",
  }[status];

  const handleTranscribe = async () => {
    if (!audioBlob) {
      return;
    }

    try {
      setIsUploading(true);
      setUploadError("");
      setUploadStatus("正在上传音频");
      const result = await transcribeAudio(audioBlob, mode);
      setTranscript((currentText) => {
        if (!currentText.trim()) {
          return result.data.optimized_text;
        }

        return `${currentText.trim()}\n${result.data.optimized_text}`;
      });
      setUploadStatus("识别完成");
    } catch (error) {
      setUploadStatus("");
      setUploadError(
        error instanceof Error ? error.message : "识别失败，请稍后重试。",
      );
    } finally {
      setIsUploading(false);
    }
  };

  const refreshHotwords = async () => {
    try {
      setHotwords(await fetchHotwords());
    } catch {
      setHotwords([]);
    }
  };

  const refreshHistory = async () => {
    try {
      setHistory(await fetchHistory());
    } catch {
      setHistory([]);
    }
  };

  const handleAddHotword = async () => {
    if (!hotwordInput.trim()) {
      return;
    }

    await createHotword(hotwordInput);
    setHotwordInput("");
    setActionMessage("热词已添加");
    await refreshHotwords();
  };

  const handleCopy = async () => {
    if (!transcript.trim()) {
      return;
    }

    await navigator.clipboard.writeText(transcript);
    setActionMessage("已复制到剪贴板");
  };

  const handleClear = () => {
    setTranscript("");
    setActionMessage("文本已清空");
  };

  const handleSaveHistory = async () => {
    if (!transcript.trim()) {
      return;
    }

    await saveHistory(transcript, mode);
    setActionMessage("历史记录已保存");
    await refreshHistory();
  };

  return (
    <main className="app-shell">
      <section className="workspace">
        <h1>智能语音输入法</h1>
        <div className="recorder-panel">
          <div className="status-row">
            <span className={`recording-dot ${isRecording ? "active" : ""}`} />
            <span>{statusText}</span>
          </div>

          <div className="controls">
            <button
              className="primary-button"
              disabled={isRecording}
              type="button"
              onClick={startRecording}
            >
              开始录音
            </button>
            <button
              className="secondary-button"
              disabled={!isRecording}
              type="button"
              onClick={stopRecording}
            >
              停止录音
            </button>
          </div>

          <div className="mode-selector" aria-label="输入模式">
            <button
              className={mode === "normal" ? "mode-button active" : "mode-button"}
              type="button"
              onClick={() => setMode("normal")}
            >
              普通输入
            </button>
            <button
              className={mode === "office" ? "mode-button active" : "mode-button"}
              type="button"
              onClick={() => setMode("office")}
            >
              办公模式
            </button>
            <button
              className={mode === "study" ? "mode-button active" : "mode-button"}
              type="button"
              onClick={() => setMode("study")}
            >
              学习笔记
            </button>
          </div>

          {audioBlob ? (
            <div className="audio-result">
              <p>已生成音频文件：{(audioBlob.size / 1024).toFixed(1)} KB</p>
              {audioUrl ? <audio controls src={audioUrl} /> : null}
              <button
                className="primary-button upload-button"
                disabled={isUploading}
                type="button"
                onClick={handleTranscribe}
              >
                {isUploading ? "上传中" : "上传识别"}
              </button>
            </div>
          ) : null}

          {errorMessage ? <p className="error-message">{errorMessage}</p> : null}
          {uploadStatus ? <p className="success-message">{uploadStatus}</p> : null}
          {uploadError ? <p className="error-message">{uploadError}</p> : null}

          <label className="transcript-label" htmlFor="transcript">
            识别结果
          </label>
          <textarea
            id="transcript"
            onChange={(event) => setTranscript(event.target.value)}
            placeholder="录音后点击上传识别，后端返回的文本会显示在这里。"
            value={transcript}
          />

          <div className="toolbar">
            <button className="secondary-button" type="button" onClick={handleCopy}>
              一键复制
            </button>
            <button className="secondary-button" type="button" onClick={handleClear}>
              一键清空
            </button>
            <button
              className="primary-button"
              type="button"
              onClick={handleSaveHistory}
            >
              保存历史
            </button>
          </div>

          {actionMessage ? <p className="success-message">{actionMessage}</p> : null}

          <section className="side-section">
            <h2>自定义热词</h2>
            <div className="input-row">
              <input
                value={hotwordInput}
                onChange={(event) => setHotwordInput(event.target.value)}
                placeholder="输入人名、项目名、专业词"
              />
              <button className="primary-button" type="button" onClick={handleAddHotword}>
                添加
              </button>
            </div>
            <div className="chip-list">
              {hotwords.map((word) => (
                <span className="chip" key={word}>
                  {word}
                </span>
              ))}
            </div>
          </section>

          <section className="side-section">
            <h2>输入历史</h2>
            <div className="history-list">
              {history.map((record) => (
                <button
                  className="history-item"
                  key={record.id}
                  type="button"
                  onClick={() => setTranscript(record.text)}
                >
                  <span>{record.text}</span>
                  <small>
                    {record.mode} · {record.created_at}
                  </small>
                </button>
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}

export default App;
