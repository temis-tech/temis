from django.db import models
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils import timezone
import base64
import os
import json

# Безопасный импорт cryptography - может не быть установлена при применении миграций
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    from cryptography.hazmat.backends import default_backend
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    # Заглушки для случаев, когда cryptography не установлена
    Fernet = None


def get_encryption_key():
    """Получить ключ шифрования из настроек или создать новый"""
    if not CRYPTOGRAPHY_AVAILABLE:
        raise ImportError('cryptography не установлена. Установите: pip install cryptography')
    
    key = getattr(settings, 'CRM_ENCRYPTION_KEY', None)
    if not key:
        # Используем SECRET_KEY для генерации ключа шифрования
        secret_key = settings.SECRET_KEY.encode()
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'crm_encryption_salt',
            iterations=100000,
            backend=default_backend()
        )
        key = base64.urlsafe_b64encode(kdf.derive(secret_key))
    else:
        if isinstance(key, str):
            key = key.encode()
    return key


def encrypt_field(value):
    """Зашифровать значение поля"""
    if not value:
        return None
    if not CRYPTOGRAPHY_AVAILABLE:
        # Если cryptography не установлена, возвращаем значение как есть (для миграций)
        return value
    try:
        f = Fernet(get_encryption_key())
        encrypted = f.encrypt(value.encode() if isinstance(value, str) else value)
        return base64.urlsafe_b64encode(encrypted).decode()
    except Exception as e:
        raise ValidationError(f'Ошибка шифрования: {str(e)}')


def decrypt_field(encrypted_value):
    """Расшифровать значение поля"""
    if not encrypted_value:
        return None
    if not CRYPTOGRAPHY_AVAILABLE:
        # Если cryptography не установлена, возвращаем значение как есть (для миграций)
        return encrypted_value
    try:
        f = Fernet(get_encryption_key())
        decoded = base64.urlsafe_b64decode(encrypted_value.encode())
        decrypted = f.decrypt(decoded)
        return decrypted.decode()
    except Exception as e:
        # Если не удалось расшифровать, возвращаем исходное значение (для миграций)
        return encrypted_value


# Используем обычные TextField, шифрование будет через методы модели


class LeadStatus(models.Model):
    """Статус лида"""
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('in_progress', 'В процессе работы'),
        ('cancelled', 'Отмена'),
        ('converted', 'Превращен в клиента'),
    ]
    
    name = models.CharField('Название статуса', max_length=50, unique=True)
    code = models.CharField('Код статуса', max_length=20, choices=STATUS_CHOICES, default='new')
    color = models.CharField('Цвет (HEX)', max_length=7, default='#007bff',
                            help_text='Цвет для отображения в интерфейсе')
    order = models.IntegerField('Порядок', default=0)
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Статус лида'
        verbose_name_plural = 'Статусы лидов'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Lead(models.Model):
    """Лид - потенциальный клиент"""
    # Связи с источниками
    booking_submission = models.ForeignKey(
        'booking.BookingSubmission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name='Отправка формы записи'
    )
    quiz_submission = models.ForeignKey(
        'quizzes.QuizSubmission',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='leads',
        verbose_name='Отправка анкеты'
    )
    
    # Персональные данные (зашифрованы)
    name = models.TextField('Имя (зашифровано)', blank=True)
    phone = models.TextField('Телефон (зашифровано)', blank=True)
    email = models.TextField('Email (зашифровано)', blank=True)
    
    # Дополнительные данные (JSON, зашифрован)
    additional_data = models.TextField('Дополнительные данные (JSON, зашифрован)', blank=True)
    
    # Статус
    status = models.ForeignKey(
        LeadStatus,
        on_delete=models.PROTECT,
        related_name='leads',
        verbose_name='Статус',
        null=True,
        blank=True
    )
    
    # Метаданные
    source = models.CharField('Источник', max_length=100, blank=True,
                              help_text='Источник лида (форма записи, анкета и т.д.)')
    notes = models.TextField('Заметки', blank=True,
                            help_text='Внутренние заметки по лиду')
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    converted_at = models.DateTimeField('Превращен в клиента', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Лид'
        verbose_name_plural = 'Лиды'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        name = self.get_name() or 'Без имени'
        return f'Лид: {name} ({self.created_at.strftime("%d.%m.%Y %H:%M")})'
    
    def get_name(self):
        """Получить расшифрованное имя"""
        if not self.name:
            return ''
        try:
            return decrypt_field(self.name)
        except:
            return self.name  # Если не зашифровано, возвращаем как есть
    
    def get_phone(self):
        """Получить расшифрованный телефон"""
        if not self.phone:
            return ''
        try:
            return decrypt_field(self.phone)
        except:
            return self.phone  # Если не зашифровано, возвращаем как есть
    
    def get_email(self):
        """Получить расшифрованный email"""
        if not self.email:
            return ''
        try:
            return decrypt_field(self.email)
        except:
            return self.email  # Если не зашифровано, возвращаем как есть
    
    def set_name(self, value):
        """Установить имя (автоматически зашифрует)"""
        if value:
            self.name = encrypt_field(value)
        else:
            self.name = ''
    
    def set_phone(self, value):
        """Установить телефон (автоматически зашифрует)"""
        if value:
            self.phone = encrypt_field(value)
        else:
            self.phone = ''
    
    def set_email(self, value):
        """Установить email (автоматически зашифрует)"""
        if value:
            self.email = encrypt_field(value)
        else:
            self.email = ''
    
    def get_additional_data(self):
        """Получить расшифрованные дополнительные данные"""
        if not self.additional_data:
            return {}
        try:
            decrypted = decrypt_field(self.additional_data)
            return json.loads(decrypted) if decrypted else {}
        except:
            return {}
    
    def set_additional_data(self, data):
        """Установить дополнительные данные (автоматически зашифрует)"""
        if data:
            encrypted = encrypt_field(json.dumps(data))
            self.additional_data = encrypted
        else:
            self.additional_data = ''
    
    def convert_to_client(self):
        """Превратить лида в клиента"""
        if self.status and self.status.code == 'converted':
            return None  # Уже превращен
        
        client = Client.objects.create(
            source_lead=self,
            additional_data_json=self.get_additional_data()
        )
        # Устанавливаем зашифрованные данные
        name = self.get_name()
        phone = self.get_phone()
        email = self.get_email()
        if name:
            client.set_name(name)
        if phone:
            client.set_phone(phone)
        if email:
            client.set_email(email)
        
        # Обновляем статус лида
        converted_status = LeadStatus.objects.filter(code='converted').first()
        if converted_status:
            self.status = converted_status
        self.converted_at = timezone.now()
        self.save()
        
        return client


class Client(models.Model):
    """Клиент - превращенный лид или созданный вручную"""
    # Связь с лидом (если был превращен из лида)
    source_lead = models.OneToOneField(
        Lead,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='client',
        verbose_name='Исходный лид'
    )
    
    # Персональные данные (зашифрованы)
    name = models.TextField('Имя (зашифровано)', blank=True)
    phone = models.TextField('Телефон (зашифровано)', blank=True)
    email = models.TextField('Email (зашифровано)', blank=True)
    
    # Дополнительные данные (JSON, зашифрован)
    additional_data_json = models.JSONField('Дополнительные данные', default=dict, blank=True)
    
    # Метаданные
    notes = models.TextField('Заметки', blank=True,
                            help_text='Внутренние заметки по клиенту')
    is_active = models.BooleanField('Активен', default=True)
    created_at = models.DateTimeField('Создан', auto_now_add=True)
    updated_at = models.DateTimeField('Обновлен', auto_now=True)
    
    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        name = self.get_name() or 'Без имени'
        return f'Клиент: {name}'
    
    def get_name(self):
        """Получить расшифрованное имя"""
        if not self.name:
            return ''
        try:
            return decrypt_field(self.name)
        except:
            return self.name  # Если не зашифровано, возвращаем как есть
    
    def get_phone(self):
        """Получить расшифрованный телефон"""
        if not self.phone:
            return ''
        try:
            return decrypt_field(self.phone)
        except:
            return self.phone  # Если не зашифровано, возвращаем как есть
    
    def get_email(self):
        """Получить расшифрованный email"""
        if not self.email:
            return ''
        try:
            return decrypt_field(self.email)
        except:
            return self.email  # Если не зашифровано, возвращаем как есть
    
    def set_name(self, value):
        """Установить имя (автоматически зашифрует)"""
        if value:
            self.name = encrypt_field(value)
        else:
            self.name = ''
    
    def set_phone(self, value):
        """Установить телефон (автоматически зашифрует)"""
        if value:
            self.phone = encrypt_field(value)
        else:
            self.phone = ''
    
    def set_email(self, value):
        """Установить email (автоматически зашифрует)"""
        if value:
            self.email = encrypt_field(value)
        else:
            self.email = ''
    
    def get_additional_data(self):
        """Получить дополнительные данные"""
        return self.additional_data_json or {}


class ClientFile(models.Model):
    """Файл клиента"""
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name='files',
        verbose_name='Клиент'
    )
    file = models.FileField('Файл', upload_to='crm/client_files/%Y/%m/%d/')
    name = models.CharField('Название файла', max_length=200, blank=True,
                           help_text='Название для отображения (если не указано, используется имя файла)')
    description = models.TextField('Описание', blank=True)
    uploaded_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Загружен пользователем'
    )
    created_at = models.DateTimeField('Загружен', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Файл клиента'
        verbose_name_plural = 'Файлы клиентов'
        ordering = ['-created_at']
    
    def __str__(self):
        return f'{self.client.get_name()} - {self.get_display_name()}'
    
    def get_display_name(self):
        """Получить название для отображения"""
        return self.name or self.file.name.split('/')[-1]
