import { contentApi } from '@/lib/api';
import Link from 'next/link';
import styles from './policies.module.css';

export default async function PoliciesPage() {
  const policies = await contentApi.getPrivacyPolicies()
    .then(res => res.data.results || res.data || [])
    .catch(() => []);

  if (!policies || policies.length === 0) {
    return (
      <main className={styles.main}>
        <div className={styles.container}>
          <h1>Политики</h1>
          <p>Список политик пуст.</p>
        </div>
      </main>
    );
  }

  return (
    <main className={styles.main}>
      <div className={styles.container}>
        <h1 className={styles.title}>Политики</h1>
        <div className={styles.list}>
          {policies.map((policy: any) => (
            <Link 
              key={policy.id} 
              href={`/policies/${policy.slug}`}
              className={styles.policyCard}
            >
              <h2 className={styles.policyTitle}>{policy.title}</h2>
              {policy.updated_at && (
                <p className={styles.updated}>
                  Обновлено: {new Date(policy.updated_at).toLocaleDateString('ru-RU')}
                </p>
              )}
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}

