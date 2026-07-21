import { Link } from 'react-router-dom';
import { UserPlus, ClipboardList, BarChart3, Leaf, Users, Shield, FileText, Map, Building2 } from 'lucide-react';
import { useCounter } from '../../hooks/useCounter';

export default function Home() {
  const blocksCounter = useCounter({ target: 3 });
  const questionsCounter = useCounter({ target: 20 });
  const levelsCounter = useCounter({ target: 4 });

  return (
    <div className="home">
      {/* Navbar */}
      <nav className="navbar">
        <div className="navbar-inner">
          <Link to="/" className="logo">ESG<span>Campus</span></Link>
          <div className="nav-links">
            <Link to="/login" className="btn btn-outline">Войти</Link>
            <Link to="/register" className="btn btn-primary">Зарегистрироваться</Link>
          </div>
        </div>
      </nav>

      {/* Hero */}
      <section className="hero">
        <div className="hero-blob-yellow" />
        <div className="hero-content">
          <div className="hero-left">
            <span className="hero-tag">КБТУ ESG Campus</span>
            <h1 className="hero-title">
              Оцените ESG<br />
              <span className="accent">готовность</span><br />
              компании
            </h1>
            <p className="hero-desc">
              Пройдите анкету по блокам E/S/G, получите рейтинг,
              персональный роадмап и PDF-отчёт
            </p>
            <div className="hero-actions">
              <Link to="/register" className="btn btn-primary btn-lg">Начать оценку →</Link>
              <Link to="/login" className="btn btn-outline btn-lg">Войти</Link>
            </div>
            <div className="hero-stats">
              <div>
                <span className="hero-stat-num" ref={blocksCounter.ref as React.RefObject<HTMLSpanElement>}>
                  {blocksCounter.value}
                </span>
                <span className="hero-stat-label">Блока оценки E/S/G</span>
              </div>
              <div>
                <span className="hero-stat-num" ref={questionsCounter.ref as React.RefObject<HTMLSpanElement>}>
                  {questionsCounter.value}+
                </span>
                <span className="hero-stat-label">Вопросов в анкете</span>
              </div>
              <div>
                <span className="hero-stat-num" ref={levelsCounter.ref as React.RefObject<HTMLSpanElement>}>
                  {levelsCounter.value}
                </span>
                <span className="hero-stat-label">Уровня рейтинга</span>
              </div>
            </div>
          </div>

          <div className="hero-right">
            <div className="hero-card">
              <p className="hero-card-title">ESG Рейтинг компании</p>
              <div className="esg-bars">
                <div className="esg-bar-row">
                  <span className="esg-bar-label e">E</span>
                  <div className="esg-bar-track">
                    <div className="esg-bar-fill e" />
                  </div>
                  <span className="esg-bar-val">78</span>
                </div>
                <div className="esg-bar-row">
                  <span className="esg-bar-label s">S</span>
                  <div className="esg-bar-track">
                    <div className="esg-bar-fill s" />
                  </div>
                  <span className="esg-bar-val">65</span>
                </div>
                <div className="esg-bar-row">
                  <span className="esg-bar-label g">G</span>
                  <div className="esg-bar-track">
                    <div className="esg-bar-fill g" />
                  </div>
                  <span className="esg-bar-val">82</span>
                </div>
              </div>
              <div className="hero-card-score">
                <span className="score-big">75</span>
                <div className="score-label-block">
                  <span className="label">Итоговый балл</span>
                  <span className="level">Продвинутый</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>