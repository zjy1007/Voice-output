import { useRef, useState } from "react";

type RecorderStatus = "idle" | "recording" | "finished" | "error";

export function useRecorder() {
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const chunksRef = useRef<BlobPart[]>([]);

  const [status, setStatus] = useState<RecorderStatus>("idle");
  const [audioBlob, setAudioBlob] = useState<Blob | null>(null);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState("");

  const cleanupStream = () => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
  };

  const revokeAudioUrl = () => {
    setAudioUrl((currentUrl) => {
      if (currentUrl) {
        URL.revokeObjectURL(currentUrl);
      }
      return null;
    });
  };

  const startRecording = async () => {
    try {
      revokeAudioUrl();
      setAudioBlob(null);
      setErrorMessage("");
      chunksRef.current = [];

      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      streamRef.current = stream;

      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          chunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = () => {
        const mimeType = mediaRecorder.mimeType || "audio/webm";
        const blob = new Blob(chunksRef.current, { type: mimeType });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        setStatus("finished");
        cleanupStream();
      };

      mediaRecorder.start();
      setStatus("recording");
    } catch (error) {
      cleanupStream();
      setStatus("error");
      setErrorMessage(
        error instanceof Error ? error.message : "无法访问麦克风，请检查浏览器权限。",
      );
    }
  };

  const stopRecording = () => {
    const mediaRecorder = mediaRecorderRef.current;
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
    }
  };

  return {
    audioBlob,
    audioUrl,
    errorMessage,
    isRecording: status === "recording",
    startRecording,
    status,
    stopRecording,
  };
}
