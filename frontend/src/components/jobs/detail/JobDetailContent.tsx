import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { RecommendedJobDetail } from '@/types/job';
import { cleanDimensionText } from '@/utils/textCleaner';
import { splitIntoParagraphs } from '@/utils/textFormat';

interface Props {
    job: RecommendedJobDetail;
}

const JobDetailContent = ({ job }: Props) => {
    const description = cleanDimensionText(job.description);
    const paragraphs = splitIntoParagraphs(description);

    return (
        <div className="space-y-6">
            {/* Job Description */}
            <Card className="border-border shadow-soft">
                <CardHeader>
                    <CardTitle className="text-lg">職缺描述</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                    {paragraphs.map((para, i) => (
                        <p key={i} className="text-muted-foreground leading-[1.85] tracking-wide text-sm">
                            {para}
                        </p>
                    ))}
                </CardContent>
            </Card>

            {/* Requirements */}
            {job.requirements.length > 0 && (
                <Card className="border-border shadow-soft">
                    <CardHeader>
                        <CardTitle className="text-lg">條件要求</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <ul className="space-y-2">
                            {job.requirements.flatMap(req => 
                                splitIntoParagraphs(cleanDimensionText(req)).map((para, index) => (
                                    <li
                                        key={`${req}-${index}`}
                                        className="flex items-start gap-3 text-muted-foreground"
                                    >
                                        <span className="inline-block h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                                        <span>{para}</span>
                                    </li>
                                ))
                            )}
                        </ul>
                    </CardContent>
                </Card>
            )}
        </div>
    );
};


export default JobDetailContent;
