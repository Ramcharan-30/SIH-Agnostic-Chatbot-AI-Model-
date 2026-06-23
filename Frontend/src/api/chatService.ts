const API_URL = import.meta.env.VITE_BACKEND_URL || "http://localhost:5000";

export async function sendMessage(sessionId: string, message: string): Promise<string> {
  try {
    const res = await fetch(`${API_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ sessionId, message }),
    });

    if (!res.ok) throw new Error("API Error");

    const data = await res.json();
    return data.reply;
  } catch (err) {
    console.error("❌ Chat API error:", err);
    return "Sorry, something went wrong!";
  }
}
