import { contentApi } from '@/lib/api';
import ContentPage from '@/components/ContentPage';
import Image from 'next/image';
import { normalizeImageUrl } from '@/lib/utils';
import { Branch } from '@/types';
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
  const branches = await contentApi.getBranches().then(res => res.data.results || res.data || []).catch(() => []) as Branch[];

  // Если есть страница контактов через конструктор, используем её
  if (contactsPage) {
    return (
      <main className={styles.main}>
        <ContentPage page={contactsPage} />
        {/* Показываем филиалы даже если есть страница через конструктор */}
        {branches.length > 0 && (
          <div className={styles.branches}>
            <h2>Наши филиалы</h2>
            <div className={styles.branchesGrid}>
              {branches.map((branch) => (
                <div key={branch.id} className={styles.branchCard}>
                  {branch.image && (
                    <div className={styles.branchImage}>
                      <Image
                        src={normalizeImageUrl(branch.image)}
                        alt={branch.name}
                        width={300}
                        height={200}
                        style={{ objectFit: 'cover', borderRadius: '8px' }}
                      />
                    </div>
                  )}
                  <h3>{branch.name}</h3>
                  <p className={styles.metro}>🚇 {branch.metro}</p>
                  <p className={styles.address}>📍 {branch.address}</p>
                  <p className={styles.phone}>📞 {branch.phone}</p>
                </div>
              ))}
            </div>
          </div>
        )}
      </main>
    );
  }

  // Иначе показываем простую страницу с контактами
  return (
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

        {/* Филиалы */}
        {branches.length > 0 && (
          <div className={styles.branches}>
            <h2>Наши филиалы</h2>
            <div className={styles.branchesGrid}>
              {branches.map((branch) => (
                <div key={branch.id} className={styles.branchCard}>
                  {branch.image && (
                    <div className={styles.branchImage}>
                      <Image
                        src={normalizeImageUrl(branch.image)}
                        alt={branch.name}
                        width={300}
                        height={200}
                        style={{ objectFit: 'cover', borderRadius: '8px', marginBottom: '1rem' }}
                      />
                    </div>
                  )}
                  <h3>{branch.name}</h3>
                  <p className={styles.metro}>🚇 {branch.metro}</p>
                  <p className={styles.address}>📍 {branch.address}</p>
                  <p className={styles.phone}>📞 {branch.phone}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {branches.length === 0 && (
          <p style={{ marginTop: '2rem', color: '#666' }}>
            Создайте страницу контактов через конструктор страниц в админке для более гибкой настройки.
          </p>
        )}
      </div>
    </main>
  );
}

