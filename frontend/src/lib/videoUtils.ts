/**
 * Утилиты для работы с видео с внешних видеохостингов
 */

export interface VideoEmbedInfo {
  embedUrl: string;
  provider: 'youtube' | 'rutube' | 'vimeo' | 'unknown';
}

/**
 * Конвертирует URL видео в embed URL для iframe
 */
export function getVideoEmbedUrl(videoUrl: string): VideoEmbedInfo | null {
  if (!videoUrl) return null;

  // YouTube
  // Поддерживаемые форматы:
  // - https://www.youtube.com/watch?v=VIDEO_ID
  // - https://youtu.be/VIDEO_ID
  // - https://www.youtube.com/embed/VIDEO_ID
  const youtubeRegex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
  const youtubeMatch = videoUrl.match(youtubeRegex);
  if (youtubeMatch) {
    return {
      embedUrl: `https://www.youtube.com/embed/${youtubeMatch[1]}`,
      provider: 'youtube',
    };
  }

  // Rutube
  // Поддерживаемые форматы:
  // - https://rutube.ru/video/VIDEO_ID/
  // - https://rutube.ru/play/embed/VIDEO_ID
  const rutubeRegex = /rutube\.ru\/(?:video|play\/embed)\/([a-zA-Z0-9_-]+)/;
  const rutubeMatch = videoUrl.match(rutubeRegex);
  if (rutubeMatch) {
    return {
      embedUrl: `https://rutube.ru/play/embed/${rutubeMatch[1]}`,
      provider: 'rutube',
    };
  }

  // Vimeo
  // Поддерживаемые форматы:
  // - https://vimeo.com/VIDEO_ID
  // - https://player.vimeo.com/video/VIDEO_ID
  const vimeoRegex = /(?:vimeo\.com\/|player\.vimeo\.com\/video\/)(\d+)/;
  const vimeoMatch = videoUrl.match(vimeoRegex);
  if (vimeoMatch) {
    return {
      embedUrl: `https://player.vimeo.com/video/${vimeoMatch[1]}`,
      provider: 'vimeo',
    };
  }

  // Если URL уже является embed URL, возвращаем как есть
  if (videoUrl.includes('/embed/') || videoUrl.includes('/play/embed/')) {
    return {
      embedUrl: videoUrl,
      provider: videoUrl.includes('youtube') ? 'youtube' : 
                videoUrl.includes('rutube') ? 'rutube' : 
                videoUrl.includes('vimeo') ? 'vimeo' : 'unknown',
    };
  }

  return null;
}
