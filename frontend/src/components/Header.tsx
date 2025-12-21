import Link from 'next/link';
import { contentApi } from '@/lib/api';
import HeaderClient from './HeaderClient';

export default async function Header() {
  const headerSettings = await contentApi.getHeaderSettings().then(res => res.data).catch((err) => {
    console.error('Error fetching header settings:', err);
    return null;
  });

  // Получаем настройки сайта для названия сайта
  const siteSettings = await contentApi.getSiteSettings().then(res => res.data).catch(() => null);
  const siteName = siteSettings?.site_name || 'Temis';

  // Получаем меню из настроек шапки (может быть выбрано конкретное меню)
  const menuItems = headerSettings?.menu?.items || [];
  const safeMenuItems = Array.isArray(menuItems) ? menuItems : [];
  
  // Отладочная информация
  if (process.env.NODE_ENV === 'development') {
    console.log('Header settings:', {
      show_menu: headerSettings?.show_menu,
      menu: headerSettings?.menu,
      menuItems: safeMenuItems.length,
    });
  }

  return (
    <>
      <HeaderClient 
        logoText={headerSettings?.logo_text || siteName}
        logoImage={headerSettings?.logo_image || undefined}
        logoUrl={headerSettings?.logo_url || '/'}
        logoHeight={headerSettings?.logo_height || 100}
        showMenu={headerSettings?.show_menu !== false}
        menuItems={safeMenuItems}
        showPhone={headerSettings?.show_phone}
        phoneText={headerSettings?.phone_text}
      />
    </>
  );
}

