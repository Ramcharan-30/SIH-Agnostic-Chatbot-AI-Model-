import { Button } from "@/components/ui/button";
import { Mail, Github, Linkedin, Twitter } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-foreground text-background py-16">
      <div className="container mx-auto px-4">
        <div className="grid gap-12 md:grid-cols-2 lg:grid-cols-4">
          <div className="space-y-4">
            <h3 className="text-xl font-bold">🎓 Campus Buddy</h3>
            <p className="text-background/80">
              Your friendly AI companion for all college queries. Making student life easier, one chat at a time.
            </p>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-semibold">Quick Links</h4>
            <div className="space-y-2">
              <div><a href="#features" className="text-background/80 hover:text-background transition-colors">Features</a></div>
              <div><a href="#demo" className="text-background/80 hover:text-background transition-colors">Try Demo</a></div>
              <div><a href="#team" className="text-background/80 hover:text-background transition-colors">Our Team</a></div>
              <div><a href="#contact" className="text-background/80 hover:text-background transition-colors">Contact</a></div>
            </div>
          </div>
          
          <div className="space-y-4">
            <h4 className="font-semibold">Support</h4>
            <div className="space-y-2">
              <div><a href="mailto:help@campusbuddy.edu" className="text-background/80 hover:text-background transition-colors">Help Center</a></div>
              <div><a href="#" className="text-background/80 hover:text-background transition-colors">Privacy Policy</a></div>
              <div><a href="#" className="text-background/80 hover:text-background transition-colors">Terms of Service</a></div>
            </div>
          </div>
          
          <div className="space-y-4" id="contact">
            <h4 className="font-semibold">Connect With Us</h4>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-background/80">
                <Mail className="h-4 w-4" />
                <a href="mailto:team@campusbuddy.edu" className="hover:text-background transition-colors">
                  team@campusbuddy.edu
                </a>
              </div>
              <div className="flex gap-2">
                <Button variant="ghost" size="icon" className="text-background/80 hover:text-background hover:bg-background/10">
                  <Github className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="text-background/80 hover:text-background hover:bg-background/10">
                  <Linkedin className="h-4 w-4" />
                </Button>
                <Button variant="ghost" size="icon" className="text-background/80 hover:text-background hover:bg-background/10">
                  <Twitter className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
        </div>
        
        <div className="border-t border-background/20 mt-12 pt-8 text-center">
          <p className="text-background/60">
            © 2024 Campus Buddy. Made with ❤️ by students, for students.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;