import { Link } from 'react-router-dom';

export default function Terms() {
  return (
    <div className="legal-page" style={{ maxWidth: 720, margin: '0 auto', padding: '3rem 1.5rem' }}>
      <Link to="/" className="logo" style={{ display: 'inline-block', marginBottom: '2rem' }}>
        ESG<span>Campus</span>
      </Link>

      <h1>Условия использования</h1>
      <p style={{ color: 'var(--text-secondary, #666)', marginBottom: '2rem' }}>
        Последнее обновление: {new Date().toLocaleDateString('ru-RU')}
      </p>

      <section style={{ marginBottom: '1.5rem' }}>
        <h2>1. Общие положения</h2>
        <p>
          Используя платформу ESG Campus, компания-пользователь соглашается с настоящими условиями.
          Платформа предоставляет инструменты для прохождения ESG-оценки, хранения результатов
          и получения отчётов на основе предоставленных данных.
        </p>
      </section>

      <section style={{ marginBottom: '1.5rem' }}>
        <h2>2. Регистрация и аккаунт</h2>
        <p>
          Для использования платформы компания указывает достоверную информацию о себе,
          включая название, отрасль и контактный email. Ответственность за сохранность
          доступа к аккаунту несёт зарегистрировавшаяся компания.
        </p>
      </section>

      <section style={{ marginBottom: '1.5rem' }}>
        <h2>3. Использование данных анкеты</h2>
        <p>
          Ответы, предоставленные компанией при прохождении ESG-анкеты, используются
          для формирования оценки и отчёта. Компания вправе запросить удаление своих
          данных в любой момент.
        </p>
      </section>

      <section style={{ marginBottom: '1.5rem' }}>
        <h2>4. Изменения условий</h2>
        <p>
          Условия использования могут обновляться. О существенных изменениях
          пользователи будут уведомлены по email.
        </p>
      </section>

      <p style={{ marginTop: '2rem' }}>
        <Link to="/register">← Вернуться к регистрации</Link>
      </p>
    </div>
  );
}