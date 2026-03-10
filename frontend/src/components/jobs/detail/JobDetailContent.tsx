import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { RecommendedJobDetail } from '@/types/job';

interface Props {
    job: RecommendedJobDetail;
}

const JobDetailContent = ({ job }: Props) => {
    return (
        <div className="space-y-6">
            {/* Description */}
            <Card className="border-border shadow-soft">
                <CardHeader>
                    <CardTitle className="text-lg">職缺描述</CardTitle>
                </CardHeader>
                <CardContent>
                    <div className="text-muted-foreground leading-relaxed whitespace-pre-line">
                        {job.description}
                    </div>
                </CardContent>
            </Card>

            {/* Requirements */}
            {job.requirements && job.requirements.length > 0 && (
                <Card className="border-border shadow-soft">
                    <CardHeader>
                        <CardTitle className="text-lg">條件要求</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2">
                            {job.requirements.map((req, index) => (
                                <li key={index} className="flex items-start gap-2 text-muted-foreground">
                                    <span className="mt-1.5 h-1.5 w-1.5 rounded-full bg-primary shrink-0" />
                                    <span>{req}</span>
                                </li>
                            ))}
                        </ul>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};

export default JobDetailContent;
