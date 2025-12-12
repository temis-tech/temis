import { contentApi } from '@/lib/api';
import styles from './privacy.module.css';

export default async function PrivacyPage() {
  const policy = await contentApi.getPrivacyPolicy().then(res => res.data).catch(() => null);

  if (!policy || !policy.is_published) {
    return (
      <main className={styles.main}>
        <div className={styles.container}>
          <h1>Политика конфиденциальности</h1>
          <p>Страница находится в разработке.</p>
        </div>
      </main>
    );
  }

  return (
    <main className={styles.main}>
      <article className={styles.container}>
        <h1 className={styles.title}>{policy.title}</h1>
        <div 
          className={styles.content}
          dangerouslySetInnerHTML={{ 
            __html: policy.content
              .replace(/<h2>/g, '<h2 style="font-size: 1.8rem; margin-top: 2rem; margin-bottom: 1rem; color: #333; font-weight: 600;">')
              .replace(/\n/g, '<br>')
          }}
        />
        <div className={styles.updated}>
          Последнее обновление: {new Date(policy.updated_at).toLocaleDateString('ru-RU')}
        </div>
      </article>
    </main>
  );
}

