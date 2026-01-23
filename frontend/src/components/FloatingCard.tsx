import { cn } from "@/lib/utils";
import { LucideIcon } from "lucide-react";

interface FloatingCardProps {
    icon: LucideIcon;
    title: string;
    subtitle: string;
    className?: string;
    animationClass?: string;
}

const FloatingCard = ({
    icon: Icon,
    title,
    subtitle,
    className,
    animationClass = "animate-float"
}: FloatingCardProps) => {
    return (
        <div
            className={cn(
                "flex items-center gap-3 bg-card rounded-xl px-4 py-3 shadow-floating",
                animationClass,
                className
            )}
        >
            <div className="flex items-center justify-center w-10 h-10 rounded-lg bg-accent">
                <Icon className="w-5 h-5 text-primary" />
            </div>
            <div>
                <p className="text-sm font-semibold text-foreground">{title}</p>
                <p className="text-xs text-muted-foreground">{subtitle}</p>
            </div>
        </div>
    );
};

export default FloatingCard;
