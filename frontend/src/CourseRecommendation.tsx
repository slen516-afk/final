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
      const incoming = location.state?.autoSearchKeywords || location.state?.autoSearch;

      if (incoming) {
        setLoading(true);
        setHasSearched(true);
        setCourses([]); 

        let keywords: string[] = [];
        
        if (Array.isArray(incoming)) {
          keywords = incoming;
          setQuery(keywords.join(", "));
        } else {
          keywords = [incoming];
          setQuery(incoming);
        }

        console.log("🚀 準備搜尋多個關鍵字:", keywords);

        try {
          const tasks = keywords.map(k => fetchCourses(k));
          const resultsArray = await Promise.all(tasks);
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
  }, [location.state]);

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter") handleManualSearch();
  };

  return (
    // ✨ 修改 1: 背景色改為淡淡的綠色系 (bg-green-50/30)
    <section className="py-16 px-4 bg-green-50/30 min-h-screen">
      <div className="container mx-auto max-w-6xl">
        <div className="text-center mb-10">
          {/* ✨ 修改 2: 標題顏色改為深綠色 (text-green-800) */}
          <h2 className="text-3xl md:text-4xl font-bold text-green-800 mb-3">
            AI 智慧課程推薦
          </h2>
          {/* ✨ 修改 3: 副標題顏色改為中綠色 (text-green-600/80) */}
          <p className="text-xl text-green-600/80 mb-6">Smart Course Recommendations</p>
          
          <div className="max-w-xl mx-auto flex gap-2">
            <Input 
              placeholder="輸入想學的技能..." 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyDown={handleKeyDown}
              // ✨ 修改 4: 輸入框 Focus 時的綠色光暈 (focus-visible:ring-green-500)
              className="h-12 text-lg bg-background focus-visible:ring-green-500"
            />
            {/* ✨ 修改 5: 按鈕改為綠色背景，hover 變深綠色 (bg-green-600 hover:bg-green-700 text-white) */}
            <Button size="lg" className="h-12 px-6 bg-green-600 hover:bg-green-700 text-white" onClick={handleManualSearch} disabled={loading}>
              {/* ✨ 修改 6: 按鈕內的 Loading 圖示改為淺綠色/白色以對比背景 (text-green-100) */}
              {loading ? <Loader2 className="animate-spin text-green-100" /> : <Search />}
              <span className="ml-2 hidden sm:inline">搜尋</span>
            </Button>
          </div>
        </div>

        <div className="mt-8">
          {loading ? (
             // ✨ 修改 7: 載入中文字顏色 (text-green-700)
             <div className="text-center text-green-700 py-12">
               {/* ✨ 修改 8: 大 Loading 圖示顏色 (text-green-600) */}
               <Loader2 className="w-8 h-8 animate-spin mx-auto mb-4 text-green-600" />
               <p>AI 正在同時為您尋找多個技能的課程資源...</p>
             </div>
          ) : courses.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
              {courses.map((course, index) => (
                <CourseCard key={`${course.url}-${index}`} course={course} />
              ))}
            </div>
          ) : hasSearched ? (
            // ✨ 修改 9: 無結果文字顏色
            <div className="text-center py-12 text-green-700/80">
              <p>找不到相關課程，請嘗試其他關鍵字</p>
            </div>
          ) : (
            // ✨ 修改 10: 初始空狀態的文字與邊框顏色 (text-green-700/60, border-green-200/50)
            <div className="text-center py-12 text-green-700/60 border-2 border-dashed border-green-200/50 rounded-xl">
              <p>請從 Dashboard 點擊「去補強」或在上方輸入關鍵字</p>
            </div>
          )}
        </div>
      </div>
    </section>
  );
};

export default CourseRecommendation;