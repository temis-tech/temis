'use client';

import { useState, useEffect, useCallback } from 'react';
import { contentApi, quizzesApi } from '@/lib/api';
import { useRouter } from 'next/navigation';
import { normalizePhone, validatePhone, filterPhoneInput } from '@/lib/utils';
import styles from './BookingForm.module.css';

interface BookingFormProps {
  formId: number;
  serviceId: number;
  serviceTitle: string;
  sourcePage?: string;
  hiddenFields?: Record<string, string>; // Дополнительные данные для скрытых полей
  onClose: () => void;
}

interface FormField {
  id: number;
  label: string;
  name: string;
  field_type: string;
  placeholder?: string;
  help_text?: string;
  is_required: boolean;
  default_value?: string;
  options?: string;
  order?: number;
}

interface FormRule {
  id: number;
  field: number;
  field_name?: string;
  field_value: string;
  quiz?: number;
  quiz_slug?: string;
  quiz_title?: string;
  is_active: boolean;
}

interface BookingFormData {
  title: string;
  description?: string;
  submit_button_text: string;
  success_message: string;
  fields: FormField[];
  rules: FormRule[];
  default_quiz?: number | null;
  default_quiz_slug?: string | null;
  default_quiz_title?: string | null;
}

export default function BookingForm({ formId, serviceId, serviceTitle, sourcePage, hiddenFields, onClose }: BookingFormProps) {
  const [form, setForm] = useState<BookingFormData | null>(null);
  const [formData, setFormData] = useState<Record<string, any>>({});
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showQuiz, setShowQuiz] = useState<{ slug: string; title: string } | null>(null);
  const router = useRouter();

  const loadForm = useCallback(async () => {
    try {
      const response = await contentApi.getBookingForm(formId);
      const formData = response.data;
      console.log('BookingForm: Загружена форма', {
        formId,
        formData,
        default_quiz: formData.default_quiz,
        default_quiz_slug: formData.default_quiz_slug,
        default_quiz_title: formData.default_quiz_title,
        rules: formData.rules?.map((r: FormRule) => ({
          id: r.id,
          field: r.field,
          field_name: r.field_name,
          field_value: r.field_value,
          quiz: r.quiz,
          quiz_slug: r.quiz_slug,
          quiz_title: r.quiz_title,
          is_active: r.is_active
        })),
        fields: formData.fields?.map((f: FormField) => ({
          id: f.id,
          name: f.name,
          label: f.label
        }))
      });
      
      setForm(formData);
      
      // Если есть анкета по умолчанию, сразу открываем вместо формы
      if (formData.default_quiz_slug && formData.default_quiz_title) {
        console.log('BookingForm: Установлена анкета по умолчанию, открываем сразу', {
          slug: formData.default_quiz_slug,
          title: formData.default_quiz_title
        });
        // Закрываем форму и переходим на анкета
        onClose();
        router.push(`/quizzes/${formData.default_quiz_slug}?service_id=${serviceId}&form_id=${formId}`);
        return;
      }
      
      // Заполняем значения по умолчанию
      const defaults: Record<string, any> = {};
      formData.fields.forEach((field: FormField) => {
        if (field.field_type === 'hidden') {
          // Для скрытых полей: сначала проверяем hiddenFields, потом default_value
          if (hiddenFields && hiddenFields[field.name]) {
            defaults[field.name] = hiddenFields[field.name];
          } else if (field.default_value) {
            // Заменяем плейсхолдеры в default_value
            let value = field.default_value.replace('{service_title}', serviceTitle);
            if (sourcePage) {
              value = value.replace('{source_page}', sourcePage);
            }
            defaults[field.name] = value;
          }
        } else if (field.default_value) {
          // Для обычных полей используем default_value с заменой плейсхолдеров
          let value = field.default_value.replace('{service_title}', serviceTitle);
          if (sourcePage) {
            value = value.replace('{source_page}', sourcePage);
          }
          defaults[field.name] = value;
        }
      });
      setFormData(defaults);
    } catch (err: any) {
      setError('Не удалось загрузить форму');
      console.error('BookingForm: Ошибка загрузки формы', err);
    } finally {
      setLoading(false);
    }
  }, [formId, onClose, router, serviceId, serviceTitle, sourcePage, hiddenFields]);

  useEffect(() => {
    loadForm();
  }, [loadForm]);

  const handleChange = (name: string, value: any) => {
    // Для полей телефона применяем маску и валидацию
    const field = form?.fields.find(f => f.name === name);
    let updatedFormData: Record<string, any>;
    
    if (field?.field_type === 'phone') {
      // Фильтруем ввод - удаляем только недопустимые символы (буквы и спецсимволы)
      // НЕ форматируем номер, только очищаем
      const filtered = filterPhoneInput(value);
      updatedFormData = { ...formData, [name]: filtered };
      setFormData(updatedFormData);
      
      // Валидация в реальном времени
      const phoneError = validatePhone(filtered, true);
      
      if (phoneError) {
        setFieldErrors((prev) => {
          const updated = { ...prev, [name]: phoneError };
          return updated;
        });
      } else {
        // Очищаем ошибку если валидно
        setFieldErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors[name];
          return newErrors;
        });
      }
    } else {
      updatedFormData = { ...formData, [name]: value };
      setFormData(updatedFormData);
      // Очищаем ошибку для этого поля, если она была
      if (fieldErrors[name]) {
        setFieldErrors((prev) => {
          const newErrors = { ...prev };
          delete newErrors[name];
          return newErrors;
        });
      }
    }
    
    // Проверяем правила после изменения поля
    if (form) {
      // Если есть анкета по умолчанию, он имеет приоритет - не проверяем правила
      if (form.default_quiz_slug && form.default_quiz_title) {
        console.log('BookingForm: Анкета по умолчанию установлена, правила игнорируются');
        return;
      }
      
      // Сбрасываем показ анкетаа, если значение изменилось
      setShowQuiz(null);
      
      // Проверяем все активные правила с активным анкетаом
      const activeRules = form.rules.filter(r => {
        const hasQuiz = r.is_active && r.quiz_slug && r.quiz_slug.trim();
        if (!hasQuiz) {
          console.log('BookingForm: Правило пропущено', {
            ruleId: r.id,
            isActive: r.is_active,
            quizSlug: r.quiz_slug,
            quizId: r.quiz
          });
        }
        return hasQuiz;
      });
      
      console.log('BookingForm: Активные правила для проверки', activeRules.length, activeRules);
      
      for (const rule of activeRules) {
        // Используем field_name если есть, иначе ищем поле по ID
        const fieldName = rule.field_name || form.fields.find(f => f.id === rule.field)?.name;
        
        if (!fieldName) {
          console.warn('BookingForm: Не найдено имя поля для правила', rule);
          continue;
        }
        
        const fieldValue = updatedFormData[fieldName];
        // Приводим значения к строкам для сравнения, чтобы избежать проблем с типами
        const fieldValueStr = String(fieldValue || '').trim();
        const ruleValueStr = String(rule.field_value || '').trim();
        
        console.log('BookingForm: Проверка правила', {
          ruleId: rule.id,
          fieldName,
          fieldValue: fieldValueStr,
          fieldValueLength: fieldValueStr.length,
          ruleValue: ruleValueStr,
          ruleValueLength: ruleValueStr.length,
          matches: fieldValueStr === ruleValueStr,
          quizSlug: rule.quiz_slug,
          quizTitle: rule.quiz_title,
          quizId: rule.quiz,
          isActive: rule.is_active,
          fullRule: rule
        });
        
        if (fieldValueStr === ruleValueStr) {
          console.log('BookingForm: Правило сработало, открываем анкета', rule.quiz_slug);
          setShowQuiz({ slug: rule.quiz_slug!, title: rule.quiz_title || 'Анкета' });
          return;
        }
      }
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    setError(null);

    try {
      // Проверяем анкета из правил
      if (showQuiz) {
        // Если есть анкета, переходим на него
        router.push(`/quizzes/${showQuiz.slug}?service_id=${serviceId}&form_id=${formId}`);
        onClose();
      } else {
        // Проверяем ошибки валидации перед отправкой
        if (Object.keys(fieldErrors).length > 0) {
          setError('Пожалуйста, исправьте ошибки в форме');
          setSubmitting(false);
          return;
        }
        
        // Валидируем и нормализуем телефоны перед отправкой
        const normalizedData = { ...formData };
        const validationErrors: string[] = [];
        
        form?.fields.forEach((field) => {
          if (field.field_type === 'phone' && normalizedData[field.name]) {
            // Валидируем телефон
            const phoneError = validatePhone(normalizedData[field.name]);
            if (phoneError) {
              validationErrors.push(`${field.label}: ${phoneError}`);
              setFieldErrors({ ...fieldErrors, [field.name]: phoneError });
            } else {
              // Нормализуем телефон (оставляем только цифры)
              normalizedData[field.name] = normalizePhone(normalizedData[field.name]);
            }
          }
        });
        
        // Если есть ошибки валидации, показываем их
        if (validationErrors.length > 0) {
          setError('Пожалуйста, исправьте ошибки в форме');
          setSubmitting(false);
          return;
        }
        
        // Отправляем форму
        await contentApi.submitBooking({
          form_id: formId,
          service_id: serviceId,
          source_page: sourcePage,
          data: normalizedData
        });
        
        alert(form?.success_message || 'Спасибо! Мы свяжемся с вами в ближайшее время.');
        onClose();
      }
    } catch (err: any) {
      setError(err.response?.data?.error || 'Произошла ошибка при отправке формы');
    } finally {
      setSubmitting(false);
    }
  };

  const renderField = (field: FormField) => {
    const value = formData[field.name] || '';
    
    switch (field.field_type) {
      case 'textarea':
        return (
          <textarea
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => handleChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            required={field.is_required}
            className={styles.input}
            rows={4}
          />
        );
      
      case 'select':
        const options = field.options?.split('\n').filter(o => o.trim()) || [];
        return (
          <select
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => handleChange(field.name, e.target.value)}
            required={field.is_required}
            className={styles.input}
          >
            <option value="">Выберите...</option>
            {options.map((opt, i) => (
              <option key={i} value={opt.trim()}>
                {opt.trim()}
              </option>
            ))}
          </select>
        );
      
      case 'radio':
        const radioOptions = field.options?.split('\n').filter(o => o.trim()) || [];
        return (
          <div className={styles.radioGroup}>
            {radioOptions.map((opt, i) => (
              <label key={i} className={styles.radioLabel}>
                <input
                  type="radio"
                  name={field.name}
                  value={opt.trim()}
                  checked={value === opt.trim()}
                  onChange={(e) => handleChange(field.name, e.target.value)}
                  required={field.is_required}
                />
                <span>{opt.trim()}</span>
              </label>
            ))}
          </div>
        );
      
      case 'checkbox':
        return (
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              name={field.name}
              checked={!!value}
              onChange={(e) => handleChange(field.name, e.target.checked)}
              required={field.is_required}
            />
            <span>{field.help_text || field.label}</span>
          </label>
        );
      
      case 'hidden':
        return (
          <input
            type="hidden"
            name={field.name}
            value={value}
          />
        );
      
      case 'phone':
        const hasError = fieldErrors[field.name];
        return (
          <>
            <input
              type="tel"
              id={field.name}
              name={field.name}
              value={value}
              onChange={(e) => handleChange(field.name, e.target.value)}
              onBlur={(e) => {
                // Финальная валидация при потере фокуса (isTyping = false)
                const phoneError = validatePhone(e.target.value, false);
                if (phoneError) {
                  setFieldErrors((prev) => ({ ...prev, [field.name]: phoneError }));
                } else {
                  setFieldErrors((prev) => {
                    const newErrors = { ...prev };
                    delete newErrors[field.name];
                    return newErrors;
                  });
                }
              }}
              placeholder={field.placeholder || 'Номер телефона'}
              required={field.is_required}
              className={`${styles.input} ${hasError ? styles.inputError : ''}`}
              maxLength={20} // Достаточно для любого формата
            />
            {hasError && (
              <div className={styles.fieldError} style={{ color: '#e74c3c', fontSize: '0.875rem', marginTop: '0.5rem' }}>
                {hasError}
              </div>
            )}
          </>
        );
      
      default:
        return (
          <input
            type={field.field_type}
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => handleChange(field.name, e.target.value)}
            placeholder={field.placeholder}
            required={field.is_required}
            className={styles.input}
          />
        );
    }
  };

  if (loading) {
    return (
      <div className={styles.overlay}>
        <div className={styles.modal}>
          <div className={styles.loading}>Загрузка формы...</div>
        </div>
      </div>
    );
  }

  if (!form) {
    return (
      <div className={styles.overlay}>
        <div className={styles.modal}>
          <div className={styles.error}>Форма не найдена</div>
          <button onClick={onClose} className={styles.closeButton}>Закрыть</button>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose}>×</button>
        
        <h2 className={styles.title}>{form.title}</h2>
        {form.description && <p className={styles.description}>{form.description}</p>}
        
        {error && <div className={styles.error}>{error}</div>}
        
        {showQuiz && (
          <div className={styles.quizNotice}>
            После отправки формы откроется анкета: <strong>{showQuiz.title}</strong>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className={styles.form}>
          {form.fields
            .filter(f => f.field_type !== 'hidden')
            .sort((a, b) => (a.order || 0) - (b.order || 0))
            .map((field) => (
              <div key={field.id} className={styles.field}>
                <label htmlFor={field.name} className={styles.label}>
                  {field.label}
                  {field.is_required && <span className={styles.required}>*</span>}
                </label>
                {renderField(field)}
                {field.help_text && field.field_type !== 'checkbox' && (
                  <div className={styles.helpText}>{field.help_text}</div>
                )}
              </div>
            ))}
          
          {form.fields
            .filter(f => f.field_type === 'hidden')
            .map((field) => (
              <div key={field.id}>{renderField(field)}</div>
            ))}
          
          <div className={styles.actions}>
            <button type="submit" className={styles.submitButton} disabled={submitting}>
              {submitting ? 'Отправка...' : form.submit_button_text}
            </button>
            <button type="button" onClick={onClose} className={styles.cancelButton}>
              Отмена
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

