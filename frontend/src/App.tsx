import { useEffect, useState } from "react";
import "./styles.css";
import { transcribeAudio } from "./api/asr";
import {
  deleteHistory,
  fetchHistory,
  saveHistory,
  updateHistory,
  type HistoryRecord,
} from "./api/history";
import { createHotword, fetchHotwords, type HotwordEntry } from "./api/hotword";
import { useRecorder } from "./hooks/useRecorder";

type TextMode = "normal" | "office" | "study" | "prompt";

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
  const [hotwordAliasesInput, setHotwordAliasesInput] = useState("");
  const [hotwords, setHotwords] = useState<HotwordEntry[]>([]);
  const [history, setHistory] = useState<HistoryRecord[]>([]);
  const [historySearch, setHistorySearch] = useState("");
  const [actionMessage, setActionMessage] = useState("");
  const [correctionTarget, setCorrectionTarget] = useState<HistoryRecord | null>(null);
  const [selectedText, setSelectedText] = useState("");
  const [replacementText, setReplacementText] = useState("");

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

  const filteredHistory = history.filter((record) => {
    const query = historySearch.trim().toLowerCase();
    if (!query) {
      return true;
    }

    return [record.text, record.mode, record.created_at]
      .join(" ")
      .toLowerCase()
      .includes(query);
  });

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

    await createHotword(hotwordInput, parseAliases(hotwordAliasesInput));
    setHotwordInput("");
    setHotwordAliasesInput("");
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

  const handleCopyHistory = async (text: string) => {
    await navigator.clipboard.writeText(text);
    setActionMessage("历史记录已复制");
  };

  const handleDeleteHistory = async (record: HistoryRecord) => {
    await deleteHistory(record.id);
    setActionMessage("历史记录已删除");
    if (correctionTarget?.id === record.id) {
      closeCorrectionDialog();
    }
    await refreshHistory();
  };

  const openCorrectionDialog = (record: HistoryRecord) => {
    setCorrectionTarget(record);
    setSelectedText("");
    setReplacementText("");
  };

  const closeCorrectionDialog = () => {
    setCorrectionTarget(null);
    setSelectedText("");
    setReplacementText("");
  };

  const applyCorrection = async () => {
    if (!correctionTarget || !selectedText || !replacementText.trim()) {
      return;
    }

    const correctedText = correctionTarget.text.replace(selectedText, replacementText.trim());
    await updateHistory(correctionTarget.id, correctedText, correctionTarget.mode);
    setTranscript(correctedText);
    setActionMessage("历史记录已纠错");
    closeCorrectionDialog();
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
            <button
              className={mode === "prompt" ? "mode-button active" : "mode-button"}
              type="button"
              onClick={() => setMode("prompt")}
            >
              Prompt优化
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
                placeholder="正确词，例如 Whisper"
              />
              <input
                value={hotwordAliasesInput}
                onChange={(event) => setHotwordAliasesInput(event.target.value)}
                placeholder="别名/误识别词，用逗号分隔"
              />
              <button className="primary-button" type="button" onClick={handleAddHotword}>
                添加
              </button>
            </div>
            <div className="chip-list">
              {hotwords.map((entry) => (
                <span className="chip" key={entry.word}>
                  {entry.word}
                  {entry.aliases.length ? ` / ${entry.aliases.join("、")}` : ""}
                </span>
              ))}
            </div>
          </section>

          <section className="side-section">
            <h2>输入历史</h2>
            <div className="history-search-bar">
              <div className="search-input-wrap">
                <span className="search-icon" aria-hidden="true">
                  ⌕
                </span>
                <input
                  value={historySearch}
                  onChange={(event) => setHistorySearch(event.target.value)}
                  placeholder="搜索历史记录"
                />
              </div>
              <button
                className="secondary-button compact-button"
                type="button"
                onClick={() => setHistorySearch("")}
              >
                全部
              </button>
              <button className="secondary-button compact-button" type="button">
                选择
              </button>
            </div>
            <p className="history-summary">
              共 {filteredHistory.length} 条
              {historySearch.trim() ? ` · 搜索：${historySearch.trim()}` : ""}
            </p>
            <div className="history-list">
              {filteredHistory.map((record) => (
                <article
                  className="history-item"
                  key={record.id}
                >
                  <button
                    className="history-text"
                    type="button"
                    onClick={() => setTranscript(record.text)}
                  >
                    {record.text}
                  </button>
                  <small>
                    {record.mode} · {record.created_at}
                  </small>
                  <div className="history-actions">
                    <button
                      className="text-button warning"
                      type="button"
                      onClick={() => openCorrectionDialog(record)}
                    >
                      纠错
                    </button>
                    <button
                      className="text-button"
                      type="button"
                      onClick={() => void handleCopyHistory(record.text)}
                    >
                      复制
                    </button>
                    <button
                      className="text-button danger"
                      type="button"
                      onClick={() => void handleDeleteHistory(record)}
                    >
                      删除
                    </button>
                  </div>
                </article>
              ))}
            </div>
          </section>
        </div>
      </section>

      {correctionTarget ? (
        <div className="dialog-backdrop" role="presentation">
          <section className="correction-dialog" role="dialog" aria-modal="true">
            <button
              className="close-button"
              type="button"
              aria-label="关闭"
              onClick={closeCorrectionDialog}
            >
              ×
            </button>
            <h2>纠错</h2>
            <p className="dialog-hint">点击或拖选识别错误的字：</p>
            <div className="token-grid">
              {[...correctionTarget.text].map((char, index) => (
                <button
                  className={selectedText === char ? "token selected" : "token"}
                  key={`${char}-${index}`}
                  type="button"
                  onClick={() => setSelectedText(char)}
                >
                  {char}
                </button>
              ))}
            </div>
            <label className="transcript-label" htmlFor="replacement">
              正确的词
            </label>
            <input
              id="replacement"
              value={replacementText}
              onChange={(event) => setReplacementText(event.target.value)}
              placeholder="输入正确的词..."
            />
            <div className="dialog-actions">
              <button className="secondary-button" type="button" onClick={closeCorrectionDialog}>
                取消
              </button>
              <button
                className="primary-button"
                disabled={!selectedText || !replacementText.trim()}
                type="button"
                onClick={() => void applyCorrection()}
              >
                添加
              </button>
            </div>
          </section>
        </div>
      ) : null}
    </main>
  );
}

function parseAliases(value: string) {
  return value
    .split(/[,，、\n]/)
    .map((alias) => alias.trim())
    .filter(Boolean);
}

export default App;
