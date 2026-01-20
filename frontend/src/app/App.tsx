import { useState } from 'react';
import { ThemeProvider } from 'next-themes';
import { Toaster } from '@/app/components/ui/sonner';
import { Sidebar } from '@/app/components/layout/Sidebar';
import { TopBar } from '@/app/components/layout/TopBar';
import { OverviewPage } from '@/app/components/pages/OverviewPage';
import { IncidentsPage } from '@/app/components/pages/IncidentsPage';
import { WorkflowsPage } from '@/app/components/pages/WorkflowsPage';
import { VendorsPage } from '@/app/components/pages/VendorsPage';
import { AnalyticsPage } from '@/app/components/pages/AnalyticsPage';
import { AuditLogPage } from '@/app/components/pages/AuditLogPage';
import { SettingsPage } from '@/app/components/pages/SettingsPage';
import { IncidentDetailPage } from '@/app/components/pages/IncidentDetailPage';
import { AuthPage } from '@/app/components/pages/AuthPage';

export type NavigationItem = 'overview' | 'incidents' | 'workflows' | 'vendors' | 'analytics' | 'audit-log' | 'settings';

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [currentPage, setCurrentPage] = useState<NavigationItem>('overview');
  const [selectedIncidentId, setSelectedIncidentId] = useState<string | null>(null);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const handleIncidentSelect = (incidentId: string) => {
    setSelectedIncidentId(incidentId);
    setCurrentPage('incidents');
  };

  const handleBackToIncidents = () => {
    setSelectedIncidentId(null);
  };

  const renderPage = () => {
    if (currentPage === 'incidents' && selectedIncidentId) {
      return (
        <IncidentDetailPage 
          incidentId={selectedIncidentId} 
          onBack={handleBackToIncidents}
        />
      );
    }

    switch (currentPage) {
      case 'overview':
        return <OverviewPage onIncidentClick={handleIncidentSelect} />;
      case 'incidents':
        return <IncidentsPage onIncidentClick={handleIncidentSelect} />;
      case 'workflows':
        return <WorkflowsPage />;
      case 'vendors':
        return <VendorsPage />;
      case 'analytics':
        return <AnalyticsPage />;
      case 'audit-log':
        return <AuditLogPage />;
      case 'settings':
        return <SettingsPage />;
      default:
        return <OverviewPage onIncidentClick={handleIncidentSelect} />;
    }
  };

  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem>
      {!isAuthenticated ? (
        <AuthPage onAuthenticate={() => setIsAuthenticated(true)} />
      ) : (
        <div className="flex h-screen w-screen overflow-hidden bg-background">
          <Sidebar 
            currentPage={currentPage} 
            onNavigate={setCurrentPage}
            collapsed={sidebarCollapsed}
            onCollapsedChange={setSidebarCollapsed}
          />
          <div className="flex flex-1 flex-col overflow-hidden">
            <TopBar />
            <main className="flex-1 overflow-auto">
              {renderPage()}
            </main>
          </div>
        </div>
      )}
      <Toaster />
    </ThemeProvider>
  );
}

export default App;