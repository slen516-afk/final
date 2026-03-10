import { useNavigate } from "react-router-dom";
import {
  MapPin,
  Building2,
  ExternalLink,
  Briefcase,
  FileSearch,
} from "lucide-react";
import { Card, CardContent, CardHeader } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import icon104 from "@/assets/104-icon.png";
import type { RecommendedJob } from "@/types/job";
import { cleanDimensionText, extractCity } from "@/utils/textCleaner";

/** Score color helper */
const getScoreColor = (score: number) => {
  if (score >= 80) return "text-emerald-600 bg-emerald-50 border-emerald-200";
  if (score >= 65) return "text-amber-600 bg-amber-50 border-amber-200";
  return "text-rose-600 bg-rose-50 border-rose-200";
};

const RecommendationJobCard = ({ job }: { job: RecommendedJob }) => {
  const navigate = useNavigate();
  const city = extractCity(job.location);
  const reason = cleanDimensionText(job.recommendation_reason);

  // Parse "85.0%" to 85.0
  const scoreNum = typeof job.match_score === 'string'
    ? parseFloat(job.match_score.replace('%', ''))
    : (job.match_score || 0);

  return (
    <Card className="overflow-hidden hover:shadow-medium hover:-translate-y-1 transition-all duration-300 group border-border hover:border-primary/30 hover:shadow-[0_8px_30px_rgba(141,73,3,0.12)]">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-4">
          {/* Title with 104 icon on the left */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <img
                src={icon104}
                alt="104人力銀行"
                className="h-6 w-6 rounded-full shadow-sm flex-shrink-0"
              />
              <h3 className="text-lg font-semibold text-foreground group-hover:text-primary transition-colors truncate">
                {job.title}
              </h3>
            </div>
            <div className="flex items-center gap-2 mt-1 text-muted-foreground">
              <Building2 className="h-4 w-4 flex-shrink-0" />
              <span className="text-sm truncate">{job.company}</span>
            </div>
          </div>

          {/* Match score – top right */}
          <div className="flex-shrink-0">
            <div
              className={`px-3 py-1.5 rounded-lg border text-sm font-bold ${getScoreColor(scoreNum)}`}
            >
              {typeof job.match_score === 'string' ? job.match_score : `${job.match_score}%`}
            </div>
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Recommendation reason with line-clamp */}
        {reason && (
          <p className="text-muted-foreground text-sm line-clamp-3">
            {reason}
          </p>
        )}

        {/* Badges: city + industry (no salary) */}
        <div className="flex flex-wrap gap-2">
          {city && (
            <Badge variant="secondary" className="flex items-center gap-1">
              <MapPin className="h-3 w-3" />
              {city}
            </Badge>
          )}
          <Badge variant="outline" className="flex items-center gap-1">
            <Briefcase className="h-3 w-3" />
            {job.industry}
          </Badge>
        </div>

        {/* Action buttons */}
        <div className="flex gap-3 pt-2">
          <Button
            size="sm"
            variant="outline"
            className="gap-1"
            onClick={() => navigate(`/jobs/${job.id}`)}
          >
            <FileSearch className="h-3 w-3" />
            查看詳細
          </Button>
          <a
            href={job.externalUrl}
            target="_blank"
            rel="noopener noreferrer"
          >
            <Button size="sm" className="gap-1">
              立即投遞
              <ExternalLink className="h-3 w-3" />
            </Button>
          </a>
        </div>
      </CardContent>
    </Card>
  );
};

export default RecommendationJobCard;