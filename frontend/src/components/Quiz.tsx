'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Quiz as QuizType, Question, AnswerOption } from '@/types';
import { contentApi, quizzesApi } from '@/lib/api';
import { normalizeImageUrl } from '@/lib/utils';
import styles from './Quiz.module.css';

interface QuizProps {
  quiz: QuizType;
  serviceId?: number;
  formId?: number;
}

export default function Quiz({ quiz, serviceId, formId }: QuizProps) {
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [answers, setAnswers] = useState<Record<number, number[] | string>>({});
  const [submitted, setSubmitted] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [userData, setUserData] = useState({ name: '', phone: '', email: '' });
  const [submitting, setSubmitting] = useState(false);
  const [showBookingForm, setShowBookingForm] = useState(false);
  const [bookingForm, setBookingForm] = useState<any>(null);
  const [bookingFormData, setBookingFormData] = useState<Record<string, any>>({});
  const [submittingBooking, setSubmittingBooking] = useState(false);
  const router = useRouter();

  const currentQuestion = quiz.questions[currentQuestionIndex];

  const handleAnswer = (questionId: number, optionId?: number, text?: string) => {
    if (currentQuestion.question_type === 'text') {
      setAnswers({ ...answers, [questionId]: text || '' });
    } else if (currentQuestion.question_type === 'single') {
      setAnswers({ ...answers, [questionId]: optionId ? [optionId] : [] });
      // Автоматически переходим на следующий вопрос для single choice
      if (optionId && currentQuestionIndex < quiz.questions.length - 1) {
        setTimeout(() => {
          setCurrentQuestionIndex(currentQuestionIndex + 1);
        }, 300); // Небольшая задержка для визуального отклика
      }
    } else {
      // Multiple choice - без автоматического перехода, только по кнопке "Далее"
      const currentAnswers = (answers[questionId] as number[]) || [];
      if (optionId) {
        const newAnswers = currentAnswers.includes(optionId)
          ? currentAnswers.filter(id => id !== optionId)
          : [...currentAnswers, optionId];
        setAnswers({ ...answers, [questionId]: newAnswers });
      }
    }
  };

  const handleNext = () => {
    if (currentQuestionIndex < quiz.questions.length - 1) {
      setCurrentQuestionIndex(currentQuestionIndex + 1);
    }
  };

  const handlePrev = () => {
    if (currentQuestionIndex > 0) {
      setCurrentQuestionIndex(currentQuestionIndex - 1);
    }
  };

  const handleSubmit = async () => {
    setSubmitting(true);
    
    const submissionData = {
      answers: quiz.questions.map(q => {
        const answer: any = {
          question_id: q.id,
        };
        if (q.question_type === 'text') {
          answer.text_answer = (answers[q.id] as string) || '';
        } else {
          answer.option_ids = (answers[q.id] as number[]) || [];
        }
        return answer;
      }),
      user_name: userData.name || '',
      user_phone: userData.phone || '',
      user_email: userData.email || '',
    };

    console.log('Quiz: Отправка данных квиза', { quiz: quiz.id, submissionData });

    try {
      // Отправляем квиз
      const quizResponse = await quizzesApi.submitQuiz({ ...submissionData, quiz: quiz.id });
      const quizSubmissionData = quizResponse.data;
      
      setResult(quizSubmissionData);
      setSubmitted(true);
      
      // Если есть form_id, загружаем форму для отображения
      if (formId) {
        try {
          const formResponse = await contentApi.getBookingForm(formId);
          const form = formResponse.data;
          setBookingForm(form);
          
          // Заполняем данные формы из userData
          const formData: Record<string, any> = {};
          form.fields.forEach((field: any) => {
            const fieldName = field.name.toLowerCase();
            if (fieldName.includes('name') || fieldName.includes('имя')) {
              formData[field.name] = userData.name || '';
            } else if (fieldName.includes('phone') || fieldName.includes('телефон')) {
              formData[field.name] = userData.phone || '';
            } else if (fieldName.includes('email') || fieldName.includes('почт')) {
              formData[field.name] = userData.email || '';
            } else if (field.default_value) {
              formData[field.name] = field.default_value;
            }
          });
          setBookingFormData(formData);
          setShowBookingForm(true);
        } catch (formError) {
          console.error('Error loading booking form:', formError);
        }
      }
    } catch (error: any) {
      console.error('Error submitting quiz:', error);
      const errorMessage = error.response?.data?.error || error.response?.data?.traceback || error.message || 'Ошибка при отправке квиза';
      console.error('Error details:', error.response?.data);
      alert(`Ошибка при отправке квиза: ${errorMessage}`);
    } finally {
      setSubmitting(false);
    }
  };

  const handleBookingFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!formId || !serviceId || !result?.id) return;
    
    setSubmittingBooking(true);
    try {
      await contentApi.submitBookingWithQuiz({
        form_id: formId,
        service_id: serviceId,
        data: bookingFormData,
        quiz_submission_id: result.id
      });
      
      alert(bookingForm?.success_message || 'Спасибо! Мы свяжемся с вами в ближайшее время.');
      router.push('/');
    } catch (error) {
      console.error('Error submitting booking form:', error);
      alert('Ошибка при отправке формы. Попробуйте еще раз.');
    } finally {
      setSubmittingBooking(false);
    }
  };

  const renderBookingField = (field: any) => {
    const value = bookingFormData[field.name] || '';
    
    switch (field.field_type) {
      case 'textarea':
        return (
          <textarea
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => setBookingFormData({ ...bookingFormData, [field.name]: e.target.value })}
            placeholder={field.placeholder}
            required={field.is_required}
            className={styles.input}
            rows={4}
          />
        );
      
      case 'select':
        const options = field.options?.split('\n').filter((o: string) => o.trim()) || [];
        return (
          <select
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => setBookingFormData({ ...bookingFormData, [field.name]: e.target.value })}
            required={field.is_required}
            className={styles.input}
          >
            <option value="">Выберите...</option>
            {options.map((opt: string, i: number) => (
              <option key={i} value={opt.trim()}>
                {opt.trim()}
              </option>
            ))}
          </select>
        );
      
      case 'checkbox':
        return (
          <label className={styles.checkboxLabel}>
            <input
              type="checkbox"
              name={field.name}
              checked={!!value}
              onChange={(e) => setBookingFormData({ ...bookingFormData, [field.name]: e.target.checked })}
              required={field.is_required}
            />
            <span>{field.help_text || field.label}</span>
          </label>
        );
      
      default:
        return (
          <input
            type={field.field_type}
            id={field.name}
            name={field.name}
            value={value}
            onChange={(e) => setBookingFormData({ ...bookingFormData, [field.name]: e.target.value })}
            placeholder={field.placeholder}
            required={field.is_required}
            className={styles.input}
          />
        );
    }
  };

  if (submitted && result) {
    const resultRange = quiz.result_ranges.find(r => r.id === result.result);
    
    // Если есть форма записи, показываем её
    if (showBookingForm && bookingForm) {
      return (
        <div className={styles.result}>
          <h2>Результат квиза</h2>
          {resultRange ? (
            <>
              <h3>{resultRange.title}</h3>
              <p>{resultRange.description}</p>
              {resultRange.image && (
                <img src={normalizeImageUrl(resultRange.image)} alt={resultRange.title} className={styles.resultImage} />
              )}
            </>
          ) : (
            <p>Результат обрабатывается...</p>
          )}
          
          <div className={styles.bookingForm}>
            <h3>{bookingForm.title}</h3>
            {bookingForm.description && <p className={styles.description}>{bookingForm.description}</p>}
            
            <form onSubmit={handleBookingFormSubmit} className={styles.form}>
              {bookingForm.fields
                .filter((f: any) => f.field_type !== 'hidden')
                .sort((a: any, b: any) => (a.order || 0) - (b.order || 0))
                .map((field: any) => (
                  <div key={field.id} className={styles.field}>
                    <label htmlFor={field.name} className={styles.label}>
                      {field.label}
                      {field.is_required && <span className={styles.required}>*</span>}
                    </label>
                    {renderBookingField(field)}
                    {field.help_text && field.field_type !== 'checkbox' && (
                      <div className={styles.helpText}>{field.help_text}</div>
                    )}
                  </div>
                ))}
              
              {bookingForm.fields
                .filter((f: any) => f.field_type === 'hidden')
                .map((field: any) => (
                  <div key={field.id}>{renderBookingField(field)}</div>
                ))}
              
              <div className={styles.actions}>
                <button type="submit" className={styles.submitButton} disabled={submittingBooking}>
                  {submittingBooking ? 'Отправка...' : bookingForm.submit_button_text}
                </button>
              </div>
            </form>
          </div>
        </div>
      );
    }
    
    // Если формы нет, показываем только результат
    return (
      <div className={styles.result}>
        <h2>Результат квиза</h2>
        {resultRange ? (
          <>
            <h3>{resultRange.title}</h3>
            <p>{resultRange.description}</p>
            {resultRange.image && (
              <img src={normalizeImageUrl(resultRange.image)} alt={resultRange.title} className={styles.resultImage} />
            )}
          </>
        ) : (
          <p>Результат обрабатывается...</p>
        )}
        <button 
          onClick={() => router.push('/')} 
          className={styles.backButton}
        >
          Вернуться на главную
        </button>
      </div>
    );
  }

  return (
    <div className={styles.quiz}>
      <h2>{quiz.title}</h2>
      {quiz.description && <p className={styles.description}>{quiz.description}</p>}

      <div className={styles.progress}>
        Вопрос {currentQuestionIndex + 1} из {quiz.questions.length}
      </div>

      <div className={styles.question}>
        <h3>{currentQuestion.text}</h3>
        {currentQuestion.question_type === 'text' ? (
          <textarea
            value={(answers[currentQuestion.id] as string) || ''}
            onChange={(e) => handleAnswer(currentQuestion.id, undefined, e.target.value)}
            onKeyDown={(e) => {
              // Автоматически переходим на следующий вопрос при нажатии Enter
              if (e.key === 'Enter' && !e.shiftKey && currentQuestionIndex < quiz.questions.length - 1) {
                e.preventDefault();
                const text = (e.target as HTMLTextAreaElement).value.trim();
                if (text) {
                  setTimeout(() => {
                    setCurrentQuestionIndex(currentQuestionIndex + 1);
                  }, 100);
                }
              }
            }}
            onBlur={(e) => {
              // Автоматически переходим на следующий вопрос при потере фокуса, если текст введен
              const text = (e.target as HTMLTextAreaElement).value.trim();
              if (text && currentQuestionIndex < quiz.questions.length - 1) {
                setTimeout(() => {
                  setCurrentQuestionIndex(currentQuestionIndex + 1);
                }, 300);
              }
            }}
            className={styles.textInput}
            placeholder="Введите ваш ответ"
          />
        ) : (
          <div className={styles.options}>
            {currentQuestion.options.map((option) => {
              const isSelected = currentQuestion.question_type === 'single'
                ? (answers[currentQuestion.id] as number[] || [])[0] === option.id
                : (answers[currentQuestion.id] as number[] || []).includes(option.id);

              return (
                <button
                  key={option.id}
                  onClick={() => handleAnswer(currentQuestion.id, option.id)}
                  className={`${styles.option} ${isSelected ? styles.selected : ''}`}
                >
                  {option.text}
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div className={styles.navigation}>
        <button onClick={handlePrev} disabled={currentQuestionIndex === 0}>
          Назад
        </button>
        {currentQuestionIndex === quiz.questions.length - 1 ? (
          <button 
            onClick={handleSubmit} 
            className={styles.submitButton}
            disabled={submitting}
          >
            {submitting ? 'Отправка...' : 'Завершить квиз'}
          </button>
        ) : (
          <button onClick={handleNext}>
            Далее
          </button>
        )}
      </div>
    </div>
  );
}

