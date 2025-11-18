import { useState } from "react";
import ChatMessage from "./components/ChatMessage";
import { askQuestion, uploadDocuments } from "./api";

const DEFAULT_SYSTEM_MESSAGE =
  "Upload private PDF/TXT files, then ask context-aware questions.";

export default function App() {
  const [messages, setMessages] = useState([
    { role: "system", content: DEFAULT_SYSTEM_MESSAGE },
  ]);
  const [question, setQuestion] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [files, setFiles] = useState([]);
  const [error, setError] = useState("");

  const handleUpload = async (event) => {
    event.preventDefault();
    if (!files.length) return;
    setIsUploading(true);
    setError("");
    try {
      const response = await uploadDocuments(files);
      setMessages((prev) => [
        ...prev,
        {
          role: "system",
          content: `Upload successful: ${response.detail}`,
        },
      ]);
      setFiles([]);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsUploading(false);
    }
  };

  const handleAsk = async () => {
    if (!question.trim()) return;
    setIsLoading(true);
    setError("");

    const newMessages = [
      ...messages,
      { role: "user", content: question },
      { role: "assistant", content: "Thinking..." },
    ];
    setMessages(newMessages);
    try {
      const answer = await askQuestion(question);
      setMessages((prev) => [
        ...prev.slice(0, -1),
        {
          role: "assistant",
          content: answer.answer,
          sources: answer.sources,
        },
      ]);
      setQuestion("");
    } catch (err) {
      setError(err.message);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>RAG Chatbot</h1>
        <p>Chat with your documents securely.</p>
      </header>

      <section className="panel">
        <form onSubmit={handleUpload} className="upload-form">
          <label className="upload-label">
            Select PDF/TXT documents
            <input
              type="file"
              accept=".pdf,.txt"
              multiple
              onChange={(event) => setFiles([...event.target.files])}
            />
          </label>
          <button type="submit" disabled={isUploading}>
            {isUploading ? "Uploading..." : "Upload"}
          </button>
        </form>
        {files.length > 0 && (
          <p className="info">{files.length} file(s) ready to upload</p>
        )}
      </section>

      <section className="chat-window">
        {messages.map((message, index) => (
          <ChatMessage key={index} {...message} />
        ))}
      </section>

      <section className="panel">
        <textarea
          placeholder="Ask something about your documents..."
          value={question}
          onChange={(event) => setQuestion(event.target.value)}
        />
        <button onClick={handleAsk} disabled={isLoading}>
          {isLoading ? "Generating..." : "Send"}
        </button>
      </section>

      {error && <p className="error">{error}</p>}
    </div>
  );
}

