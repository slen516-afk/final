import { Header } from "@/components/Header";
import { HeroSection } from "@/components/HeroSection";
import { QuickExperienceZone } from "@/components/QuickExperienceZone";
import { ServicesSection } from "@/components/ServicesSection";
import { Footer } from "@/components/Footer";
import { CareerGuideWidget } from "@/components/CareerGuideWidget";

const Index = () => {
  return (
    <div className="min-h-screen">
      <Header />
      <main>
        <HeroSection />
        <QuickExperienceZone />
        <ServicesSection />
      </main>
      <Footer />
      <CareerGuideWidget />
    </div>
  );
};

export default Index;