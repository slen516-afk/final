import { Card, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
    MapPin,
    Building2,
    Briefcase,
    FileText,
    ExternalLink,
} from 'lucide-react';
import icon104 from '@/assets/104-icon.png';
import type { RecommendedJobDetail } from '@/types/job';
import { cleanDimensionText } from '@/utils/textCleaner';

interface Props {
    job: RecommendedJobDetail;
    onGenerateLetter: () => void;
}

const JobDetailHeader = ({ job, onGenerateLetter }: Props) => {
    const title = cleanDimensionText(job.title);
    const company = cleanDimensionText(job.company);

    return (
        <Card className="overflow-hidden border-border shadow-soft">
            <CardHeader className="pb-4">
                <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                        <CardTitle className="text-2xl md:text-3xl mb-2">{title}</CardTitle>
                        <div className="flex items-center gap-2 text-lg text-muted-foreground">
                            <Building2 className="h-5 w-5 flex-shrink-0" />
                            <span>{company}</span>
                        </div>
                    </div>
                    <img
                        src={icon104}
                        alt="104人力銀行"
                        className="h-12 w-12 rounded-full shadow-sm flex-shrink-0"
                    />
                </div>

                {/* Meta badges — no salary */}
                <div className="flex flex-wrap gap-3 mt-4">
                    <Badge variant="secondary" className="flex items-center gap-1 px-3 py-1">
                        <MapPin className="h-3.5 w-3.5" />
                        {job.location}
                    </Badge>
                    <Badge variant="outline" className="flex items-center gap-1 px-3 py-1">
                        <Briefcase className="h-3.5 w-3.5" />
                        {job.industry}
                    </Badge>
                </div>

                {/* Action buttons */}
                <div className="flex flex-wrap gap-3 mt-6">
                    <Button onClick={onGenerateLetter} variant="outline" className="gap-2">
                        <FileText className="h-4 w-4" />
                        生成推薦信
                    </Button>
                    <a href={job.externalUrl} target="_blank" rel="noopener noreferrer">
                        <Button className="gap-2">
                            立即應徵
                            <ExternalLink className="h-4 w-4" />
                        </Button>
                    </a>
                </div>
            </CardHeader>
        </Card>
    );
};

export default JobDetailHeader;
