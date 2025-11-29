// Color picker widget for Django admin
// Используем нативный HTML5 color input для круговой палитры
(function() {
    'use strict';
    
    function initColorPicker() {
        // Получаем jQuery
        var $ = (typeof django !== 'undefined' && django.jQuery) ? django.jQuery : 
                (typeof jQuery !== 'undefined' ? jQuery : null);
        
        if (!$) {
            console.warn('Color picker: jQuery not found');
            return;
        }
        
        // Ищем все текстовые поля с "color" или "gradient" в имени
        $('input[type="text"][name*="color"], input[type="text"][name*="gradient"]').each(function() {
            var $textInput = $(this);
            
            // Пропускаем, если уже обработано
            if ($textInput.closest('.color-picker-wrapper').length > 0) {
                return;
            }
            
            var currentValue = $textInput.val() || '#667eea';
            
            // Создаем контейнер
            var $wrapper = $('<div>', {
                class: 'color-picker-wrapper',
                style: 'display: flex; align-items: center; gap: 1rem; margin-top: 0.5rem;'
            });
            
            // Создаем HTML5 color input (круговая палитра браузера)
            var $colorInput = $('<input>', {
                type: 'color',
                value: currentValue,
                class: 'color-picker-input',
                style: 'width: 60px; height: 60px; border: 2px solid #ddd; border-radius: 8px; cursor: pointer; padding: 0;',
                title: 'Нажмите для выбора цвета'
            });
            
            // Обновляем текстовое поле при изменении цвета в палитре
            $colorInput.on('input change', function() {
                var newColor = $(this).val();
                $textInput.val(newColor);
                $textInput.trigger('change');
            });
            
            // Обновляем color picker при изменении текстового поля
            $textInput.on('input blur', function() {
                var val = $(this).val().trim();
                if (/^#[0-9A-F]{6}$/i.test(val)) {
                    $colorInput.val(val);
                } else if (/^[0-9A-F]{6}$/i.test(val)) {
                    val = '#' + val;
                    $textInput.val(val);
                    $colorInput.val(val);
                }
            });
            
            // Обертываем текстовое поле
            $textInput.wrap($wrapper);
            $colorInput.insertBefore($textInput);
            
            // Добавляем подсказку
            var $hint = $('<div>', {
                class: 'color-picker-hint',
                style: 'font-size: 0.85rem; color: #666; margin-top: 0.25rem;',
                text: 'Нажмите на цветной квадрат для выбора цвета'
            });
            $textInput.after($hint);
        });
    }
    
    // Множественные способы инициализации для гарантии работы
    function tryInit() {
        var $ = (typeof django !== 'undefined' && django.jQuery) ? django.jQuery : 
                (typeof jQuery !== 'undefined' ? jQuery : null);
        
        if ($) {
            if ($(document).ready) {
                $(document).ready(function() {
                    setTimeout(initColorPicker, 300);
                });
            } else {
                setTimeout(initColorPicker, 300);
            }
        } else {
            // Пробуем еще раз через некоторое время
            setTimeout(tryInit, 200);
        }
    }
    
    // Начинаем инициализацию
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', tryInit);
    } else {
        tryInit();
    }
    
    // Также пробуем через window.onload
    if (window.addEventListener) {
        window.addEventListener('load', function() {
            setTimeout(initColorPicker, 500);
        });
    }
})();
