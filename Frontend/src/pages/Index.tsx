import Header from "@/components/Header";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import ChatDemo from "@/components/ChatDemo";
import Team from "@/components/Team";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <Hero />
        <section id="features">
          <Features />
        </section>
        <section id="demo">
          <ChatDemo />
        </section>
        <section id="team">
          <Team />
        </section>
      </main>
      <Footer />
    </div>
  );
};

export default Index;
