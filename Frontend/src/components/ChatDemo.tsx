import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Send } from "lucide-react";

const ChatDemo = () => {
  const messages = [
    {
      type: "user",
      content: "When is the last date to pay semester fees?",
      time: "2:30 PM"
    },
    {
      type: "bot",
      content: "Hi! 👋 The last date for semester fee payment is March 15th, 2024. You can pay online through the student portal or visit the accounts office. Would you like me to send you the payment link?",
      time: "2:30 PM"
    },
    {
      type: "user",
      content: "Yes, please send the link",
      time: "2:31 PM"
    },
    {
      type: "bot",
      content: "Here's your payment link: student.college.edu/pay 💳\n\nYou'll need your student ID and the amount is ₹45,000. Any other questions?",
      time: "2:31 PM"
    }
  ];

  return (
    <section className="py-20">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">
            See Campus Buddy in Action
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Experience how quick and helpful our AI assistant can be
          </p>
        </div>
        
        <div className="max-w-2xl mx-auto">
          <Card className="shadow-soft">
            <CardHeader className="campus-gradient text-white">
              <CardTitle className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-white/20 flex items-center justify-center">
                  🤖
                </div>
                Campus Buddy Chat
                <div className="ml-auto flex items-center gap-2 text-sm">
                  <div className="w-2 h-2 bg-green-400 rounded-full"></div>
                  Online
                </div>
              </CardTitle>
            </CardHeader>
            
            <CardContent className="p-0">
              <div className="h-96 overflow-y-auto p-6 space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={index}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                        message.type === 'user'
                          ? 'bg-primary text-primary-foreground'
                          : 'bg-muted text-foreground'
                      }`}
                    >
                      <p className="text-sm whitespace-pre-line">{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.type === 'user' 
                          ? 'text-primary-foreground/70' 
                          : 'text-muted-foreground'
                      }`}>
                        {message.time}
                      </p>
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="border-t p-4">
                <div className="flex gap-2">
                  <input
                    type="text"
                    placeholder="Ask Campus Buddy anything..."
                    className="flex-1 rounded-full border px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    disabled
                  />
                  <Button size="sm" className="rounded-full campus-gradient">
                    <Send className="h-4 w-4" />
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
          
          <div className="text-center mt-8">
            <Button size="lg" className="campus-gradient hover-lift" asChild>
              <a href="/chat">Start Chatting with Campus Buddy</a>
            </Button>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ChatDemo;