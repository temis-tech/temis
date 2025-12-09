/**
 * JavaScript для админки интеграций MoyKlass
 * Автоматически обновляет выпадающие списки полей источника при выборе формы/анкеты
 */
(function() {
    'use strict';
    
    // Ждем загрузки jQuery
    if (typeof django === 'undefined' || typeof django.jQuery === 'undefined') {
        console.error('django.jQuery не загружен');
        return;
    }
    
    var $ = django.jQuery;
    
    function updateSourceFieldChoices(integrationId, sourceType, sourceId) {
        if (!sourceId) {
            // Очищаем все select поля
            $('.source-field-select').each(function() {
                $(this).html('<option value="">Сначала выберите форму/анкету</option>');
                $(this).prop('disabled', true);
            });
            return;
        }
        
        // Загружаем поля через AJAX
        var url = '/admin/moyklass/moyklassintegration/get-source-fields/';
        $.ajax({
            url: url,
            data: {
                'source_type': sourceType,
                'source_id': sourceId
            },
            success: function(data) {
                if (data.fields && data.fields.length > 0) {
                    // Обновляем все select поля
                    $('.source-field-select').each(function() {
                        var $select = $(this);
                        var currentValue = $select.val();
                        
                        // Очищаем и заполняем заново
                        $select.html('<option value="">---------</option>');
                        $select.prop('disabled', false);
                        
                        data.fields.forEach(function(field) {
                            var optionText = field.label + ' (' + field.name + ')';
                            if (field.type) {
                                optionText += ' - ' + field.type;
                            }
                            var $option = $('<option></option>')
                                .attr('value', field.name)
                                .text(optionText);
                            
                            // Восстанавливаем выбранное значение
                            if (field.name === currentValue) {
                                $option.prop('selected', true);
                            }
                            
                            $select.append($option);
                        });
                    });
                } else {
                    $('.source-field-select').each(function() {
                        $(this).html('<option value="">Поля не найдены</option>');
                        $(this).prop('disabled', true);
                    });
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка загрузки полей:', error);
                $('.source-field-select').each(function() {
                    $(this).html('<option value="">Ошибка загрузки полей</option>');
                    $(this).prop('disabled', true);
                });
            }
        });
    }
    
    function updateSourceFieldsHint(integrationId, sourceType, sourceId) {
        // Обновляем подсказку с полями
        $('.source-fields-hint').remove();
        
        if (!sourceId) {
            return;
        }
        
        var hint = $('<div class="source-fields-hint" style="margin-top: 10px; padding: 10px; background: #f0f0f0; border-radius: 4px;"></div>');
        hint.html('<strong>Доступные поля источника:</strong><br>Загрузка...');
        
        var $inline = $('.inline-group').first();
        if ($inline.length) {
            $inline.before(hint);
        } else {
            $('#moyklassfieldmapping_set-group').before(hint);
        }
        
        // Загружаем поля через AJAX
        var url = '/admin/moyklass/moyklassintegration/get-source-fields/';
        $.ajax({
            url: url,
            data: {
                'source_type': sourceType,
                'source_id': sourceId
            },
            success: function(data) {
                if (data.fields && data.fields.length > 0) {
                    var fieldsList = '<ul style="margin: 5px 0; padding-left: 20px;">';
                    data.fields.forEach(function(field) {
                        fieldsList += '<li><code>' + field.name + '</code> - ' + field.label;
                        if (field.type) {
                            fieldsList += ' (' + field.type + ')';
                        }
                        fieldsList += '</li>';
                    });
                    fieldsList += '</ul>';
                    hint.html('<strong>Доступные поля источника:</strong>' + fieldsList);
                } else {
                    hint.html('<em>Поля не найдены</em>');
                }
            },
            error: function(xhr, status, error) {
                console.error('Ошибка загрузки полей:', error);
                hint.html('<em>Ошибка загрузки полей</em>');
            }
        });
    }
    
    $(document).ready(function() {
        // Функция для обновления полей при изменении формы/анкеты
        function refreshFields() {
            var sourceType = $('#id_source_type').val();
            var bookingFormId = $('#id_booking_form').val();
            var quizId = $('#id_quiz').val();
            var sourceId = sourceType === 'booking_form' ? bookingFormId : quizId;
            
            // Получаем ID интеграции (если редактируем существующую)
            var integrationId = null;
            var match = window.location.pathname.match(/moyklassintegration\/(\d+)/);
            if (match) {
                integrationId = match[1];
            }
            
            // Обновляем выпадающие списки
            updateSourceFieldChoices(integrationId, sourceType, sourceId);
            
            // Обновляем подсказку
            updateSourceFieldsHint(integrationId, sourceType, sourceId);
        }
        
        // Обновляем при изменении типа источника
        $('#id_source_type').on('change', function() {
            refreshFields();
        });
        
        // Обновляем при изменении формы/анкеты
        $('#id_booking_form, #id_quiz').on('change', function() {
            refreshFields();
        });
        
        // Обновляем при добавлении новой строки inline
        $(document).on('formset:added', function(event, $row) {
            refreshFields();
        });
        
        // Обновляем при загрузке страницы
        refreshFields();
    });
})();
