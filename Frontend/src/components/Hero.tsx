import { Button } from "@/components/ui/button";
import heroImage from "@/assets/hero-students-chatbot.jpg";

const Hero = () => {
  return (
    <section className="relative overflow-hidden bg-gradient-to-br from-background to-campus-blue/5 py-20 lg:py-32">
      <div className="container mx-auto px-4">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <div className="space-y-8 text-center lg:text-left">
            <div className="space-y-4">
              <h1 className="text-4xl font-bold tracking-tight sm:text-5xl xl:text-6xl">
                 Meet Your{" "}
                <span className="campus-gradient bg-clip-text text-transparent">
                  Campus Buddy!
                </span>
              </h1>
              <p className="text-xl text-muted-foreground">
                Your 24×7 multilingual assistant for all college queries.
              </p>
            </div>
            
            <div className="flex flex-col gap-4 sm:flex-row sm:justify-center lg:justify-start">
              <Button size="lg" className="campus-gradient hover-lift">
                Try Campus Buddy Now
              </Button>
              <Button variant="outline" size="lg" className="hover-lift">
                Learn More
              </Button>
            </div>
            
            <div className="flex items-center justify-center gap-8 text-sm text-muted-foreground lg:justify-start">
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-green-500"></div>
                Available 24/7
              </div>
              <div className="flex items-center gap-2">
                <div className="h-2 w-2 rounded-full bg-campus-yellow"></div>
                Multi-language
              </div>
            </div>
          </div>
          
          <div className="relative">
            <div className="relative overflow-hidden rounded-3xl shadow-soft">
              <img
                src={heroImage}
                alt="Students interacting with Campus Buddy AI chatbot"
                className="h-full w-full object-cover"
              />
            </div>
            <div className="absolute -bottom-4 -right-4 rounded-2xl bg-campus-yellow p-4 shadow-glow">
              <div className="text-center">
                <div className="text-2xl font-bold text-campus-yellow-foreground">500+</div>
                <div className="text-sm text-campus-yellow-foreground/80">Happy Students</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default Hero;