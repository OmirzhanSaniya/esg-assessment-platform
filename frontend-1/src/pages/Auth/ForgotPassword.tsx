import { useState } from 'react';
import { Link } from 'react-router-dom';

const FEATURES = ['Быстрое восстановление', 'Безопасная ссылка', 'Письмо придёт за 1 минуту'];

export default function ForgotPassword() {
  const [email, setEmail]   = useState('');
  const [sent,  setSent]    = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: POST /api/v1/auth/forgot-password/
    setSent(true);
  };

  return (
    <div className="auth-page">

      {/* ── Left panel ── */}
      <div className="auth-left">
        <Link to="/" className="auth-left-logo">ESG<span>Campus</span></Link>

        <div className="auth-left-content">
          <h2>Восстановление пароля</h2>
          <p>Введите email вашей компании и мы отправим ссылку для сброса пароля</p>
        </div>

        <div className="auth-left-features">
          {FEATURES.map(f => (
            <div key={f} className="auth-feature">
              <div className="auth-feature-dot" />{f}
            </div>
          ))}
        </div>
      </div>

      {/* ── Right panel ── */}
      <div className="auth-right">
        <div className="auth-form-wrap">
          <Link to="/" className="auth-left-logo" style={{ color: '#0F172A', marginBottom: 28, display: 'block' }}>
            ESG<span style={{ color: '#22C55E' }}>Campus</span>
          </Link>

          {sent ? <SuccessState email={email} /> : <FormState email={email} setEmail={setEmail} onSubmit={handleSubmit} />}
        </div>
      </div>

    </div>
  );
}