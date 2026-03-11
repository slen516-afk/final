import { Card, CardContent, CardHeader } from '@/components/ui/card';
import { Skeleton } from '@/components/ui/skeleton';

const JobDetailSkeleton = () => (
    <div className="space-y-6">
        <Card>
            <CardHeader className="space-y-4">
                <div className="flex items-start justify-between">
                    <div className="flex-1 space-y-3">
                        <Skeleton className="h-8 w-3/4" />
                        <Skeleton className="h-5 w-1/2" />
                    </div>
                    <Skeleton className="h-12 w-12 rounded-full" />
                </div>
                <div className="flex flex-wrap gap-3">
                    <Skeleton className="h-6 w-24" />
                    <Skeleton className="h-6 w-28" />
                </div>
            </CardHeader>
        </Card>
        <Card>
            <CardHeader><Skeleton className="h-6 w-32" /></CardHeader>
            <CardContent className="space-y-3">
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-full" />
                <Skeleton className="h-4 w-3/4" />
            </CardContent>
        </Card>
        <Card>
            <CardHeader><Skeleton className="h-6 w-32" /></CardHeader>
            <CardContent className="space-y-2">
                {[...Array(4)].map((_, i) => <Skeleton key={i} className="h-4 w-full" />)}
            </CardContent>
        </Card>
    </div>
);

export default JobDetailSkeleton;
