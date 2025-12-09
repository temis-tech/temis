"""
Модуль синхронизации данных с MoyKlass CRM
"""
import time
from typing import Dict, Any, Optional
from django.utils import timezone
from django.db import transaction
from .models import MoyKlassSettings, MoyKlassSyncLog
from .client import MoyKlassClient, MoyKlassAPIError


class MoyKlassSync:
    """Класс для синхронизации данных с MoyKlass"""
    
    def __init__(self, settings: Optional[MoyKlassSettings] = None):
        if settings:
            self.settings = settings
        else:
            self.settings = MoyKlassSettings.objects.first()
            if not self.settings:
                raise ValueError('Настройки MoyKlass не найдены')
        
        self.client = MoyKlassClient(self.settings)
    
    def sync_students(self, log: Optional[MoyKlassSyncLog] = None) -> Dict[str, Any]:
        """
        Синхронизирует учеников/лидов
        
        Args:
            log: Лог синхронизации для записи результатов
        
        Returns:
            Словарь с результатами синхронизации
        """
        if not self.settings.sync_students:
            return {'skipped': True, 'message': 'Синхронизация учеников отключена'}
        
        results = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'error_messages': []
        }
        
        try:
            page = 1
            per_page = 50
            
            while True:
                response = self.client.get_students(page=page, per_page=per_page)
                students = response.get('data', [])
                
                if not students:
                    break
                
                for student_data in students:
                    try:
                        results['processed'] += 1
                        # Здесь можно добавить логику сохранения в локальную БД
                        # Например, создать модель Student и синхронизировать данные
                        # student, created = Student.objects.update_or_create(
                        #     moyklass_id=student_data['id'],
                        #     defaults={...}
                        # )
                        # if created:
                        #     results['created'] += 1
                        # else:
                        #     results['updated'] += 1
                    except Exception as e:
                        results['errors'] += 1
                        results['error_messages'].append(str(e))
                
                # Проверяем, есть ли еще страницы
                pagination = response.get('pagination', {})
                if not pagination.get('hasNext', False):
                    break
                
                page += 1
            
            if log:
                log.records_processed = results['processed']
                log.records_created = results['created']
                log.records_updated = results['updated']
                log.records_errors = results['errors']
                if results['error_messages']:
                    log.error_message = '\n'.join(results['error_messages'][:10])
                log.save()
            
            return results
            
        except MoyKlassAPIError as e:
            if log:
                log.status = 'error'
                log.error_message = str(e)
                log.save()
            raise
    
    def sync_payments(self, log: Optional[MoyKlassSyncLog] = None) -> Dict[str, Any]:
        """
        Синхронизирует платежи
        
        Args:
            log: Лог синхронизации для записи результатов
        
        Returns:
            Словарь с результатами синхронизации
        """
        if not self.settings.sync_payments:
            return {'skipped': True, 'message': 'Синхронизация платежей отключена'}
        
        results = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'error_messages': []
        }
        
        try:
            page = 1
            per_page = 50
            
            while True:
                response = self.client.get_payments(page=page, per_page=per_page)
                payments = response.get('data', [])
                
                if not payments:
                    break
                
                for payment_data in payments:
                    try:
                        results['processed'] += 1
                        # Здесь можно добавить логику сохранения платежей
                    except Exception as e:
                        results['errors'] += 1
                        results['error_messages'].append(str(e))
                
                pagination = response.get('pagination', {})
                if not pagination.get('hasNext', False):
                    break
                
                page += 1
            
            if log:
                log.records_processed = results['processed']
                log.records_created = results['created']
                log.records_updated = results['updated']
                log.records_errors = results['errors']
                if results['error_messages']:
                    log.error_message = '\n'.join(results['error_messages'][:10])
                log.save()
            
            return results
            
        except MoyKlassAPIError as e:
            if log:
                log.status = 'error'
                log.error_message = str(e)
                log.save()
            raise
    
    def sync_bookings(self, log: Optional[MoyKlassSyncLog] = None) -> Dict[str, Any]:
        """
        Синхронизирует записи в группы
        
        Args:
            log: Лог синхронизации для записи результатов
        
        Returns:
            Словарь с результатами синхронизации
        """
        if not self.settings.sync_bookings:
            return {'skipped': True, 'message': 'Синхронизация записей отключена'}
        
        results = {
            'processed': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'error_messages': []
        }
        
        try:
            page = 1
            per_page = 50
            
            while True:
                response = self.client.get_bookings(page=page, per_page=per_page)
                bookings = response.get('data', [])
                
                if not bookings:
                    break
                
                for booking_data in bookings:
                    try:
                        results['processed'] += 1
                        # Здесь можно добавить логику сохранения записей
                    except Exception as e:
                        results['errors'] += 1
                        results['error_messages'].append(str(e))
                
                pagination = response.get('pagination', {})
                if not pagination.get('hasNext', False):
                    break
                
                page += 1
            
            if log:
                log.records_processed = results['processed']
                log.records_created = results['created']
                log.records_updated = results['updated']
                log.records_errors = results['errors']
                if results['error_messages']:
                    log.error_message = '\n'.join(results['error_messages'][:10])
                log.save()
            
            return results
            
        except MoyKlassAPIError as e:
            if log:
                log.status = 'error'
                log.error_message = str(e)
                log.save()
            raise
    
    def sync_all(self) -> Dict[str, Any]:
        """
        Выполняет полную синхронизацию всех включенных типов данных
        
        Returns:
            Словарь с результатами синхронизации
        """
        start_time = time.time()
        
        # Создаем лог для полной синхронизации
        log = MoyKlassSyncLog(
            sync_type='full',
            status='success'
        )
        log.save()
        
        results = {
            'students': {},
            'payments': {},
            'bookings': {},
            'total_processed': 0,
            'total_created': 0,
            'total_updated': 0,
            'total_errors': 0
        }
        
        try:
            # Синхронизируем учеников
            if self.settings.sync_students:
                student_log = MoyKlassSyncLog(
                    sync_type='students',
                    status='success'
                )
                student_log.save()
                results['students'] = self.sync_students(student_log)
                results['total_processed'] += results['students'].get('processed', 0)
                results['total_created'] += results['students'].get('created', 0)
                results['total_updated'] += results['students'].get('updated', 0)
                results['total_errors'] += results['students'].get('errors', 0)
            
            # Синхронизируем платежи
            if self.settings.sync_payments:
                payment_log = MoyKlassSyncLog(
                    sync_type='payments',
                    status='success'
                )
                payment_log.save()
                results['payments'] = self.sync_payments(payment_log)
                results['total_processed'] += results['payments'].get('processed', 0)
                results['total_created'] += results['payments'].get('created', 0)
                results['total_updated'] += results['payments'].get('updated', 0)
                results['total_errors'] += results['payments'].get('errors', 0)
            
            # Синхронизируем записи
            if self.settings.sync_bookings:
                booking_log = MoyKlassSyncLog(
                    sync_type='bookings',
                    status='success'
                )
                booking_log.save()
                results['bookings'] = self.sync_bookings(booking_log)
                results['total_processed'] += results['bookings'].get('processed', 0)
                results['total_created'] += results['bookings'].get('created', 0)
                results['total_updated'] += results['bookings'].get('updated', 0)
                results['total_errors'] += results['bookings'].get('errors', 0)
            
            # Обновляем общий лог
            log.records_processed = results['total_processed']
            log.records_created = results['total_created']
            log.records_updated = results['total_updated']
            log.records_errors = results['total_errors']
            
            if results['total_errors'] > 0:
                log.status = 'partial'
            
            log.finished_at = timezone.now()
            log.duration_seconds = time.time() - start_time
            log.save()
            
            # Обновляем время последней синхронизации
            self.settings.last_sync_at = timezone.now()
            self.settings.save(update_fields=['last_sync_at'])
            
            return results
            
        except Exception as e:
            log.status = 'error'
            log.error_message = str(e)
            log.finished_at = timezone.now()
            log.duration_seconds = time.time() - start_time
            log.save()
            raise

