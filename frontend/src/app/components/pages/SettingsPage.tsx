import { Card } from '@/app/components/ui/card';
import { Label } from '@/app/components/ui/label';
import { Input } from '@/app/components/ui/input';
import { Button } from '@/app/components/ui/button';
import { Switch } from '@/app/components/ui/switch';
import { Separator } from '@/app/components/ui/separator';
import { Badge } from '@/app/components/ui/badge';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/app/components/ui/select';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/app/components/ui/alert-dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/app/components/ui/tabs';
import { Bell, Shield, Users, Zap, AlertTriangle, Info } from 'lucide-react';
import { toast } from 'sonner';
import { useState } from 'react';

export function SettingsPage() {
  const [showAutoRecoveryDialog, setShowAutoRecoveryDialog] = useState(false);
  const [showSensitivityDialog, setShowSensitivityDialog] = useState(false);
  const [autoRecoveryEnabled, setAutoRecoveryEnabled] = useState(true);
  const [detectionSensitivity, setDetectionSensitivity] = useState('medium');

  const handleSave = () => {
    toast.success('Settings saved successfully', {
      description: 'Your changes have been applied to the system.',
    });
  };

  return (
    <div className="p-8 space-y-6">
      {/* Page Header */}
      <div>
        <h1>Settings</h1>
        <p className="mt-2 text-muted-foreground">
          Configure system behavior, notifications, and team preferences
        </p>
      </div>

      <Tabs defaultValue="general" className="space-y-4">
        <TabsList>
          <TabsTrigger value="general">General</TabsTrigger>
          <TabsTrigger value="notifications">Notifications</TabsTrigger>
          <TabsTrigger value="ai">AI Configuration</TabsTrigger>
          <TabsTrigger value="team">Team & Access</TabsTrigger>
        </TabsList>

        <TabsContent value="general" className="space-y-4">
          <Card className="p-6">
            <div className="space-y-6">
              <div>
                <h3 className="mb-4">System Configuration</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Auto-detection enabled</Label>
                      <p className="text-sm text-muted-foreground">
                        Automatically detect and create incidents for workflow failures
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-1 flex-1">
                      <div className="flex items-center gap-2">
                        <Label>Auto-recovery actions</Label>
                        <Badge variant="destructive" className="gap-1">
                          <AlertTriangle className="h-3 w-3" />
                          High Risk
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        Allow AI to execute low-risk recovery actions without approval
                      </p>
                      <div className="mt-2 rounded-md border border-[var(--status-warning)] bg-[var(--status-warning-bg)] p-3">
                        <div className="flex items-start gap-2">
                          <Info className="h-4 w-4 text-[var(--status-warning)] shrink-0 mt-0.5" />
                          <div className="text-xs text-[var(--status-warning)]">
                            <p className="font-medium mb-1">Impact:</p>
                            <ul className="list-disc list-inside space-y-0.5">
                              <li>System may perform retries, failovers, and rollbacks automatically</li>
                              <li>Actions are logged and auditable but may affect production workflows</li>
                              <li>Recommended only for tested, non-critical workflows</li>
                            </ul>
                          </div>
                        </div>
                      </div>
                    </div>
                    <Switch 
                      checked={autoRecoveryEnabled} 
                      onCheckedChange={(checked) => {
                        if (!checked) {
                          setAutoRecoveryEnabled(false);
                        } else {
                          setShowAutoRecoveryDialog(true);
                        }
                      }}
                    />
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <Label>Detection sensitivity</Label>
                      <Badge variant="outline" className="gap-1">
                        <AlertTriangle className="h-3 w-3" />
                        Affects alert volume
                      </Badge>
                    </div>
                    <Select 
                      value={detectionSensitivity}
                      onValueChange={(value) => {
                        if (value === 'high') {
                          setShowSensitivityDialog(true);
                        } else {
                          setDetectionSensitivity(value);
                        }
                      }}
                    >
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="low">Low - Fewer false positives</SelectItem>
                        <SelectItem value="medium">Medium - Balanced</SelectItem>
                        <SelectItem value="high">High - More sensitive</SelectItem>
                      </SelectContent>
                    </Select>
                    <div className="rounded-md border bg-muted/50 p-3">
                      <p className="text-xs text-muted-foreground">
                        <strong>Current setting: {detectionSensitivity === 'low' ? 'Low' : detectionSensitivity === 'high' ? 'High' : 'Medium'}</strong>
                        <br />
                        {detectionSensitivity === 'low' && 'Optimized for precision. May miss edge cases.'}
                        {detectionSensitivity === 'medium' && 'Balanced approach suitable for most environments.'}
                        {detectionSensitivity === 'high' && 'Catches issues early but may increase false positive rate by 20-30%.'}
                      </p>
                    </div>
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <Label>Incident retention period</Label>
                    <Select defaultValue="90">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="30">30 days</SelectItem>
                        <SelectItem value="90">90 days (recommended)</SelectItem>
                        <SelectItem value="180">180 days</SelectItem>
                        <SelectItem value="365">1 year</SelectItem>
                        <SelectItem value="forever">Forever (compliance mode)</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-xs text-muted-foreground">
                      Audit logs are retained separately per compliance requirements
                    </p>
                  </div>
                </div>
              </div>

              <Separator />

              <div>
                <h3 className="mb-4">Thresholds</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <Label htmlFor="failure-threshold">Failure rate threshold (%)</Label>
                    <Input 
                      id="failure-threshold" 
                      type="number" 
                      defaultValue="15" 
                      min="1" 
                      max="100"
                    />
                    <p className="text-sm text-muted-foreground">
                      Create incident when failure rate exceeds this value
                    </p>
                  </div>
                  <div className="space-y-2">
                    <Label htmlFor="response-threshold">Response time threshold (ms)</Label>
                    <Input 
                      id="response-threshold" 
                      type="number" 
                      defaultValue="3000" 
                      min="100"
                    />
                    <p className="text-sm text-muted-foreground">
                      Alert when response time exceeds this value
                    </p>
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline">Reset to Defaults</Button>
                <Button onClick={handleSave}>Save Changes</Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="notifications" className="space-y-4">
          <Card className="p-6">
            <div className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Bell className="h-5 w-5" />
                  <h3>Notification Preferences</h3>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Critical incidents</Label>
                      <p className="text-sm text-muted-foreground">
                        Immediate notifications for critical severity incidents
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>High severity incidents</Label>
                      <p className="text-sm text-muted-foreground">
                        Notifications for high severity incidents
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Recovery actions</Label>
                      <p className="text-sm text-muted-foreground">
                        Notify when recovery actions are executed
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Weekly summary</Label>
                      <p className="text-sm text-muted-foreground">
                        Receive weekly system health and incident summary
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <Label>Notification channels</Label>
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <Switch defaultChecked id="email" />
                        <Label htmlFor="email" className="cursor-pointer">Email</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <Switch defaultChecked id="slack" />
                        <Label htmlFor="slack" className="cursor-pointer">Slack</Label>
                      </div>
                      <div className="flex items-center gap-2">
                        <Switch id="pagerduty" />
                        <Label htmlFor="pagerduty" className="cursor-pointer">PagerDuty</Label>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button variant="outline">Test Notifications</Button>
                <Button onClick={handleSave}>Save Changes</Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="ai" className="space-y-4">
          <Card className="p-6">
            <div className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Zap className="h-5 w-5" />
                  <h3>AI & Automation</h3>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Hypothesis generation</Label>
                      <p className="text-sm text-muted-foreground">
                        Generate AI-powered diagnostic hypotheses for incidents
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <Label>Minimum confidence threshold</Label>
                    <Select defaultValue="70">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="50">50% - More hypotheses, lower confidence</SelectItem>
                        <SelectItem value="70">70% - Balanced</SelectItem>
                        <SelectItem value="85">85% - Fewer, high-confidence hypotheses</SelectItem>
                      </SelectContent>
                    </Select>
                    <p className="text-sm text-muted-foreground">
                      Only show hypotheses above this confidence level
                    </p>
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Automatic retry</Label>
                      <p className="text-sm text-muted-foreground">
                        Automatically retry failed workflows (low risk)
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Automatic failover</Label>
                      <p className="text-sm text-muted-foreground">
                        Automatically failover to backup systems (requires approval for high-risk)
                      </p>
                    </div>
                    <Switch />
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <Label>Evidence collection depth</Label>
                    <Select defaultValue="standard">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="minimal">Minimal - Faster analysis</SelectItem>
                        <SelectItem value="standard">Standard - Balanced</SelectItem>
                        <SelectItem value="comprehensive">Comprehensive - More evidence</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button onClick={handleSave}>Save Changes</Button>
              </div>
            </div>
          </Card>
        </TabsContent>

        <TabsContent value="team" className="space-y-4">
          <Card className="p-6">
            <div className="space-y-6">
              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Users className="h-5 w-5" />
                  <h3>Team Members</h3>
                </div>
                <div className="space-y-3">
                  {[
                    { name: 'Sarah Chen', email: 'sarah.chen@company.com', role: 'Admin' },
                    { name: 'James Wong', email: 'james.wong@company.com', role: 'Admin' },
                    { name: 'Alex Rodriguez', email: 'alex.rodriguez@company.com', role: 'Operator' },
                    { name: 'Maria Garcia', email: 'maria.garcia@company.com', role: 'Viewer' },
                  ].map((member) => (
                    <div key={member.email} className="flex items-center justify-between p-3 rounded-lg border">
                      <div className="flex items-center gap-3">
                        <div className="h-10 w-10 rounded-full bg-muted flex items-center justify-center font-medium">
                          {member.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div>
                          <p className="text-sm font-medium">{member.name}</p>
                          <p className="text-xs text-muted-foreground">{member.email}</p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        <Select defaultValue={member.role.toLowerCase()}>
                          <SelectTrigger className="w-[120px]">
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="admin">Admin</SelectItem>
                            <SelectItem value="operator">Operator</SelectItem>
                            <SelectItem value="viewer">Viewer</SelectItem>
                          </SelectContent>
                        </Select>
                        <Button variant="ghost" size="sm">Remove</Button>
                      </div>
                    </div>
                  ))}
                </div>
                <Button variant="outline" className="mt-4 w-full">
                  Invite Team Member
                </Button>
              </div>

              <Separator />

              <div>
                <div className="flex items-center gap-2 mb-4">
                  <Shield className="h-5 w-5" />
                  <h3>Access Control</h3>
                </div>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Require approval for high-risk actions</Label>
                      <p className="text-sm text-muted-foreground">
                        All high-risk recovery actions require approval from Admin role
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <Separator />

                  <div className="flex items-center justify-between">
                    <div className="space-y-0.5">
                      <Label>Multi-factor authentication (MFA)</Label>
                      <p className="text-sm text-muted-foreground">
                        Require MFA for all team members
                      </p>
                    </div>
                    <Switch defaultChecked />
                  </div>

                  <Separator />

                  <div className="space-y-2">
                    <Label>Session timeout</Label>
                    <Select defaultValue="4">
                      <SelectTrigger>
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="1">1 hour</SelectItem>
                        <SelectItem value="4">4 hours</SelectItem>
                        <SelectItem value="8">8 hours</SelectItem>
                        <SelectItem value="24">24 hours</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </div>

              <div className="flex justify-end gap-2 pt-4">
                <Button onClick={handleSave}>Save Changes</Button>
              </div>
            </div>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Confirmation Dialogs */}
      <AlertDialog open={showAutoRecoveryDialog} onOpenChange={setShowAutoRecoveryDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle className="flex items-center gap-2">
              <AlertTriangle className="h-5 w-5 text-[var(--status-warning)]" />
              Enable Auto-Recovery Actions?
            </AlertDialogTitle>
            <AlertDialogDescription className="space-y-3 pt-2">
              <p>
                Enabling this setting allows the system to automatically execute recovery actions without human approval.
              </p>
              <div className="rounded-md border border-[var(--status-warning)] bg-[var(--status-warning-bg)] p-3">
                <p className="text-sm text-[var(--status-warning)] font-medium mb-2">
                  Potential Impact:
                </p>
                <ul className="text-xs text-[var(--status-warning)] list-disc list-inside space-y-1">
                  <li>Workflows may be automatically retried or failed over</li>
                  <li>Actions may affect production environments</li>
                  <li>All actions are logged and auditable</li>
                  <li>You can disable this at any time</li>
                </ul>
              </div>
              <p className="text-sm">
                Are you sure you want to enable automatic recovery actions?
              </p>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setAutoRecoveryEnabled(false)}>
              Cancel
            </AlertDialogCancel>
            <AlertDialogAction 
              onClick={() => {
                setAutoRecoveryEnabled(true);
                setShowAutoRecoveryDialog(false);
                toast.success('Auto-recovery enabled', {
                  description: 'The system will now execute low-risk recovery actions automatically.',
                });
              }}
            >
              Enable Auto-Recovery
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>

      <AlertDialog open={showSensitivityDialog} onOpenChange={setShowSensitivityDialog}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Increase Detection Sensitivity to High?</AlertDialogTitle>
            <AlertDialogDescription className="space-y-3 pt-2">
              <p>
                High sensitivity will increase the incident detection rate by approximately 30%.
              </p>
              <div className="rounded-md border bg-muted p-3">
                <p className="text-sm font-medium mb-2">Expected Changes:</p>
                <ul className="text-xs text-muted-foreground list-disc list-inside space-y-1">
                  <li>Earlier detection of edge cases and anomalies</li>
                  <li>Approximately 20-30% increase in false positives</li>
                  <li>Higher operational alert volume</li>
                  <li>Recommended for critical workflows only</li>
                </ul>
              </div>
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel onClick={() => setShowSensitivityDialog(false)}>
              Keep Current Setting
            </AlertDialogCancel>
            <AlertDialogAction 
              onClick={() => {
                setDetectionSensitivity('high');
                setShowSensitivityDialog(false);
                toast.success('Sensitivity increased', {
                  description: 'Detection sensitivity is now set to High.',
                });
              }}
            >
              Confirm High Sensitivity
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </div>
  );
}