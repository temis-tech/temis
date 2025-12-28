'use client';

import Link from 'next/link';
import { useState } from 'react';
import { normalizeImageUrl } from '@/lib/utils';
import BranchSelector from './BranchSelector';
import styles from './Header.module.css';

interface MenuItem {
  id: number;
  item_type?: 'link' | 'branch_selector';
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
  logoWidth?: number;
  logoMobileScale?: number;
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
  logoWidth = 150,
  logoMobileScale = 100,
  showMenu, 
  menuItems,
  showPhone,
  phoneText 
}: HeaderClientProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  
  // Отладка: проверяем значение logoMobileScale
  if (process.env.NODE_ENV === 'development') {
    console.log('HeaderClient logoMobileScale:', logoMobileScale);
  }

  return (
    <header className={styles.header}>
      <div className={styles.container}>
        <Link 
          href={logoUrl} 
          className={styles.logo}
          style={{ 
            '--mobile-scale': `${logoMobileScale}` 
          } as React.CSSProperties}
        >
          {logoImage && (
            <img 
              src={normalizeImageUrl(logoImage)} 
              alt={logoText} 
              className={styles.logoImage}
              style={{ 
                maxHeight: `${logoHeight}px`, 
                maxWidth: `${logoWidth}px`,
                '--mobile-scale': `${logoMobileScale}`
              } as React.CSSProperties}
            />
          )}
          {logoText && (
            <span className={styles.logoText}>{logoText}</span>
          )}
        </Link>
        <div className={styles.headerRight}>
          {showMenu && menuItems && Array.isArray(menuItems) && menuItems.length > 0 && (
          <nav className={`${styles.nav} ${isMenuOpen ? styles.navOpen : ''}`}>
            {menuItems.map((item) => {
              if (!item) return null;
              
              // Селектор филиала
              if (item.item_type === 'branch_selector') {
                return (
                  <div key={item.id} className={styles.menuBranchSelector}>
                    <BranchSelector 
                      showLabel={false}
                    />
                  </div>
                );
              }
              
              const content = item.image ? (
                <img src={normalizeImageUrl(item.image)} alt={item.title || 'Menu item'} className={styles.menuImage} />
              ) : (
                item.title || ''
              );
              
              // Если есть вложенные пункты меню
              if (item.children && item.children.length > 0) {
                return (
                  <div key={item.id} className={styles.dropdown}>
                    <span className={styles.dropdownToggle}>
                      {content}
                      <span className={styles.dropdownArrow}>▼</span>
                    </span>
                    <div className={styles.dropdownMenu}>
                      {item.children.map((child) => {
                        // Селектор филиала во вложенном меню (не рекомендуется, но поддерживается)
                        if (child.item_type === 'branch_selector') {
                          return (
                            <div key={child.id} className={styles.menuBranchSelector}>
                              <BranchSelector 
                                showLabel={false}
                              />
                            </div>
                          );
                        }
                        
                        const childContent = child.image ? (
                          <img src={normalizeImageUrl(child.image)} alt={child.title || 'Menu item'} className={styles.menuImage} />
                        ) : (
                          child.title || ''
                        );
                        
                        return child.is_external ? (
                          <a
                            key={child.id}
                            href={child.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            onClick={() => setIsMenuOpen(false)}
                            className={child.image ? styles.menuImageLink : ''}
                          >
                            {childContent}
                          </a>
                        ) : (
                          <Link
                            key={child.id}
                            href={child.url}
                            onClick={() => setIsMenuOpen(false)}
                            className={child.image ? styles.menuImageLink : ''}
                          >
                            {childContent}
                          </Link>
                        );
                      })}
                    </div>
                  </div>
                );
              }
              
              // Обычный пункт меню без вложенных
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
        </div>
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

