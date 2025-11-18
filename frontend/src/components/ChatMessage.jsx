export default function ChatMessage({ role, content, sources }) {
  const getAvatar = () => {
    if (role === "user") return "U";
    if (role === "assistant") return "AI";
    return "S";
  };

  const getRoleName = () => {
    if (role === "assistant") return "Assistant";
    if (role === "user") return "You";
    return "System";
  };

  if (role === "system") {
    return (
      <div className={`message ${role}`}>
        <div className="message-avatar">{getAvatar()}</div>
        <div className="message-content">
          <p>{content}</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`message ${role}`}>
      <div className="message-avatar">{getAvatar()}</div>
      <div className="message-content">
        <strong>{getRoleName()}</strong>
        <p>{content === "Thinking..." ? (
          <span className="thinking">
            <span></span>
            <span></span>
            <span></span>
          </span>
        ) : (
          content
        )}</p>
        {sources?.length > 0 && (
          <details className="sources">
            <summary>📎 Sources ({sources.length})</summary>
            <ul>
              {sources.map((source, index) => (
                <li key={index}>
                  <span>
                    {source.source.split(/[/\\]/).pop()}
                    {source.page && ` · Page ${source.page}`}
                  </span>
                </li>
              ))}
            </ul>
          </details>
        )}
      </div>
    </div>
  );
}

