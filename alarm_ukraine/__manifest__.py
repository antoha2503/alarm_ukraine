{
    "name": "Alerm in Ukraine",
    "version": "1.0.0",
    "category": "Tools",
    "summary": "Automated Ukraine Air Alert (Повітряна Тривога) tracking in Systray with sound notifications and employee region-based auto-popups. Моніторинг повітряних тривог України безпосередньо в Odoo.",
    "description": """Alerm in Ukraine — модуль для моніторингу повітряних тривог України
        безпосередньо в інтерфейсі Odoo.
        
        Модуль автоматично отримує інформацію про статус повітряної тривоги
        для регіону користувача та оновлює дані кожні 15 секунд.
        
        Передбачено звукове та візуальне сповіщення про початок тривоги,
        а також можливість використання власного API Key.
        
        Джерело даних:
        https://map.ukrainealarm.com""",
    "author": "TytencoSoft",
    "license": "LGPL-3",
    'price': "0",
    'currency': 'USD',
    'images': ['static/description/icon.png'],
    "depends": ['hr','contacts'],
    "data": [
        "views/res_config_settings_views.xml",
        "security/ir.model.access.csv",
        "data/location_data.xml"
    ],
    'assets': {
        'web.assets_backend': [
            'alarm_ukraine/static/src/js/alarm.js',
            'alarm_ukraine/static/src/xml/systray_alarm.xml',
        ],
    },
    "installable": True,
    "autoinstall": False,
}
