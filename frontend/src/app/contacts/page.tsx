import { contentApi } from '@/lib/api';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import styles from './contacts.module.css';

export default async function ContactsPage() {
  const [contacts, branches] = await Promise.all([
    contentApi.getContacts().then(res => res.data.results?.[0] || res.data?.[0]),
    contentApi.getBranches().then(res => res.data.results || res.data),
  ]);

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

          <div className={styles.branches}>
            <h2>Наши филиалы</h2>
            <div className={styles.branchesGrid}>
              {branches.map((branch: any) => (
                <div key={branch.id} className={styles.branchCard}>
                  <h3>{branch.name}</h3>
                  <p className={styles.address}>📍 {branch.address}</p>
                  <p className={styles.metro}>🚇 {branch.metro}</p>
                  <p className={styles.phone}>{branch.phone}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

