import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ExternalLink, Flame } from "lucide-react";

// 定義資料介面
export interface Course {
  title: string;
  description: string;
  url: string;
  thumbnail: string;
  source?: string;
}

interface CourseCardProps {
  course: Course;
}

const CourseCard = ({ course }: CourseCardProps) => {
  // 判斷是否為官方推薦課程 (Sunny Course)
  const isOfficial = course.source === "Sunny Course";

  return (
    <Card className={`group overflow-hidden transition-all duration-300 hover:shadow-lg hover:-translate-y-1 h-full flex flex-col ${
      isOfficial ? "border-2 border-yellow-400 bg-yellow-50/30" : ""
    }`}>
      <div className="aspect-video overflow-hidden relative">
        <img
          src={course.thumbnail}
          alt={course.title}
          className="h-full w-full object-cover transition-transform duration-300 group-hover:scale-105"
          // 如果圖片載入失敗，給一個預設圖 (可選)
          onError={(e) => {
            (e.target as HTMLImageElement).src = "https://placehold.co/600x400?text=No+Image";
          }}
        />
        {isOfficial && (
          <div className="absolute top-2 right-2 bg-yellow-500 text-white text-xs font-bold px-2 py-1 rounded-full flex items-center gap-1 shadow-md">
            <Flame className="w-3 h-3" /> 官方推薦
          </div>
        )}
      </div>

      <CardHeader className="pb-2">
        <CardTitle className="text-lg leading-tight">
          <span className="block text-foreground">{course.title}</span>
          {course.source && (
             <span className="inline-block mt-2 text-xs bg-secondary text-secondary-foreground px-2 py-0.5 rounded">
               {course.source}
             </span>
          )}
        </CardTitle>
      </CardHeader>

      <CardContent className="pb-2 flex-grow">
        <CardDescription className="line-clamp-3 text-sm">
          {course.description || "點擊查看詳細教學內容..."}
        </CardDescription>
      </CardContent>

      <CardFooter className="mt-auto pt-4">
        <Button
          asChild
          className={`w-full gap-2 ${isOfficial ? "bg-yellow-500 hover:bg-yellow-600 text-white" : ""}`}
          variant={isOfficial ? "default" : "default"}
        >
          <a href={course.url} target="_blank" rel="noopener noreferrer">
            {isOfficial ? "立即上課" : "觀看教學"}
            <ExternalLink className="h-4 w-4" />
          </a>
        </Button>
      </CardFooter>
    </Card>
  );
};

export default CourseCard;