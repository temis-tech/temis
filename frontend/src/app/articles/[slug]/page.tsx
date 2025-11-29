import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import Image from 'next/image';
import styles from './article.module.css';

export default async function ArticlePage({ params }: { params: { slug: string } }) {
  const article = await contentApi.getArticleBySlug(params.slug).then(res => res.data);

  return (
    <>
      <Header />
      <main className={styles.main}>
        <article className={styles.container}>
          <h1 className={styles.title}>{article.title}</h1>
          {article.image && (
            <div className={styles.imageWrapper}>
              <Image
                src={normalizeImageUrl(article.image)}
                alt={article.title}
                width={800}
                height={400}
                className={styles.image}
              />
            </div>
          )}
          <div 
            className={styles.content}
            dangerouslySetInnerHTML={{ __html: article.content }}
          />
          <div className={styles.meta}>
            <span>Опубликовано: {new Date(article.created_at).toLocaleDateString('ru-RU')}</span>
            <span>👁 {article.views_count} просмотров</span>
          </div>
        </article>
      </main>
      <Footer />
    </>
  );
}

