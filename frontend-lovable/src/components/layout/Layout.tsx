import { ReactNode } from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import CareerGuide from '@/components/career-guide/CareerGuide';
import DevStateToggles from '@/components/debug/DevStateToggles';

interface LayoutProps {
  children: ReactNode;
}

const Layout = ({ children }: LayoutProps) => {
  return (
    <div className="flex min-h-screen flex-col overflow-x-hidden max-w-[100vw]">
      <Navbar />
      <main className="flex-1 overflow-x-hidden max-w-full bg-card">{children}</main>
      <Footer />
      <CareerGuide />
      <DevStateToggles />
    </div>
  );
};

export default Layout;
