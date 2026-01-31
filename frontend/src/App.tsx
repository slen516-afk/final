import SideProjectGenerator from "./pages/SideProjectGenerator";
import { Toaster } from "@/components/ui/toaster";
import CourseRecommendation from './CourseRecommendation';
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import About from "./pages/About";
import Services from "./pages/Services";
import Contact from "./pages/Contact";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import History from "./pages/History";
import Recommendations from "./pages/Recommendations";
import CareerMap from "./pages/CareerMap";
import InterviewPrep from "./pages/InterviewPrep";
import ThankYouLetter from "./pages/ThankYouLetter";
import Achievements from "./pages/Achievements";
import NotFound from "./pages/NotFound";
// 1. 引入你的上傳元件
import ResumeUploader from "./components/ResumeUploader";

const queryClient = new QueryClient();

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Index />} />
          <Route path="/dashboard/side-projects" element={<SideProjectGenerator />} />
          <Route path="/about" element={<About />} />
          <Route path="/services" element={<Services />} />
          <Route path="/contact" element={<Contact />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/dashboard/history" element={<History />} />
          <Route path="/dashboard/recommendations" element={<Recommendations />} />
          <Route path="/dashboard/career-map" element={<CareerMap />} />
          <Route path="/dashboard/interview-prep" element={<InterviewPrep />} />
          <Route path="/dashboard/thank-you" element={<ThankYouLetter />} />
          <Route path="/dashboard/achievements" element={<Achievements />} />

          {/* 2. 新增測試路由：加上一些簡單的排版讓它置中 */}
          <Route path="/resume-upload" element={
            <div className="flex justify-center items-center min-h-screen bg-gray-50">
              <ResumeUploader />
            </div>
          } />
          {/* 👇👇👇 2. 新增這一段：課程搜尋測試頁 */}
          <Route path="/course-search" element={
            <div className="flex justify-center items-center min-h-screen bg-gray-50 p-4">
              {/* 這裡使用了元件，上面的 import 就會亮起來了 */}
              <div className="w-full max-w-4xl bg-white p-6 rounded-lg shadow-md">
                 <CourseRecommendation />
              </div>
            </div>
          } />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;