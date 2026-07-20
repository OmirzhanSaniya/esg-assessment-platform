import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { companyAPI, assessmentAPI } from '../../api/client';
import type { AssessmentResult } from '../../types';
import './Dashboard.css';

interface Profile {
  name: string;
  industry: string;
  current_result?: AssessmentResult;
}

const ESG_BLOCKS = ['E', 'S', 'G'] as const;
type EsgBlock = (typeof ESG_BLOCKS)[number];

const BLOCK_LABELS: Record<EsgBlock, string> = {
  E: 'Environmental',
  S: 'Social',
  G: 'Governance',
};

const LEVEL_COLORS: Record<string, string> = {
  'Начальный': '#EF4444',
  'Развивающийся': '#F59E0B',
  'Продвинутый': '#3B82F6',
  'Лидер': '#10B981',
};
const DEFAULT_LEVEL_COLOR = '#6B7280';

function getLevelColor(level: string): string {
  return LEVEL_COLORS[level] ?? DEFAULT_LEVEL_COLOR;
}
/* ---------------------------------------------------------------- */

function LevelBadge({ level }: { level: string }) {
    return (
      <span className="level-badge" style={{ background: getLevelColor(level) }}>
        {level}
      </span>
    );
  }
  
  function ScoreCircle({ block, value }: { block: EsgBlock; value: number }) {
    return (
      <div className="score-block">
        <div className="score-circle" style={{ '--pct': `${value}%` } as React.CSSProperties}>
          <span>{value}</span>
        </div>
        <p>{BLOCK_LABELS[block]}</p>
      </div>
    );
  }
/* ---------------------------------------------------------------- */

export default function Dashboard() {
    const [profile, setProfile] = useState<Profile | null>(null);
    const [history, setHistory] = useState<AssessmentResult[]>([]);
    const [loading, setLoading] = useState(true);
    const { logout } = useAuth();
    const navigate = useNavigate();
  
    useEffect(() => {
      Promise.all([companyAPI.getProfile(), companyAPI.getHistory()])
        .then(([p, h]) => {
          setProfile(p.data);
          setHistory(h.data);
        })
        .catch(() => {})
        .finally(() => setLoading(false));
    }, []);
  
    const handleDownloadPdf = async (id: number) => {
      const res = await assessmentAPI.downloadPdf(id);
      const url = URL.createObjectURL(new Blob([res.data]));
      const a = document.createElement('a');
      a.href = url;
      a.download = `esg-report-${id}.pdf`;
      a.click();
      URL.revokeObjectURL(url); // освобождаем память — иначе blob-URL висит до перезагрузки страницы
    };
  
    const handleLogout = () => {
      logout();
      navigate('/');
    };
  
    if (loading) return <div className="loading">Загрузка...</div>;
  
    const result = profile?.current_result;
  
    return (
      <div className="dashboard">
        <nav className="dashboard-nav">
          <Link to="/" className="logo">
            ESG<span>Campus</span>
          </Link>
          <div className="nav-right">
            <Link to="/assessment" className="btn btn-primary">Пройти оценку</Link>
            <button className="btn btn-outline" onClick={handleLogout}>Выйти</button>
          </div>
        </nav>
  
        <main className="dashboard-main">
          {/* Profile */}
          <div className="dash-header">
            <div>
              <h1>{profile?.name || 'Компания'}</h1>
              <span className="industry-tag">{profile?.industry}</span>
            </div>
            <Link to="/assessment" className="btn btn-primary">+ Пройти оценку заново</Link>
          </div>
  
          {/* Current score */}
          {result ? (
            <div className="score-card">
              <h2>Текущий ESG-рейтинг</h2>
              <div className="scores-row">
                {ESG_BLOCKS.map((block) => (
                  <ScoreCircle
                    key={block}
                    block={block}
                    value={result[`score_${block.toLowerCase()}` as keyof AssessmentResult] as number}
                  />
                ))}
                <div className="score-total">
                  <span className="total-num">{result.score_total}</span>
                  <span className="total-label">Итоговый балл</span>
                  <LevelBadge level={result.level} />
                </div>
              </div>
            </div>
          ) : (
            <div className="empty-card">
              <p>Вы ещё не проходили оценку</p>
              <Link to="/assessment" className="btn btn-primary">Начать оценку</Link>
            </div>
          )}
  
          {/* History */}
          <div className="history-section">
            <h2>История оценок</h2>
            {history.length === 0 ? (
              <p className="empty-text">Оценок пока нет</p>
            ) : (
              <table className="history-table">
                <thead>
                  <tr>
                    <th>Дата</th>
                    <th>E</th>
                    <th>S</th>
                    <th>G</th>
                    <th>Итог</th>
                    <th>Уровень</th>
                    <th />
                  </tr>
                </thead>
                <tbody>
                  {history.map((r) => (
                    <tr key={r.id}>
                      <td>{new Date(r.created_at).toLocaleDateString('ru-RU')}</td>
                      <td>{r.score_e}</td>
                      <td>{r.score_s}</td>
                      <td>{r.score_g}</td>
                      <td><strong>{r.score_total}</strong></td>
                      <td><LevelBadge level={r.level} /></td>
                      <td>
                        <button className="btn btn-outline btn-sm" onClick={() => handleDownloadPdf(r.id)}>
                          PDF
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            )}
          </div>
        </main>
      </div>
    );
  } 