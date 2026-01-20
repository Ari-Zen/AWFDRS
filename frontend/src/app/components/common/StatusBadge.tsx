import { cn } from '@/app/components/ui/utils';
import { AlertCircle, AlertTriangle, Info, CheckCircle } from 'lucide-react';
import type { SeverityLevel, IncidentStatus, WorkflowStatus, VendorStatus } from '@/app/types';

interface StatusBadgeProps {
  status: SeverityLevel | IncidentStatus | WorkflowStatus | VendorStatus;
  className?: string;
  type?: 'severity' | 'status';
}

interface SeverityBadgeProps {
  severity: SeverityLevel;
  className?: string;
}

const statusConfig = {
  // Severity - keep strong colors for impact
  critical: { 
    label: 'Critical', 
    bg: 'var(--status-critical-bg)', 
    text: 'var(--status-critical)',
    border: 'var(--status-critical)',
    icon: AlertCircle
  },
  high: { 
    label: 'High', 
    bg: 'var(--status-warning-bg)', 
    text: 'var(--status-warning)',
    border: 'var(--status-warning)',
    icon: AlertTriangle
  },
  medium: { 
    label: 'Medium', 
    bg: 'var(--status-info-bg)', 
    text: 'var(--status-info)',
    border: 'var(--status-info)',
    icon: Info
  },
  low: { 
    label: 'Low', 
    bg: 'var(--status-neutral-bg)', 
    text: 'var(--status-neutral)',
    border: 'var(--status-neutral)',
    icon: CheckCircle
  },
  
  // Incident Status - neutral tones, lifecycle emphasis
  active: { 
    label: 'Active', 
    neutral: true
  },
  investigating: { 
    label: 'Investigating', 
    neutral: true
  },
  recovering: { 
    label: 'Recovering', 
    neutral: true
  },
  resolved: { 
    label: 'Resolved', 
    bg: 'var(--status-success-bg)', 
    text: 'var(--status-success)',
    border: 'var(--status-success)'
  },
  escalated: { 
    label: 'Escalated', 
    neutral: true
  },
  
  // Workflow Status
  healthy: { 
    label: 'Healthy', 
    bg: 'var(--status-success-bg)', 
    text: 'var(--status-success)',
    border: 'var(--status-success)'
  },
  degraded: { 
    label: 'Degraded', 
    bg: 'var(--status-warning-bg)', 
    text: 'var(--status-warning)',
    border: 'var(--status-warning)'
  },
  failing: { 
    label: 'Failing', 
    bg: 'var(--status-critical-bg)', 
    text: 'var(--status-critical)',
    border: 'var(--status-critical)'
  },
  offline: { 
    label: 'Offline', 
    neutral: true
  },
  
  // Vendor Status
  operational: { 
    label: 'Operational', 
    bg: 'var(--status-success-bg)', 
    text: 'var(--status-success)',
    border: 'var(--status-success)'
  },
  outage: { 
    label: 'Outage', 
    bg: 'var(--status-critical-bg)', 
    text: 'var(--status-critical)',
    border: 'var(--status-critical)'
  },
  maintenance: { 
    label: 'Maintenance', 
    bg: 'var(--status-info-bg)', 
    text: 'var(--status-info)',
    border: 'var(--status-info)'
  },
};

export function SeverityBadge({ severity, className }: SeverityBadgeProps) {
  const config = statusConfig[severity];
  const Icon = config.icon;

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1 rounded-md border px-2.5 py-0.5 text-xs font-semibold transition-colors",
        className
      )}
      style={{
        backgroundColor: config.bg,
        color: config.text,
        borderColor: config.border,
      }}
    >
      {Icon && <Icon className="h-3 w-3" />}
      {config.label}
    </span>
  );
}

export function StatusBadge({ status, className, type = 'status' }: StatusBadgeProps) {
  const config = statusConfig[status];
  
  // If it's a severity type, use SeverityBadge
  if (type === 'severity' || ['critical', 'high', 'medium', 'low'].includes(status)) {
    return <SeverityBadge severity={status as SeverityLevel} className={className} />;
  }

  // For neutral status badges (lifecycle indicators)
  if (config.neutral) {
    return (
      <span
        className={cn(
          "inline-flex items-center rounded-md border border-border bg-muted/40 px-2.5 py-0.5 text-xs font-medium text-muted-foreground transition-colors",
          className
        )}
      >
        {config.label}
      </span>
    );
  }

  // For colored status badges
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-md border px-2.5 py-0.5 text-xs font-medium transition-colors",
        className
      )}
      style={{
        backgroundColor: config.bg,
        color: config.text,
        borderColor: config.border,
      }}
    >
      {config.label}
    </span>
  );
}