from django.db import models
from django.core.validators import MinValueValidator
from django.utils.text import slugify


class Quiz(models.Model):
    """Анкета/Анкета"""
    title = models.CharField('Название', max_length=200)
    slug = models.SlugField('URL', unique=True, blank=True)
    description = models.TextField('Описание', blank=True)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)

    class Meta:
        verbose_name = 'Анкета'
        verbose_name_plural = 'Анкетаы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class Question(models.Model):
    """Вопрос в анкетае"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name='Анкета')
    text = models.TextField('Текст вопроса')
    order = models.IntegerField('Порядок', default=0)
    question_type = models.CharField('Тип вопроса', max_length=20, 
                                     choices=[
                                         ('single', 'Один ответ'),
                                         ('multiple', 'Несколько ответов'),
                                         ('text', 'Текстовый ответ'),
                                     ],
                                     default='single')
    is_required = models.BooleanField('Обязательный', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.quiz.title} - {self.text[:50]}'


class AnswerOption(models.Model):
    """Вариант ответа на вопрос"""
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name='Вопрос')
    text = models.CharField('Текст ответа', max_length=500)
    points = models.IntegerField('Баллы', default=0, validators=[MinValueValidator(0)])
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Вариант ответа'
        verbose_name_plural = 'Варианты ответов'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.question.text[:30]} - {self.text[:30]}'


class ResultRange(models.Model):
    """Диапазон результатов по баллам"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='result_ranges', verbose_name='Анкета')
    min_points = models.IntegerField('Минимальные баллы', validators=[MinValueValidator(0)])
    max_points = models.IntegerField('Максимальные баллы', validators=[MinValueValidator(0)], null=True, blank=True)
    title = models.CharField('Заголовок результата', max_length=200)
    description = models.TextField('Описание результата')
    image = models.ImageField('Изображение', upload_to='quiz_results/', blank=True, null=True)
    order = models.IntegerField('Порядок', default=0)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Диапазон результатов'
        verbose_name_plural = 'Диапазоны результатов'
        ordering = ['order', 'min_points']

    def __str__(self):
        if self.max_points:
            return f'{self.quiz.title} - {self.min_points}-{self.max_points} баллов: {self.title}'
        return f'{self.quiz.title} - от {self.min_points} баллов: {self.title}'

    def matches_points(self, points):
        """Проверяет, попадают ли баллы в диапазон"""
        if self.max_points:
            return self.min_points <= points <= self.max_points
        return points >= self.min_points


class QuizSubmission(models.Model):
    """Отправка анкетаа пользователем"""
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='submissions', verbose_name='Анкета')
    total_points = models.IntegerField('Всего баллов', default=0)
    result = models.ForeignKey(ResultRange, on_delete=models.SET_NULL, null=True, blank=True, 
                              verbose_name='Результат', related_name='submissions')
    user_name = models.CharField('Имя пользователя', max_length=200, blank=True)
    user_phone = models.CharField('Телефон пользователя', max_length=20, blank=True)
    user_email = models.EmailField('Email пользователя', blank=True)
    created_at = models.DateTimeField('Создана', auto_now_add=True)

    class Meta:
        verbose_name = 'Отправка анкетаа'
        verbose_name_plural = 'Отправки анкетаов'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.quiz.title} - {self.total_points} баллов - {self.created_at.strftime("%d.%m.%Y %H:%M")}'


class SubmissionAnswer(models.Model):
    """Ответ пользователя на вопрос"""
    submission = models.ForeignKey(QuizSubmission, on_delete=models.CASCADE, related_name='answers', 
                                  verbose_name='Отправка')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, verbose_name='Вопрос')
    selected_options = models.ManyToManyField(AnswerOption, blank=True, verbose_name='Выбранные варианты')
    text_answer = models.TextField('Текстовый ответ', blank=True)
    points = models.IntegerField('Баллы за ответ', default=0)
    created_at = models.DateTimeField('Создан', auto_now_add=True)

    class Meta:
        verbose_name = 'Ответ на вопрос'
        verbose_name_plural = 'Ответы на вопросы'

    def __str__(self):
        if self.selected_options.exists():
            return f'{self.question.text[:30]} - {", ".join([opt.text[:20] for opt in self.selected_options.all()])}'
        return f'{self.question.text[:30]} - {self.text_answer[:30]}'

