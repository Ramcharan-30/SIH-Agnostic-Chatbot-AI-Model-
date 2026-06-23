import { Card, CardContent } from "@/components/ui/card";

const teamMembers = [
  {
    name: "Arjun Patel",
    role: "AI Developer",
    year: "3rd Year CS",
    avatar: "👨🏽‍💻"
  },
  {
    name: "Priya Sharma",
    role: "Frontend Developer",
    year: "2nd Year IT",
    avatar: "👩🏽‍💻"
  },
  {
    name: "Rahul Kumar",
    role: "Backend Developer", 
    year: "3rd Year CS",
    avatar: "👨🏽‍💻"
  },
  {
    name: "Sneha Singh",
    role: "UI/UX Designer",
    year: "2nd Year Design",
    avatar: "👩🏽‍🎨"
  }
];

const Team = () => {
  return (
    <section className="py-20 bg-muted/30">
      <div className="container mx-auto px-4">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-4">
            Built by Students, for Students
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            We understand student problems because we are students too! 🎓
          </p>
        </div>
        
        <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
          {teamMembers.map((member, index) => (
            <Card key={index} className="text-center hover-lift border-0 shadow-soft">
              <CardContent className="p-6">
                <div className="text-6xl mb-4">{member.avatar}</div>
                <h3 className="font-semibold text-lg mb-1">{member.name}</h3>
                <p className="text-primary font-medium mb-1">{member.role}</p>
                <p className="text-sm text-muted-foreground">{member.year}</p>
              </CardContent>
            </Card>
          ))}
        </div>
        
        <div className="text-center mt-12">
          <div className="inline-flex items-center gap-2 rounded-full bg-campus-yellow/20 px-6 py-3">
            <span className="text-2xl">💡</span>
            <span className="font-medium">
              Got feedback or want to join our team? 
              <a href="#contact" className="text-primary hover:underline ml-1">
                Let's talk!
              </a>
            </span>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Team;