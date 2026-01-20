import { LucideIcon } from 'lucide-react';
import { Card } from '@/app/components/ui/card';
import { cn } from '@/app/components/ui/utils';

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: {
    value: string;
    positive: boolean;
  };
  subtitle?: string;
  variant?: 'default' | 'critical' | 'warning' | 'success';
  className?: string;
}

export function MetricCard({ 
  title, 
  value, 
  icon: Icon, 
  trend, 
  subtitle,
  variant = 'default',
  className 
}: MetricCardProps) {
  const variantStyles = {
    default: 'bg-card',
    critical: 'bg-card border-[var(--status-critical)]',
    warning: 'bg-card border-[var(--status-warning)]',
    success: 'bg-card border-[var(--status-success)]',
  };

  const iconStyles = {
    default: 'text-muted-foreground',
    critical: 'text-[var(--status-critical)]',
    warning: 'text-[var(--status-warning)]',
    success: 'text-[var(--status-success)]',
  };

  return (
    <Card className={cn(variantStyles[variant], "p-6", className)}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm text-muted-foreground">{title}</p>
          <p className="mt-2 text-3xl font-semibold">{value}</p>
          {subtitle && (
            <p className="mt-1 text-xs text-muted-foreground">{subtitle}</p>
          )}
          {trend && (
            <div className="mt-2 flex items-center gap-1">
              <span
                className={cn(
                  "text-xs font-medium",
                  trend.positive ? "text-[var(--status-success)]" : "text-[var(--status-critical)]"
                )}
              >
                {trend.positive ? '↑' : '↓'} {trend.value}
              </span>
              <span className="text-xs text-muted-foreground">vs last hour</span>
            </div>
          )}
        </div>
        <div className={cn("rounded-md bg-muted p-3", iconStyles[variant])}>
          <Icon className="h-6 w-6" />
        </div>
      </div>
    </Card>
  );
}
