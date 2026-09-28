import React, { useState } from 'react';
import { Eye, EyeOff, Lock, Mail, Store, ArrowRight, Loader2, AlertCircle, Sparkles, CheckCircle2 } from 'lucide-react';
import { authAPI } from '../../api/services';

interface LoginPageProps {
  onSuccess: (tokenData: any) => void;
  onSwitchToSignUp: () => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onSuccess, onSwitchToSignUp }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [forgotPasswordNotice, setForgotPasswordNotice] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);
    setForgotPasswordNotice(null);

    if (!email.trim() || !password.trim()) {
      setErrorMessage('Please enter both email and password.');
      return;
    }

    setIsLoading(true);

    try {
      const res = await authAPI.login(email.trim(), password);
      onSuccess(res);
    } catch (err: any) {
      console.error('Login error:', err);
      const msg = err?.message || 'Invalid email or password. Please check your credentials and try again.';
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  const handleForgotPassword = () => {
    setErrorMessage(null);
    setForgotPasswordNotice('Password reset link requested. Please check your email inbox or contact shop support.');
  };

  return (
    <div className="min-h-screen bg-[#F5F4EF] flex items-center justify-center p-4 font-sans text-[#111111]">
      <div className="w-full max-w-md bg-white rounded-[12px] border-2 border-[#111111] shadow-[8px_8px_0_#111111] overflow-hidden flex flex-col">
        
        {/* Header Branding */}
        <div className="p-6 bg-[#111111] text-white border-b-2 border-[#111111] flex flex-col items-center text-center relative">
          <div className="w-12 h-12 rounded-[8px] bg-[#F4C84A] text-[#111111] flex items-center justify-center font-bold mb-3 border border-[#111111] shadow-[2px_2px_0_#ffffff]">
            <Store className="w-7 h-7" />
          </div>
          <h1 className="text-xl font-bold font-mono uppercase tracking-wider text-white">DUKAANPULSE OS</h1>
          <p className="text-xs text-[#A0A0A0] font-mono mt-1">Kirana & General Store Operating System</p>
        </div>

        {/* Form Body */}
        <div className="p-6 space-y-5 bg-[#FBFBFA]">
          <div className="text-center">
            <h2 className="text-lg font-bold text-[#111111]">Welcome Back</h2>
            <p className="text-xs text-[#6B6B6B]">Sign in to manage inventory, billing & Khata ledgers</p>
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div className="p-3 bg-rose-50 border border-rose-400 rounded-[6px] flex items-start gap-2 text-rose-900 text-xs font-medium">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div>{errorMessage}</div>
            </div>
          )}

          {/* Forgot Password Notice */}
          {forgotPasswordNotice && (
            <div className="p-3 bg-amber-50 border border-amber-400 rounded-[6px] flex items-start gap-2 text-amber-950 text-xs font-medium">
              <CheckCircle2 className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <div>{forgotPasswordNotice}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Email Field */}
            <div className="space-y-1">
              <label className="text-xs font-bold font-mono text-[#111111] uppercase tracking-wide flex items-center gap-1.5">
                <Mail className="w-3.5 h-3.5" /> Email Address
              </label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="store@kirana.com"
                className="w-full px-3.5 py-2.5 bg-white rounded-[6px] border border-[#111111] text-xs font-medium text-[#111111] placeholder:text-[#999999] focus:outline-none focus:ring-2 focus:ring-[#F4C84A]"
              />
            </div>

            {/* Password Field */}
            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="text-xs font-bold font-mono text-[#111111] uppercase tracking-wide flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5" /> Password
                </label>
                <button
                  type="button"
                  onClick={handleForgotPassword}
                  className="text-[11px] font-bold text-[#111111] hover:underline cursor-pointer"
                >
                  Forgot Password?
                </button>
              </div>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full px-3.5 py-2.5 bg-white rounded-[6px] border border-[#111111] text-xs font-medium text-[#111111] placeholder:text-[#999999] focus:outline-none focus:ring-2 focus:ring-[#F4C84A] pr-10"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-[#111111] cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Remember Me Checkbox */}
            <div className="flex items-center justify-between pt-1">
              <label className="flex items-center gap-2 cursor-pointer">
                <input
                  type="checkbox"
                  checked={rememberMe}
                  onChange={(e) => setRememberMe(e.target.checked)}
                  className="w-4 h-4 rounded border-[#111111] text-[#111111] focus:ring-[#F4C84A]"
                />
                <span className="text-xs text-[#444444] font-medium">Remember me on this browser</span>
              </label>
            </div>

            {/* Sign In CTA Button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 bg-[#111111] hover:bg-black text-white rounded-[6px] border border-[#111111] font-bold text-xs shadow-[3px_3px_0_#111111] flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-75"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-[#F4C84A]" />
                  <span>AUTHENTICATING...</span>
                </>
              ) : (
                <>
                  <span>SIGN IN TO STORE</span>
                  <ArrowRight className="w-4 h-4 text-[#F4C84A]" />
                </>
              )}
            </button>
          </form>

          {/* Footer Switch */}
          <div className="pt-3 border-t border-[#E5E2D9] text-center">
            <p className="text-xs text-[#6B6B6B]">
              New to DukaanPulse?{' '}
              <button
                onClick={onSwitchToSignUp}
                className="font-bold text-[#111111] underline hover:text-black cursor-pointer"
              >
                Register New Kirana Shop
              </button>
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};
