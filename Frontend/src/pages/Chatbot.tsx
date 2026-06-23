import { useState, useRef, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Send, ArrowLeft } from "lucide-react";
import { Link } from "react-router-dom";

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
      content: "Hi! 👋 I'm Campus Buddy, your multilingual AI assistant. I can help you with fee deadlines, scholarship info, timetables, and more. How can I assist you today?",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);
  const [inputValue, setInputValue] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

 const handleSendMessage = async () => {
  if (!inputValue.trim()) return;

  const currentTime = new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  // Add user message
  const userMessage: Message = {
    id: Date.now().toString(),
    type: "user",
    content: inputValue,
    time: currentTime
  };

  setMessages(prev => [...prev, userMessage]);
  const userInput = inputValue;
  setInputValue("");

  try {
    // 🔗 Call backend API
    const res = await fetch(`${import.meta.env.VITE_BACKEND_URL}/api/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ 
        sessionId: "user-123", // Or generate dynamic session per user
        message: userInput 
      })
    });

    const data = await res.json();

    // Add bot response
    const botMessage: Message = {
      id: (Date.now() + 1).toString(),
      type: "bot",
      content: data.reply || "⚠️ No response from server",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, botMessage]);

  } catch (error) {
    console.error("❌ Chat API error:", error);

    const errorMessage: Message = {
      id: (Date.now() + 2).toString(),
      type: "bot",
      content: "⚠️ Sorry, something went wrong. Please try again.",
      time: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages(prev => [...prev, errorMessage]);
  }
};


  const generateBotResponse = (prompt: string): string => {
    const lowerPrompt = prompt.toLowerCase();
    
    if (lowerPrompt.includes("fee") || lowerPrompt.includes("payment")) {
      return "📅 The semester fee deadline is March 15th, 2024. You can pay online through the student portal at student.college.edu/pay. The fee amount is ₹45,000. Need help with anything else?";
    }
    
    if (lowerPrompt.includes("scholarship")) {
      return "🎓 Here are the available scholarships:\n\n1. Merit Scholarship - Apply by Feb 28th\n2. Need-based Aid - Rolling applications\n3. Sports Scholarship - Contact sports office\n\nWould you like details about any specific scholarship?";
    }
    
    if (lowerPrompt.includes("timetable") || lowerPrompt.includes("schedule")) {
      return "📚 Your timetable is available on the student portal. Recent updates:\n\n• CS101 - Moved to Room 204\n• Math lecture cancelled tomorrow\n• Lab sessions extended by 30 mins\n\nCheck the portal for the latest updates!";
    }
    
    if (lowerPrompt.includes("contact") || lowerPrompt.includes("office")) {
      return "📞 Here are important office contacts:\n\n• Academic Office: ext. 2201\n• Accounts Office: ext. 2301\n• Library: ext. 2401\n• IT Support: ext. 2501\n\nOffice hours: 9 AM - 5 PM, Monday to Friday";
    }
    
    if (lowerPrompt.includes("hello") || lowerPrompt.includes("hi")) {
      return "Hello! 😊 I'm here to help with all your campus queries. You can ask me about fees, scholarships, timetables, office contacts, and much more!";
    }

    return "🤖 Thanks for your question! I'm still learning, but I can help you with:\n\n• Fee deadlines and payments\n• Scholarship information\n• Timetable updates\n• Office contacts\n• Campus facilities\n\nTry asking about any of these topics!";
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-campus-blue/5 to-campus-yellow/5">
      {/* Header */}
      <div className="border-b bg-background/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link to="/">
              <Button variant="ghost" size="sm" className="gap-2">
                <ArrowLeft className="h-4 w-4" />
                Back to Home
              </Button>
            </Link>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full campus-gradient flex items-center justify-center">
                <span className="text-lg">🤖</span>
              </div>
              <div>
                <h1 className="text-xl font-bold">Campus Buddy</h1>
                <p className="text-sm text-muted-foreground">Your AI Campus Assistant</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Chat Container */}
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <Card className="h-[600px] flex flex-col shadow-soft">
          <CardHeader className="campus-gradient text-white">
            <CardTitle className="flex items-center justify-between">
              <span>Chat with Campus Buddy</span>
              <div className="flex items-center gap-2 text-sm">
                <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                Online
              </div>
            </CardTitle>
          </CardHeader>
          
          <CardContent className="flex-1 flex flex-col p-0">
            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-4">
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.type === 'user'
                        ? 'campus-gradient text-white'
                        : 'bg-muted text-foreground'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-line">{message.content}</p>
                    <p className={`text-xs mt-1 ${
                      message.type === 'user' 
                        ? 'text-white/70' 
                        : 'text-muted-foreground'
                    }`}>
                      {message.time}
                    </p>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
            
            {/* Input */}
            <div className="border-t p-4">
              <div className="flex gap-2">
                <Input
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Ask Campus Buddy anything..."
                  className="flex-1 rounded-full"
                />
                <Button 
                  onClick={handleSendMessage}
                  size="sm" 
                  className="rounded-full campus-gradient hover:opacity-90"
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