import { ArrowLeft, AlertTriangle, Clock, Users, TrendingUp, Shield, CheckCircle2, AlertCircle } from 'lucide-react';
import { Button } from '@/app/components/ui/button';
import { Card } from '@/app/components/ui/card';
import { SeverityBadge, StatusBadge } from '@/app/components/common/StatusBadge';
import { Progress } from '@/app/components/ui/progress';
import { Badge } from '@/app/components/ui/badge';
import { Separator } from '@/app/components/ui/separator';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/app/components/ui/dialog';
import { incidentService } from '@/app/api';
import type { Incident, RecoveryActionItem } from '@/app/types';
import type { APIError } from '@/app/api/errors';
import { useState, useEffect } from 'react';
import { toast } from 'sonner';

interface IncidentDetailPageProps {
  incidentId: string;
  onBack: () => void;
}

export function IncidentDetailPage({ incidentId, onBack }: IncidentDetailPageProps) {
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<APIError | null>(null);
  const [selectedAction, setSelectedAction] = useState<RecoveryActionItem | null>(null);

  // Fetch incident details from backend
  useEffect(() => {
    async function fetchIncidentDetail() {
      setLoading(true);
      setError(null);

      const response = await incidentService.getIncidentDetail(incidentId);

      if (response.error) {
        setError(response.error);
        setLoading(false);
        return;
      }

      setIncident(response.data || null);
      setLoading(false);
    }

    fetchIncidentDetail();
  }, [incidentId]);

  // Loading state
  if (loading) {
    return (
      <div className="p-8">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1>Loading incident...</h1>
        </div>
        <div className="flex items-center justify-center py-12">
          <div className="inline-block h-8 w-8 animate-spin rounded-full border-4 border-solid border-current border-r-transparent align-[-0.125em] motion-reduce:animate-[spin_1.5s_linear_infinite]" />
        </div>
      </div>
    );
  }

  // Error state
  if (error || !incident) {
    return (
      <div className="p-8">
        <div className="flex items-center gap-4 mb-6">
          <Button variant="ghost" size="icon" onClick={onBack}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h1>Failed to load incident</h1>
        </div>
        <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-6 flex items-start gap-3">
          <AlertCircle className="h-5 w-5 text-destructive mt-0.5" />
          <div className="flex-1">
            <h3 className="font-semibold text-destructive">
              {error?.message || "Incident not found"}
            </h3>
            {error?.detail && (
              <p className="text-sm text-destructive/90 mt-1">{error.detail}</p>
            )}
            <Button
              variant="outline"
              size="sm"
              className="mt-3"
              onClick={onBack}
            >
              Go Back
            </Button>
          </div>
        </div>
      </div>
    );
  }

  const handleExecuteAction = (action: RecoveryActionItem) => {
    toast.success(`Recovery action "${action.description}" has been queued for execution`, {
      description: 'The action will be executed after final safety checks.',
    });
    setSelectedAction(null);
  };

  return (
    <div className="p-8 space-y-6">
      {/* Header */}
      <div className="flex items-start gap-4">
        <Button variant="ghost" size="icon" onClick={onBack}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1>{incident.title}</h1>
          </div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-sm text-muted-foreground">{incident.id}</span>
            <Separator orientation="vertical" className="h-4" />
            <SeverityBadge severity={incident.severity} />
            <StatusBadge status={incident.status} />
          </div>
        </div>
        {incident.status !== 'resolved' && (
          <div className="flex gap-2">
            <Button variant="outline">Escalate</Button>
            <Button>Take Ownership</Button>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column - Summary & Impact */}
        <div className="lg:col-span-2 space-y-6">
          {/* Summary */}
          <Card className="p-6">
            <h3 className="mb-4">Incident Summary</h3>
            <p className="text-sm leading-relaxed">{incident.description}</p>
            
            <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t">
              <div>
                <div className="flex items-center gap-2 text-muted-foreground mb-1">
                  <Clock className="h-4 w-4" />
                  <span className="text-xs">Detected</span>
                </div>
                <p className="text-sm font-medium">
                  {new Date(incident.detectedAt).toLocaleString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}
                </p>
              </div>
              <div>
                <div className="flex items-center gap-2 text-muted-foreground mb-1">
                  <TrendingUp className="h-4 w-4" />
                  <span className="text-xs">Duration</span>
                </div>
                <p className="text-sm font-medium">
                  {Math.round((new Date(incident.lastUpdated).getTime() - new Date(incident.detectedAt).getTime()) / 60000)}m
                </p>
              </div>
              <div>
                <div className="flex items-center gap-2 text-muted-foreground mb-1">
                  <Users className="h-4 w-4" />
                  <span className="text-xs">Impact</span>
                </div>
                <p className="text-sm font-medium">
                  {incident.impactedUsers?.toLocaleString() || 'N/A'} users
                </p>
              </div>
            </div>
          </Card>

          {/* AI Hypotheses */}
          <Card className="p-6">
            <div className="flex items-center gap-2 mb-4">
              <h3>AI-Generated Hypotheses</h3>
              <Badge variant="outline" className="text-xs">
                {incident.aiHypotheses.length} hypothesis{incident.aiHypotheses.length !== 1 ? 'es' : ''}
              </Badge>
            </div>
            <div className="space-y-4">
              {incident.aiHypotheses.map((hypothesis, index) => (
                <div key={hypothesis.id} className="rounded-lg border p-4 bg-muted/30">
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                      <span className="flex h-6 w-6 items-center justify-center rounded-full bg-primary text-xs text-primary-foreground">
                        {index + 1}
                      </span>
                      <span className="text-sm font-medium">Confidence: {hypothesis.confidence}%</span>
                    </div>
                    <Progress value={hypothesis.confidence} className="w-24 h-2" />
                  </div>
                  <h4 className="text-sm font-medium mb-2">{hypothesis.hypothesis}</h4>
                  
                  <div className="mt-3">
                    <p className="text-xs text-muted-foreground mb-2">Supporting Evidence:</p>
                    <ul className="space-y-1">
                      {hypothesis.evidence.map((evidence, idx) => (
                        <li key={idx} className="text-xs flex items-start gap-2">
                          <CheckCircle2 className="h-3 w-3 text-[var(--status-success)] mt-0.5 flex-shrink-0" />
                          <span>{evidence}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {hypothesis.suggestedAction && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-xs text-muted-foreground mb-1">Suggested Action:</p>
                      <p className="text-sm">{hypothesis.suggestedAction}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Recovery Actions */}
          {incident.recoveryActions && incident.recoveryActions.length > 0 && (
            <Card className="p-6">
              <div className="flex items-center gap-2 mb-4">
                <Shield className="h-5 w-5" />
                <h3>Available Recovery Actions</h3>
              </div>
              <p className="text-sm text-muted-foreground mb-4">
                AI-recommended actions with risk assessment and impact analysis
              </p>
              <div className="space-y-3">
                {incident.recoveryActions.map((action) => (
                  <div key={action.id} className="rounded-lg border p-4">
                    <div className="flex items-start justify-between mb-2">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <h4 className="text-sm font-medium">{action.description}</h4>
                        </div>
                        <div className="flex items-center gap-3 mt-2">
                          <Badge 
                            variant="outline"
                            style={{
                              backgroundColor: action.risk === 'high' 
                                ? 'var(--status-critical-bg)' 
                                : action.risk === 'medium' 
                                ? 'var(--status-warning-bg)' 
                                : 'var(--status-success-bg)',
                              color: action.risk === 'high' 
                                ? 'var(--status-critical)' 
                                : action.risk === 'medium' 
                                ? 'var(--status-warning)' 
                                : 'var(--status-success)',
                              borderColor: action.risk === 'high' 
                                ? 'var(--status-critical)' 
                                : action.risk === 'medium' 
                                ? 'var(--status-warning)' 
                                : 'var(--status-success)',
                            }}
                          >
                            {action.risk.toUpperCase()} RISK
                          </Badge>
                          {action.requiresApproval && (
                            <Badge variant="outline">Requires Approval</Badge>
                          )}
                        </div>
                        {action.estimatedImpact && (
                          <p className="text-xs text-muted-foreground mt-2">
                            Impact: {action.estimatedImpact}
                          </p>
                        )}
                      </div>
                      <Dialog>
                        <DialogTrigger asChild>
                          <Button 
                            size="sm"
                            variant={action.requiresApproval ? "default" : "outline"}
                            onClick={() => setSelectedAction(action)}
                          >
                            {action.requiresApproval ? 'Review & Approve' : 'Execute'}
                          </Button>
                        </DialogTrigger>
                        <DialogContent>
                          <DialogHeader>
                            <DialogTitle>Confirm Recovery Action</DialogTitle>
                            <DialogDescription>
                              Review the action details and potential impact before proceeding
                            </DialogDescription>
                          </DialogHeader>
                          <div className="space-y-4 py-4">
                            <div>
                              <p className="text-sm font-medium mb-1">Action</p>
                              <p className="text-sm text-muted-foreground">{action.description}</p>
                            </div>
                            <div>
                              <p className="text-sm font-medium mb-1">Risk Level</p>
                              <Badge 
                                variant="outline"
                                style={{
                                  backgroundColor: action.risk === 'high' 
                                    ? 'var(--status-critical-bg)' 
                                    : action.risk === 'medium' 
                                    ? 'var(--status-warning-bg)' 
                                    : 'var(--status-success-bg)',
                                  color: action.risk === 'high' 
                                    ? 'var(--status-critical)' 
                                    : action.risk === 'medium' 
                                    ? 'var(--status-warning)' 
                                    : 'var(--status-success)',
                                  borderColor: action.risk === 'high' 
                                    ? 'var(--status-critical)' 
                                    : action.risk === 'medium' 
                                    ? 'var(--status-warning)' 
                                    : 'var(--status-success)',
                                }}
                              >
                                {action.risk.toUpperCase()}
                              </Badge>
                            </div>
                            {action.estimatedImpact && (
                              <div>
                                <p className="text-sm font-medium mb-1">Estimated Impact</p>
                                <p className="text-sm text-muted-foreground">{action.estimatedImpact}</p>
                              </div>
                            )}
                            <div className="rounded-md border border-[var(--status-warning)] bg-[var(--status-warning-bg)] p-4">
                              <p className="text-xs" style={{ color: 'var(--status-warning)' }}>
                                <strong>Warning:</strong> This action will be logged in the audit trail and cannot be undone. 
                                Ensure you have reviewed all implications before proceeding.
                              </p>
                            </div>
                          </div>
                          <DialogFooter>
                            <Button variant="outline" onClick={() => setSelectedAction(null)}>Cancel</Button>
                            <Button onClick={() => handleExecuteAction(action)}>
                              Confirm & Execute
                            </Button>
                          </DialogFooter>
                        </DialogContent>
                      </Dialog>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </div>

        {/* Right Column - Timeline & Metadata */}
        <div className="space-y-6">
          {/* Workflows Affected */}
          <Card className="p-6">
            <h3 className="mb-4">Affected Workflows</h3>
            <div className="space-y-2">
              {incident.workflowsAffected.map((workflow) => (
                <div key={workflow} className="flex items-center gap-2 rounded-md border p-2 text-sm">
                  <AlertTriangle className="h-4 w-4 text-[var(--status-warning)]" />
                  <span>{workflow}</span>
                </div>
              ))}
            </div>
          </Card>

          {/* Timeline */}
          <Card className="p-6">
            <h3 className="mb-4">Event Timeline</h3>
            <div className="space-y-4">
              {incident.timeline.map((event, index) => (
                <div key={event.id} className="relative">
                  {index !== incident.timeline.length - 1 && (
                    <div className="absolute left-2 top-6 h-full w-px bg-border" />
                  )}
                  <div className="flex gap-3">
                    <div className="relative flex h-4 w-4 flex-shrink-0 items-center justify-center rounded-full border-2 border-primary bg-background mt-1">
                      <div className="h-2 w-2 rounded-full bg-primary" />
                    </div>
                    <div className="flex-1 pb-4">
                      <p className="text-sm">{event.event}</p>
                      <div className="mt-1 flex items-center gap-2 text-xs text-muted-foreground">
                        <span>
                          {new Date(event.timestamp).toLocaleTimeString('en-US', {
                            hour: '2-digit',
                            minute: '2-digit',
                            second: '2-digit'
                          })}
                        </span>
                        {event.actor && event.actor !== 'System' && (
                          <>
                            <span>•</span>
                            <span>{event.actor}</span>
                          </>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}