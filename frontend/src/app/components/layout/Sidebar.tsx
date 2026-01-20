import { 
  LayoutDashboard, 
  AlertTriangle, 
  Workflow, 
  Building2, 
  BarChart3, 
  FileText, 
  Settings,
  ChevronLeft,
  ChevronRight
} from 'lucide-react';
import type { NavigationItem } from '@/app/App';
import { Button } from '@/app/components/ui/button';
import { cn } from '@/app/components/ui/utils';

interface SidebarProps {
  currentPage: NavigationItem;
  onNavigate: (page: NavigationItem) => void;
  collapsed: boolean;
  onCollapsedChange: (collapsed: boolean) => void;
}

interface NavItem {
  id: NavigationItem;
  label: string;
  icon: React.ComponentType<{ className?: string }>;
}

const navItems: NavItem[] = [
  { id: 'overview', label: 'Overview', icon: LayoutDashboard },
  { id: 'incidents', label: 'Incidents', icon: AlertTriangle },
  { id: 'workflows', label: 'Workflows', icon: Workflow },
  { id: 'vendors', label: 'Vendors', icon: Building2 },
  { id: 'analytics', label: 'Analytics', icon: BarChart3 },
  { id: 'audit-log', label: 'Audit Log', icon: FileText },
  { id: 'settings', label: 'Settings', icon: Settings },
];

export function Sidebar({ currentPage, onNavigate, collapsed, onCollapsedChange }: SidebarProps) {
  return (
    <div 
      className={cn(
        "flex flex-col border-r bg-[var(--sidebar)] transition-all duration-200",
        collapsed ? "w-16" : "w-64"
      )}
      style={{ 
        borderColor: 'var(--sidebar-border)',
        color: 'var(--sidebar-foreground)'
      }}
    >
      {/* Header */}
      <div className="flex h-16 items-center justify-between border-b px-4" style={{ borderColor: 'var(--sidebar-border)' }}>
        {!collapsed && (
          <div className="flex items-center gap-2">
            <div className="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--sidebar-primary)]">
              <Workflow className="h-5 w-5" style={{ color: 'var(--sidebar-primary-foreground)' }} />
            </div>
            <div>
              <h1 className="text-sm font-semibold leading-none">WorkflowAI</h1>
              <p className="text-xs text-muted-foreground">Recovery System</p>
            </div>
          </div>
        )}
        {collapsed && (
          <div className="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--sidebar-primary)] mx-auto">
            <Workflow className="h-5 w-5" style={{ color: 'var(--sidebar-primary-foreground)' }} />
          </div>
        )}
      </div>

      {/* Navigation */}
      <nav className="flex-1 space-y-1 p-3">
        {navItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentPage === item.id;
          
          return (
            <button
              key={item.id}
              onClick={() => onNavigate(item.id)}
              className={cn(
                "flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                isActive 
                  ? "bg-[var(--sidebar-primary)] text-[var(--sidebar-primary-foreground)]" 
                  : "text-[var(--sidebar-foreground)] hover:bg-[var(--sidebar-accent)] hover:text-[var(--sidebar-accent-foreground)]",
                collapsed && "justify-center"
              )}
            >
              <Icon className={cn("h-5 w-5 flex-shrink-0")} />
              {!collapsed && <span>{item.label}</span>}
            </button>
          );
        })}
      </nav>

      {/* Collapse Toggle */}
      <div className="border-t p-3" style={{ borderColor: 'var(--sidebar-border)' }}>
        <Button
          variant="ghost"
          size="sm"
          onClick={() => onCollapsedChange(!collapsed)}
          className={cn("w-full", collapsed && "px-2")}
        >
          {collapsed ? (
            <ChevronRight className="h-4 w-4" />
          ) : (
            <>
              <ChevronLeft className="h-4 w-4 mr-2" />
              <span>Collapse</span>
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
