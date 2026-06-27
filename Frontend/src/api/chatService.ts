const API_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

export async function sendMessage(sessionId: string, message: string): Promise<string> {
  const res = await fetch(`${API_URL}/api/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sessionId, message }),
  });

  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    throw new Error(data.error || "API Error");
  }

  return data.answer || data.reply || "Sorry, I couldn't find an answer.";
}
