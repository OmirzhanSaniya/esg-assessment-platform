import { useState } from 'react';
import { Link } from 'react-router-dom';

const BLOCKS = ['E', 'S', 'G'] as const;
type Block = (typeof BLOCKS)[number];

const BLOCK_LABELS: Record<Block, string> = {
  E: 'Environmental',
  S: 'Social',
  G: 'Governance',
};

const BLOCK_SUBTITLES: Record<Block, string> = {
  E: 'Экологический след и воздействие на окружающую среду',
  S: 'Отношения с сотрудниками, клиентами и обществом',
  G: 'Корпоративное управление, прозрачность и этика',
};

type QuestionType = 'yes_no' | 'single_choice' | 'scale' | 'percentage';

interface Question {
  id: number;
  text: string;
  block: Block;
  type: QuestionType;
  order: number;
  is_controversy?: boolean;
  severity?: 1 | 2 | 3 | 4;
}

const MOCK_QUESTIONS: Question[] = [
  { id: 1, text: 'Есть ли в компании политика управления отходами?', block: 'E', type: 'yes_no', order: 1 },
  { id: 2, text: 'Как часто проводится экологический аудит?', block: 'E', type: 'single_choice', order: 2 },
  { id: 3, text: 'Оцените уровень экологической ответственности компании', block: 'E', type: 'scale', order: 3 },
  { id: 4, text: 'Измеряете ли вы углеродный след компании?', block: 'E', type: 'yes_no', order: 4 },
  { id: 5, text: 'Есть ли программа обучения и развития персонала?', block: 'S', type: 'yes_no', order: 1 },
  { id: 6, text: 'Как часто проводятся корпоративные мероприятия?', block: 'S', type: 'single_choice', order: 2 },
  { id: 7, text: 'Оцените уровень социальной ответственности компании', block: 'S', type: 'scale', order: 3 },
  { id: 8, text: 'Есть ли политика равных возможностей для сотрудников?', block: 'S', type: 'yes_no', order: 4 },
  { id: 9, text: 'Есть ли антикоррупционная политика?', block: 'G', type: 'yes_no', order: 1 },
  { id: 10, text: 'Как часто проводится аудит корпоративного управления?', block: 'G', type: 'single_choice', order: 2 },
  { id: 11, text: 'Оцените уровень прозрачности управления компанией', block: 'G', type: 'scale', order: 3 },
  { id: 12, text: 'Публикуете ли вы отчёты о деятельности компании?', block: 'G', type: 'yes_no', order: 4 },
  { id: 13, text: 'Какая доля выручки от «зелёных» продуктов?', block: 'E', type: 'percentage', order: 5 },

];

const YES_NO_OPTIONS = [
  { label: 'Да', value: 3 },
  { label: 'Нет', value: 0 },
];

const FREQUENCY_OPTIONS = [
  { label: 'Никогда', value: 0 },
  { label: 'Иногда', value: 1 },
  { label: 'Регулярно', value: 2 },
  { label: 'Всегда', value: 3 },
];

const SCALE_VALUES = [1, 2, 3, 4, 5];

const SEVERITY_CLASS: Record<number, string> = {
  1: 'sev-1',
  2: 'sev-2',
  3: 'sev-3',
  4: 'sev-4',
};

const SEVERITY_LABEL: Record<number, string> = {
  1: 'Низкий риск',
  2: 'Средний риск',
  3: 'Высокий риск',
  4: 'Критический риск',
};

export default function Assessment() {
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number>>({});

  const currentBlock = BLOCKS[step];
  const blockQuestions = MOCK_QUESTIONS.filter((q) => q.block === currentBlock);
  const answeredInBlock = blockQuestions.filter((q) => answers[q.id] !== undefined).length;
  const allAnswered = answeredInBlock === blockQuestions.length;
  const progressPct = Math.round((Object.keys(answers).length / MOCK_QUESTIONS.length) * 100);

  const handleAnswer = (id: number, value: number) => {
    setAnswers((prev) => ({ ...prev, [id]: value }));
  };

  const handleNext = () => allAnswered && step < 2 && setStep(step + 1);
  const handleBack = () => step > 0 && setStep(step - 1);
  const handleSubmit = () => alert('Готово! Ждём бэкенд для отправки результатов.');

  return (
    <div className="assessment-page">
      <nav className="assessment-nav">
        <Link to="/" className="logo">
          ESG<span>Campus</span>
        </Link>
        <span className="progress-text">ESG-анкета</span>
        <Link to="/" className="assessment-back">Выйти</Link>
      </nav>

      <main className="assessment-main">
        {/* Progress */}
        <div className="progress-wrap">
          <div className="progress-steps">
            {BLOCKS.map((block, i) => (
              <div
                key={block}
                className={`progress-step ${i < step ? 'done' : ''} ${i === step ? 'active' : ''}`}
              >
                <div className="step-dot">{i < step ? '✓' : i + 1}</div>
                <span className="step-dot-label">{BLOCK_LABELS[block]}</span>
              </div>
            ))}
          </div>

          <div className="progress-bar-wrap">
            <div className="progress-bar-fill" style={{ width: `${progressPct}%` }} />
          </div>

          <div className="progress-info">
            <span className="progress-text">
              Шаг {step + 1} из 3 — {BLOCK_LABELS[currentBlock]}
            </span>
            <span className="progress-pct">{progressPct}%</span>
          </div>
        </div>

        {/* Questions */}
        <div className="questions-card">
          <div className="questions-card-header">
            <div className={`block-badge ${currentBlock}`}>{currentBlock}</div>
            <div className="block-header-text">
              <h2>{BLOCK_LABELS[currentBlock]}</h2>
              <p>{BLOCK_SUBTITLES[currentBlock]}</p>
            </div>
          </div>

          <div className="questions-list">
          {blockQuestions.map((q, idx) => {
              const isFlag = !!q.is_controversy;
              const severityClass = isFlag && q.severity ? SEVERITY_CLASS[q.severity] : '';

              return (
                <div key={q.id} className={`question-item ${isFlag ? `is-flag ${severityClass}` : ''}`}>
                <div>
                  {isFlag && (
                    <span className={`flag-badge ${severityClass}`}>
                      <span className="flag-badge-icon">⚠️</span>
                      {q.severity ? SEVERITY_LABEL[q.severity] : 'Красный флаг'}
                    </span>
                  )}
                  <span className="question-num">Вопрос {idx + 1}</span>
                </div>
                <p className="question-text">{q.text}</p>

                {q.type === 'yes_no' && (
                  <div className="options-row">
                    {YES_NO_OPTIONS.map((opt) => (
                      <button
                        key={opt.value}
                        className={`option-btn ${answers[q.id] === opt.value ? 'selected' : ''}`}
                        onClick={() => handleAnswer(q.id, opt.value)}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                )}

                {q.type === 'single_choice' && (
                  <div className="options-row">
                    {FREQUENCY_OPTIONS.map((opt) => (
                      <button
                        key={opt.value}
                        className={`option-btn ${answers[q.id] === opt.value ? 'selected' : ''}`}
                        onClick={() => handleAnswer(q.id, opt.value)}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                )}

{q.type === 'scale' && (
                  <div>
                    <div className="scale-row">
                      {SCALE_VALUES.map((v) => (
                        <button
                          key={v}
                          className={`scale-btn ${answers[q.id] === v ? 'selected' : ''}`}
                          onClick={() => handleAnswer(q.id, v)}
                        >
                          {v}
                        </button>
                      ))}
                    </div>
                    <div className="scale-labels">
                      <span>Низкий</span>
                      <span>Высокий</span>
                    </div>
                  </div>
                )}

                {q.type === 'percentage' && (
                  <div className="percentage-input-wrap">
                    <input
                      type="number"
                      min={0}
                      max={100}
                      value={answers[q.id] ?? ''}
                      onChange={(e) => {
                        const raw = Number(e.target.value);
                        const clamped = Math.max(0, Math.min(100, raw));
                        handleAnswer(q.id, clamped);
                      }}
                      className="percentage-input"
                    />
                    <span className="percentage-sign">%</span>
                  </div>
                )}
              </div>
              );
              })}
            
          </div>

          <div className="assessment-footer">
            <div>
              {step > 0 && (
                <button className="btn btn-outline btn-sm" onClick={handleBack}>
                  ← Назад
                </button>
              )}
            </div>

            <span className="progress-text">
              {answeredInBlock} / {blockQuestions.length} отвечено
            </span>

            {step < 2 ? (
              <button className="btn btn-primary btn-sm" onClick={handleNext} disabled={!allAnswered}>
                Далее →
              </button>
            ) : (
              <button className="btn btn-primary btn-sm" onClick={handleSubmit} disabled={!allAnswered}>
                Получить результат →
              </button>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}