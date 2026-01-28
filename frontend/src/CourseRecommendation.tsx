import { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import CourseCard from "@/components/ui/CourseCard";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Search, Loader2 } from "lucide-react";

// 定義資料介面
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
  
  const location = useLocation();

  // 抽出單一搜尋邏輯
  const fetchCourses = async (keyword: string) => {
    try {
      const response = await fetch(`${API_BASE}/api/learning/recommendations`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_interest: keyword }),
      });
      const data = await response.json();
      return data.status === "success" ? data.data : [];
    } catch (error) {
      console.error(`搜尋 ${keyword} 失敗:`, error);
      return [];
    }
  };

  // 1. 手動搜尋 (只搜一個)
  const handleManualSearch = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setHasSearched(true);
    setCourses([]); 

    const results = await fetchCourses(query);
    setCourses(results);
    setLoading(false);
  };

  // 2. 🔥 自動搜尋 (支援多關鍵字陣列)
  useEffect(() => {
    const initAutoSearch = async () => {
      // 👇 這裡改了：優先讀取 autoSearchKeywords (陣列)，其次才是 autoSearch (單字串)
      const incoming = location.state?.autoSearchKeywords || location.state?.autoSearch;

      if (incoming) {
        setLoading(true);
        setHasSearched(true);
        setCourses([]); 

        let keywords: string[] = [];
        
        // 判斷是單一字串還是陣列
        if (Array.isArray(incoming)) {
          keywords = incoming; // 是陣列 (從 Dashboard 傳來的)
          setQuery(keywords.join(", ")); // 搜尋框顯示所有關鍵字
        } else {
          keywords = [incoming]; // 是單一字串
          setQuery(incoming);
        }

        console.log("🚀 準備搜尋多個關鍵字:", keywords);

        try {
          // 🔥 使用 Promise.all 同時發送多個請求
          const tasks = keywords.map(k => fetchCourses(k));
          const resultsArray = await Promise.all(tasks);

          // 合併所有結果
          const mergedCourses = resultsArray.flat();
          
          setCourses(mergedCourses);
        } catch (e) {
          console.error("自動搜尋出錯:", e);
        } finally {
          setLoading(false);
        }
      }
    };

    initAutoSearch();
  }, [location.state]); // 監聽導航狀態

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleManualSearch();
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
            <Button size="lg" className="h-12 px-6" onClick={handleManualSearch} disabled={loading}>
              {loading ? <Loader2 className="animate-spin" /> : <Search />}
              <span className="ml-2 hidden sm:inline">搜尋</span>
            </Button>
          </div>
        </div>

        <div className="mt-8">
          {loading ? (
             <div className="text-center text-muted-foreground py-12">
               <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4" />
               <p>AI 正在同時為您尋找多個技能的課程資源...</p>
             </div>
          ) : courses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {courses.map((course, index) => (
                // 加上 index 當 key 避免重複資料報錯
                <CourseCard key={`${course.url}-${index}`} course={course} />
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