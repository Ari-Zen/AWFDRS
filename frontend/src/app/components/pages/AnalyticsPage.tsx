import { Card } from '@/app/components/ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { 
  BarChart, 
  Bar, 
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend,
  ResponsiveContainer,
  TooltipProps 
} from 'recharts';
import { TrendingUp, TrendingDown, AlertTriangle, CheckCircle2, Info } from 'lucide-react';
import {
  Tooltip as UITooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/app/components/ui/tooltip';

const incidentsByDay = [
  { day: 'Mon', critical: 1, high: 2, medium: 3, low: 1 },
  { day: 'Tue', critical: 0, high: 1, medium: 2, low: 2 },
  { day: 'Wed', critical: 2, high: 3, medium: 1, low: 0 },
  { day: 'Thu', critical: 0, high: 1, medium: 4, low: 1 },
  { day: 'Fri', critical: 1, high: 2, medium: 2, low: 3 },
  { day: 'Sat', critical: 0, high: 0, medium: 1, low: 1 },
  { day: 'Sun', critical: 1, high: 1, medium: 2, low: 1 },
];

const mttrData = [
  { week: 'Week 1', mttr: 65 },
  { week: 'Week 2', mttr: 58 },
  { week: 'Week 3', mttr: 52 },
  { week: 'Week 4', mttr: 42 },
];

const workflowCategoryData = [
  { name: 'Financial', value: 12, color: 'var(--chart-1)' },
  { name: 'HR', value: 8, color: 'var(--chart-2)' },
  { name: 'Compliance', value: 6, color: 'var(--chart-3)' },
  { name: 'IT Operations', value: 10, color: 'var(--chart-4)' },
  { name: 'Security', value: 7, color: 'var(--chart-5)' },
  { name: 'Data', value: 4, color: 'var(--chart-1)' },
];

const recoveryActionData = [
  { action: 'Retry', count: 45, success: 38 },
  { action: 'Failover', count: 12, success: 11 },
  { action: 'Rollback', count: 8, success: 7 },
  { action: 'Manual', count: 15, success: 14 },
  { action: 'Escalate', count: 5, success: 5 },
];

// Custom tooltip for incidents chart
const CustomIncidentTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    const total = payload.reduce((sum, entry) => sum + (entry.value || 0), 0);
    return (
      <div className="rounded-lg border bg-card p-3 shadow-lg">
        <p className="font-medium mb-2">{label}</p>
        <div className="space-y-1">
          {payload.map((entry, index) => (
            <div key={index} className="flex items-center justify-between gap-3 text-sm">
              <div className="flex items-center gap-2">
                <div className="h-2.5 w-2.5 rounded-full" style={{ backgroundColor: entry.color }} />
                <span className="text-muted-foreground">{entry.name}:</span>
              </div>
              <span className="font-medium">{entry.value}</span>
            </div>
          ))}
          <div className="pt-2 mt-2 border-t flex items-center justify-between">
            <span className="text-xs text-muted-foreground">Total:</span>
            <span className="text-sm font-semibold">{total} incidents</span>
          </div>
        </div>
      </div>
    );
  }
  return null;
};

// Custom tooltip for MTTR chart
const CustomMTTRTooltip = ({ active, payload, label }: TooltipProps<number, string>) => {
  if (active && payload && payload.length) {
    return (
      <div className="rounded-lg border bg-card p-3 shadow-lg">
        <p className="font-medium mb-1">{label}</p>
        <p className="text-sm text-muted-foreground mb-2">Mean Time to Recovery</p>
        <div className="flex items-baseline gap-1">
          <span className="text-xl font-semibold" style={{ color: payload[0].color }}>
            {payload[0].value}
          </span>
          <span className="text-sm text-muted-foreground">minutes</span>
        </div>
        <p className="text-xs text-muted-foreground mt-2">
          Average time from detection to resolution
        </p>
      </div>
    );
  }
  return null;
};

export function AnalyticsPage() {
  return (
    <div className="p-8 space-y-6">
      {/* Page Header */}
      <div>
        <h1>Analytics & Insights</h1>
        <p className="mt-2 text-muted-foreground">
          Historical trends, performance metrics, and AI effectiveness analysis
        </p>
      </div>

      {/* Key Insights */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground">MTTR (Mean Time to Recovery)</p>
              <p className="text-2xl font-semibold mt-1">42m</p>
              <div className="flex items-center gap-1 mt-2">
                <TrendingDown className="h-3 w-3 text-[var(--status-success)]" />
                <span className="text-xs text-[var(--status-success)]">↓ 15% this week</span>
              </div>
            </div>
            <CheckCircle2 className="h-8 w-8 text-[var(--status-success)]" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground">AI Hypothesis Accuracy</p>
              <p className="text-2xl font-semibold mt-1">87%</p>
              <div className="flex items-center gap-1 mt-2">
                <TrendingUp className="h-3 w-3 text-[var(--status-success)]" />
                <span className="text-xs text-[var(--status-success)]">↑ 3% this week</span>
              </div>
            </div>
            <TrendingUp className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Incidents This Week</p>
              <p className="text-2xl font-semibold mt-1">18</p>
              <div className="flex items-center gap-1 mt-2">
                <TrendingDown className="h-3 w-3 text-[var(--status-success)]" />
                <span className="text-xs text-[var(--status-success)]">↓ 22% vs last week</span>
              </div>
            </div>
            <AlertTriangle className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>

        <Card className="p-4">
          <div className="flex items-start justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Auto-Recovery Rate</p>
              <p className="text-2xl font-semibold mt-1">73%</p>
              <div className="flex items-center gap-1 mt-2">
                <TrendingUp className="h-3 w-3 text-[var(--status-success)]" />
                <span className="text-xs text-[var(--status-success)]">↑ 8% this month</span>
              </div>
            </div>
            <CheckCircle2 className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
      </div>

      {/* Charts Tabs */}
      <Tabs defaultValue="incidents" className="space-y-4">
        <TabsList>
          <TabsTrigger value="incidents">Incident Trends</TabsTrigger>
          <TabsTrigger value="performance">Performance Metrics</TabsTrigger>
          <TabsTrigger value="workflows">Workflow Distribution</TabsTrigger>
          <TabsTrigger value="recovery">Recovery Actions</TabsTrigger>
        </TabsList>

        <TabsContent value="incidents" className="space-y-4">
          <Card className="p-6">
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h3>Incidents by Severity (Last 7 Days)</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Daily breakdown showing distribution across severity levels. 
                  Track patterns to identify high-risk periods.
                </p>
              </div>
              <TooltipProvider>
                <UITooltip>
                  <TooltipTrigger>
                    <Info className="h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p className="text-xs">
                      Stacked bar chart showing incident counts by severity. 
                      Use this to identify incident clusters and plan capacity accordingly.
                    </p>
                  </TooltipContent>
                </UITooltip>
              </TooltipProvider>
            </div>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={incidentsByDay}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.5} />
                <XAxis 
                  dataKey="day" 
                  stroke="var(--muted-foreground)" 
                  fontSize={12}
                  tickLine={false}
                />
                <YAxis 
                  stroke="var(--muted-foreground)" 
                  fontSize={12}
                  tickLine={false}
                  label={{ 
                    value: 'Incident Count', 
                    angle: -90, 
                    position: 'insideLeft',
                    style: { fontSize: 12, fill: 'var(--muted-foreground)' }
                  }}
                />
                <Tooltip content={<CustomIncidentTooltip />} />
                <Legend 
                  wrapperStyle={{ paddingTop: '20px' }}
                  iconType="circle"
                />
                <Bar dataKey="critical" stackId="a" fill="var(--status-critical)" name="Critical" radius={[0, 0, 0, 0]} />
                <Bar dataKey="high" stackId="a" fill="var(--status-warning)" name="High" radius={[0, 0, 0, 0]} />
                <Bar dataKey="medium" stackId="a" fill="var(--status-info)" name="Medium" radius={[0, 0, 0, 0]} />
                <Bar dataKey="low" stackId="a" fill="var(--status-neutral)" name="Low" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>

        <TabsContent value="performance" className="space-y-4">
          <Card className="p-6">
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h3>Mean Time to Recovery (MTTR) Trend</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Measures operational efficiency. Lower MTTR indicates faster incident resolution.
                  Target: &lt;45 minutes for critical incidents.
                </p>
              </div>
              <TooltipProvider>
                <UITooltip>
                  <TooltipTrigger>
                    <Info className="h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p className="text-xs">
                      MTTR tracks average time from incident detection to resolution. 
                      Declining trend indicates improving operational maturity.
                    </p>
                  </TooltipContent>
                </UITooltip>
              </TooltipProvider>
            </div>
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={mttrData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.5} />
                <XAxis 
                  dataKey="week" 
                  stroke="var(--muted-foreground)" 
                  fontSize={12}
                  tickLine={false}
                />
                <YAxis 
                  stroke="var(--muted-foreground)" 
                  fontSize={12}
                  tickLine={false}
                  label={{ 
                    value: 'Minutes', 
                    angle: -90, 
                    position: 'insideLeft',
                    style: { fontSize: 12, fill: 'var(--muted-foreground)' }
                  }} 
                />
                <Tooltip content={<CustomMTTRTooltip />} />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Line 
                  type="monotone" 
                  dataKey="mttr" 
                  stroke="var(--status-success)" 
                  strokeWidth={3}
                  name="MTTR (minutes)"
                  dot={{ fill: 'var(--status-success)', r: 5, strokeWidth: 2, stroke: 'var(--card)' }}
                  activeDot={{ r: 7 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>

        <TabsContent value="workflows" className="space-y-4">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <Card className="p-6">
              <div className="mb-4 flex items-start justify-between">
                <div>
                  <h3>Workflows by Category</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    Shows workflow coverage across business functions
                  </p>
                </div>
                <TooltipProvider>
                  <UITooltip>
                    <TooltipTrigger>
                      <Info className="h-4 w-4 text-muted-foreground" />
                    </TooltipTrigger>
                    <TooltipContent className="max-w-xs">
                      <p className="text-xs">
                        Distribution of monitored workflows by department. 
                        Helps identify coverage gaps across the organization.
                      </p>
                    </TooltipContent>
                  </UITooltip>
                </TooltipProvider>
              </div>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={workflowCategoryData}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {workflowCategoryData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <Tooltip 
                    contentStyle={{ 
                      backgroundColor: 'var(--card)', 
                      border: '1px solid var(--border)',
                      borderRadius: '8px',
                      fontSize: '12px'
                    }} 
                  />
                </PieChart>
              </ResponsiveContainer>
            </Card>

            <Card className="p-6">
              <div className="mb-4">
                <h3>Category Details</h3>
                <p className="text-sm text-muted-foreground mt-1">Workflow count by business function</p>
              </div>
              <div className="space-y-3">
                {workflowCategoryData.map((category) => (
                  <div key={category.name} className="flex items-center justify-between">
                    <div className="flex items-center gap-2">
                      <div 
                        className="h-3 w-3 rounded-full" 
                        style={{ backgroundColor: category.color }}
                      />
                      <span className="text-sm">{category.name}</span>
                    </div>
                    <span className="text-sm font-medium tabular-nums">{category.value} workflows</span>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="recovery" className="space-y-4">
          <Card className="p-6">
            <div className="mb-4 flex items-start justify-between">
              <div>
                <h3>Recovery Action Effectiveness</h3>
                <p className="text-sm text-muted-foreground mt-1">
                  Success rates help determine optimal recovery strategies per failure type.
                  High success rates indicate well-tuned automation.
                </p>
              </div>
              <TooltipProvider>
                <UITooltip>
                  <TooltipTrigger>
                    <Info className="h-4 w-4 text-muted-foreground" />
                  </TooltipTrigger>
                  <TooltipContent className="max-w-xs">
                    <p className="text-xs">
                      Compare total attempts vs successful recoveries. 
                      Use insights to refine action selection logic.
                    </p>
                  </TooltipContent>
                </UITooltip>
              </TooltipProvider>
            </div>
            <ResponsiveContainer width="100%" height={350}>
              <BarChart data={recoveryActionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" opacity={0.5} />
                <XAxis 
                  dataKey="action" 
                  stroke="var(--muted-foreground)" 
                  fontSize={12}
                  tickLine={false}
                />
                <YAxis 
                  stroke="var(--muted-foreground)" 
                  fontSize={12}
                  tickLine={false}
                  label={{ 
                    value: 'Count', 
                    angle: -90, 
                    position: 'insideLeft',
                    style: { fontSize: 12, fill: 'var(--muted-foreground)' }
                  }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: 'var(--card)', 
                    border: '1px solid var(--border)',
                    borderRadius: '8px',
                    fontSize: '12px'
                  }} 
                  formatter={(value: any, name: string) => [
                    value,
                    name === 'count' ? 'Total Attempts' : 'Successful'
                  ]}
                />
                <Legend wrapperStyle={{ paddingTop: '20px' }} />
                <Bar dataKey="count" fill="var(--status-info)" name="Total Attempts" radius={[4, 4, 0, 0]} />
                <Bar dataKey="success" fill="var(--status-success)" name="Successful" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}