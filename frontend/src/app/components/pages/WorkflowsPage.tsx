import { useState } from 'react';
import { Search, Filter, Workflow as WorkflowIcon, TrendingUp, Clock, AlertCircle } from 'lucide-react';
import { Input } from '@/app/components/ui/input';
import { StatusBadge } from '@/app/components/common/StatusBadge';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/app/components/ui/table';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import { mockWorkflows } from '@/app/data/mockData';
import { Card } from '@/app/components/ui/card';
import { Badge } from '@/app/components/ui/badge';

export function WorkflowsPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  const filteredWorkflows = mockWorkflows.filter((workflow) => {
    const matchesSearch = workflow.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         workflow.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesStatus = statusFilter === 'all' || workflow.status === statusFilter;
    const matchesCategory = categoryFilter === 'all' || workflow.category === categoryFilter;
    return matchesSearch && matchesStatus && matchesCategory;
  });

  const categories = Array.from(new Set(mockWorkflows.map(w => w.category)));
  const healthyCount = mockWorkflows.filter(w => w.status === 'healthy').length;
  const degradedCount = mockWorkflows.filter(w => w.status === 'degraded').length;
  const failingCount = mockWorkflows.filter(w => w.status === 'failing').length;

  return (
    <div className="p-8 space-y-6">
      {/* Page Header */}
      <div>
        <h1>Workflows</h1>
        <p className="mt-2 text-muted-foreground">
          Monitor all mission-critical workflows and their dependencies
        </p>
      </div>

      {/* Status Summary */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Total Workflows</p>
              <p className="text-2xl font-semibold mt-1">{mockWorkflows.length}</p>
            </div>
            <WorkflowIcon className="h-8 w-8 text-muted-foreground" />
          </div>
        </Card>
        <Card className="p-4 border-[var(--status-success)]">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Healthy</p>
              <p className="text-2xl font-semibold mt-1" style={{ color: 'var(--status-success)' }}>{healthyCount}</p>
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
            <AlertCircle className="h-8 w-8" style={{ color: 'var(--status-warning)' }} />
          </div>
        </Card>
        <Card className="p-4 border-[var(--status-critical)]">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Failing</p>
              <p className="text-2xl font-semibold mt-1" style={{ color: 'var(--status-critical)' }}>{failingCount}</p>
            </div>
            <AlertCircle className="h-8 w-8" style={{ color: 'var(--status-critical)' }} />
          </div>
        </Card>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search workflows..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        
        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="healthy">Healthy</SelectItem>
            <SelectItem value="degraded">Degraded</SelectItem>
            <SelectItem value="failing">Failing</SelectItem>
            <SelectItem value="offline">Offline</SelectItem>
          </SelectContent>
        </Select>

        <Select value={categoryFilter} onValueChange={setCategoryFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Category" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Categories</SelectItem>
            {categories.map((category) => (
              <SelectItem key={category} value={category}>{category}</SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>

      {/* Workflows Table */}
      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Workflow Name</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Category</TableHead>
              <TableHead>Success Rate</TableHead>
              <TableHead>Avg Duration</TableHead>
              <TableHead>Last Run</TableHead>
              <TableHead>Dependencies</TableHead>
              <TableHead>Incidents</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredWorkflows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={8} className="text-center py-12 text-muted-foreground">
                  No workflows found matching your filters
                </TableCell>
              </TableRow>
            ) : (
              filteredWorkflows.map((workflow) => (
                <TableRow key={workflow.id} className="hover:bg-accent">
                  <TableCell>
                    <div>
                      <div className="font-medium">{workflow.name}</div>
                      <div className="text-xs text-muted-foreground">{workflow.id}</div>
                    </div>
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={workflow.status} />
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{workflow.category}</Badge>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div 
                        className="h-2 w-16 rounded-full bg-muted overflow-hidden"
                      >
                        <div 
                          className="h-full transition-all"
                          style={{ 
                            width: `${workflow.successRate}%`,
                            backgroundColor: workflow.successRate >= 90 
                              ? 'var(--status-success)' 
                              : workflow.successRate >= 70 
                              ? 'var(--status-warning)' 
                              : 'var(--status-critical)'
                          }}
                        />
                      </div>
                      <span className="text-sm">{workflow.successRate}%</span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1 text-sm">
                      <Clock className="h-3 w-3 text-muted-foreground" />
                      {workflow.avgDuration < 60 
                        ? `${workflow.avgDuration}s` 
                        : `${Math.round(workflow.avgDuration / 60)}m`}
                    </div>
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(workflow.lastRun).toLocaleString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </TableCell>
                  <TableCell>
                    <Badge variant="secondary">{workflow.dependencies.length}</Badge>
                  </TableCell>
                  <TableCell>
                    {workflow.activeIncidents > 0 ? (
                      <Badge 
                        variant="outline"
                        style={{
                          backgroundColor: 'var(--status-critical-bg)',
                          color: 'var(--status-critical)',
                          borderColor: 'var(--status-critical)'
                        }}
                      >
                        {workflow.activeIncidents}
                      </Badge>
                    ) : (
                      <span className="text-sm text-muted-foreground">None</span>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
}
