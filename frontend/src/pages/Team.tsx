import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { useState } from "react";
import { Palette, Server, Brain, Database, ChevronDown, Users } from "lucide-react";

const Team = () => {
  const [openKey, setOpenKey] = useState<string | null>(null);

  // 團隊資料
  const teams = [
    {
      key: "frontend",
      title: "前端團隊",
      role: "UI / UX / 前端開發",
      description: "負責使用者介面設計、前端互動與使用體驗優化",
      icon: Palette,
      members: [
        {
          name: "Alice",
          role: "Frontend Engineer",
          avatar: "/avatars/alice.png",
        },
        {
          name: "Bob",
          role: "UI Designer",
          avatar: "/avatars/bob.png",
        },
      ],
    },
    {
      key: "backend",
      title: "後端團隊",
      role: "API / 系統架構",
      description: "負責伺服器、API、資料流程與系統穩定性",
      icon: Server,
      members: [
        {
          name: "Alice",
          role: "Frontend Engineer",
          avatar: "/avatars/alice.png",
        },
        {
          name: "Bob",
          role: "UI Designer",
          avatar: "/avatars/bob.png",
        },
      ],
    },
    {
      key: "model",
      title: "模型團隊",
      role: "AI / ML / Recommendation",
      description: "負責模型訓練、推論與推薦邏輯設計",
      icon: Brain,
      members: [
        {
          name: "Alice",
          role: "Frontend Engineer",
          avatar: "/avatars/alice.png",
        },
        {
          name: "Bob",
          role: "UI Designer",
          avatar: "/avatars/bob.png",
        },
      ],
    },
    {
      key: "data",
      title: "資料團隊",
      role: "Data / ETL / Analysis",
      description: "負責資料清洗、分析與特徵工程",
      icon: Database,
      members: [
        {
          name: "Alice",
          role: "Frontend Engineer",
          avatar: "/avatars/alice.png",
        },
        {
          name: "Bob",
          role: "UI Designer",
          avatar: "/avatars/bob.png",
        },
      ],
    },
  ];
  return (
    <div className="container py-12 animate-fade-in">
      <div className="text-center mb-12">
        <div className="inline-flex items-center justify-center h-16 w-16 rounded-full bg-primary/10 mb-6">
          <Users className="h-8 w-8 text-primary" />
        </div>
        <h1 className="text-3xl font-bold mb-4">職星領航員團隊組成</h1>
        {/* <p className="text-muted-foreground max-w-2xl mx-auto">
          認識我們專業的團隊成員
        </p> */}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-4xl mx-auto">
        {/* {[1, 2, 3].map((i) => (
          <Card key={i} className="text-center">
            <CardHeader>
              <div className="h-24 w-24 rounded-full bg-muted mx-auto mb-4" />
              <CardTitle>團隊成員 {i}</CardTitle>
              <CardDescription>職位名稱</CardDescription>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-muted-foreground">
                團隊成員簡介內容待補充
              </p>
            </CardContent>
          </Card>
        ))} */}
        {teams.map((team) => {
          const Icon = team.icon;
          const isOpen = openKey === team.key;

          return (
            <Card key={team.key} className="cursor-pointer transition hover:shadow-md">
              <CardHeader className="text-center relative">
                {/* icon */}
                <div className="h-16 w-16 mx-auto mb-4 rounded-xl bg-primary/10 flex items-center justify-center">
                  <Icon className="h-8 w-8 text-primary" />
                </div>

                <CardTitle>{team.title}</CardTitle>
                <CardDescription>{team.role}</CardDescription>

                {/* 展開按鈕, 唯一可點防誤觸 */}
                <button
                  type="button"
                  onClick={() => setOpenKey(isOpen ? null : team.key)}
                  className="absolute right-4 top-4 rounded-md p-1 hover:bg-muted"
                >
                  <ChevronDown
                    className={`h-4 w-4 text-muted-foreground transition-transform ${isOpen ? "rotate-180" : ""}`}
                  />
                </button>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground mb-4">{team.description}</p>

                {/* 成員區 */}
                <div className={`overflow-hidden ${isOpen ? "animate-accordion-down" : "animate-accordion-up"}`}>
                  {isOpen && (
                    <div className="grid grid-cols-1 gap-3">
                      {team.members.map((member) => (
                        <div key={member.name} className="flex items-center gap-3 rounded-lg border bg-card p-3">
                          <img
                            src={member.avatar}
                            alt={member.name}
                            className="h-10 w-10 rounded-full object-cover bg-muted"
                          />
                          <div>
                            <p className="text-sm font-medium">{member.name}</p>
                            <p className="text-xs text-muted-foreground">{member.role}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          );
        })}
      </div>
    </div>
  );
};

export default Team;
