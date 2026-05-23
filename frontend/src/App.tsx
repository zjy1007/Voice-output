import { useState } from "react";
import "./styles.css";
import { transcribeAudio } from "./api/asr";
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
  const [transcript, setTranscript] = useState("");
  const [uploadStatus, setUploadStatus] = useState("");
  const [uploadError, setUploadError] = useState("");
  const [isUploading, setIsUploading] = useState(false);

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
      const result = await transcribeAudio(audioBlob);
      setTranscript(result.data.optimized_text);
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
            placeholder="录音后点击上传识别，后端返回的文本会显示在这里。"
            readOnly
            value={transcript}
          />
        </div>
      </section>
    </main>
  );
}

export default App;
