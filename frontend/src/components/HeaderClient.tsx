'use client';

import Link from 'next/link';
import { useState } from 'react';
import { normalizeImageUrl } from '@/lib/utils';
import styles from './Header.module.css';

interface MenuItem {
  id: number;
  title?: string;
  image?: string;
  url: string;
  is_external?: boolean;
  children?: MenuItem[];
}

interface HeaderClientProps {
  logoText: string;
  logoImage?: string;
  logoUrl: string;
  logoHeight?: number;
  showMenu: boolean;
  menuItems: MenuItem[];
  showPhone?: boolean;
  phoneText?: string;
}

export default function HeaderClient({ 
  logoText, 
  logoImage,
  logoUrl,
  logoHeight = 100,
  showMenu, 
  menuItems,
  showPhone,
  phoneText 
}: HeaderClientProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link href={logoUrl} className={styles.logo}>
          {logoImage && (
            <img 
              src={normalizeImageUrl(logoImage)} 
              alt={logoText} 
              className={styles.logoImage}
              style={{ maxHeight: `${logoHeight}px` }}
            />
          )}
          {logoText && (
            <span className={styles.logoText}>{logoText}</span>
          )}
        </Link>
        {showMenu && menuItems && Array.isArray(menuItems) && menuItems.length > 0 && (
          <nav className={`${styles.nav} ${isMenuOpen ? styles.navOpen : ''}`}>
            {menuItems.map((item) => {
              if (!item) return null;
              
              const content = item.image ? (
                <img src={normalizeImageUrl(item.image)} alt={item.title || 'Menu item'} className={styles.menuImage} />
              ) : (
                item.title || ''
              );
              
              return item.is_external ? (
                <a 
                  key={item.id} 
                  href={item.url} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  onClick={() => setIsMenuOpen(false)}
                  className={item.image ? styles.menuImageLink : ''}
                >
                  {content}
                </a>
              ) : (
                <Link 
                  key={item.id} 
                  href={item.url} 
                  onClick={() => setIsMenuOpen(false)}
                  className={item.image ? styles.menuImageLink : ''}
                >
                  {content}
                </Link>
              );
            })}
          </nav>
        )}
        {showPhone && phoneText && (
          <a href={`tel:${phoneText}`} className={styles.phone}>
            {phoneText}
          </a>
        )}
        <button 
          className={styles.menuButton}
          onClick={() => setIsMenuOpen(!isMenuOpen)}
          aria-label="Меню"
        >
          <span></span>
          <span></span>
          <span></span>
        </button>
      </div>
    </header>
  );
}

