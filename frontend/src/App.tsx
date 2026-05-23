import "./styles.css";
import { useRecorder } from "./hooks/useRecorder";

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

  const statusText = {
    idle: "等待录音",
    recording: "正在录音",
    finished: "录音结束",
    error: "录音出错",
  }[status];

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

          {audioBlob ? (
            <div className="audio-result">
              <p>已生成音频文件：{(audioBlob.size / 1024).toFixed(1)} KB</p>
              {audioUrl ? <audio controls src={audioUrl} /> : null}
            </div>
          ) : null}

          {errorMessage ? <p className="error-message">{errorMessage}</p> : null}

          <label className="transcript-label" htmlFor="transcript">
            识别结果
          </label>
          <textarea
            id="transcript"
            placeholder="下一阶段接入 ASR 后，识别文本会显示在这里。"
            readOnly
          />
        </div>
      </section>
    </main>
  );
}

export default App;
