"""
Клиент для работы с API MoyKlass
Документация: https://api.moyklass.com/
"""
import requests
import time
from typing import Dict, Any, Optional, List
from django.utils import timezone
from django.conf import settings
from .models import MoyKlassSettings, MoyKlassRequestLog


class MoyKlassAPIError(Exception):
    """Ошибка при работе с API MoyKlass"""
    pass


class MoyKlassClient:
    """Клиент для работы с API MoyKlass"""
    
    BASE_URL = 'https://api.moyklass.com'
    API_VERSION = 'v1'
    
    def __init__(self, settings_instance: Optional[MoyKlassSettings] = None):
        """
        Инициализация клиента
        
        Args:
            settings_instance: Экземпляр настроек MoyKlassSettings. 
                              Если не указан, будет загружен автоматически.
        """
        if settings_instance:
            self.settings = settings_instance
        else:
            self.settings = MoyKlassSettings.objects.first()
            if not self.settings:
                raise MoyKlassAPIError('Настройки MoyKlass не найдены. Создайте их в админке.')
        
        if not self.settings.is_active:
            raise MoyKlassAPIError('Интеграция MoyKlass неактивна')
        
        if not self.settings.api_key:
            raise MoyKlassAPIError('API ключ не настроен')
    
    def _get_access_token(self) -> str:
        """Получает действительный токен доступа"""
        # Проверяем, есть ли действительный токен
        if self.settings.is_token_valid():
            return self.settings.access_token
        
        # Получаем новый токен
        return self._refresh_token()
    
    def _refresh_token(self) -> str:
        """Получает новый токен доступа"""
        url = f'{self.BASE_URL}/{self.API_VERSION}/company/auth/getToken'
        
        response = requests.post(
            url,
            json={'apiKey': self.settings.api_key},
            timeout=10
        )
        
        self._log_request('POST', url, {'apiKey': '***'}, response)
        
        if response.status_code != 200:
            error_msg = response.json().get('message', 'Ошибка авторизации')
            raise MoyKlassAPIError(f'Ошибка получения токена: {error_msg}')
        
        data = response.json()
        self.settings.access_token = data.get('accessToken')
        expires_at_str = data.get('expiresAt')
        
        if expires_at_str:
            from datetime import datetime
            self.settings.token_expires_at = datetime.fromisoformat(
                expires_at_str.replace('Z', '+00:00')
            )
        else:
            # Если дата не указана, устанавливаем токен на 1 час
            self.settings.token_expires_at = timezone.now() + timezone.timedelta(hours=1)
        
        self.settings.save(update_fields=['access_token', 'token_expires_at'])
        
        return self.settings.access_token
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Выполняет запрос к API
        
        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Endpoint API (без базового URL)
            data: Данные для тела запроса
            params: Параметры URL
        
        Returns:
            Ответ API в виде словаря
        """
        token = self._get_access_token()
        url = f'{self.BASE_URL}/{self.API_VERSION}/{endpoint.lstrip("/")}'
        
        headers = {
            'x-access-token': token,
            'Content-Type': 'application/json'
        }
        
        start_time = time.time()
        
        try:
            response = requests.request(
                method,
                url,
                json=data,
                params=params,
                headers=headers,
                timeout=30
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 401:
                # Токен истек, пробуем обновить
                token = self._refresh_token()
                headers['x-access-token'] = token
                
                response = requests.request(
                    method,
                    url,
                    json=data,
                    params=params,
                    headers=headers,
                    timeout=30
                )
                
                duration_ms = (time.time() - start_time) * 1000
            
            # Проверяем статус ответа
            if response.status_code >= 400:
                error_detail = 'Неизвестная ошибка'
                try:
                    error_data = response.json()
                    if isinstance(error_data, dict):
                        error_detail = error_data.get('message') or error_data.get('error') or error_data.get('detail') or str(error_data)
                    else:
                        error_detail = str(error_data)
                except:
                    error_detail = response.text[:500] if response.text else f'HTTP {response.status_code}'
                
                # Логируем ошибку с полной информацией
                if self.settings.log_requests:
                    self._log_request(method, endpoint, data, response, duration_ms, error_detail)
                
                error_msg = f'Ошибка API: {error_detail} (статус {response.status_code})'
                raise MoyKlassAPIError(error_msg)
            
            # Логируем успешный запрос
            if self.settings.log_requests:
                self._log_request(method, endpoint, data, response, duration_ms)
            
            if response.content:
                return response.json()
            return {}
            
        except MoyKlassAPIError:
            # Пробрасываем ошибки API дальше
            raise
        except requests.exceptions.RequestException as e:
            duration_ms = (time.time() - start_time) * 1000
            if self.settings.log_requests:
                self._log_request(method, endpoint, data, None, duration_ms, str(e))
            raise MoyKlassAPIError(f'Ошибка запроса к API: {str(e)}')
    
    def _log_request(
        self,
        method: str,
        endpoint: str,
        request_data: Optional[Dict],
        response: Optional[requests.Response],
        duration_ms: Optional[float] = None,
        error: Optional[str] = None
    ):
        """Логирует запрос к API"""
        # Формируем данные запроса для лога
        request_data_str = ''
        if request_data:
            try:
                import json
                request_data_str = json.dumps(request_data, ensure_ascii=False, indent=2)
            except:
                request_data_str = str(request_data)
        
        # Формируем данные ответа для лога
        response_text = ''
        if response:
            try:
                if response.text:
                    # Ограничиваем размер для базы данных (2000 символов)
                    response_text = response.text[:2000]
                    # Если ответ обрезан, добавляем пометку
                    if len(response.text) > 2000:
                        response_text += '\n... (обрезано)'
            except Exception as e:
                response_text = f'Ошибка получения ответа: {str(e)}'
        
        # Формируем сообщение об ошибке
        error_message = error or ''
        if response and response.status_code >= 400 and not error_message:
            # Если ошибка не передана, но статус указывает на ошибку, пытаемся извлечь из ответа
            try:
                error_data = response.json()
                if isinstance(error_data, dict):
                    error_message = error_data.get('message') or error_data.get('error') or error_data.get('detail') or ''
            except:
                pass
        
        log = MoyKlassRequestLog(
            method=method,
            endpoint=endpoint,
            request_data=request_data_str,
            response_status=response.status_code if response else None,
            response_data=response_text,
            error_message=error_message,
            duration_ms=duration_ms
        )
        log.save()
    
    # ==================== КОМПАНИЯ ====================
    
    def get_company_info(self) -> Dict[str, Any]:
        """Получает информацию о компании"""
        return self._make_request('GET', '/company')
    
    # ==================== УЧЕНИКИ/ЛИДЫ ====================
    
    def get_students(
        self,
        page: int = 1,
        per_page: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Получает список учеников/лидов
        
        Args:
            page: Номер страницы
            per_page: Количество записей на странице
            filters: Дополнительные фильтры
        """
        params = {'page': page, 'perPage': per_page}
        if filters:
            params.update(filters)
        
        return self._make_request('GET', '/company/users', params=params)
    
    def get_student(self, student_id: int) -> Dict[str, Any]:
        """Получает информацию об ученике"""
        return self._make_request('GET', f'/company/users/{student_id}')
    
    def create_student(self, data: Dict[str, Any], tags: Optional[List[str]] = None, is_lead: bool = True) -> Dict[str, Any]:
        """
        Создает нового ученика/лида
        
        Args:
            data: Данные ученика
            tags: Список тегов для добавления к лиду
            is_lead: Создавать как лида (True) или как клиента (False)
        """
        # Удаляем теги из data, если они там есть (добавим отдельно)
        data_without_tags = {k: v for k, v in data.items() if k != 'tags'}
        
        # Дополнительная нормализация телефона перед отправкой
        if 'phone' in data_without_tags:
            phone = str(data_without_tags['phone']).strip()
            # Удаляем все нецифровые символы
            phone_digits = ''.join(filter(str.isdigit, phone))
            if phone_digits:
                # Проверяем длину
                if len(phone_digits) < 10:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(
                        f'Телефон слишком короткий перед отправкой в MoyKlass: "{phone_digits}" '
                        f'(длина {len(phone_digits)}, требуется 10-15). Исходное значение: "{phone}"'
                    )
                elif len(phone_digits) > 15:
                    phone_digits = phone_digits[:15]
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f'Телефон обрезан до 15 цифр: "{phone_digits}"')
                
                data_without_tags['phone'] = phone_digits
            else:
                # Если не удалось нормализовать, удаляем поле, чтобы не отправлять некорректные данные
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Не удалось нормализовать телефон "{phone}", поле будет удалено из запроса')
                data_without_tags.pop('phone', None)
        
        # Логируем данные перед отправкой
        import logging
        logger = logging.getLogger(__name__)
        logger.debug(f'Отправка данных в MoyKlass для создания лида: {data_without_tags}')
        
        # Создаем пользователя (без тегов)
        # В MoyKlass все созданные через API пользователи по умолчанию являются лидами
        result = self._make_request('POST', '/company/users', data=data_without_tags)
        
        # Если есть теги и пользователь создан, добавляем теги отдельным запросом
        if tags and result.get('id'):
            try:
                self.add_tags_to_student(result['id'], tags)
            except Exception as e:
                # Логируем, но не прерываем выполнение
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(f'Не удалось добавить теги к лиду {result["id"]}: {str(e)}')
        
        return result
    
    def get_tags(self) -> List[Dict[str, Any]]:
        """
        Получает список всех тегов для пользователей (учеников/лидов) компании
        Использует endpoint GET /v1/company/userTags согласно документации MoyKlass API
        
        Returns:
            Список тегов с полями id, name и т.д.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        # Используем правильный endpoint согласно документации MoyKlass API
        # GET /v1/company/userTags - возвращает список тегов для пользователей (учеников/лидов)
        endpoint = '/company/userTags'
        
        try:
            logger.debug(f'Запрос тегов через endpoint: {endpoint}')
            response = self._make_request('GET', endpoint)
            
            # Логируем ответ для отладки
            logger.debug(f'Ответ от API: {type(response)}, keys: {list(response.keys()) if isinstance(response, dict) else "not a dict"}')
            
            # API может возвращать данные в разных форматах
            if isinstance(response, dict):
                # Если это словарь с полем data
                if 'data' in response:
                    tags = response['data']
                    if isinstance(tags, list):
                        logger.info(f'Получено {len(tags)} тегов из {endpoint}')
                        return tags
                # Если это словарь с полем tags
                elif 'tags' in response:
                    tags = response['tags']
                    if isinstance(tags, list):
                        logger.info(f'Получено {len(tags)} тегов из {endpoint}')
                        return tags
                # Если это пагинированный ответ
                elif isinstance(response.get('items'), list):
                    tags = response['items']
                    logger.info(f'Получено {len(tags)} тегов из {endpoint} (пагинация)')
                    return tags
                # Если сам ответ - это массив тегов в каком-то поле
                else:
                    # Проверяем, может быть весь ответ - это массив тегов
                    for key in response.keys():
                        if isinstance(response[key], list):
                            tags = response[key]
                            logger.info(f'Получено {len(tags)} тегов из поля {key}')
                            return tags
            elif isinstance(response, list):
                # Если ответ - это сразу список тегов
                logger.info(f'Получено {len(response)} тегов (прямой список)')
                return response
            
            logger.warning(f'Неожиданный формат ответа от {endpoint}: {type(response)}')
            return []
            
        except Exception as e:
            logger.error(f'Ошибка при получении тегов из {endpoint}: {str(e)}', exc_info=True)
            return []
    
    def find_or_create_tag(self, tag_name: str) -> Optional[int]:
        """
        Находит тег по названию или создает новый
        
        Args:
            tag_name: Название тега
            
        Returns:
            ID тега или None, если не удалось найти/создать
        """
        # Сначала пытаемся найти существующий тег
        tags = self.get_tags()
        for tag in tags:
            if isinstance(tag, dict):
                tag_id = tag.get('id')
                tag_name_from_api = tag.get('name') or tag.get('title')
                if tag_name_from_api and tag_name_from_api.lower() == tag_name.lower():
                    return tag_id
            elif isinstance(tag, str):
                # Если API возвращает просто строки, ищем по названию
                if tag.lower() == tag_name.lower():
                    # Не можем вернуть ID, если API не предоставляет его
                    return None
        
        # Если тег не найден, пытаемся создать его
        try:
            result = self._make_request('POST', '/company/tags', data={'name': tag_name})
            if isinstance(result, dict):
                return result.get('id')
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Не удалось создать тег "{tag_name}": {str(e)}')
        
        return None
    
    def add_tags_to_student(self, student_id: int, tags: List[str]) -> Dict[str, Any]:
        """
        Добавляет теги к ученику/лиду
        
        Args:
            student_id: ID ученика
            tags: Список названий тегов (строки) или ID тегов (целые числа)
        """
        # Преобразуем названия тегов в ID
        tag_ids = []
        for tag in tags:
            if isinstance(tag, int):
                # Уже ID
                tag_ids.append(tag)
            elif isinstance(tag, str):
                # Название тега - нужно найти или создать
                tag_id = self.find_or_create_tag(tag)
                if tag_id:
                    tag_ids.append(tag_id)
                else:
                    import logging
                    logger = logging.getLogger(__name__)
                    logger.warning(f'Не удалось найти или создать тег "{tag}" для пользователя {student_id}')
        
        if not tag_ids:
            # Если не удалось получить ни одного ID тега, возвращаем пустой ответ
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f'Нет валидных ID тегов для добавления к пользователю {student_id}')
            return {}
        
        # Используем endpoint для изменения тегов с ID
        return self._make_request('POST', f'/company/users/{student_id}/tags', data={'tags': tag_ids})
    
    def update_student(self, student_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Обновляет данные ученика"""
        return self._make_request('PUT', f'/company/users/{student_id}', data=data)
    
    # ==================== ПЛАТЕЖИ ====================
    
    def get_payments(
        self,
        page: int = 1,
        per_page: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Получает список платежей"""
        params = {'page': page, 'perPage': per_page}
        if filters:
            params.update(filters)
        
        return self._make_request('GET', '/company/payments', params=params)
    
    def get_payment(self, payment_id: int) -> Dict[str, Any]:
        """Получает информацию о платеже"""
        return self._make_request('GET', f'/company/payments/{payment_id}')
    
    def create_payment(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создает новый платеж"""
        return self._make_request('POST', '/company/payments', data=data)
    
    # ==================== ЗАПИСИ В ГРУППУ ====================
    
    def get_bookings(
        self,
        page: int = 1,
        per_page: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Получает список записей в группы"""
        params = {'page': page, 'perPage': per_page}
        if filters:
            params.update(filters)
        
        return self._make_request('GET', '/company/bookings', params=params)
    
    def get_booking(self, booking_id: int) -> Dict[str, Any]:
        """Получает информацию о записи"""
        return self._make_request('GET', f'/company/bookings/{booking_id}')
    
    def create_booking(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Создает новую запись в группу"""
        return self._make_request('POST', '/company/bookings', data=data)
    
    # ==================== ГРУППЫ ====================
    
    def get_groups(
        self,
        page: int = 1,
        per_page: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Получает список групп"""
        params = {'page': page, 'perPage': per_page}
        if filters:
            params.update(filters)
        
        return self._make_request('GET', '/company/groups', params=params)
    
    def get_group(self, group_id: int) -> Dict[str, Any]:
        """Получает информацию о группе"""
        return self._make_request('GET', f'/company/groups/{group_id}')
    
    # ==================== СОТРУДНИКИ ====================
    
    def get_staff(
        self,
        page: int = 1,
        per_page: int = 50
    ) -> Dict[str, Any]:
        """Получает список сотрудников"""
        params = {'page': page, 'perPage': per_page}
        return self._make_request('GET', '/company/staff', params=params)
    
    def get_staff_member(self, staff_id: int) -> Dict[str, Any]:
        """Получает информацию о сотруднике"""
        return self._make_request('GET', f'/company/staff/{staff_id}')
    
    # ==================== ЗАНЯТИЯ ====================
    
    def get_lessons(
        self,
        page: int = 1,
        per_page: int = 50,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Получает список занятий"""
        params = {'page': page, 'perPage': per_page}
        if filters:
            params.update(filters)
        
        return self._make_request('GET', '/company/lessons', params=params)
    
    def get_lesson(self, lesson_id: int) -> Dict[str, Any]:
        """Получает информацию о занятии"""
        return self._make_request('GET', f'/company/lessons/{lesson_id}')

