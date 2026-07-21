import { Link } from 'react-router-dom';

export default function Privacy() {
  return (
    <div className="legal-page" style={{ maxWidth: 720, margin: '0 auto', padding: '3rem 1.5rem' }}>
      <Link to="/" className="logo" style={{ display: 'inline-block', marginBottom: '2rem' }}>
        ESG<span>Campus</span>
      </Link>

      <h1>Политика конфиденциальности</h1>
      <p style={{ color: 'var(--text-secondary, #666)', marginBottom: '2rem' }}>
        Последнее обновление: {new Date().toLocaleDateString('ru-RU')}
      </p>

      <section style={{ marginBottom: '1.5rem' }}>
        <h2>1. Какие данные мы собираем</h2>
        <p>
          При регистрации мы собираем название компании, отрасль, под-отрасль, email
          и пароль (хранится в зашифрованном виде). При прохождении ESG-анкеты
          сохраняются ответы на вопросы опросника.
        </p>
      </section>

      <section style={{ marginBottom: '1.5rem' }}>
        <h2>2. Как используются данные</h2>
        <p>
          Данные используются для формирования ESG-оценки компании, генерации отчётов
          и поддержания работы аккаунта. Данные не передаются третьим лицам без
          согласия компании, за исключением случаев, предусмотренных законом.
        </p>
      </section>

      <section style={{ marginBottom: '1.5rem' }}>
        <h2>3. Хранение данных</h2>
        <p>
          Данные хранятся на защищённых серверах и доступны только авторизованным
          сотрудникам платформы для целей технической поддержки и разработки.
        </p>
      </section>

      <section style={{ marginBottom: '1.5rem' }}>
        <h2>4. Права компании</h2>
        <p>
          Компания вправе запросить экспорт, изменение или полное удаление своих данных,
          обратившись в поддержку платформы.
        </p>
      </section>

      <p style={{ marginTop: '2rem' }}>
        <Link to="/register">← Вернуться к регистрации</Link>
      </p>
    </div>
  );
}