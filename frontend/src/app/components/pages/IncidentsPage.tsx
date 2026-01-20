import { useState, useEffect } from 'react';
import { Search, Filter, AlertTriangle, Link2, ExternalLink, AlertCircle } from 'lucide-react';
import { Input } from '@/app/components/ui/input';
import { Button } from '@/app/components/ui/button';
import { SeverityBadge, StatusBadge } from '@/app/components/common/StatusBadge';
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
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from '@/app/components/ui/tooltip';
import { Badge } from '@/app/components/ui/badge';
import { incidentService } from '@/app/api';
import type { Incident } from '@/app/types';
import type { APIError } from '@/app/api/errors';

interface IncidentsPageProps {
  onIncidentClick: (incidentId: string) => void;
}

export function IncidentsPage({ onIncidentClick }: IncidentsPageProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  // API state
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<APIError | null>(null);

  // Fetch incidents from backend
  useEffect(() => {
    async function fetchIncidents() {
      setLoading(true);
      setError(null);

      const response = await incidentService.listIncidents();

      if (response.error) {
        setError(response.error);
        setLoading(false);
        return;
      }

      setIncidents(response.data || []);
      setLoading(false);
    }

    fetchIncidents();
  }, []);

  // Client-side filtering
  const filteredIncidents = incidents.filter((incident) => {
    const matchesSearch = incident.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         incident.id.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesSeverity = severityFilter === 'all' || incident.severity === severityFilter;
    const matchesStatus = statusFilter === 'all' || incident.status === statusFilter;
    return matchesSearch && matchesSeverity && matchesStatus;
  });

  const activeCount = incidents.filter(i => i.status !== 'resolved').length;

  return (
    <div className="p-8 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1>Incidents</h1>
          <p className="mt-2 text-muted-foreground">
            Monitor and manage workflow failures with AI-assisted diagnostics
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center gap-2 rounded-lg border px-4 py-2 bg-card">
            <AlertTriangle className="h-4 w-4 text-[var(--status-critical)]" />
            <span className="text-sm font-medium">{activeCount} Active</span>
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search incidents..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        
        <Select value={severityFilter} onValueChange={setSeverityFilter}>
          <SelectTrigger className="w-[180px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Severity" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Severities</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
            <SelectItem value="high">High</SelectItem>
            <SelectItem value="medium">Medium</SelectItem>
            <SelectItem value="low">Low</SelectItem>
          </SelectContent>
        </Select>

        <Select value={statusFilter} onValueChange={setStatusFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Statuses</SelectItem>
            <SelectItem value="active">Active</SelectItem>
            <SelectItem value="investigating">Investigating</SelectItem>
            <SelectItem value="recovering">Recovering</SelectItem>
            <SelectItem value="resolved">Resolved</SelectItem>
            <SelectItem value="escalated">Escalated</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Error State */}
      {error && (
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-destructive">Failed to load incidents</h3>
            <p className="text-sm text-destructive/90 mt-1">{error.message}</p>
            {error.detail && (
              <p className="text-xs text-muted-foreground mt-2">
                Technical details: {error.detail}
              </p>
            )}
            <Button
              variant="outline"
              size="sm"
              className="mt-3"
              onClick={() => window.location.reload()}
            >
              Retry
            </Button>
          </div>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="rounded-lg border bg-card p-12 text-center">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
          <p className="mt-4 text-muted-foreground">Loading incidents...</p>
        </div>
      )}

      {/* Incidents Table */}
      {!loading && !error && (
        <div className="rounded-lg border bg-card">
          <Table>
            <TableHeader>
              <TableRow className="hover:bg-transparent border-b-2">
                <TableHead className="font-semibold">Incident ID</TableHead>
                <TableHead className="font-semibold">Title</TableHead>
                <TableHead className="font-semibold">Severity</TableHead>
                <TableHead className="font-semibold">Status</TableHead>
                <TableHead className="font-semibold">Relationships</TableHead>
                <TableHead className="text-right font-semibold">Impact</TableHead>
                <TableHead className="font-semibold">Detected</TableHead>
                <TableHead className="text-right font-semibold">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredIncidents.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-12 text-muted-foreground">
                    {incidents.length === 0
                      ? "No incidents detected. All workflows are healthy."
                      : "No incidents found matching your filters"}
                  </TableCell>
                </TableRow>
              ) : (
              filteredIncidents.map((incident) => (
                <TableRow 
                  key={incident.id} 
                  className="cursor-pointer hover:bg-accent/50 focus-within:bg-accent/50 transition-colors"
                  onClick={() => onIncidentClick(incident.id)}
                  tabIndex={0}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      onIncidentClick(incident.id);
                    }
                  }}
                >
                  <TableCell className="font-mono text-sm">{incident.id}</TableCell>
                  <TableCell className="max-w-md">
                    <div className="truncate font-medium">{incident.title}</div>
                  </TableCell>
                  <TableCell>
                    <SeverityBadge severity={incident.severity} />
                  </TableCell>
                  <TableCell>
                    <StatusBadge status={incident.status} />
                  </TableCell>
                  <TableCell>
                    <TooltipProvider>
                      <div className="flex items-center gap-2">
                        <Tooltip>
                          <TooltipTrigger asChild>
                            <Badge variant="outline" className="cursor-help gap-1">
                              <Link2 className="h-3 w-3" />
                              {incident.workflowsAffected.length} workflows
                            </Badge>
                          </TooltipTrigger>
                          <TooltipContent>
                            <div className="space-y-1">
                              <p className="font-medium text-xs">Affected Workflows:</p>
                              {incident.workflowsAffected.map((w, i) => (
                                <p key={i} className="text-xs">• {w}</p>
                              ))}
                            </div>
                          </TooltipContent>
                        </Tooltip>
                      </div>
                    </TooltipProvider>
                  </TableCell>
                  <TableCell className="text-right tabular-nums">
                    {incident.impactedUsers && (
                      <div className="text-sm">
                        <div className="font-medium">{incident.impactedUsers.toLocaleString()}</div>
                        <div className="text-xs text-muted-foreground">users</div>
                        {incident.impactedTransactions && (
                          <div className="text-xs text-muted-foreground mt-0.5">
                            {incident.impactedTransactions.toLocaleString()} txn
                          </div>
                        )}
                      </div>
                    )}
                  </TableCell>
                  <TableCell className="text-sm text-muted-foreground">
                    {new Date(incident.detectedAt).toLocaleString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </TableCell>
                  <TableCell className="text-right">
                    <Button 
                      variant="ghost" 
                      size="sm"
                      className="gap-1"
                      onClick={(e) => {
                        e.stopPropagation();
                        onIncidentClick(incident.id);
                      }}
                    >
                      View Details
                      <ExternalLink className="h-3 w-3" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))
              )}
            </TableBody>
          </Table>
        </div>
      )}
    </div>
  );
}