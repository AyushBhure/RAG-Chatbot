import { useState, useEffect, useRef } from "react";
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
  const chatWindowRef = useRef(null);

  // Auto-scroll to bottom when messages change
  useEffect(() => {
    if (chatWindowRef.current) {
      // Small delay to ensure DOM has updated
      setTimeout(() => {
        chatWindowRef.current.scrollTo({
          top: chatWindowRef.current.scrollHeight,
          behavior: "smooth",
        });
      }, 100);
    }
  }, [messages]);

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
      const errorMessage = err.response?.data?.detail || err.message || "Upload failed";
      setError(errorMessage);
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
      const errorMessage = err.response?.data?.detail || err.message || "Failed to get answer";
      setError(errorMessage);
      setMessages((prev) => prev.slice(0, -1));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleAsk();
    }
  };

  return (
    <div className="app">
      <div className="important-notice">
        <div className="notice-content">
          <strong>Important Notice:</strong> This application is currently not fully functional.
          <details className="notice-details">
            <summary>Why is it not working? (Click to expand)</summary>
            <ul>
              <li><strong>Backend API Not Deployed:</strong> Only the frontend is deployed on Vercel. The FastAPI backend server is not running, so API calls to <code>/api/upload</code> and <code>/api/ask</code> will fail.</li>
              <li><strong>Missing Serverless Functions:</strong> The backend API endpoints need to be deployed as Vercel serverless functions, but they are not currently configured or deployed.</li>
              <li><strong>No Vector Database:</strong> Even if the backend was deployed, it would need a persistent vector database (like Pinecone) since Vercel's filesystem is ephemeral.</li>
              <li><strong>Environment Variables:</strong> Required environment variables (like <code>OPENAI_API_KEY</code>) are not configured in the Vercel deployment.</li>
            </ul>
            <p><strong>To make it work:</strong> Deploy the backend API as Vercel serverless functions, configure environment variables, and set up a persistent vector database.</p>
          </details>
        </div>
      </div>
      <header>
        <div>
          <h1>RAG Chatbot</h1>
          <p>Chat with your documents securely</p>
        </div>
      </header>

      <section className="upload-section">
        <form onSubmit={handleUpload} className="upload-form">
          <label className="upload-label">
            Select Documents
            <input
              type="file"
              accept=".pdf,.txt"
              multiple
              onChange={(event) => setFiles([...event.target.files])}
            />
          </label>
          {files.length > 0 && (
            <span className="file-info">
              {files.length} file{files.length > 1 ? "s" : ""} selected
            </span>
          )}
          <button
            type="submit"
            className="upload-btn"
            disabled={isUploading || !files.length}
          >
            {isUploading ? "Uploading..." : "Upload"}
          </button>
        </form>
      </section>

      <section className="chat-window" ref={chatWindowRef}>
        {messages.length === 1 && messages[0].role === "system" ? (
          <div
            style={{
              display: "flex",
              flexDirection: "column",
              alignItems: "center",
              justifyContent: "center",
              height: "100%",
              textAlign: "center",
              color: "#8e8ea0",
            }}
          >
            <h2 style={{ fontSize: "1.5rem", marginBottom: "0.5rem", color: "#ececf1" }}>
              Upload documents to get started
            </h2>
            <p>Upload PDF or TXT files and ask questions about their content</p>
          </div>
        ) : (
          messages.map((message, index) => (
            <ChatMessage key={index} {...message} />
          ))
        )}
      </section>

      <section className="input-section">
        <div className="input-container">
          <textarea
            placeholder="Message RAG Chatbot..."
            value={question}
            onChange={(event) => {
              setQuestion(event.target.value);
              event.target.style.height = "auto";
              event.target.style.height = `${Math.min(event.target.scrollHeight, 200)}px`;
            }}
            onKeyPress={handleKeyPress}
            rows={1}
            disabled={isLoading}
          />
          <button
            className="send-btn"
            onClick={handleAsk}
            disabled={isLoading || !question.trim()}
            type="button"
            title="Send message"
          >
            {isLoading ? (
              <div className="thinking">
                <span></span>
                <span></span>
                <span></span>
              </div>
            ) : (
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
              >
                <path d="M22 2L11 13M22 2l-7 20-4-9-9-4 20-7z" />
              </svg>
            )}
          </button>
        </div>
      </section>

      {error && <p className="error">{error}</p>}
    </div>
  );
}

