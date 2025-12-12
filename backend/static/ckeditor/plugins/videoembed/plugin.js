/**
 * CKEditor Video Embed Plugin
 * Позволяет вставлять видео с YouTube, Rutube, Vimeo и других видеохостингов
 */

(function() {
    CKEDITOR.plugins.add('videoembed', {
        icons: 'videoembed',
        init: function(editor) {
            // Добавляем команду для вставки видео
            editor.addCommand('insertVideo', {
                exec: function(editor) {
                    var url = prompt('Вставьте ссылку на видео (YouTube, Rutube, Vimeo):', '');
                    if (url) {
                        var embedUrl = convertVideoUrlToEmbed(url);
                        if (embedUrl) {
                            var width = prompt('Ширина видео (px):', '800');
                            var height = prompt('Высота видео (px):', '450');
                            
                            width = width || '800';
                            height = height || '450';
                            
                            var aspectRatio = (parseInt(height) / parseInt(width)) * 100;
                            
                            // Убеждаемся, что embedUrl использует HTTPS
                            if (embedUrl.startsWith('http://')) {
                                embedUrl = embedUrl.replace('http://', 'https://');
                            }
                            
                            var html = '<div style="position: relative; padding-bottom: ' + aspectRatio + '%; height: 0; overflow: hidden; max-width: 100%; margin: 1rem 0;">' +
                                      '<iframe src="' + embedUrl + '" ' +
                                      'style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border: none;" ' +
                                      'allowfullscreen ' +
                                      'allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" ' +
                                      'frameborder="0" ' +
                                      'loading="lazy"></iframe>' +
                                      '</div>';
                            
                            editor.insertHtml(html);
                        } else {
                            alert('Не удалось распознать URL видео. Поддерживаются YouTube, Rutube и Vimeo.');
                        }
                    }
                }
            });
            
            // Добавляем кнопку в тулбар
            editor.ui.addButton('VideoEmbed', {
                label: 'Вставить видео',
                command: 'insertVideo',
                toolbar: 'insert'
            });
        }
    });
    
    /**
     * Конвертирует URL видео в embed URL
     */
    function convertVideoUrlToEmbed(url) {
        if (!url) return null;
        
        // YouTube
        var youtubeRegex = /(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/;
        var youtubeMatch = url.match(youtubeRegex);
        if (youtubeMatch) {
            return 'https://www.youtube.com/embed/' + youtubeMatch[1];
        }
        
        // Rutube
        var rutubeRegex = /rutube\.ru\/(?:video|play\/embed)\/([a-zA-Z0-9_-]+)/;
        var rutubeMatch = url.match(rutubeRegex);
        if (rutubeMatch) {
            return 'https://rutube.ru/play/embed/' + rutubeMatch[1];
        }
        
        // Vimeo
        var vimeoRegex = /(?:vimeo\.com\/|player\.vimeo\.com\/video\/)(\d+)/;
        var vimeoMatch = url.match(vimeoRegex);
        if (vimeoMatch) {
            return 'https://player.vimeo.com/video/' + vimeoMatch[1];
        }
        
        // Если URL уже является embed URL, возвращаем как есть
        if (url.includes('/embed/') || url.includes('/play/embed/')) {
            return url;
        }
        
        return null;
    }
})();
