/**
 * Утилиты для работы с видео
 */

/**
 * Конвертирует URL видео в embed URL для YouTube, Rutube, Vimeo
 */
export function convertVideoUrlToEmbed(url: string | null | undefined): string | null {
  if (!url) return null

  // YouTube
  const youtubeRegex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/
  const youtubeMatch = url.match(youtubeRegex)
  if (youtubeMatch) {
    return `https://www.youtube.com/embed/${youtubeMatch[1]}`
  }

  // Rutube
  const rutubeRegex = /rutube\.ru\/(?:video|play\/embed)\/([a-zA-Z0-9_-]+)/
  const rutubeMatch = url.match(rutubeRegex)
  if (rutubeMatch) {
    return `https://rutube.ru/play/embed/${rutubeMatch[1]}`
  }

  // Vimeo
  const vimeoRegex = /(?:vimeo\.com\/|player\.vimeo\.com\/video\/)(\d+)/
  const vimeoMatch = url.match(vimeoRegex)
  if (vimeoMatch) {
    return `https://player.vimeo.com/video/${vimeoMatch[1]}`
  }

  // Если URL уже является embed URL, возвращаем как есть
  if (url.includes('/embed/') || url.includes('/play/embed/')) {
    return url
  }

  return null
}

/**
 * Получает URL превью для видео с хостинга
 */
export function getVideoThumbnail(videoUrl: string | null | undefined, videoEmbedUrl: string | null | undefined): string | null {
  if (!videoUrl && !videoEmbedUrl) return null

  const url = videoEmbedUrl || videoUrl
  if (!url) return null

  // YouTube
  const youtubeRegex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/
  const youtubeMatch = url.match(youtubeRegex)
  if (youtubeMatch) {
    return `https://img.youtube.com/vi/${youtubeMatch[1]}/maxresdefault.jpg`
  }

  // Rutube - используем API для получения превью
  const rutubeRegex = /rutube\.ru\/(?:video|play\/embed)\/([a-zA-Z0-9_-]+)/
  const rutubeMatch = url.match(rutubeRegex)
  if (rutubeMatch) {
    // Rutube не предоставляет прямую ссылку на превью, нужно использовать API
    // Пока возвращаем null, можно добавить позже
    return null
  }

  // Vimeo - используем API для получения превью
  const vimeoRegex = /(?:vimeo\.com\/|player\.vimeo\.com\/video\/)(\d+)/
  const vimeoMatch = url.match(vimeoRegex)
  if (vimeoMatch) {
    // Vimeo требует API для получения превью
    // Пока возвращаем null, можно добавить позже
    return null
  }

  return null
}

