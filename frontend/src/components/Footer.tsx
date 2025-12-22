import { contentApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import styles from './Footer.module.css';
import Link from 'next/link';
import { MenuItem } from '@/types';

export default async function Footer() {
  let contacts = null;
  let footerSettings = null;
  
  try {
    [contacts, footerSettings] = await Promise.all([
      contentApi.getContacts().then(res => res.data.results?.[0] || res.data?.[0]).catch(() => null),
      contentApi.getFooterSettings().then(res => res.data).catch(() => null),
    ]);
  } catch (error) {
    console.error('Error loading footer data:', error);
    // При ошибке не показываем футер, чтобы не показывать старые данные
    return null;
  }

  // Если нет настроек, не показываем футер
  if (!footerSettings && !contacts) {
    return null;
  }

  // Получаем меню из настроек футера
  const menuItems = footerSettings?.menu?.items || [];
  
  // Фильтруем меню, убирая пункты со старыми данными
  const filteredMenuItems = Array.isArray(menuItems) ? menuItems.filter((item: MenuItem) => {
    if (!item) return false;
    const title = item.title || '';
    // Убираем пункты меню, которые содержат упоминания логопедии
    if (title && (title.includes('Логопед') || title.includes('логопед') || title.includes('Логопеды'))) {
      return false;
    }
    return true;
  }) : [];

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
          {footerSettings?.show_navigation && filteredMenuItems && filteredMenuItems.length > 0 && (
            <div className={styles.section}>
              <h3>Навигация</h3>
              {filteredMenuItems.map((item: MenuItem) => {
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
          {footerSettings?.show_social && footerSettings?.social_networks && footerSettings.social_networks.length > 0 && (
            <div className={styles.section}>
              <h3>Социальные сети</h3>
              <div className={styles.socialNetworks}>
                {footerSettings.social_networks.map((network: any) => (
                  <a
                    key={network.id}
                    href={network.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className={styles.socialLink}
                    title={network.name}
                  >
                    {network.icon ? (
                      <img src={normalizeImageUrl(network.icon)} alt={network.name} className={styles.socialIcon} />
                    ) : (
                      <span className={styles.socialIconText}>{network.name}</span>
                    )}
                  </a>
                ))}
              </div>
            </div>
          )}
        </div>
        <div className={styles.copyright}>
          <p>{footerSettings?.copyright_text || '© 2024. Все права защищены'}</p>
          <Link href="/policies">Политики</Link>
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

