import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    emoji: "📅",
    title: "Fee Deadlines",
    description: "Never miss a payment deadline again. Get timely reminders and payment links."
  },
  {
    emoji: "📝",
    title: "Scholarship Info",
    description: "Find and apply for scholarships that match your profile and academic performance."
  },
  {
    emoji: "📚",
    title: "Timetable & Notices",
    description: "Stay updated with class schedules, exam dates, and important announcements."
  },
  {
    emoji: "🗣️",
    title: "Multilingual Support",
    description: "Chat in your preferred language - Hindi, English, or any regional language."
  }
];

const Features = () => {
  return (
    <section className="py-20 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">
            How Campus Buddy Helps You
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Everything you need to navigate college life, all in one friendly chatbot
          </p>
        </div>
        
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {features.map((feature, index) => (
            <Card key={index} className="text-center hover-lift border-0 shadow-soft">
              <CardHeader>
                <div className="text-5xl mb-4">{feature.emoji}</div>
                <CardTitle className="text-xl">{feature.title}</CardTitle>
              </CardHeader>
              <CardContent>
                <CardDescription className="text-base">
                  {feature.description}
                </CardDescription>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
};

export default Features;