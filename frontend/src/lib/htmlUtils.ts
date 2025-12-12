/**
 * Утилиты для обработки HTML контента
 */

/**
 * Нормализует HTML контент, заменяя HTTP на HTTPS в ссылках и iframe
 */
export function normalizeHtmlContent(html: string | null | undefined): string {
  if (!html) return '';
  
  // Заменяем http:// на https:// в src атрибутах (iframe, img, video и т.д.)
  html = html.replace(/src=["']http:\/\//gi, 'src="https://');
  html = html.replace(/src=["']http:\/\//gi, "src='https://");
  
  // Заменяем http:// на https:// в href атрибутах
  html = html.replace(/href=["']http:\/\//gi, 'href="https://');
  html = html.replace(/href=["']http:\/\//gi, "href='https://");
  
  // Заменяем http:// на https:// в URL внутри стилей
  html = html.replace(/url\(["']?http:\/\//gi, "url('https://");
  html = html.replace(/url\(["']?http:\/\//gi, 'url("https://');
  
  // Убираем sandbox атрибуты из iframe, если они блокируют скрипты
  // Или заменяем на sandbox с разрешением скриптов
  html = html.replace(
    /<iframe([^>]*)\ssandbox=["']([^"']*)["']([^>]*)>/gi,
    (match, before, sandbox, after) => {
      // Если sandbox не содержит allow-scripts, добавляем его
      if (!sandbox.includes('allow-scripts')) {
        const newSandbox = sandbox ? `${sandbox} allow-scripts` : 'allow-scripts';
        return `<iframe${before} sandbox="${newSandbox}"${after}>`;
      }
      return match;
    }
  );
  
  return html;
}
