
from odoo import models, fields

class ResConfigSettings(models.TransientModel):
    # Наследуем стандартную модель настроек Odoo
    _inherit = 'res.config.settings'

    alarm_ua_api_token = fields.Char(
        string='API Токен Воздушных Тревог',
        config_parameter='alarm_ukraine.api_token', # Уникальный ключ в БД
        help='Введите ваш персональный токен из документации API'
    )
