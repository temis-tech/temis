import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import styles from './Footer.module.css';
import Link from 'next/link';
import { MenuItem } from '@/types';

export default async function Footer() {
  const [contacts, footerSettings, menuItems] = await Promise.all([
    contentApi.getContacts().then(res => res.data.results?.[0] || res.data?.[0]).catch(() => null),
    contentApi.getFooterSettings().then(res => res.data).catch(() => null),
    contentApi.getMenu().then(res => res.data.results || res.data || []).catch(() => []),
  ]);

  return (
    <footer className={styles.footer}>
      <div className={styles.container}>
        <div className={styles.content}>
          {footerSettings?.show_contacts && contacts && (
            <div className={styles.section}>
              <h3>Контакты</h3>
              <p>{contacts.phone}</p>
              {contacts.phone_secondary && <p>{contacts.phone_secondary}</p>}
              {contacts.email && <p>{contacts.email}</p>}
              {contacts.inn && <p>ИНН: {contacts.inn}</p>}
            </div>
          )}
          {footerSettings?.show_navigation && menuItems && Array.isArray(menuItems) && menuItems.length > 0 && (
            <div className={styles.section}>
              <h3>Навигация</h3>
              {menuItems.map((item: MenuItem) => {
                const content = item.image ? (
                  <img src={normalizeImageUrl(item.image)} alt={item.title || 'Menu item'} style={{ maxHeight: '30px' }} />
                ) : (
                  item.title || ''
                );
                
                return item.is_external ? (
                  <a key={item.id} href={item.url} target="_blank" rel="noopener noreferrer">
                    {content}
                  </a>
                ) : (
                  <Link key={item.id} href={item.url}>
                    {content}
                  </Link>
                );
              })}
            </div>
          )}
        </div>
        <div className={styles.copyright}>
          <p>{footerSettings?.copyright_text || '© 2024. Все права защищены'}</p>
          <Link href="/privacy">Политика конфиденциальности</Link>
        </div>
        {footerSettings?.additional_text && (
          <div className={styles.additionalText}>
            {footerSettings.additional_text}
          </div>
        )}
      </div>
    </footer>
  );
}

