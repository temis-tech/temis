import Link from 'next/link';
import { contentApi } from '@/lib/api';
import HeaderClient from './HeaderClient';

export default async function Header() {
  const [headerSettings, menuItems] = await Promise.all([
    contentApi.getHeaderSettings().then(res => res.data).catch(() => null),
    contentApi.getMenu().then(res => res.data.results || res.data || []).catch(() => []),
  ]);

  // Убеждаемся, что menuItems - это массив
  const safeMenuItems = Array.isArray(menuItems) ? menuItems : [];

  const headerHeight = headerSettings?.header_height || 140;
  const mobileHeaderHeight = Math.min(headerHeight * 0.85, 120);

  return (
    <>
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

