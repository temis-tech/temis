import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import { Specialist } from '@/types';
import Image from 'next/image';
import styles from './specialists.module.css';

export default async function SpecialistsPage() {
  const specialists = await contentApi.getSpecialists().then(res => res.data.results || res.data);

  return (
    <>
      <Header />
      <main className={styles.main}>
        <div className={styles.container}>
          <h1 className={styles.title}>Педагоги логопедического центра</h1>
          <p className={styles.subtitle}>
            Развиваем чёткость произношения, связную речь и ясность мышления с помощью логопедического массажа и логопедических упражнений.
            Работаем с задержкой речевого развития, автоматизацией звуков и коммуникативными навыками. Для каждого своя программа, игра и поддержка.
          </p>
          <div className={styles.grid}>
            {specialists.map((specialist: Specialist) => (
              <div key={specialist.id} className={styles.card}>
                {specialist.photo && (
                  <div className={styles.photoWrapper}>
                    <Image
                      src={normalizeImageUrl(specialist.photo)}
                      alt={specialist.name}
                      width={200}
                      height={200}
                      className={styles.photo}
                    />
                  </div>
                )}
                <h3 className={styles.name}>{specialist.name}</h3>
                <p className={styles.position}>{specialist.position}</p>
                {specialist.branch_name && (
                  <p className={styles.branch}>📍 {specialist.branch_name}</p>
                )}
                {specialist.bio && (
                  <div className={styles.bio}>{specialist.bio}</div>
                )}
              </div>
            ))}
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}

