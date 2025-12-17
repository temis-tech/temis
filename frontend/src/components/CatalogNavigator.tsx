'use client';

import { CatalogItem } from '@/types';
import Link from 'next/link';
import styles from './CatalogNavigator.module.css';

interface CatalogNavigatorProps {
  items: CatalogItem[];
  title?: string;
  className?: string;
}

export default function CatalogNavigator({ 
  items, 
  title = 'Навигация по статьям',
  className = ''
}: CatalogNavigatorProps) {
  if (!items || items.length === 0) {
    return null;
  }

  // Фильтруем только элементы, у которых есть своя страница
  const navigableItems = items.filter(item => item.has_own_page && item.url);

  if (navigableItems.length === 0) {
    return null;
  }

  return (
    <nav className={`${styles.container} ${className}`}>
      {title && (
        <h2 className={styles.title}>{title}</h2>
      )}
      <ul className={styles.list}>
        {navigableItems.map((item) => (
          <li key={item.id} className={styles.item}>
            <Link href={item.url} className={styles.link}>
              {item.title}
            </Link>
          </li>
        ))}
      </ul>
    </nav>
  );
}
