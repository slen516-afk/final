import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AppProvider } from "./contexts/AppContext";
import { ResumeProvider } from "./contexts/ResumeContext";
import Layout from "./components/layout/Layout";
import ProtectedRoute from "./components/gatekeeper/ProtectedRoute";

// Pages
import Index from "./pages/Index";
import Team from "./pages/Team";
import FAQ from "./pages/FAQ";
import SkillSearch from "./pages/jobs/SkillSearch";
import JobDetail from "./pages/jobs/JobDetail";
import Recommendations from "./pages/jobs/Recommendations";
import Optimize from "./pages/resume/Optimize";
import Skills from "./pages/analysis/Skills";

import MemberCenter from "./pages/member/MemberCenter";
import RegisterForm from "./pages/auth/RegisterForm";
import UploadResume from "./pages/member/UploadResume";

import CareerPath from "./pages/member/CareerPath";
import MyResumes from "./pages/member/MyResumes";
import Personality from "./pages/member/survey/Personality";
import PersonalityTest from "./pages/member/survey/PersonalityTest";

import NotFound from "./pages/NotFound";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <AppProvider>
      <ResumeProvider>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Layout>
            <Routes>
              {/* 基礎 */}
              <Route path="/" element={<Index />} />
              <Route path="/team" element={<Team />} />
              <Route path="/faq" element={<FAQ />} />
              
              {/* 核心 (Protected) */}
              <Route path="/jobs/skill-search" element={
                <ProtectedRoute><SkillSearch /></ProtectedRoute>
              } />
              <Route path="/jobs/recommendations" element={
                <ProtectedRoute><Recommendations /></ProtectedRoute>
              } />
              <Route path="/jobs/:id" element={<JobDetail />} />
              <Route path="/resume/optimize" element={
                <ProtectedRoute><Optimize /></ProtectedRoute>
              } />
              <Route path="/analysis/skills" element={
                <ProtectedRoute><Skills /></ProtectedRoute>
              } />
              
              {/* 會員 */}
              <Route path="/member/center" element={<MemberCenter />} />
              <Route path="/auth/register-form" element={<RegisterForm />} />
              <Route path="/member/upload-resume" element={<UploadResume />} />
              
              <Route path="/member/career-path" element={<CareerPath />} />
              <Route path="/member/my-resumes" element={<MyResumes />} />
              <Route path="/member/survey/personality" element={<Personality />} />
              <Route path="/member/survey/personality-test" element={<PersonalityTest />} />
              
              
              {/* Catch-all */}
              <Route path="*" element={<NotFound />} />
            </Routes>
          </Layout>
        </BrowserRouter>
      </TooltipProvider>
      </ResumeProvider>
    </AppProvider>
  </QueryClientProvider>
);

export default App;
