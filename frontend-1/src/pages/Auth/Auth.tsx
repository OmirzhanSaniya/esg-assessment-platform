import { useMemo, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { authAPI } from '../../api/client';
import './Auth.css';

import { SECTORS, SUB_INDUSTRIES } from '../../constants/industries';
const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/* ---------------------------------------------------------------- */
/* Small inline icons — shared by both forms */

function EyeIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none">
      <path d="M1.5 10S4.5 4 10 4s8.5 6 8.5 6-3 6-8.5 6-8.5-6-8.5-6z" stroke="currentColor" strokeWidth="1.4" />
      <circle cx="10" cy="10" r="2.5" stroke="currentColor" strokeWidth="1.4" />
    </svg>
  );
}

function EyeOffIcon() {
  return (
    <svg viewBox="0 0 20 20" fill="none">
      <path d="M2.5 2.5l15 15" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <path d="M8.3 4.3C8.85 4.1 9.42 4 10 4c5.5 0 8.5 6 8.5 6a13.9 13.9 0 01-2.9 3.7M5.6 5.7C3.2 7.2 1.5 10 1.5 10S4.5 16 10 16c1 0 1.9-.16 2.7-.44" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <path d="M8.1 8.1a2.5 2.5 0 003.5 3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
    </svg>
  );
}

function AlertIcon() {
  return (
    <svg viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.4" />
      <path d="M8 5v3.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" />
      <circle cx="8" cy="11" r="0.9" fill="currentColor" />
    </svg>
  );
}

/* ---------------------------------------------------------------- */
/* Shared field pieces — used by both Login and Register            */

/** Inline error line under a field. Renders nothing if there's no message. */
function FieldError({ message, className = '' }: { message?: string; className?: string }) {
  if (!message) return null;
  return (
    <p className={`field-error ${className}`}>
      <AlertIcon />
      {message}
    </p>
  );
}

/** Password input with a show/hide toggle. Wraps a plain <input>. */
function PasswordInput({
  id,
  name,
  value,
  onChange,
  placeholder,
  minLength,
}: {
  id: string;
  name?: string;
  value: string;
  onChange: (e: React.ChangeEvent<HTMLInputElement>) => void;
  placeholder?: string;
  minLength?: number;
}) {
  const [visible, setVisible] = useState(false);

  return (
    <div className="field-input-wrap">
      <input
        id={id}
        name={name}
        type={visible ? 'text' : 'password'}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        minLength={minLength}
        className={visible ? 'has-toggle' : ''}
      />
      <button
        type="button"
        className="toggle-visibility"
        onClick={() => setVisible((v) => !v)}
        aria-label={visible ? 'Скрыть пароль' : 'Показать пароль'}
      >
        {visible ? <EyeOffIcon /> : <EyeIcon />}
      </button>
    </div>
  );
}

/* ---------------------------------------------------------------- */
/* Password strength — quick heuristic, not a security guarantee.
   Used only to nudge users toward a stronger password client-side. */

type StrengthLevel = 0 | 1 | 2 | 3 | 4;

function getPasswordStrength(pw: string): { level: StrengthLevel; label: string } {
  if (!pw) return { level: 0, label: '' };

  let score = 0;
  if (pw.length >= 8) score++;
  if (pw.length >= 12) score++;
  if (/[A-Z]/.test(pw) && /[a-z]/.test(pw)) score++;
  if (/[0-9]/.test(pw) && /[^A-Za-z0-9]/.test(pw)) score++;

  const labels: Record<Exclude<StrengthLevel, 0>, string> = {
    1: 'Слабый',
    2: 'Средний',
    3: 'Хороший',
    4: 'Надёжный',
  };
  const level = Math.max(1, Math.min(score, 4)) as Exclude<StrengthLevel, 0>;
  return { level, label: labels[level] };
}

function PasswordStrengthMeter({ password }: { password: string }) {
  if (!password) return null;
  const { level, label } = getPasswordStrength(password);

  return (
    <>
      <div className="password-strength" data-level={level}>
        {[0, 1, 2, 3].map((i) => (
          <span key={i} className="password-strength-bar" />
        ))}
      </div>
      <p className="password-strength-label">{label}</p>
    </>
  );
}
/* ==================================================================
   LOGIN
   ================================================================== */

   export function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [remember, setRemember] = useState(true);
    const [fieldErrors, setFieldErrors] = useState<{ email?: string; password?: string }>({});
    const [formError, setFormError] = useState('');
    const [loading, setLoading] = useState(false);
  
    const { login } = useAuth();
    const navigate = useNavigate();
  
    const validate = () => {
      const errors: typeof fieldErrors = {};
      if (!EMAIL_RE.test(email)) errors.email = 'Введите корректный email';
      if (!password) errors.password = 'Введите пароль';
      setFieldErrors(errors);
      return Object.keys(errors).length === 0;
    };
  
    const handleSubmit = async (e: React.FormEvent) => {
      e.preventDefault();
      setFormError('');
      if (!validate()) return;
  
      setLoading(true);
      try {
        await login(email, password);
        if (remember) {
          localStorage.setItem('esg_remember_email', email);
        } else {
          localStorage.removeItem('esg_remember_email');
        }
        navigate('/dashboard');
      } catch {
        setFormError('Неверный email или пароль');
      } finally {
        setLoading(false);
      }
    };
  
    return (
      <div className="auth-page">
        <div className="auth-blob blob1" />
        <div className="auth-blob blob2" />
        <div className="auth-card">
          <Link to="/" className="auth-logo">
            ESG<span>Campus</span>
          </Link>
          <h1>Войти</h1>
          <p className="auth-sub">Введите данные вашей компании</p>
  
          {formError && (
            <div className="auth-banner error">
              <AlertIcon />
              <span>{formError}</span>
            </div>
          )}
  
          <form onSubmit={handleSubmit} noValidate>
            <div className={`field ${fieldErrors.email ? 'has-error' : ''}`}>
              <label htmlFor="login-email">Email</label>
              <input
                id="login-email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="company@example.com"
              />
              <FieldError message={fieldErrors.email} />
            </div>
  
            <div className={`field ${fieldErrors.password ? 'has-error' : ''}`}>
              <label htmlFor="login-password">Пароль</label>
              <PasswordInput
                id="login-password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
              <FieldError message={fieldErrors.password} />
            </div>
  
            <div className="row-between">
              <label className="field-checkbox field-checkbox--inline">
                <input type="checkbox" checked={remember} onChange={(e) => setRemember(e.target.checked)} />
                Запомнить меня
              </label>
              <Link to="/forgot-password" className="forgot-link">
                Забыли пароль?
              </Link>
            </div>
  
            <button type="submit" className="btn btn-primary auth-btn" disabled={loading}>
              {loading && <span className="spinner" />}
              {loading ? 'Входим...' : 'Войти'}
            </button>
          </form>
  
          <p className="auth-switch">
            Нет аккаунта? <Link to="/register">Зарегистрироваться</Link>
          </p>
        </div>
      </div>
    );
  }
