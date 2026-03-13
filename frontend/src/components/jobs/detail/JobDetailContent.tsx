import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import type { RecommendedJobDetail } from '@/types/job';
import { cleanDimensionText } from '@/utils/textCleaner';
import { splitIntoParagraphs } from '@/utils/textFormat';

interface Props {
    job: RecommendedJobDetail;
}

const requirementTitles = [
    '工作經歷',
    '學歷要求',
    '科系要求',
    '語文條件',
];

const JobDetailContent = ({ job }: Props) => {
    const description = cleanDimensionText(job.description);
    const paragraphs = splitIntoParagraphs(description);

    // Flatten requirements first, strip ads, then split into paragraphs
    const rawReqText = job.requirements.join('\n').replace(/提升英文能力/g, '').replace(/提升專業能力/g, '');
    const reqParagraphs = splitIntoParagraphs(cleanDimensionText(rawReqText));

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
            <Card className="border-border shadow-soft">
                <CardHeader>
                    <CardTitle className="text-lg">條件要求</CardTitle>
                </CardHeader>
                <CardContent>
                    <ul className="space-y-4">
                        {reqParagraphs.map((para, index) => {
                            if (!para || para.trim().length === 0) return null;

                            const title = index < 4 ? requirementTitles[index] : null;

                            return (
                                <li
                                    key={index}
                                    className="flex items-start gap-3 text-muted-foreground"
                                >
                                    <span className="inline-block h-1.5 w-1.5 rounded-full bg-primary mt-2 flex-shrink-0" />
                                    <div className="flex flex-col sm:flex-row sm:gap-2 w-full">
                                        {title && (
                                            <span className="font-medium text-foreground min-w-[75px] flex-shrink-0">
                                                {title}：
                                            </span>
                                        )}
                                        <div className="flex flex-col space-y-1">
                                            <span className="leading-relaxed">{para}</span>
                                        </div>
                                    </div>
                                </li>
                            );
                        })}
                    </ul>
                </CardContent>
            </Card>
        </div>
    );
};


export default JobDetailContent;
