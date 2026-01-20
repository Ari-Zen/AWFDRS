import { Bell, Moon, Sun, User } from 'lucide-react';
import { useTheme } from 'next-themes';
import { Button } from '@/app/components/ui/button';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/app/components/ui/dropdown-menu';
import { Badge } from '@/app/components/ui/badge';

export function TopBar() {
  const { theme, setTheme } = useTheme();

  return (
    <div className="flex h-16 items-center justify-between border-b bg-card px-6 shadow-sm">
      <div className="flex items-center gap-4">
        <div>
          <p className="text-xs text-muted-foreground/70">
            {new Date().toLocaleDateString('en-US', { 
              weekday: 'long', 
              year: 'numeric', 
              month: 'long', 
              day: 'numeric' 
            })} • {new Date().toLocaleTimeString('en-US', { 
              hour: '2-digit', 
              minute: '2-digit',
              timeZoneName: 'short'
            })}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-1 border-l pl-4">
        {/* Notifications */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="relative h-9 w-9">
              <Bell className="h-[18px] w-[18px]" />
              <Badge 
                variant="destructive" 
                className="absolute -right-1 -top-1 h-5 w-5 rounded-full p-0 text-[10px] flex items-center justify-center"
              >
                2
              </Badge>
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-80">
            <div className="p-4">
              <h4 className="mb-2 font-medium">Active Notifications</h4>
              <div className="space-y-2">
                <div className="rounded-md border p-3">
                  <p className="text-sm">
                    <span className="font-medium text-[var(--status-critical)]">Critical:</span> Payment processing failure
                  </p>
                  <p className="text-xs text-muted-foreground">2 minutes ago</p>
                </div>
                <div className="rounded-md border p-3">
                  <p className="text-sm">
                    <span className="font-medium text-[var(--status-warning)]">Medium:</span> Onboarding workflow delayed
                  </p>
                  <p className="text-xs text-muted-foreground">1 hour ago</p>
                </div>
              </div>
            </div>
          </DropdownMenuContent>
        </DropdownMenu>

        {/* Theme Toggle */}
        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          <Sun className="h-[18px] w-[18px] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[18px] w-[18px] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>

        {/* User Menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" size="icon" className="h-9 w-9">
              <User className="h-[18px] w-[18px]" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end">
            <div className="px-2 py-1.5">
              <p className="text-sm font-medium">Sarah Chen</p>
              <p className="text-xs text-muted-foreground">sarah.chen@company.com</p>
              <p className="text-xs text-muted-foreground mt-1">Senior SRE</p>
            </div>
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Team Settings</DropdownMenuItem>
            <DropdownMenuItem>Documentation</DropdownMenuItem>
            <DropdownMenuItem className="text-destructive">Sign Out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </div>
  );
}