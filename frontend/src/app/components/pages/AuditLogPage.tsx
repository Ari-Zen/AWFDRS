import { useState } from 'react';
import { Search, Filter, Download, CheckCircle2, XCircle } from 'lucide-react';
import { Input } from '@/app/components/ui/input';
import { Button } from '@/app/components/ui/button';
import { Badge } from '@/app/components/ui/badge';
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
import { mockAuditLog } from '@/app/data/mockData';

export function AuditLogPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [actionFilter, setActionFilter] = useState<string>('all');
  const [resultFilter, setResultFilter] = useState<string>('all');

  const filteredLogs = mockAuditLog.filter((log) => {
    const matchesSearch = 
      log.action.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.resource.toLowerCase().includes(searchQuery.toLowerCase()) ||
      log.actor.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesAction = actionFilter === 'all' || log.action.includes(actionFilter);
    const matchesResult = resultFilter === 'all' || log.result === resultFilter;
    return matchesSearch && matchesAction && matchesResult;
  });

  const actionTypes = Array.from(new Set(mockAuditLog.map(log => log.action.split('.')[0])));

  return (
    <div className="p-8 space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1>Audit Log</h1>
          <p className="mt-2 text-muted-foreground">
            Complete audit trail of all system actions and human interventions
          </p>
        </div>
        <Button variant="outline">
          <Download className="mr-2 h-4 w-4" />
          Export Logs
        </Button>
      </div>

      {/* Filters */}
      <div className="flex items-center gap-4">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search audit logs..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-9"
          />
        </div>
        
        <Select value={actionFilter} onValueChange={setActionFilter}>
          <SelectTrigger className="w-[200px]">
            <Filter className="mr-2 h-4 w-4" />
            <SelectValue placeholder="Action Type" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Actions</SelectItem>
            {actionTypes.map((type) => (
              <SelectItem key={type} value={type}>{type}</SelectItem>
            ))}
          </SelectContent>
        </Select>

        <Select value={resultFilter} onValueChange={setResultFilter}>
          <SelectTrigger className="w-[180px]">
            <SelectValue placeholder="Result" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All Results</SelectItem>
            <SelectItem value="success">Success</SelectItem>
            <SelectItem value="failure">Failure</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {/* Audit Log Table */}
      <div className="rounded-lg border bg-card">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead>Timestamp</TableHead>
              <TableHead>Actor</TableHead>
              <TableHead>Action</TableHead>
              <TableHead>Resource</TableHead>
              <TableHead>Result</TableHead>
              <TableHead className="text-right">Details</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filteredLogs.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="text-center py-12 text-muted-foreground">
                  No audit logs found matching your filters
                </TableCell>
              </TableRow>
            ) : (
              filteredLogs.map((log) => (
                <TableRow key={log.id} className="hover:bg-accent">
                  <TableCell className="font-mono text-sm">
                    {new Date(log.timestamp).toLocaleString('en-US', {
                      month: 'short',
                      day: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit',
                      second: '2-digit'
                    })}
                  </TableCell>
                  <TableCell>
                    <div className="flex items-center gap-2">
                      <div className="h-6 w-6 rounded-full bg-muted flex items-center justify-center text-xs font-medium">
                        {log.actor === 'system' ? 'S' : log.actor.charAt(0).toUpperCase()}
                      </div>
                      <span className="text-sm">
                        {log.actor === 'system' ? 'System' : log.actor.split('@')[0]}
                      </span>
                    </div>
                  </TableCell>
                  <TableCell>
                    <Badge variant="outline">{log.action}</Badge>
                  </TableCell>
                  <TableCell className="font-mono text-sm">{log.resource}</TableCell>
                  <TableCell>
                    <div className="flex items-center gap-1">
                      {log.result === 'success' ? (
                        <>
                          <CheckCircle2 className="h-4 w-4 text-[var(--status-success)]" />
                          <span className="text-sm text-[var(--status-success)]">Success</span>
                        </>
                      ) : (
                        <>
                          <XCircle className="h-4 w-4 text-[var(--status-critical)]" />
                          <span className="text-sm text-[var(--status-critical)]">Failure</span>
                        </>
                      )}
                    </div>
                  </TableCell>
                  <TableCell className="text-right">
                    {log.metadata && (
                      <Button variant="ghost" size="sm">View Metadata</Button>
                    )}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>

      {/* Compliance Notice */}
      <div className="rounded-lg border border-[var(--status-info)] bg-[var(--status-info-bg)] p-4">
        <div className="flex gap-3">
          <div 
            className="flex h-8 w-8 items-center justify-center rounded-full flex-shrink-0"
            style={{ backgroundColor: 'var(--status-info)', color: 'var(--status-info-foreground)' }}
          >
            <CheckCircle2 className="h-4 w-4" />
          </div>
          <div>
            <h4 className="font-medium mb-1" style={{ color: 'var(--status-info)' }}>
              Compliance & Retention
            </h4>
            <p className="text-sm" style={{ color: 'var(--status-info)' }}>
              All actions are immutably logged and retained for 7 years in compliance with SOC2, ISO 27001, 
              and applicable regulatory requirements. Logs include full context for forensic analysis and are 
              cryptographically signed to prevent tampering.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
