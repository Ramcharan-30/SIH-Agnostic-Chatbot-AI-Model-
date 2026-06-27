import { useState, useRef, useEffect } from "react";
import { Link } from "react-router-dom";
import { Send, ArrowLeft } from "lucide-react";

import { sendMessage } from "@/api/chatService";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Message {
  id: string;
  type: "user" | "bot";
  content: string;
  time: string;
}

const Chatbot = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "1",
      type: "bot",
      content:
        "Hi! I'm Campus Buddy, your multilingual AI assistant. I can help you with fee deadlines, scholarship info, timetables, and more. How can I assist you today?",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;

    const currentTime = new Date().toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    const userMessage: Message = {
      id: Date.now().toString(),
      type: "user",
      content: inputValue,
      time: currentTime,
    };

    setMessages((prev) => [...prev, userMessage]);
    const userInput = inputValue;
    setInputValue("");

    try {
      const reply = await sendMessage("user-123", userInput);

      const botMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: "bot",
        content: reply,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Chat API error:", error);

      const errorMessage: Message = {
        id: (Date.now() + 2).toString(),
        type: "bot",
        content: "Sorry, something went wrong. Please try again.",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      };

      setMessages((prev) => [...prev, errorMessage]);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") {
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-campus-blue/5 to-campus-yellow/5">
      <div className="sticky top-0 z-10 border-b bg-background/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link to="/">
              <Button variant="ghost" size="sm" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back to Home
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              <div className="campus-gradient flex h-10 w-10 items-center justify-center rounded-full">
                <span className="text-lg">CB</span>
              </div>
              <div>
                <h1 className="text-xl font-bold">Campus Buddy</h1>
                <p className="text-sm text-muted-foreground">Your AI Campus Assistant</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="container mx-auto max-w-4xl px-4 py-8">
        <Card className="flex h-[600px] flex-col shadow-soft">
          <CardHeader className="campus-gradient text-white">
            <CardTitle className="flex items-center justify-between">
              <span>Chat with Campus Buddy</span>
              <div className="flex items-center gap-2 text-sm">
                <div className="h-2 w-2 rounded-full bg-green-400"></div>
                Online
              </div>
            </CardTitle>
          </CardHeader>

          <CardContent className="flex flex-1 flex-col p-0">
            <div className="flex-1 space-y-4 overflow-y-auto p-6">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.type === "user"
                        ? "campus-gradient text-white"
                        : "bg-muted text-foreground"
                    }`}
                  >
                    <p className="whitespace-pre-line text-sm">{message.content}</p>
                    <p
                      className={`mt-1 text-xs ${
                        message.type === "user" ? "text-white/70" : "text-muted-foreground"
                      }`}
                    >
                      {message.time}
                    </p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Ask Campus Buddy anything..."
                  className="flex-1 rounded-full"
                />
                <Button
                  onClick={handleSendMessage}
                  size="sm"
                  className="campus-gradient rounded-full hover:opacity-90"
                  disabled={!inputValue.trim()}
                >
                  <Send className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Chatbot;
