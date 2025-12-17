/**
 * Утилиты для работы с видео
 */

/**
 * Конвертирует URL видео в embed URL для YouTube, Rutube, Vimeo, VK
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

  // VK (ВКонтакте)
  // Формат URL: https://vk.com/...?z=video-227252503_456239169 или https://vk.com/video-227252503_456239169
  const vkRegex = /video-(\d+)_(\d+)/
  const vkMatch = url.match(vkRegex)
  if (vkMatch) {
    const ownerId = vkMatch[1]
    const videoId = vkMatch[2]
    // Извлекаем hash из URL, если он есть
    const hashMatch = url.match(/hash=([a-zA-Z0-9]+)/)
    const hash = hashMatch ? hashMatch[1] : null
    
    if (hash) {
      return `https://vk.com/video_ext.php?oid=${ownerId}&id=${videoId}&hash=${hash}`
    } else {
      // Возвращаем упрощенный формат (может потребоваться дополнительная обработка)
      return `https://vk.com/video-${ownerId}_${videoId}`
    }
  }

  // Если URL уже является embed URL, возвращаем как есть
  if (url.includes('/embed/') || url.includes('/play/embed/') || url.includes('/video_ext.php')) {
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

  // VK (ВКонтакте) - извлекаем параметры для получения превью
  const vkRegex = /video-(\d+)_(\d+)/
  const vkMatch = url.match(vkRegex)
  if (vkMatch) {
    const ownerId = vkMatch[1]
    const videoId = vkMatch[2]
    // VK предоставляет превью через API, но можно попробовать использовать прямой URL
    // Формат: https://vk.com/video-{owner_id}_{video_id}
    // Для превью можно использовать: https://pp.userapi.com/c{server}/{hash}/video/{owner_id}_{video_id}.jpg
    // Но это требует дополнительных параметров, которые недоступны из обычного URL
    // Пока возвращаем null, можно добавить позже через API
    return null
  }

  return null
}

