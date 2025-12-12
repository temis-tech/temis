import Link from 'next/link';
import { contentApi } from '@/lib/api';
import HeaderClient from './HeaderClient';

export default async function Header() {
  const headerSettings = await contentApi.getHeaderSettings().then(res => res.data).catch((err) => {
    console.error('Error fetching header settings:', err);
    return null;
  });

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

  // CSS переменная теперь устанавливается в layout.tsx глобально
  // Оставляем здесь только для обратной совместимости, если layout не загрузился
  const headerHeight = headerSettings?.header_height || 140;
  const mobileHeaderHeight = Math.min(headerHeight * 0.85, 120);

  return (
    <>
      {/* Дублируем установку переменной на случай, если layout не загрузился */}
      <style dangerouslySetInnerHTML={{
        __html: `
          :root {
            --header-height: ${headerHeight}px;
          }
          @media (max-width: 768px) {
            :root {
              --header-height: ${mobileHeaderHeight}px;
            }
          }
        `
      }} />
      <HeaderClient 
        logoText={headerSettings?.logo_text || 'Радуга слов'}
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

