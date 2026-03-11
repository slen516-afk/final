import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { TrendingUp, AlertTriangle, Lightbulb } from 'lucide-react';
import type { RecommendedJobDetail } from '@/types/job';
import { cleanDimensionText } from '@/utils/textCleaner';

interface Props {
    job: RecommendedJobDetail;
}

const JobDetailUserAnalysis = ({ job }: Props) => {
    const strengths = cleanDimensionText(job.strengths);
    const weaknesses = cleanDimensionText(job.weaknesses);
    const tips = cleanDimensionText(job.interview_tips);

    return (
        <Card className="border-border shadow-soft bg-[#fbf1e8]">
            <CardHeader>
                <CardTitle className="text-lg">用戶專屬分析</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
                {/* Strengths */}
                {strengths && (
                    <div className="bg-white rounded-lg p-4 border border-border">
                        <div className="flex items-center gap-2 mb-2">
                            <TrendingUp className="h-5 w-5 text-emerald-600" />
                            <h4 className="font-semibold text-foreground">優勢分析</h4>
                        </div>
                        <p className="text-muted-foreground text-sm leading-relaxed whitespace-pre-line">
                            {strengths}
                        </p>
                    </div>
                )}

                {/* Weaknesses */}
                {weaknesses && (
                    <div className="bg-white rounded-lg p-4 border border-border">
                        <div className="flex items-center gap-2 mb-2">
                            <AlertTriangle className="h-5 w-5 text-amber-500" />
                            <h4 className="font-semibold text-foreground">劣勢分析</h4>
                        </div>
                        <p className="text-muted-foreground text-sm leading-relaxed whitespace-pre-line">
                            {weaknesses}
                        </p>
                    </div>
                )}

                {/* Interview Tips */}
                {tips && (
                    <div className="bg-white rounded-lg p-4 border border-primary/20 shadow-sm">
                        <div className="flex items-center gap-2 mb-2">
                            <Lightbulb className="h-5 w-5 text-primary" />
                            <h4 className="font-bold text-foreground">專家建議：面試準備</h4>
                        </div>
                        <p className="text-muted-foreground text-sm leading-relaxed whitespace-pre-line">
                            {tips}
                        </p>
                    </div>
                )}
            </CardContent>
        </Card>
    );
};

export default JobDetailUserAnalysis;
