export default function ChatMessage({ role, content, sources }) {
  return (
    <div className={`message ${role}`}>
      <strong>{role === "assistant" ? "Assistant" : role}</strong>
      <p>{content}</p>
      {sources?.length ? (
        <details>
          <summary>Sources</summary>
          <ul>
            {sources.map((source, index) => (
              <li key={index}>
                <span>{source.source}</span>
                {source.page && <span> · page {source.page}</span>}
              </li>
            ))}
          </ul>
        </details>
      ) : null}
    </div>
  );
}

