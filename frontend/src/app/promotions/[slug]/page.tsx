import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import Image from 'next/image';
import styles from './promotion.module.css';

export default async function PromotionPage({ params }: { params: { slug: string } }) {
  const promotion = await contentApi.getPromotionBySlug(params.slug).then(res => res.data);

  return (
    <>
      <Header />
      <main className={styles.main}>
        <article className={styles.container}>
          <h1 className={styles.title}>{promotion.title}</h1>
          {promotion.image && (
            <div className={styles.imageWrapper}>
              <Image
                src={normalizeImageUrl(promotion.image)}
                alt={promotion.title}
                width={800}
                height={400}
                className={styles.image}
              />
            </div>
          )}
          <div 
            className={styles.content}
            dangerouslySetInnerHTML={{ __html: promotion.description }}
          />
          {promotion.start_date && promotion.end_date && (
            <div className={styles.dates}>
              <p>Действует с {new Date(promotion.start_date).toLocaleDateString('ru-RU')} 
                 по {new Date(promotion.end_date).toLocaleDateString('ru-RU')}</p>
            </div>
          )}
        </article>
      </main>
      <Footer />
    </>
  );
}

