import { contentApi } from '@/lib/api';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import ContentPage from '@/components/ContentPage';
import styles from './contacts.module.css';

export default async function ContactsPage() {
  // Пытаемся найти страницу контактов через конструктор
  let contactsPage = null;
  try {
    const response = await contentApi.getContentPageBySlug('contacts').catch(() => null);
    if (response?.data) {
      contactsPage = response.data;
    }
  } catch (error) {
    // Игнорируем ошибку
  }

  const contacts = await contentApi.getContacts().then(res => res.data.results?.[0] || res.data?.[0]).catch(() => null);

  // Если есть страница контактов через конструктор, используем её
  if (contactsPage) {
    return (
      <>
        <Header />
        <main className={styles.main}>
          <ContentPage page={contactsPage} />
        </main>
        <Footer />
      </>
    );
  }

  // Иначе показываем простую страницу с контактами
  return (
    <>
      <Header />
      <main className={styles.main}>
        <div className={styles.container}>
          <h1 className={styles.title}>Контакты</h1>
          
          {contacts && (
            <div className={styles.contacts}>
              <div className={styles.contactCard}>
                <h2>Телефоны</h2>
                <p className={styles.phone}>{contacts.phone}</p>
                {contacts.phone_secondary && (
                  <p className={styles.phone}>{contacts.phone_secondary}</p>
                )}
                {contacts.email && (
                  <p className={styles.email}>📧 {contacts.email}</p>
                )}
                {contacts.inn && (
                  <p className={styles.inn}>ИНН: {contacts.inn}</p>
                )}
              </div>
            </div>
          )}

          <p style={{ marginTop: '2rem', color: '#666' }}>
            Создайте страницу контактов через конструктор страниц в админке для более гибкой настройки.
          </p>
        </div>
      </main>
      <Footer />
    </>
  );
}

