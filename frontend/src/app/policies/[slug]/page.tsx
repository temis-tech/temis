import { contentApi } from '@/lib/api';
import Link from 'next/link';
import styles from '../policies.module.css';
import { notFound } from 'next/navigation';

export default async function PolicyDetailPage({ params }: { params: { slug: string } }) {
  const policy = await contentApi.getPrivacyPolicyBySlug(params.slug)
    .then(res => res.data)
    .catch(() => null);

  if (!policy || !policy.is_published) {
    notFound();
  }

  return (
    <main className={styles.main}>
      <article className={styles.container}>
        <Link href="/policies" className={styles.backLink}>
          ← Назад к списку политик
        </Link>
        <h1 className={styles.detailTitle}>{policy.title}</h1>
        <div 
          className={styles.content}
          dangerouslySetInnerHTML={{ 
            __html: policy.content
              .replace(/<h2>/g, '<h2 style="font-size: 1.8rem; margin-top: 2rem; margin-bottom: 1rem; color: #333; font-weight: 600;">')
              .replace(/\n/g, '<br>')
          }}
        />
        {policy.updated_at && (
          <div className={styles.updated}>
            Последнее обновление: {new Date(policy.updated_at).toLocaleDateString('ru-RU')}
          </div>
        )}
      </article>
    </main>
  );
}

