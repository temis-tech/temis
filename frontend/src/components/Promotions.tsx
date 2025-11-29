import { Promotion } from '@/types';
import { normalizeImageUrl } from '@/lib/utils';
import styles from './Promotions.module.css';
import Image from 'next/image';
import Link from 'next/link';

interface PromotionsProps {
  promotions: Promotion[];
}

export default function Promotions({ promotions }: PromotionsProps) {
  if (promotions.length === 0) return null;

  return (
    <section className={styles.promotions} id="promotions">
      <div className={styles.container}>
        <h2 className={styles.title}>Акции логопедического центра</h2>
        <div className={styles.grid}>
          {promotions.map((promotion) => (
            <Link key={promotion.id} href={`/promotions/${promotion.slug}`} className={styles.card}>
              {promotion.image && (
                <div className={styles.imageWrapper}>
                  <Image
                    src={normalizeImageUrl(promotion.image)}
                    alt={promotion.title}
                    width={400}
                    height={300}
                    className={styles.image}
                  />
                </div>
              )}
              <h3 className={styles.cardTitle}>{promotion.title}</h3>
              <p className={styles.cardDescription}>
                {promotion.description.substring(0, 150)}...
              </p>
            </Link>
          ))}
        </div>
      </div>
    </section>
  );
}

