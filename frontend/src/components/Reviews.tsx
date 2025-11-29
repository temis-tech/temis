import { Review } from '@/types';
import { normalizeImageUrl } from '@/lib/utils';
import styles from './Reviews.module.css';
import Image from 'next/image';

interface ReviewsProps {
  reviews: Review[];
}

export default function Reviews({ reviews }: ReviewsProps) {
  return (
    <section className={styles.reviews} id="reviews">
      <div className={styles.container}>
        <h2 className={styles.title}>Отзывы</h2>
        <div className={styles.grid}>
          {reviews.map((review) => (
            <div key={review.id} className={styles.card}>
              {review.author_photo && (
                <div className={styles.photoWrapper}>
                  <Image
                    src={normalizeImageUrl(review.author_photo)}
                    alt={review.author_name}
                    width={80}
                    height={80}
                    className={styles.photo}
                  />
                </div>
              )}
              <h3 className={styles.authorName}>{review.author_name}</h3>
              <div className={styles.rating}>
                {'⭐'.repeat(review.rating)}
              </div>
              <p className={styles.text}>{review.text}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

