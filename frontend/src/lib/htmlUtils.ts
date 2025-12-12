/**
 * Утилиты для обработки HTML контента
 */

/**
 * Нормализует HTML контент, заменяя HTTP на HTTPS в ссылках и iframe
 * Также исправляет CSS для видео контейнеров, чтобы они правильно встраивались в поток
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
  
  // Исправляем контейнеры видео: добавляем display: block, clear: both и width: 100%
  // Это гарантирует, что видео правильно встраивается в поток документа
  html = html.replace(
    /<div([^>]*)\sstyle=["']([^"']*position:\s*relative[^"']*)["']([^>]*)>/gi,
    (match, before, style, after) => {
      // Проверяем, что это контейнер видео (содержит padding-bottom и height: 0)
      if (style.includes('padding-bottom') && style.includes('height: 0')) {
        // Добавляем display: block, clear: both и width: 100%, если их нет
        if (!style.includes('display:')) {
          style = style + '; display: block';
        }
        if (!style.includes('clear:')) {
          style = style + '; clear: both';
        }
        if (!style.includes('width:')) {
          style = style + '; width: 100%';
        }
        return `<div${before} style="${style}"${after}>`;
      }
      return match;
    }
  );
  
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
