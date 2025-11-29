import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Article } from '@/types';
import Link from 'next/link';
import Image from 'next/image';
import styles from './articles.module.css';

export default async function ArticlesPage() {
  const articles = await contentApi.getArticles().then(res => res.data.results || res.data);

  return (
    <>
      <Header />
      <main>
        <div className={styles.container}>
          <h1 className={styles.title}>Статьи</h1>
          <div className={styles.grid}>
            {articles.map((article: Article) => (
              <Link key={article.id} href={`/articles/${article.slug}`} className={styles.card}>
                {article.image && (
                  <div className={styles.imageWrapper}>
                    <Image
                      src={normalizeImageUrl(article.image)}
                      alt={article.title}
                      width={400}
                      height={250}
                      className={styles.image}
                    />
                  </div>
                )}
                <h3 className={styles.cardTitle}>{article.title}</h3>
                {article.short_description && (
                  <p className={styles.cardDescription}>{article.short_description}</p>
                )}
                <div className={styles.meta}>
                  <span>{new Date(article.created_at).toLocaleDateString('ru-RU')}</span>
                  <span>👁 {article.views_count}</span>
                </div>
              </Link>
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

