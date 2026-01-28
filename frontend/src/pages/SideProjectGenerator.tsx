import { useState } from "react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Card, CardContent, CardHeader, CardTitle, CardFooter } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Lightbulb, Code2, Rocket, Loader2, Star, Sparkles, AlertCircle } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:5000";

const SideProjectGenerator = () => {
  const [inputSkills, setInputSkills] = useState("");
  const [loading, setLoading] = useState(false);
  const [suggestions, setSuggestions] = useState([]);

  const handleGenerate = async () => {
    if (!inputSkills.trim()) return;
    setLoading(true);
    setSuggestions([]); 

    try {
      const response = await fetch(`${API_BASE}/api/projects/suggestions`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          skills: inputSkills.split(","), 
          interests: "Web Development"   
        }),
      });

      const data = await response.json();
      
      // 支援 { suggestions: [...] } 或直接 [...] 格式
      const resultList = data.suggestions || data || [];
      
      if (Array.isArray(resultList)) {
        setSuggestions(resultList);
      } else {
        console.error("格式錯誤:", data);
      }
    } catch (error) {
      console.error("API Error:", error);
      alert("連線失敗，請確認後端是否啟動");
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        
        {/* Header */}
        <div className="flex flex-col gap-2">
          <h1 className="text-3xl font-bold tracking-tight flex items-center gap-2 text-indigo-600">
            <Rocket className="h-8 w-8" />
            AI 專案點子生成器
          </h1>
          <p className="text-muted-foreground text-lg">
            不知道要做什麼 Side Project？輸入你會的技能，讓 AI 幫你想！
          </p>
        </div>

        {/* Input Section */}
        <div className="bg-white p-6 rounded-xl shadow-sm border border-slate-200">
            <h3 className="text-lg font-semibold mb-2 flex items-center gap-2">
              <Code2 className="w-5 h-5 text-slate-500" />
              輸入技能關鍵字
            </h3>
            <div className="flex gap-4">
              <Input 
                placeholder="例如: Python, React, OpenAI API..." 
                className="text-lg h-12"
                value={inputSkills}
                onChange={(e) => setInputSkills(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
              />
              <Button size="lg" className="h-12 px-8 bg-indigo-600 hover:bg-indigo-700 text-white" onClick={handleGenerate} disabled={loading}>
                {loading ? <Loader2 className="animate-spin" /> : <Sparkles className="mr-2 h-4 w-4" />}
                生成點子
              </Button>
            </div>
        </div>

        {/* Results Section */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {suggestions.map((project, index) => (
            <Card key={index} className="flex flex-col hover:shadow-xl transition-all border-t-4 border-t-indigo-500 bg-white">
              <CardHeader>
                <div className="flex justify-between items-start mb-2">
                  <Badge variant="outline" className="bg-indigo-50 text-indigo-700">
                    {project.difficulty || "中等"}
                  </Badge>
                  <div className="flex text-yellow-400">
                    {[...Array(4)].map((_, i) => <Star key={i} className="w-3 h-3 fill-current" />)}
                  </div>
                </div>
                <CardTitle className="text-xl text-slate-900">
                  {project.project_name || "未命名專案"}
                </CardTitle>
              </CardHeader>
              
              <CardContent className="flex-1 space-y-4">
                <p className="text-slate-600 line-clamp-3">{project.description}</p>
                <div className="flex flex-wrap gap-2">
                  {Array.isArray(project.tech_stack) && project.tech_stack.map((tech, i) => (
                    <Badge key={i} variant="secondary">{tech}</Badge>
                  ))}
                </div>
              </CardContent>

              <CardFooter className="pt-4 border-t bg-slate-50/50 text-xs text-slate-600">
                 <ul className="list-disc list-inside w-full">
                   {Array.isArray(project.key_features) && project.key_features.slice(0, 2).map((f, i) => (
                     <li key={i}>{f}</li>
                   ))}
                 </ul>
              </CardFooter>
            </Card>
          ))}
        </div>

        {/* Empty State */}
        {!loading && suggestions.length === 0 && (
          <div className="text-center py-20 opacity-50 border-2 border-dashed rounded-xl">
            <Lightbulb className="w-16 h-16 mx-auto mb-4 text-slate-300" />
            <p>請在上方輸入技能開始生成</p>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default SideProjectGenerator;