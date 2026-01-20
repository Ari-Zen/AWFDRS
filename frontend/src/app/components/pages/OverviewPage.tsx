import { Activity, AlertTriangle, CheckCircle2, Clock, TrendingUp, Workflow } from 'lucide-react';
import { MetricCard } from '@/app/components/common/MetricCard';
import { SeverityBadge, StatusBadge } from '@/app/components/common/StatusBadge';
import { Card } from '@/app/components/ui/card';
import { Button } from '@/app/components/ui/button';
import { mockIncidents, mockSystemMetrics, mockWorkflows } from '@/app/data/mockData';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface OverviewPageProps {
  onIncidentClick: (incidentId: string) => void;
}

const mockChartData = [
  { time: '00:00', incidents: 0, workflows: 45 },
  { time: '04:00', incidents: 1, workflows: 44 },
  { time: '08:00', incidents: 0, workflows: 45 },
  { time: '12:00', incidents: 1, workflows: 43 },
  { time: '14:00', incidents: 2, workflows: 41 },
  { time: 'Now', incidents: 2, workflows: 41 },
];

export function OverviewPage({ onIncidentClick }: OverviewPageProps) {
  const activeIncidents = mockIncidents.filter(i => i.status !== 'resolved');
  const recentIncidents = mockIncidents.slice(0, 3);
  const criticalWorkflows = mockWorkflows.filter(w => w.status === 'failing' || w.status === 'degraded');

  return (
    <div className="p-8 space-y-8">
      {/* Page Header */}
      <div>
        <h1>System Overview</h1>
        <p className="mt-2 text-muted-foreground">
          Real-time monitoring and autonomous failure detection across all mission-critical workflows
        </p>
      </div>

      {/* Key Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <MetricCard
          title="Active Incidents"
          value={mockSystemMetrics.activeIncidents}
          icon={AlertTriangle}
          variant={mockSystemMetrics.criticalIncidents > 0 ? 'critical' : 'default'}
          subtitle={`${mockSystemMetrics.criticalIncidents} critical`}
        />
        <MetricCard
          title="Workflow Health"
          value={`${Math.round((mockSystemMetrics.healthyWorkflows / mockSystemMetrics.totalWorkflows) * 100)}%`}
          icon={Workflow}
          variant={mockSystemMetrics.healthyWorkflows / mockSystemMetrics.totalWorkflows > 0.9 ? 'success' : 'warning'}
          subtitle={`${mockSystemMetrics.healthyWorkflows}/${mockSystemMetrics.totalWorkflows} healthy`}
        />
        <MetricCard
          title="System Uptime"
          value={`${mockSystemMetrics.uptime}%`}
          icon={Activity}
          variant="success"
          trend={{ value: '0.2%', positive: true }}
        />
        <MetricCard
          title="Avg Recovery Time"
          value={`${mockSystemMetrics.avgRecoveryTime}m`}
          icon={Clock}
          trend={{ value: '12m', positive: true }}
          subtitle="Last 7 days"
        />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <div className="mb-4">
            <h3>Incident Trend</h3>
            <p className="text-sm text-muted-foreground">Last 24 hours</p>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={mockChartData}>
              <defs>
                <linearGradient id="colorIncidents" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--status-critical)" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="var(--status-critical)" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="time" stroke="var(--muted-foreground)" style={{ fontSize: '12px' }} />
              <YAxis stroke="var(--muted-foreground)" style={{ fontSize: '12px' }} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'var(--card)', 
                  border: '1px solid var(--border)',
                  borderRadius: '8px'
                }} 
              />
              <Area 
                type="monotone" 
                dataKey="incidents" 
                stroke="var(--status-critical)" 
                fillOpacity={1} 
                fill="url(#colorIncidents)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>

        <Card className="p-6">
          <div className="mb-4">
            <h3>Healthy Workflows</h3>
            <p className="text-sm text-muted-foreground">Last 24 hours</p>
          </div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={mockChartData}>
              <defs>
                <linearGradient id="colorWorkflows" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="var(--status-success)" stopOpacity={0.3}/>
                  <stop offset="95%" stopColor="var(--status-success)" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
              <XAxis dataKey="time" stroke="var(--muted-foreground)" style={{ fontSize: '12px' }} />
              <YAxis stroke="var(--muted-foreground)" style={{ fontSize: '12px' }} domain={[35, 47]} />
              <Tooltip 
                contentStyle={{ 
                  backgroundColor: 'var(--card)', 
                  border: '1px solid var(--border)',
                  borderRadius: '8px'
                }} 
              />
              <Area 
                type="monotone" 
                dataKey="workflows" 
                stroke="var(--status-success)" 
                fillOpacity={1} 
                fill="url(#colorWorkflows)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Recent Incidents & Critical Workflows */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3>Recent Incidents</h3>
              <p className="text-sm text-muted-foreground">{activeIncidents.length} active</p>
            </div>
            <Button variant="ghost" size="sm">View All</Button>
          </div>
          <div className="space-y-4">
            {recentIncidents.map((incident) => (
              <div
                key={incident.id}
                className="flex items-start gap-4 rounded-lg border p-4 hover:bg-accent cursor-pointer transition-colors"
                onClick={() => onIncidentClick(incident.id)}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1">
                    <SeverityBadge severity={incident.severity} />
                    <StatusBadge status={incident.status} />
                  </div>
                  <h4 className="text-sm font-medium truncate">{incident.title}</h4>
                  <p className="text-xs text-muted-foreground mt-1">
                    {incident.id} • Detected {new Date(incident.detectedAt).toLocaleTimeString()}
                  </p>
                  {incident.impactedUsers && (
                    <p className="text-xs text-muted-foreground mt-1">
                      Impact: {incident.impactedUsers.toLocaleString()} users
                    </p>
                  )}
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <div className="mb-4 flex items-center justify-between">
            <div>
              <h3>Workflows Requiring Attention</h3>
              <p className="text-sm text-muted-foreground">{criticalWorkflows.length} degraded or failing</p>
            </div>
            <Button variant="ghost" size="sm">View All</Button>
          </div>
          <div className="space-y-4">
            {criticalWorkflows.map((workflow) => (
              <div
                key={workflow.id}
                className="flex items-start gap-4 rounded-lg border p-4"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <StatusBadge status={workflow.status} />
                  </div>
                  <h4 className="text-sm font-medium">{workflow.name}</h4>
                  <div className="flex items-center gap-4 mt-2">
                    <div className="flex items-center gap-1">
                      {workflow.status === 'failing' ? (
                        <AlertTriangle className="h-3 w-3 text-[var(--status-critical)]" />
                      ) : (
                        <TrendingUp className="h-3 w-3 text-[var(--status-warning)]" />
                      )}
                      <span className="text-xs text-muted-foreground">
                        {workflow.successRate}% success rate
                      </span>
                    </div>
                    {workflow.activeIncidents > 0 && (
                      <span className="text-xs text-muted-foreground">
                        {workflow.activeIncidents} active incident{workflow.activeIncidents > 1 ? 's' : ''}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            ))}
            {criticalWorkflows.length === 0 && (
              <div className="flex flex-col items-center justify-center py-8 text-center">
                <CheckCircle2 className="h-12 w-12 text-[var(--status-success)] mb-3" />
                <p className="text-sm font-medium">All workflows healthy</p>
                <p className="text-xs text-muted-foreground mt-1">No attention required at this time</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}