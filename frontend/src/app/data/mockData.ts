import type { Incident, Workflow, Vendor, AuditLogEntry, SystemMetrics } from '@/app/types';

export const mockIncidents: Incident[] = [
  {
    id: 'INC-2026-001',
    title: 'Payment processing timeout in Stripe integration',
    severity: 'critical',
    status: 'investigating',
    workflowsAffected: ['payment-processing', 'subscription-renewal'],
    detectedAt: '2026-01-19T14:23:00Z',
    lastUpdated: '2026-01-19T14:45:00Z',
    impactedUsers: 1247,
    impactedTransactions: 342,
    description: 'Payment processing workflow experiencing elevated timeout rates (87% failure) when communicating with Stripe API. Multiple retry attempts exhausted.',
    aiHypotheses: [
      {
        id: 'hyp-1',
        hypothesis: 'Stripe API gateway timeout due to regional network congestion',
        confidence: 87,
        evidence: [
          'Elevated latency observed in us-east-1 region (avg 4200ms vs baseline 180ms)',
          'Similar pattern detected in 3 other customers using same region',
          'No deployment or configuration changes in last 6 hours'
        ],
        suggestedAction: 'Implement automatic failover to backup payment processor or retry with exponential backoff'
      },
      {
        id: 'hyp-2',
        hypothesis: 'Rate limiting triggered by unusual transaction volume spike',
        confidence: 62,
        evidence: [
          'Transaction volume increased 340% in last 30 minutes',
          'Stripe API returning 429 status codes intermittently',
          'Correlation with marketing campaign launch at 14:15 UTC'
        ],
        suggestedAction: 'Temporarily queue transactions and process with controlled rate'
      }
    ],
    timeline: [
      {
        id: 'evt-1',
        timestamp: '2026-01-19T14:23:12Z',
        event: 'Anomaly detected: Payment processing failure rate exceeded threshold (15%)',
        type: 'detection',
        actor: 'System'
      },
      {
        id: 'evt-2',
        timestamp: '2026-01-19T14:23:45Z',
        event: 'AI analysis initiated: Gathering evidence from logs, metrics, and vendor status',
        type: 'analysis',
        actor: 'AI Agent'
      },
      {
        id: 'evt-3',
        timestamp: '2026-01-19T14:25:30Z',
        event: 'Incident created: INC-2026-001 - Severity set to CRITICAL',
        type: 'action',
        actor: 'System'
      },
      {
        id: 'evt-4',
        timestamp: '2026-01-19T14:26:15Z',
        event: 'Notification sent to on-call SRE team',
        type: 'action',
        actor: 'System'
      },
      {
        id: 'evt-5',
        timestamp: '2026-01-19T14:28:00Z',
        event: 'Status updated to INVESTIGATING by sarah.chen@company.com',
        type: 'update',
        actor: 'sarah.chen@company.com'
      }
    ],
    recoveryActions: [
      {
        id: 'act-1',
        action: 'failover',
        description: 'Failover payment processing to backup provider (PayPal)',
        risk: 'medium',
        requiresApproval: true,
        estimatedImpact: 'Will affect 100% of payment transactions; backup provider has different settlement timing'
      },
      {
        id: 'act-2',
        action: 'retry',
        description: 'Retry failed transactions with exponential backoff (max 5 attempts)',
        risk: 'low',
        requiresApproval: false,
        estimatedImpact: 'May delay transaction completion by up to 2 minutes'
      },
      {
        id: 'act-3',
        action: 'escalate',
        description: 'Escalate to Stripe enterprise support with priority ticket',
        risk: 'low',
        requiresApproval: false,
        estimatedImpact: 'No direct system impact; may expedite vendor resolution'
      }
    ]
  },
  {
    id: 'INC-2026-002',
    title: 'Employee onboarding workflow stuck in approval stage',
    severity: 'medium',
    status: 'active',
    workflowsAffected: ['employee-onboarding', 'okta-provisioning'],
    detectedAt: '2026-01-19T13:15:00Z',
    lastUpdated: '2026-01-19T14:30:00Z',
    impactedUsers: 23,
    description: 'Onboarding workflow failing to complete approval step; automated approval not triggering despite meeting criteria.',
    aiHypotheses: [
      {
        id: 'hyp-3',
        hypothesis: 'Okta webhook delivery failure preventing approval completion',
        confidence: 78,
        evidence: [
          'Webhook delivery logs show 503 errors from Okta',
          'Manual approval override succeeds immediately',
          'Okta status page reports API performance degradation'
        ],
        suggestedAction: 'Implement manual approval workflow temporarily until Okta service restored'
      }
    ],
    timeline: [
      {
        id: 'evt-6',
        timestamp: '2026-01-19T13:15:22Z',
        event: 'Workflow completion time exceeded SLA (2 hours)',
        type: 'detection',
        actor: 'System'
      },
      {
        id: 'evt-7',
        timestamp: '2026-01-19T13:16:00Z',
        event: 'Incident created: INC-2026-002',
        type: 'action',
        actor: 'System'
      }
    ],
    recoveryActions: [
      {
        id: 'act-4',
        action: 'manual-intervention',
        description: 'Trigger manual approval for pending onboarding requests',
        risk: 'low',
        requiresApproval: true,
        estimatedImpact: 'Requires HR manager approval for 23 pending requests'
      }
    ]
  },
  {
    id: 'INC-2026-003',
    title: 'Compliance report generation timeout',
    severity: 'high',
    status: 'resolved',
    workflowsAffected: ['compliance-reporting'],
    detectedAt: '2026-01-19T09:30:00Z',
    lastUpdated: '2026-01-19T11:15:00Z',
    description: 'Daily SOC2 compliance report generation exceeded timeout limit. Root cause: database query optimization needed.',
    aiHypotheses: [
      {
        id: 'hyp-4',
        hypothesis: 'Database query performance degradation due to table growth',
        confidence: 95,
        evidence: [
          'Audit log table grew 340% in last month',
          'Query execution time increased from 45s to 12min',
          'Adding index on timestamp column resolved issue'
        ]
      }
    ],
    timeline: [
      {
        id: 'evt-8',
        timestamp: '2026-01-19T09:30:15Z',
        event: 'Report generation timeout after 15 minutes',
        type: 'detection',
        actor: 'System'
      },
      {
        id: 'evt-9',
        timestamp: '2026-01-19T10:45:00Z',
        event: 'Database index added by DBA team',
        type: 'action',
        actor: 'james.wong@company.com'
      },
      {
        id: 'evt-10',
        timestamp: '2026-01-19T11:00:00Z',
        event: 'Report generation completed successfully (runtime: 52s)',
        type: 'resolution',
        actor: 'System'
      },
      {
        id: 'evt-11',
        timestamp: '2026-01-19T11:15:00Z',
        event: 'Incident marked as RESOLVED',
        type: 'resolution',
        actor: 'james.wong@company.com'
      }
    ]
  }
];

export const mockWorkflows: Workflow[] = [
  {
    id: 'wf-001',
    name: 'Payment Processing',
    status: 'failing',
    category: 'Financial',
    lastRun: '2026-01-19T14:45:00Z',
    successRate: 13,
    avgDuration: 4200,
    dependencies: ['stripe-api', 'payment-gateway', 'fraud-detection'],
    vendor: 'Stripe',
    activeIncidents: 1
  },
  {
    id: 'wf-002',
    name: 'Subscription Renewal',
    status: 'degraded',
    category: 'Financial',
    lastRun: '2026-01-19T14:40:00Z',
    successRate: 67,
    avgDuration: 1800,
    dependencies: ['payment-processing', 'email-notification'],
    vendor: 'Stripe',
    activeIncidents: 1
  },
  {
    id: 'wf-003',
    name: 'Employee Onboarding',
    status: 'degraded',
    category: 'HR',
    lastRun: '2026-01-19T14:30:00Z',
    successRate: 72,
    avgDuration: 7200,
    dependencies: ['okta-provisioning', 'slack-invitation', 'github-access'],
    vendor: 'Okta',
    activeIncidents: 1
  },
  {
    id: 'wf-004',
    name: 'Compliance Reporting',
    status: 'healthy',
    category: 'Compliance',
    lastRun: '2026-01-19T11:00:00Z',
    successRate: 100,
    avgDuration: 52,
    dependencies: ['database', 'audit-log-service'],
    activeIncidents: 0
  },
  {
    id: 'wf-005',
    name: 'Customer Data Sync',
    status: 'healthy',
    category: 'Data',
    lastRun: '2026-01-19T14:00:00Z',
    successRate: 98,
    avgDuration: 340,
    dependencies: ['salesforce-api', 'data-warehouse'],
    vendor: 'Salesforce',
    activeIncidents: 0
  },
  {
    id: 'wf-006',
    name: 'IT Asset Provisioning',
    status: 'healthy',
    category: 'IT Operations',
    lastRun: '2026-01-19T13:30:00Z',
    successRate: 95,
    avgDuration: 450,
    dependencies: ['jamf-api', 'inventory-system'],
    vendor: 'Jamf',
    activeIncidents: 0
  },
  {
    id: 'wf-007',
    name: 'Security Alert Processing',
    status: 'healthy',
    category: 'Security',
    lastRun: '2026-01-19T14:50:00Z',
    successRate: 100,
    avgDuration: 120,
    dependencies: ['siem', 'pagerduty-api'],
    vendor: 'PagerDuty',
    activeIncidents: 0
  },
  {
    id: 'wf-008',
    name: 'Invoice Generation',
    status: 'healthy',
    category: 'Financial',
    lastRun: '2026-01-19T12:00:00Z',
    successRate: 99,
    avgDuration: 890,
    dependencies: ['billing-system', 'pdf-generator', 'email-service'],
    activeIncidents: 0
  }
];

export const mockVendors: Vendor[] = [
  {
    id: 'vnd-001',
    name: 'Stripe',
    status: 'degraded',
    lastStatusChange: '2026-01-19T14:23:00Z',
    integrationType: 'REST API',
    workflowsConnected: 12,
    uptime: 97.8,
    avgResponseTime: 4200
  },
  {
    id: 'vnd-002',
    name: 'Okta',
    status: 'degraded',
    lastStatusChange: '2026-01-19T13:15:00Z',
    integrationType: 'OAuth 2.0',
    workflowsConnected: 8,
    uptime: 98.5,
    avgResponseTime: 850
  },
  {
    id: 'vnd-003',
    name: 'Salesforce',
    status: 'operational',
    lastStatusChange: '2026-01-18T09:00:00Z',
    integrationType: 'REST API',
    workflowsConnected: 15,
    uptime: 99.9,
    avgResponseTime: 340
  },
  {
    id: 'vnd-004',
    name: 'PagerDuty',
    status: 'operational',
    lastStatusChange: '2026-01-15T12:00:00Z',
    integrationType: 'Webhooks',
    workflowsConnected: 6,
    uptime: 99.95,
    avgResponseTime: 120
  },
  {
    id: 'vnd-005',
    name: 'AWS',
    status: 'operational',
    lastStatusChange: '2026-01-10T08:00:00Z',
    integrationType: 'SDK',
    workflowsConnected: 45,
    uptime: 99.99,
    avgResponseTime: 89
  },
  {
    id: 'vnd-006',
    name: 'Jamf',
    status: 'operational',
    lastStatusChange: '2026-01-12T14:00:00Z',
    integrationType: 'REST API',
    workflowsConnected: 4,
    uptime: 99.2,
    avgResponseTime: 450
  }
];

export const mockAuditLog: AuditLogEntry[] = [
  {
    id: 'aud-001',
    timestamp: '2026-01-19T14:28:00Z',
    actor: 'sarah.chen@company.com',
    action: 'incident.status.update',
    resource: 'INC-2026-001',
    result: 'success',
    metadata: {
      previousStatus: 'active',
      newStatus: 'investigating',
      reason: 'Taking ownership of payment processing incident'
    }
  },
  {
    id: 'aud-002',
    timestamp: '2026-01-19T14:26:15Z',
    actor: 'system',
    action: 'notification.send',
    resource: 'INC-2026-001',
    result: 'success',
    metadata: {
      recipients: ['sre-team@company.com'],
      channel: 'email,slack'
    }
  },
  {
    id: 'aud-003',
    timestamp: '2026-01-19T14:25:30Z',
    actor: 'system',
    action: 'incident.create',
    resource: 'INC-2026-001',
    result: 'success',
    metadata: {
      severity: 'critical',
      workflowsAffected: ['payment-processing', 'subscription-renewal']
    }
  },
  {
    id: 'aud-004',
    timestamp: '2026-01-19T11:15:00Z',
    actor: 'james.wong@company.com',
    action: 'incident.resolve',
    resource: 'INC-2026-003',
    result: 'success',
    metadata: {
      resolution: 'Database index optimization applied',
      duration: '6300s'
    }
  },
  {
    id: 'aud-005',
    timestamp: '2026-01-19T10:45:00Z',
    actor: 'james.wong@company.com',
    action: 'recovery.execute',
    resource: 'INC-2026-003',
    result: 'success',
    metadata: {
      action: 'database.index.create',
      table: 'audit_logs',
      column: 'timestamp'
    }
  },
  {
    id: 'aud-006',
    timestamp: '2026-01-19T09:45:00Z',
    actor: 'alex.rodriguez@company.com',
    action: 'workflow.manual.trigger',
    resource: 'wf-004',
    result: 'failure',
    metadata: {
      reason: 'Timeout exceeded after 15 minutes'
    }
  }
];

export const mockSystemMetrics: SystemMetrics = {
  totalWorkflows: 47,
  healthyWorkflows: 41,
  activeIncidents: 2,
  criticalIncidents: 1,
  avgRecoveryTime: 42,
  uptime: 99.2
};
