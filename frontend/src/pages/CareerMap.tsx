import { useState, useRef, useEffect, useCallback } from "react";
import { DashboardLayout } from "@/components/dashboard/DashboardLayout";
import { Button } from "@/components/ui/button";
import { ZoomIn, ZoomOut, Maximize2, Star, Info } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { cn } from "@/lib/utils";

/**
 * Interactive Career Map
 * 
 * Supabase tables required:
 * 
 * Table: career_nodes
 * - id: UUID
 * - user_id: UUID (foreign key)
 * - node_type: TEXT ('past' | 'current' | 'future')
 * - job_title: TEXT
 * - company: TEXT (nullable for future nodes)
 * - start_date: DATE (nullable for future)
 * - end_date: DATE (nullable)
 * - skills: TEXT[]
 * - achievements: TEXT[]
 * - order_index: INTEGER (for positioning)
 * - created_at: TIMESTAMP
 * 
 * Table: career_paths
 * - id: UUID
 * - from_node_id: UUID (foreign key)
 * - to_node_id: UUID (foreign key)
 * - path_type: TEXT ('solid' | 'dotted')
 * - probability: FLOAT (for future paths, based on similar profiles)
 * - required_skills: TEXT[] (for future transitions)
 * - required_certifications: TEXT[]
 * 
 * Table: similar_profiles
 * - id: UUID
 * - base_profile_id: UUID (reference user)
 * - matched_profile_id: UUID (anonymous similar user)
 * - similarity_score: FLOAT
 * - common_skills: TEXT[]
 */

interface CareerNode {
  id: string;
  type: "past" | "current" | "future";
  title: string;
  company?: string;
  year?: string;
  skills: string[];
  achievements?: string[];
  requiredCerts?: string[];
}

const sampleNodes: CareerNode[] = [
  {
    id: "1",
    type: "past",
    title: "Junior Developer",
    company: "StartupXYZ",
    year: "2019",
    skills: ["HTML", "CSS", "JavaScript"],
    achievements: ["建立公司官網", "學習 React 框架"],
  },
  {
    id: "2",
    type: "past",
    title: "Frontend Developer",
    company: "TechCorp",
    year: "2020",
    skills: ["React", "Redux", "TypeScript"],
    achievements: ["主導產品重構", "效能優化 50%"],
  },
  {
    id: "3",
    type: "past",
    title: "Senior Frontend Engineer",
    company: "MegaTech",
    year: "2022",
    skills: ["Next.js", "GraphQL", "Testing"],
    achievements: ["帶領 5 人團隊", "建立設計系統"],
  },
  {
    id: "4",
    type: "current",
    title: "Staff Engineer",
    company: "InnovateCo",
    year: "2024",
    skills: ["Architecture", "Mentoring", "Strategy"],
    achievements: ["跨團隊技術決策", "技術文化建設"],
  },
  {
    id: "5",
    type: "future",
    title: "Engineering Manager",
    skills: ["People Management", "Budgeting", "Hiring"],
    requiredCerts: ["PMP", "Leadership Training"],
  },
  {
    id: "6",
    type: "future",
    title: "Principal Engineer",
    skills: ["System Design", "Technical Vision", "Innovation"],
    requiredCerts: ["AWS Solutions Architect", "Domain Expert"],
  },
  {
    id: "7",
    type: "future",
    title: "CTO",
    skills: ["Business Strategy", "Board Communication", "M&A Tech Due Diligence"],
    requiredCerts: ["MBA (Optional)", "Executive Coaching"],
  },
];

export default function CareerMap() {
  const containerRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  const [pan, setPan] = useState({ x: 0, y: 0 });
  const [isPanning, setIsPanning] = useState(false);
  const [startPan, setStartPan] = useState({ x: 0, y: 0 });
  const [hoveredNode, setHoveredNode] = useState<CareerNode | null>(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

  const handleZoomIn = () => setScale((s) => Math.min(s + 0.2, 2));
  const handleZoomOut = () => setScale((s) => Math.max(s - 0.2, 0.5));
  const handleReset = () => {
    setScale(1);
    setPan({ x: 0, y: 0 });
  };

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    if (e.button !== 0) return;
    setIsPanning(true);
    setStartPan({ x: e.clientX - pan.x, y: e.clientY - pan.y });
  }, [pan]);

  const handleMouseMove = useCallback((e: React.MouseEvent) => {
    if (!isPanning) return;
    setPan({
      x: e.clientX - startPan.x,
      y: e.clientY - startPan.y,
    });
  }, [isPanning, startPan]);

  const handleMouseUp = useCallback(() => {
    setIsPanning(false);
  }, []);

  const handleNodeHover = (node: CareerNode, e: React.MouseEvent) => {
    setHoveredNode(node);
    setTooltipPos({ x: e.clientX, y: e.clientY });
  };

  // Calculate node positions
  const nodeWidth = 180;
  const nodeGap = 100;
  const startX = 100;
  const centerY = 200;

  return (
    <DashboardLayout>
      <div className="h-screen flex flex-col">
        {/* Header */}
        <header className="px-6 py-4 border-b border-border bg-card/50 flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-foreground">職涯地圖</h1>
            <p className="text-sm text-muted-foreground">
              視覺化您的職涯路徑，探索未來可能性
            </p>
          </div>
          <div className="flex items-center gap-2">
            <Button variant="outline" size="icon" onClick={handleZoomOut}>
              <ZoomOut className="w-4 h-4" />
            </Button>
            <span className="text-sm text-muted-foreground w-16 text-center">
              {Math.round(scale * 100)}%
            </span>
            <Button variant="outline" size="icon" onClick={handleZoomIn}>
              <ZoomIn className="w-4 h-4" />
            </Button>
            <Button variant="outline" size="icon" onClick={handleReset}>
              <Maximize2 className="w-4 h-4" />
            </Button>
          </div>
        </header>

        {/* Legend */}
        <div className="px-6 py-3 border-b border-border bg-muted/30 flex items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-primary" />
            <span className="text-sm text-muted-foreground">過去經歷</span>
          </div>
          <div className="flex items-center gap-2">
            <Star className="w-4 h-4 text-amber-500" />
            <span className="text-sm text-muted-foreground">目前位置 (北極星)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full border-2 border-primary bg-transparent" />
            <span className="text-sm text-muted-foreground">未來可能</span>
          </div>
          <div className="flex items-center gap-2 ml-auto">
            <Info className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-muted-foreground">懸停節點查看詳情</span>
          </div>
        </div>

        {/* Map Canvas */}
        <div
          ref={containerRef}
          className="flex-1 overflow-hidden bg-gradient-to-br from-background via-muted/20 to-background cursor-grab active:cursor-grabbing"
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
        >
          <svg
            width="100%"
            height="100%"
            style={{
              transform: `translate(${pan.x}px, ${pan.y}px) scale(${scale})`,
              transformOrigin: "center center",
            }}
          >
            {/* Connection Lines */}
            <g>
              {sampleNodes.map((node, index) => {
                if (index === sampleNodes.length - 1) return null;
                const x1 = startX + index * (nodeWidth + nodeGap) + nodeWidth;
                const x2 = startX + (index + 1) * (nodeWidth + nodeGap);
                const isFuturePath = node.type === "future" || sampleNodes[index + 1].type === "future";

                return (
                  <line
                    key={`line-${node.id}`}
                    x1={x1}
                    y1={centerY}
                    x2={x2}
                    y2={centerY}
                    stroke="hsl(var(--primary))"
                    strokeWidth={2}
                    strokeDasharray={isFuturePath ? "8 4" : "none"}
                    opacity={isFuturePath ? 0.5 : 1}
                  />
                );
              })}
            </g>

            {/* Nodes */}
            <g>
              {sampleNodes.map((node, index) => {
                const x = startX + index * (nodeWidth + nodeGap);
                const isCurrent = node.type === "current";
                const isFuture = node.type === "future";

                return (
                  <g
                    key={node.id}
                    transform={`translate(${x}, ${centerY - 60})`}
                    onMouseEnter={(e) => handleNodeHover(node, e as unknown as React.MouseEvent)}
                    onMouseLeave={() => setHoveredNode(null)}
                    className="cursor-pointer"
                  >
                    {/* Node Card */}
                    <rect
                      width={nodeWidth}
                      height={120}
                      rx={12}
                      fill={isCurrent ? "hsl(var(--primary))" : "hsl(var(--card))"}
                      stroke={isFuture ? "hsl(var(--primary))" : "hsl(var(--border))"}
                      strokeWidth={isFuture ? 2 : 1}
                      strokeDasharray={isFuture ? "6 3" : "none"}
                      className="transition-all hover:filter hover:brightness-95"
                    />

                    {/* North Star for Current */}
                    {isCurrent && (
                      <g transform={`translate(${nodeWidth / 2 - 12}, -20)`}>
                        <Star
                          className="text-amber-400 fill-amber-400"
                          size={24}
                        />
                      </g>
                    )}

                    {/* Node Indicator */}
                    <circle
                      cx={nodeWidth / 2}
                      cy={0}
                      r={8}
                      fill={isFuture ? "transparent" : "hsl(var(--primary))"}
                      stroke="hsl(var(--primary))"
                      strokeWidth={2}
                    />

                    {/* Title */}
                    <text
                      x={nodeWidth / 2}
                      y={45}
                      textAnchor="middle"
                      className="fill-current text-sm font-semibold"
                      fill={isCurrent ? "hsl(var(--primary-foreground))" : "hsl(var(--foreground))"}
                    >
                      {node.title}
                    </text>

                    {/* Company/Year */}
                    {node.company && (
                      <text
                        x={nodeWidth / 2}
                        y={68}
                        textAnchor="middle"
                        className="fill-current text-xs"
                        fill={isCurrent ? "hsl(var(--primary-foreground) / 0.8)" : "hsl(var(--muted-foreground))"}
                      >
                        {node.company}
                      </text>
                    )}

                    {node.year && (
                      <text
                        x={nodeWidth / 2}
                        y={88}
                        textAnchor="middle"
                        className="fill-current text-xs"
                        fill={isCurrent ? "hsl(var(--primary-foreground) / 0.7)" : "hsl(var(--muted-foreground))"}
                      >
                        {node.year}
                      </text>
                    )}

                    {isFuture && (
                      <text
                        x={nodeWidth / 2}
                        y={75}
                        textAnchor="middle"
                        className="fill-current text-xs italic"
                        fill="hsl(var(--muted-foreground))"
                      >
                        未來路徑
                      </text>
                    )}
                  </g>
                );
              })}
            </g>
          </svg>
        </div>

        {/* Tooltip */}
        <AnimatePresence>
          {hoveredNode && (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 10 }}
              className="fixed z-50 w-72 p-4 rounded-xl shadow-elevated bg-card border border-border pointer-events-none"
              style={{
                left: tooltipPos.x + 20,
                top: tooltipPos.y - 50,
              }}
            >
              <h4 className="font-semibold text-foreground mb-2">
                {hoveredNode.title}
              </h4>
              {hoveredNode.company && (
                <p className="text-sm text-muted-foreground mb-3">
                  {hoveredNode.company} • {hoveredNode.year}
                </p>
              )}

              <div className="space-y-3">
                <div>
                  <h5 className="text-xs font-medium text-muted-foreground mb-1">
                    {hoveredNode.type === "future" ? "所需技能" : "核心技能"}
                  </h5>
                  <div className="flex flex-wrap gap-1">
                    {hoveredNode.skills.map((skill, i) => (
                      <span
                        key={i}
                        className="px-2 py-0.5 text-xs rounded-full bg-primary/10 text-primary"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {hoveredNode.achievements && (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground mb-1">
                      成就
                    </h5>
                    <ul className="text-xs text-foreground space-y-1">
                      {hoveredNode.achievements.map((ach, i) => (
                        <li key={i}>• {ach}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {hoveredNode.requiredCerts && (
                  <div>
                    <h5 className="text-xs font-medium text-muted-foreground mb-1">
                      建議認證
                    </h5>
                    <ul className="text-xs text-amber-600 dark:text-amber-400 space-y-1">
                      {hoveredNode.requiredCerts.map((cert, i) => (
                        <li key={i}>📜 {cert}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </DashboardLayout>
  );
}
