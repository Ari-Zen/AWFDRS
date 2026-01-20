import { useState } from 'react';
import { Eye, EyeOff, Shield, AlertCircle } from 'lucide-react';
import { Card } from '@/app/components/ui/card';
import { Input } from '@/app/components/ui/input';
import { Label } from '@/app/components/ui/label';
import { Button } from '@/app/components/ui/button';
import { Separator } from '@/app/components/ui/separator';

interface AuthPageProps {
  onAuthenticate: () => void;
}

export function AuthPage({ onAuthenticate }: AuthPageProps) {
  const [showPassword, setShowPassword] = useState(false);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (!email || !password) {
      setError('Please enter both email and password');
      return;
    }

    setIsLoading(true);
    
    // Simulate authentication delay
    setTimeout(() => {
      setIsLoading(false);
      onAuthenticate();
    }, 1000);
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-md space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <div className="flex items-center justify-center gap-2 mb-4">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary">
              <Shield className="h-6 w-6 text-primary-foreground" />
            </div>
            <h1 className="text-2xl font-semibold tracking-tight">AWFDRS</h1>
          </div>
          <h2 className="text-xl font-medium">Autonomous Workflow Failure Detection & Recovery</h2>
          <p className="text-sm text-muted-foreground">
            Secure access to enterprise workflow monitoring
          </p>
        </div>

        {/* Authentication Card */}
        <Card className="p-6">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Field */}
            <div className="space-y-2">
              <Label htmlFor="email">Email Address</Label>
              <Input
                id="email"
                type="email"
                placeholder="you@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                autoComplete="email"
                disabled={isLoading}
                required
              />
            </div>

            {/* Password Field */}
            <div className="space-y-2">
              <Label htmlFor="password">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  placeholder="Enter your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  autoComplete="current-password"
                  disabled={isLoading}
                  required
                  className="pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground transition-colors"
                  tabIndex={-1}
                >
                  {showPassword ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                  <span className="sr-only">
                    {showPassword ? 'Hide password' : 'Show password'}
                  </span>
                </button>
              </div>
            </div>

            {/* Error Message */}
            {error && (
              <div className="rounded-md border border-destructive bg-destructive/10 p-3 flex items-start gap-2">
                <AlertCircle className="h-4 w-4 text-destructive shrink-0 mt-0.5" />
                <p className="text-sm text-destructive">{error}</p>
              </div>
            )}

            {/* Sign In Button */}
            <Button 
              type="submit" 
              className="w-full" 
              disabled={isLoading}
            >
              {isLoading ? 'Signing In...' : 'Sign In'}
            </Button>

            {/* Forgot Password */}
            <div className="text-center">
              <button
                type="button"
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                onClick={() => {}}
              >
                Forgot your password?
              </button>
            </div>

            {/* Divider */}
            <div className="relative">
              <div className="absolute inset-0 flex items-center">
                <Separator />
              </div>
              <div className="relative flex justify-center text-xs uppercase">
                <span className="bg-card px-2 text-muted-foreground">
                  Or continue with
                </span>
              </div>
            </div>

            {/* SSO Button */}
            <Button 
              type="button" 
              variant="outline" 
              className="w-full"
              disabled={isLoading}
            >
              Sign in with SSO
            </Button>
          </form>
        </Card>

        {/* Security Notice */}
        <Card className="p-4 border-border/50">
          <div className="flex items-start gap-3 text-xs text-muted-foreground">
            <Shield className="h-4 w-4 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <p className="font-medium text-foreground">Security & Compliance</p>
              <p>
                All access attempts are logged and monitored. This system is intended for authorized personnel only. 
                By signing in, you acknowledge that your activities will be recorded for security and audit purposes.
              </p>
            </div>
          </div>
        </Card>

        {/* Footer Links */}
        <div className="flex items-center justify-center gap-4 text-xs text-muted-foreground">
          <button
            type="button"
            className="hover:text-foreground transition-colors"
            onClick={() => {}}
          >
            Privacy Policy
          </button>
          <span>•</span>
          <button
            type="button"
            className="hover:text-foreground transition-colors"
            onClick={() => {}}
          >
            Terms of Service
          </button>
          <span>•</span>
          <button
            type="button"
            className="hover:text-foreground transition-colors"
            onClick={() => {}}
          >
            Support
          </button>
        </div>
      </div>
    </div>
  );
}
