# -*- coding: utf-8 -*-
import requests
import logging
from datetime import datetime, timedelta
from odoo import api, fields, models

_logger = logging.getLogger(__name__)

class EkraineLocations(models.Model):
    _name = 'alarm.ukraine.locations'
    _description = "Ukraine Locations"

    @api.model
    def get_alarm_status(self):
        # 1. Получаем токен из настроек (вторым аргументом идет дефолтный токен, если поле пустое)
        ICPSudo = self.env['ir.config_parameter'].sudo()
        token = ICPSudo.get_param('alarm_ukraine.api_token', 'f6535e88:5a739ba8759c0357eda0b2ceadc7d52c')

        if not token:
            return {
                'city': 'Токен не настроен',
                'alert': False,
                'updated': False
            }

        # 2. Определяем регион сотрудника
        state = self.env.user.employee_id.private_state_id
        try:
            if state:
                regionID = state.code
            else:
                regionID = "31"
        except AttributeError:
            regionID = "14"

        # 3. ПРОВЕРКА КЭША ДЛЯ КОНКРЕТНОГО РЕГИОНА
        # Формируем уникальные ключи кэша для этого региона (например: alarm_ukraine.last_check_31)
        key_last_check = f'alarm_ukraine.last_check_{regionID}'
        key_cached_alert = f'alarm_ukraine.cached_alert_{regionID}'
        key_cached_city = f'alarm_ukraine.cached_city_{regionID}'
        key_cached_updated = f'alarm_ukraine.cached_updated_{regionID}'

        # Достаем данные кэша из ir_config_parameter через DBeaver их тоже можно будет увидеть
        last_check_str = ICPSudo.get_param(key_last_check, '1970-01-01 00:00:00')
        cached_alert = ICPSudo.get_param(key_cached_alert, 'False') == 'True'
        cached_city = ICPSudo.get_param(key_cached_city, 'Не визначено')
        cached_updated = ICPSudo.get_param(key_cached_updated, False)

        try:
            last_check_time = datetime.strptime(last_check_str, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            last_check_time = datetime.fromtimestamp(0)

        # Если прошло меньше 15 секунд — НЕ СТУЧИМСЯ во внешнее API, отдаем кэш!
        if datetime.now() < last_check_time + timedelta(seconds=15) and last_check_str != '1970-01-01 00:00:00':
            return {
                "city": cached_city,
                "alert": cached_alert,
                "updated": cached_updated,
            }

        # 4. ВРЕМЯ ВЫШЛО — ДЕЛАЕМ РЕАЛЬНЫЙ ЗАПРОС К API
        if regionID:
            url = f"https://api.ukrainealarm.com/api/v3/alerts/{regionID}"
        else:
            url = "https://api.ukrainealarm.com/api/v3/alerts"

        headers = {
            "Authorization": token,
            "Accept": "application/json"
        }

        try:
            response = requests.get(url=url, headers=headers, timeout=10)
            response.raise_for_status()
            result = response.json()

            # Парсим ответ от твоего API
            has_alert = bool(result[0].get('activeAlerts'))
            city_data = f"{result[0]['regionName']}"
            api_updated_time = result[0]['lastUpdate']
            current_time_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 5. ПЕРЕЗАПИСЫВАЕМ КЭШ В БАЗУ ДАННЫХ ДЛЯ СЛЕДУЮЩИХ ЗАПРОСОВ
            ICPSudo.set_param(key_last_check, current_time_str)
            ICPSudo.set_param(key_cached_alert, str(has_alert))
            ICPSudo.set_param(key_cached_city, city_data)
            ICPSudo.set_param(key_cached_updated, api_updated_time)

            return {
                "city": city_data,
                "alert": has_alert,
                "updated": api_updated_time,
            }

        except Exception as e:
            # Если внешнее API недоступно или выдало ошибку лимитов — Odoo не падает,
            # а плавно возвращает пользователю последний успешный кэш этого региона.
            _logger.error("Ошибка API Повітряних Тривог для региона %s: %s", regionID, str(e))
            return {
                "city": f"[Кэш] {cached_city}",
                "alert": cached_alert,
                "updated": cached_updated,
            }
