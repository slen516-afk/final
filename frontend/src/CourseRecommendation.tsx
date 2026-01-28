import { useState, useEffect } from "react"; // ✅ 加入 useEffect
import { useLocation } from "react-router-dom"; // ✅ 加入 useLocation
import CourseCard from "@/components/ui/CourseCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Loader2 } from "lucide-react";

// 定義 Course 型別 (如果你是 .tsx)
interface Course {
  title: string;
  description: string;
  url: string;
  thumbnail: string;
  source?: string;
}

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

const CourseRecommendation = () => {
  const [query, setQuery] = useState("");
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(false);
  const [hasSearched, setHasSearched] = useState(false);
  
  const location = useLocation(); // ✅ 取得導航帶來的狀態

  // 將搜尋邏輯抽取出來，以便手動與自動都能呼叫
  const performSearch = async (searchQuery: string) => {
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    setHasSearched(true);
    setCourses([]);

    try {
      const response = await fetch(`${API_BASE}/api/learning/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_interest: searchQuery }),
      });

      const data = await response.json();
      if (data.status === "success") {
        setCourses(data.data);
      }
    } catch (error) {
      console.error("API Error:", error);
    } finally {
      setLoading(false);
    }
  };

  // 1. 手動搜尋觸發
  const handleSearch = () => performSearch(query);

  // 2. ✅ 自動搜尋觸發：當頁面載入時檢查是否有行李
  useEffect(() => {
    const autoSearchKey = location.state?.autoSearch;
    if (autoSearchKey) {
      setQuery(autoSearchKey); // 把關鍵字填入輸入框
      performSearch(autoSearchKey); // 直接發動搜尋
    }
  }, [location.state]); // 監聽導航狀態變化

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleSearch();
  };

  return (
    <section className="py-16 px-4 bg-secondary/30 min-h-screen">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-10">
          <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-3">
            AI 智慧課程推薦
          </h2>
          <p className="text-xl text-muted-foreground mb-6">Smart Course Recommendations</p>
          
          <div className="max-w-xl mx-auto flex gap-2">
            <Input 
              placeholder="輸入想學的技能..." 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              className="h-12 text-lg bg-background"
            />
            <Button size="lg" className="h-12 px-6" onClick={handleSearch} disabled={loading}>
              {loading ? <Loader2 className="animate-spin" /> : <Search />}
              <span className="ml-2 hidden sm:inline">搜尋</span>
            </Button>
          </div>
        </div>

        <div className="mt-8">
          {loading ? (
             <div className="text-center text-muted-foreground py-12">
               <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
               <p>AI 正在根據你的需求分析最佳資源...</p>
             </div>
          ) : courses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {courses.map((course, index) => (
                <CourseCard key={index} course={course} />
              ))}
            </div>
          ) : hasSearched ? (
            <div className="text-center py-12 text-muted-foreground">
              <p>找不到相關課程，請嘗試其他關鍵字</p>
            </div>
          ) : (
            <div className="text-center py-12 text-muted-foreground/60 border-2 border-dashed rounded-xl">
              <p>請從 Dashboard 點擊「去補強」或在上方輸入關鍵字</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default CourseRecommendation;