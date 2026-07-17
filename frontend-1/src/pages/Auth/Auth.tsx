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
