import { useState } from "react";
import { sendMessage } from "../api/chatService";

export function useChat(sessionId: string) {
  const [messages, setMessages] = useState<{ sender: string; text: string }[]>([]);

  async function handleSend(userMessage: string) {
    setMessages((prev) => [...prev, { sender: "user", text: userMessage }]);

    const reply = await sendMessage(sessionId, userMessage);

    setMessages((prev) => [...prev, { sender: "bot", text: reply }]);
  }

  return { messages, handleSend };
}
