'use client';

import { Branch } from '@/types';
import { normalizeImageUrl } from '@/lib/utils';
import Image from 'next/image';
import Link from 'next/link';
import styles from './BranchesList.module.css';

interface BranchesListProps {
  branches: Branch[];
  title?: string;
  showTitle?: boolean;
  className?: string;
}

export default function BranchesList({ 
  branches, 
  title = 'Наши филиалы',
  showTitle = true,
  className = '' 
}: BranchesListProps) {
  if (!branches || branches.length === 0) {
    return null;
  }

  return (
    <div className={`${styles.container} ${className}`}>
      {showTitle && title && (
        <h2 className={styles.title}>{title}</h2>
      )}
      <div className={styles.grid}>
        {branches.map((branch) => (
          <div key={branch.id} className={styles.card}>
            {branch.image && (
              <div className={styles.imageWrapper}>
                <Image
                  src={normalizeImageUrl(branch.image)}
                  alt={branch.name}
                  width={400}
                  height={250}
                  className={styles.image}
                  style={{ objectFit: 'cover', borderRadius: '8px' }}
                />
              </div>
            )}
            <div className={styles.content}>
              <h3 className={styles.name}>{branch.name}</h3>
              {branch.metro && (
                <p className={styles.metro}>🚇 {branch.metro}</p>
              )}
              {branch.address && (
                <p className={styles.address}>📍 {branch.address}</p>
              )}
              {branch.phone && (
                <a href={`tel:${branch.phone}`} className={styles.phone}>
                  📞 {branch.phone}
                </a>
              )}
              {branch.content_page && typeof branch.content_page === 'object' && branch.content_page.slug && (
                <Link href={`/${branch.content_page.slug}/`} className={styles.link}>
                  Подробнее →
                </Link>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
