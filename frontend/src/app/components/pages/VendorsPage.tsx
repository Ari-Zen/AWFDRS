import { Building2, Clock, Workflow, TrendingUp, TrendingDown, Minus, AlertTriangle } from 'lucide-react';
import { Card } from '@/app/components/ui/card';
import { StatusBadge } from '@/app/components/common/StatusBadge';
import { Badge } from '@/app/components/ui/badge';
import { Progress } from '@/app/components/ui/progress';
import { mockVendors } from '@/app/data/mockData';

// Helper to determine trend (mock logic for demo)
const getTrend = (vendor: any): 'improving' | 'stable' | 'worsening' => {
  if (vendor.status === 'operational') return 'stable';
  if (vendor.uptime > 98) return 'improving';
  if (vendor.uptime < 95) return 'worsening';
  return 'stable';
};

export function VendorsPage() {
  const operationalCount = mockVendors.filter(v => v.status === 'operational').length;
  const degradedCount = mockVendors.filter(v => v.status === 'degraded').length;

  return (
    <div className="p-8 space-y-6">
      {/* Page Header */}
      <div>
        <h1>Vendors & Integrations</h1>
        <p className="mt-2 text-muted-foreground">
          Monitor external service providers and API integrations
        </p>
      </div>

      {/* Status Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Vendors</p>
              <p className="text-2xl font-semibold mt-1">{mockVendors.length}</p>
            </div>
            <Building2 className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
        <Card className="p-4 border-[var(--status-success)]">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Operational</p>
              <p className="text-2xl font-semibold mt-1" style={{ color: 'var(--status-success)' }}>{operationalCount}</p>
            </div>
            <TrendingUp className="h-8 w-8" style={{ color: 'var(--status-success)' }} />
          </div>
        </Card>
        <Card className="p-4 border-[var(--status-warning)]">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Degraded</p>
              <p className="text-2xl font-semibold mt-1" style={{ color: 'var(--status-warning)' }}>{degradedCount}</p>
            </div>
            <Building2 className="h-8 w-8" style={{ color: 'var(--status-warning)' }} />
          </div>
        </Card>
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Avg Uptime</p>
              <p className="text-2xl font-semibold mt-1">
                {(mockVendors.reduce((acc, v) => acc + v.uptime, 0) / mockVendors.length).toFixed(1)}%
              </p>
            </div>
            <TrendingUp className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
      </div>

      {/* Vendors Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {mockVendors.map((vendor) => {
          const trend = getTrend(vendor);
          return (
            <Card key={vendor.id} className="p-6">
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-muted">
                    <Building2 className="h-6 w-6" />
                  </div>
                  <div>
                    <h3 className="font-medium">{vendor.name}</h3>
                    <p className="text-sm text-muted-foreground">{vendor.integrationType}</p>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <StatusBadge status={vendor.status} />
                  {vendor.status !== 'operational' && (
                    <Badge 
                      variant="outline" 
                      className="gap-1 text-xs"
                    >
                      {trend === 'improving' && (
                        <>
                          <TrendingUp className="h-3 w-3 text-[var(--status-success)]" />
                          <span className="text-[var(--status-success)]">Improving</span>
                        </>
                      )}
                      {trend === 'stable' && (
                        <>
                          <Minus className="h-3 w-3 text-muted-foreground" />
                          <span className="text-muted-foreground">Stable</span>
                        </>
                      )}
                      {trend === 'worsening' && (
                        <>
                          <TrendingDown className="h-3 w-3 text-[var(--status-warning)]" />
                          <span className="text-[var(--status-warning)]">Worsening</span>
                        </>
                      )}
                    </Badge>
                  )}
                </div>
              </div>

              <div className="space-y-4">
                {/* Uptime */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Uptime (30 days)</span>
                    <span className="text-sm font-medium">{vendor.uptime}%</span>
                  </div>
                  <Progress value={vendor.uptime} className="h-2" />
                </div>

                {/* Metrics Grid */}
                <div className="grid grid-cols-3 gap-4 pt-4 border-t">
                  <div>
                    <div className="flex items-center gap-1 text-muted-foreground mb-1">
                      <Workflow className="h-3 w-3" />
                      <span className="text-xs">Workflows</span>
                    </div>
                    <p className="text-sm font-medium">{vendor.workflowsConnected}</p>
                  </div>
                  <div>
                    <div className="flex items-center gap-1 text-muted-foreground mb-1">
                      <Clock className="h-3 w-3" />
                      <span className="text-xs">Avg Response</span>
                    </div>
                    <p className="text-sm font-medium">{vendor.avgResponseTime}ms</p>
                  </div>
                  <div>
                    <div className="flex items-center gap-1 text-muted-foreground mb-1">
                      <TrendingUp className="h-3 w-3" />
                      <span className="text-xs">Last Update</span>
                    </div>
                    <p className="text-sm font-medium">
                      {new Date(vendor.lastStatusChange).toLocaleDateString('en-US', {
                        month: 'short',
                        day: 'numeric'
                      })}
                    </p>
                  </div>
                </div>

                {/* Compact Status Summary - only for new degradation */}
                {vendor.status === 'outage' && (
                  <div 
                    className="rounded-md border border-[var(--status-critical)] bg-[var(--status-critical-bg)] p-2.5 mt-4 flex items-start gap-2"
                  >
                    <AlertTriangle className="h-4 w-4 text-[var(--status-critical)] shrink-0 mt-0.5" />
                    <p className="text-xs text-[var(--status-critical)]">
                      <strong>Outage detected.</strong> {vendor.workflowsConnected} workflows may be impacted.
                    </p>
                  </div>
                )}
                {vendor.status === 'degraded' && trend === 'worsening' && (
                  <div 
                    className="rounded-md border border-[var(--status-warning)] bg-[var(--status-warning-bg)] p-2.5 mt-4 flex items-start gap-2"
                  >
                    <TrendingDown className="h-4 w-4 text-[var(--status-warning)] shrink-0 mt-0.5" />
                    <p className="text-xs text-[var(--status-warning)]">
                      <strong>Performance degrading.</strong> Monitor for potential impact.
                    </p>
                  </div>
                )}
              </div>
            </Card>
          );
        })}
      </div>
    </div>
  );
}