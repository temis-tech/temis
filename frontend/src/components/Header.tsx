import Link from 'next/link';
import { contentApi } from '@/lib/api';
import HeaderClient from './HeaderClient';

export default async function Header() {
  let headerSettings = null;
  let siteSettings = null;
  
  try {
    headerSettings = await contentApi.getHeaderSettings().then(res => res.data).catch((err) => {
      console.error('Error fetching header settings:', err);
      return null;
    });

    // Получаем настройки сайта для названия сайта
    siteSettings = await contentApi.getSiteSettings().then(res => res.data).catch(() => null);
  } catch (error) {
    console.error('Error loading header data:', error);
    // При ошибке не показываем ничего, чтобы не показывать старые данные
    return null;
  }

  // Если нет настроек, не показываем шапку
  // Это предотвратит показ старых данных при падении бэкенда
  if (!headerSettings && !siteSettings) {
    return null;
  }

  // Если есть ошибка при загрузке, не показываем шапку
  const siteName = siteSettings?.site_name || 'Temis';
  
  // Если siteName все еще "Радуга слов" (старое значение по умолчанию), не показываем
  if (siteName && (siteName === 'Радуга слов' || siteName.includes('Радуга') || siteName.includes('радуга'))) {
    return null;
  }

  // Получаем меню из настроек шапки (может быть выбрано конкретное меню)
  const menuItems = headerSettings?.menu?.items || [];
  const safeMenuItems = Array.isArray(menuItems) ? menuItems : [];
  
  // Фильтруем меню, убирая пункты со старыми данными
  const filteredMenuItems = safeMenuItems.filter((item: any) => {
    if (!item) return false;
    const title = item.title || '';
    // Убираем пункты меню, которые содержат упоминания логопедии
    if (title.includes('Логопед') || title.includes('логопед') || title.includes('Логопеды')) {
      return false;
    }
    return true;
  });
  
  // Отладочная информация
  if (process.env.NODE_ENV === 'development') {
    console.log('Header settings:', {
      show_menu: headerSettings?.show_menu,
      menu: headerSettings?.menu,
      menuItems: filteredMenuItems.length,
    });
  }

  // Проверяем logoText на старые данные
  const logoText = headerSettings?.logo_text || siteName;
  if (logoText && (logoText.includes('Радуга слов') || logoText.includes('радуга'))) {
    // Если в логотипе старые данные, используем только siteName (если он валиден)
    const cleanLogoText = siteName && siteName !== 'Радуга слов' && !siteName.includes('Радуга') ? siteName : 'Temis';
    return (
      <>
        <HeaderClient 
          logoText={cleanLogoText}
          logoImage={headerSettings?.logo_image || undefined}
          logoUrl={headerSettings?.logo_url || '/'}
          logoHeight={headerSettings?.logo_height || 100}
          logoWidth={headerSettings?.logo_width || 150}
          showMenu={false} // Не показываем меню, если есть подозрение на старые данные
          menuItems={[]}
          showPhone={headerSettings?.show_phone}
          phoneText={headerSettings?.phone_text}
        />
      </>
    );
  }

  return (
    <>
      <HeaderClient 
        logoText={logoText}
        logoImage={headerSettings?.logo_image || undefined}
        logoUrl={headerSettings?.logo_url || '/'}
        logoHeight={headerSettings?.logo_height || 100}
        logoWidth={headerSettings?.logo_width || 150}
        showMenu={headerSettings?.show_menu !== false}
        menuItems={filteredMenuItems}
        showPhone={headerSettings?.show_phone}
        phoneText={headerSettings?.phone_text}
      />
    </>
  );
}

