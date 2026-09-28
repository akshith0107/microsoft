import React, { useState } from 'react';
import { Eye, EyeOff, Lock, Mail, Store, User, Phone, ArrowRight, Loader2, AlertCircle, CheckCircle2 } from 'lucide-react';
import { authAPI } from '../../api/services';

interface SignUpPageProps {
  onSuccess: (tokenData: any) => void;
  onSwitchToLogin: () => void;
}

export const SignUpPage: React.FC<SignUpPageProps> = ({ onSuccess, onSwitchToLogin }) => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [shopName, setShopName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage(null);

    if (!name.trim() || !email.trim() || !password || !shopName.trim()) {
      setErrorMessage('Please fill out all required fields.');
      return;
    }

    if (password.length < 8) {
      setErrorMessage('Password must be at least 8 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please re-enter your password.');
      return;
    }

    setIsLoading(true);

    try {
      const res = await authAPI.signup({
        name: name.trim(),
        email: email.trim(),
        phone: phone.trim() || undefined,
        password,
        shop_name: shopName.trim()
      });

      onSuccess(res);
    } catch (err: any) {
      console.error('Signup error:', err);
      const msg = err?.message || 'Failed to create shop account. Email might already be registered.';
      setErrorMessage(msg);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#F5F4EF] flex items-center justify-center p-4 font-sans text-[#111111]">
      <div className="w-full max-w-md bg-white rounded-[12px] border-2 border-[#111111] shadow-[8px_8px_0_#111111] overflow-hidden flex flex-col my-6">
        
        {/* Header Branding */}
        <div className="p-6 bg-[#111111] text-white border-b-2 border-[#111111] flex flex-col items-center text-center relative">
          <div className="w-12 h-12 rounded-[8px] bg-[#F4C84A] text-[#111111] flex items-center justify-center font-bold mb-3 border border-[#111111] shadow-[2px_2px_0_#ffffff]">
            <Store className="w-7 h-7" />
          </div>
          <h1 className="text-xl font-bold font-mono uppercase tracking-wider text-white">REGISTER KIRANA STORE</h1>
          <p className="text-xs text-[#A0A0A0] font-mono mt-1">DukaanPulse Operating System Setup</p>
        </div>

        {/* Form Body */}
        <div className="p-6 space-y-4 bg-[#FBFBFA]">
          <div className="text-center">
            <h2 className="text-lg font-bold text-[#111111]">Create Shop Account</h2>
            <p className="text-xs text-[#6B6B6B]">Set up your store profile and start managing sales in seconds</p>
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div className="p-3 bg-rose-50 border border-rose-400 rounded-[6px] flex items-start gap-2 text-rose-900 text-xs font-medium">
              <AlertCircle className="w-4 h-4 text-rose-600 shrink-0 mt-0.5" />
              <div>{errorMessage}</div>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            {/* Shop Name */}
            <div className="space-y-1">
              <label className="text-xs font-bold font-mono text-[#111111] uppercase tracking-wide flex items-center gap-1.5">
                <Store className="w-3.5 h-3.5 text-[#111111]" /> Shop / Store Name *
              </label>
              <input
                type="text"
                required
                value={shopName}
                onChange={(e) => setShopName(e.target.value)}
                placeholder="e.g. Gupta Kirana & Provision Store"
                className="w-full px-3.5 py-2 bg-white rounded-[6px] border border-[#111111] text-xs font-medium text-[#111111] placeholder:text-[#999999] focus:outline-none focus:ring-2 focus:ring-[#F4C84A]"
              />
            </div>

            {/* Owner Name */}
            <div className="space-y-1">
              <label className="text-xs font-bold font-mono text-[#111111] uppercase tracking-wide flex items-center gap-1.5">
                <User className="w-3.5 h-3.5" /> Owner Full Name *
              </label>
              <input
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Rajesh Gupta"
                className="w-full px-3.5 py-2 bg-white rounded-[6px] border border-[#111111] text-xs font-medium text-[#111111] placeholder:text-[#999999] focus:outline-none focus:ring-2 focus:ring-[#F4C84A]"
              />
            </div>

            {/* Email & Phone */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-bold font-mono text-[#111111] uppercase tracking-wide flex items-center gap-1.5">
                  <Mail className="w-3.5 h-3.5" /> Email *
                </label>
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="rajesh@kirana.com"
                  className="w-full px-3.5 py-2 bg-white rounded-[6px] border border-[#111111] text-xs font-medium text-[#111111] placeholder:text-[#999999] focus:outline-none focus:ring-2 focus:ring-[#F4C84A]"
                />
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold font-mono text-[#111111] uppercase tracking-wide flex items-center gap-1.5">
                  <Phone className="w-3.5 h-3.5" /> Mobile (Optional)
                </label>
                <input
                  type="tel"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  placeholder="9876543210"
                  className="w-full px-3.5 py-2 bg-white rounded-[6px] border border-[#111111] text-xs font-medium text-[#111111] placeholder:text-[#999999] focus:outline-none focus:ring-2 focus:ring-[#F4C84A]"
                />
              </div>
            </div>

            {/* Password & Confirm Password */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              <div className="space-y-1">
                <label className="text-xs font-bold font-mono text-[#111111] uppercase tracking-wide flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5" /> Password *
                </label>
                <div className="relative">
                  <input
                    type={showPassword ? 'text' : 'password'}
                    required
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Min 8 chars"
                    className="w-full px-3.5 py-2 bg-white rounded-[6px] border border-[#111111] text-xs font-medium text-[#111111] placeholder:text-[#999999] focus:outline-none focus:ring-2 focus:ring-[#F4C84A] pr-9"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-2.5 top-1/2 -translate-y-1/2 text-gray-500 hover:text-[#111111]"
                  >
                    {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-xs font-bold font-mono text-[#111111] uppercase tracking-wide flex items-center gap-1.5">
                  <Lock className="w-3.5 h-3.5" /> Confirm *
                </label>
                <input
                  type={showPassword ? 'text' : 'password'}
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="Repeat password"
                  className="w-full px-3.5 py-2 bg-white rounded-[6px] border border-[#111111] text-xs font-medium text-[#111111] placeholder:text-[#999999] focus:outline-none focus:ring-2 focus:ring-[#F4C84A]"
                />
              </div>
            </div>

            {/* Create Account CTA */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-3 mt-2 bg-[#111111] hover:bg-black text-white rounded-[6px] border border-[#111111] font-bold text-xs shadow-[3px_3px_0_#111111] flex items-center justify-center gap-2 transition-all cursor-pointer disabled:opacity-75"
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin text-[#F4C84A]" />
                  <span>CREATING STORE ACCOUNT...</span>
                </>
              ) : (
                <>
                  <span>CREATE ACCOUNT & START</span>
                  <ArrowRight className="w-4 h-4 text-[#F4C84A]" />
                </>
              )}
            </button>
          </form>

          {/* Footer Switch */}
          <div className="pt-3 border-t border-[#E5E2D9] text-center">
            <p className="text-xs text-[#6B6B6B]">
              Already have an account?{' '}
              <button
                onClick={onSwitchToLogin}
                className="font-bold text-[#111111] underline hover:text-black cursor-pointer"
              >
                Sign In to Existing Shop
              </button>
            </p>
          </div>
        </div>

      </div>
    </div>
  );
};
