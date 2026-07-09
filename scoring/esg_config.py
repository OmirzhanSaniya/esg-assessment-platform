"""
esg_config.py — данные и логика методологии ESG-скоринга.
Синтез LSEG / MSCI / S&P Global CSA / Sustainalytics / Sustainable Fitch.
Порт с JS-версии (esg-config.js) — идентичная логика, чистый Python без внешних зависимостей.

Использование (Django/FastAPI/Flask — без разницы, это чистая логика):
    from esg_config import calculate_esg_score, ESG_CONFIG

    result = calculate_esg_score(
        answers={"E1_1": 75, "E1_2": 40, ...},
        controversy_answers={"C1": False, "C4": True, ...},
        sector_id="tech",
        sub_industry_id="software"
    )
"""

from typing import Optional


# ============================================================
# 1. ВЕСА СЕКТОРОВ (Уровень 1) — сумма E+S+G всегда = 1.0
# ============================================================
SECTORS = [
    {"id": "energy",        "name": "Энергетика (нефть, газ, уголь)",                     "weights": {"E": 0.55, "S": 0.20, "G": 0.25}},
    {"id": "mining",        "name": "Добывающая промышленность и металлургия",            "weights": {"E": 0.50, "S": 0.30, "G": 0.20}},
    {"id": "utilities",     "name": "Коммунальные услуги (Utilities)",                    "weights": {"E": 0.45, "S": 0.25, "G": 0.30}},
    {"id": "manufacturing", "name": "Промышленное производство",                          "weights": {"E": 0.40, "S": 0.30, "G": 0.30}},
    {"id": "construction",  "name": "Строительство и недвижимость",                       "weights": {"E": 0.35, "S": 0.30, "G": 0.35}},
    {"id": "transport",     "name": "Транспорт и логистика",                              "weights": {"E": 0.45, "S": 0.30, "G": 0.25}},
    {"id": "financial",     "name": "Финансовые услуги",                                  "weights": {"E": 0.10, "S": 0.35, "G": 0.55}},
    {"id": "tech",          "name": "Технологии и ПО",                                    "weights": {"E": 0.15, "S": 0.40, "G": 0.45}},
    {"id": "telecom",       "name": "Телекоммуникации и медиа",                           "weights": {"E": 0.15, "S": 0.45, "G": 0.40}},
    {"id": "retail",        "name": "Ритейл и товары народного потребления",              "weights": {"E": 0.25, "S": 0.45, "G": 0.30}},
    {"id": "healthcare",    "name": "Здравоохранение и фармацевтика",                     "weights": {"E": 0.15, "S": 0.45, "G": 0.40}},
    {"id": "agriculture",   "name": "Сельское хозяйство и производство продуктов питания", "weights": {"E": 0.45, "S": 0.35, "G": 0.20}},
    {"id": "services",      "name": "Профессиональные услуги / образование / консалтинг", "weights": {"E": 0.20, "S": 0.40, "G": 0.40}},
    {"id": "other",         "name": "Прочее",                                             "weights": {"E": 0.33, "S": 0.34, "G": 0.33}},
]

# ============================================================
# 2. ПОД-ОТРАСЛИ (Уровень 2, опционально) — override весов сектора
# ============================================================
SUB_INDUSTRIES = {
    "energy": [
        {"id": "oil_gas",    "name": "Нефть и газ (добыча/переработка)", "weights": {"E": 0.60, "S": 0.20, "G": 0.20}},
        {"id": "coal",       "name": "Уголь",                            "weights": {"E": 0.65, "S": 0.15, "G": 0.20}},
        {"id": "renewables", "name": "Возобновляемая энергетика",        "weights": {"E": 0.40, "S": 0.25, "G": 0.35}},
    ],
    "mining": [
        {"id": "metal_mining", "name": "Горнодобыча (металлы/руды)",  "weights": {"E": 0.50, "S": 0.35, "G": 0.15}},
        {"id": "steel",        "name": "Металлургия/сталь",           "weights": {"E": 0.50, "S": 0.30, "G": 0.20}},
        {"id": "chemicals",    "name": "Химическая промышленность",   "weights": {"E": 0.55, "S": 0.25, "G": 0.20}},
    ],
    "utilities": [
        {"id": "power", "name": "Электроэнергетика",             "weights": {"E": 0.50, "S": 0.20, "G": 0.30}},
        {"id": "water", "name": "Водоснабжение и водоотведение", "weights": {"E": 0.40, "S": 0.30, "G": 0.30}},
    ],
    "manufacturing": [
        {"id": "machinery",  "name": "Машиностроение",                             "weights": {"E": 0.40, "S": 0.30, "G": 0.30}},
        {"id": "automotive", "name": "Автомобилестроение",                         "weights": {"E": 0.45, "S": 0.30, "G": 0.25}},
        {"id": "aerospace",  "name": "Аэрокосмическая и оборонная промышленность", "weights": {"E": 0.35, "S": 0.30, "G": 0.35}},
    ],
    "construction": [
        {"id": "residential", "name": "Девелопмент жилой недвижимости", "weights": {"E": 0.30, "S": 0.35, "G": 0.35}},
        {"id": "commercial",  "name": "Коммерческое строительство",    "weights": {"E": 0.40, "S": 0.25, "G": 0.35}},
    ],
    "transport": [
        {"id": "aviation",  "name": "Авиаперевозки",                       "weights": {"E": 0.55, "S": 0.25, "G": 0.20}},
        {"id": "shipping",  "name": "Морские и железнодорожные перевозки", "weights": {"E": 0.45, "S": 0.30, "G": 0.25}},
        {"id": "logistics", "name": "Логистика и курьерские услуги",       "weights": {"E": 0.35, "S": 0.35, "G": 0.30}},
    ],
    "financial": [
        {"id": "banking",    "name": "Банки",                             "weights": {"E": 0.10, "S": 0.30, "G": 0.60}},
        {"id": "insurance",  "name": "Страхование",                       "weights": {"E": 0.10, "S": 0.35, "G": 0.55}},
        {"id": "asset_mgmt", "name": "Инвестфонды и управление активами", "weights": {"E": 0.15, "S": 0.30, "G": 0.55}},
    ],
    "tech": [
        {"id": "software",       "name": "Разработка ПО / SaaS",               "weights": {"E": 0.10, "S": 0.40, "G": 0.50}},
        {"id": "electronics",    "name": "Производство электроники / хардвер", "weights": {"E": 0.30, "S": 0.40, "G": 0.30}},
        {"id": "semiconductors", "name": "Полупроводники",                    "weights": {"E": 0.35, "S": 0.35, "G": 0.30}},
    ],
    "telecom": [
        {"id": "telecom_operators", "name": "Телеком-операторы", "weights": {"E": 0.20, "S": 0.40, "G": 0.40}},
        {"id": "media",             "name": "Медиа и контент",   "weights": {"E": 0.10, "S": 0.50, "G": 0.40}},
    ],
    "retail": [
        {"id": "retail_general", "name": "Розничная торговля (офлайн/онлайн)", "weights": {"E": 0.20, "S": 0.45, "G": 0.35}},
        {"id": "apparel",        "name": "Производство одежды и текстиля",    "weights": {"E": 0.30, "S": 0.50, "G": 0.20}},
        {"id": "food_bev",       "name": "Продукты питания и напитки",        "weights": {"E": 0.35, "S": 0.40, "G": 0.25}},
    ],
    "healthcare": [
        {"id": "pharma",  "name": "Фармацевтика",                "weights": {"E": 0.15, "S": 0.45, "G": 0.40}},
        {"id": "clinics", "name": "Медицинские услуги / клиники", "weights": {"E": 0.10, "S": 0.55, "G": 0.35}},
        {"id": "biotech", "name": "Биотехнологии",               "weights": {"E": 0.15, "S": 0.40, "G": 0.45}},
    ],
    "agriculture": [
        {"id": "crops",     "name": "Растениеводство",            "weights": {"E": 0.45, "S": 0.35, "G": 0.20}},
        {"id": "livestock", "name": "Животноводство",             "weights": {"E": 0.55, "S": 0.30, "G": 0.15}},
        {"id": "fishing",   "name": "Рыболовство и аквакультура", "weights": {"E": 0.50, "S": 0.30, "G": 0.20}},
    ],
    # services и other — без под-отраслей, используются веса сектора
}

# ============================================================
# 3. АНКЕТА — вопросы по категориям
#    type: "scale"   -> ответ 0/25/50/75/100
#    type: "percent" -> числовой % с нормализацией min->0, target->100
# ============================================================
QUESTIONS = [
    # --- E1. Ресурсопользование ---
    {"id": "E1_1", "pillar": "E", "category": "E1", "text": "Есть ли у компании формализованная политика энергоэффективности?", "type": "scale"},
    {"id": "E1_2", "pillar": "E", "category": "E1", "text": "Какая доля потребляемой энергии приходится на возобновляемые источники?", "type": "percent", "min": 0, "target": 100},
    {"id": "E1_3", "pillar": "E", "category": "E1", "text": "Ведётся ли систематический учёт водопотребления?", "type": "scale"},
    {"id": "E1_4", "pillar": "E", "category": "E1", "text": "Есть ли программа снижения материалоёмкости производства/услуг?", "type": "scale"},

    # --- E2. Выбросы и отходы ---
    {"id": "E2_1", "pillar": "E", "category": "E2", "text": "Ведётся ли учёт выбросов парниковых газов (Scope 1 и 2)?", "type": "scale"},
    {"id": "E2_2", "pillar": "E", "category": "E2", "text": "Есть ли у компании публично заявленная цель по снижению выбросов?", "type": "scale"},
    {"id": "E2_3", "pillar": "E", "category": "E2", "text": "Есть ли программа управления отходами (переработка, снижение отходов)?", "type": "scale"},
    {"id": "E2_4", "pillar": "E", "category": "E2", "text": "Проводится ли оценка воздействия деятельности на биоразнообразие?", "type": "scale"},

    # --- E3. Экологические инновации ---
    {"id": "E3_1", "pillar": "E", "category": "E3", "text": "Какая доля выручки приходится на «зелёные» продукты/услуги?", "type": "percent", "min": 0, "target": 30},
    {"id": "E3_2", "pillar": "E", "category": "E3", "text": "Инвестирует ли компания в R&D, направленный на снижение экологического воздействия?", "type": "scale"},

    # --- S1. Персонал ---
    {"id": "S1_1", "pillar": "S", "category": "S1", "text": "Есть ли формализованная система охраны труда и техники безопасности?", "type": "scale"},
    {"id": "S1_2", "pillar": "S", "category": "S1", "text": "Какой процент сотрудников проходит регулярное профессиональное обучение?", "type": "percent", "min": 0, "target": 80},
    {"id": "S1_3", "pillar": "S", "category": "S1", "text": "Публикует ли компания данные по текучести кадров?", "type": "scale"},
    {"id": "S1_4", "pillar": "S", "category": "S1", "text": "Есть ли политика по гендерному/диверсити балансу в найме?", "type": "scale"},

    # --- S2. Права человека и цепочка поставок ---
    {"id": "S2_1", "pillar": "S", "category": "S2", "text": "Есть ли формализованная политика по правам человека?", "type": "scale"},
    {"id": "S2_2", "pillar": "S", "category": "S2", "text": "Проводится ли due diligence поставщиков на предмет трудовых/экологических практик?", "type": "scale"},
    {"id": "S2_3", "pillar": "S", "category": "S2", "text": "Есть ли механизм подачи жалоб для сотрудников/поставщиков (whistleblowing)?", "type": "scale"},

    # --- S3. Сообщество ---
    {"id": "S3_1", "pillar": "S", "category": "S3", "text": "Инвестирует ли компания в локальные сообщества (программы, гранты, партнёрства)?", "type": "scale"},
    {"id": "S3_2", "pillar": "S", "category": "S3", "text": "Оценивается ли социальное воздействие деятельности компании на местные сообщества?", "type": "scale"},

    # --- S4. Ответственность за продукт ---
    {"id": "S4_1", "pillar": "S", "category": "S4", "text": "Есть ли формализованная система контроля качества и безопасности продукции?", "type": "scale"},
    {"id": "S4_2", "pillar": "S", "category": "S4", "text": "Есть ли политика защиты персональных данных клиентов?", "type": "scale"},
    {"id": "S4_3", "pillar": "S", "category": "S4", "text": "Проводится ли проверка маркетинговых материалов на предмет вводящих в заблуждение заявлений?", "type": "scale"},

    # --- G1. Менеджмент ---
    {"id": "G1_1", "pillar": "G", "category": "G1", "text": "Какая доля независимых директоров в составе совета?", "type": "percent", "min": 0, "target": 50},
    {"id": "G1_2", "pillar": "G", "category": "G1", "text": "Есть ли комитет по устойчивому развитию/ESG на уровне совета директоров?", "type": "scale"},
    {"id": "G1_3", "pillar": "G", "category": "G1", "text": "Какая доля женщин в составе совета директоров?", "type": "percent", "min": 0, "target": 40},

    # --- G2. Права акционеров ---
    {"id": "G2_1", "pillar": "G", "category": "G2", "text": "Обеспечено ли равное право голоса для всех акционеров (один голос — одна акция)?", "type": "scale"},
    {"id": "G2_2", "pillar": "G", "category": "G2", "text": "Есть ли прозрачная политика вознаграждения руководства, привязанная к ESG-показателям?", "type": "scale"},

    # --- G3. CSR-стратегия и этика ---
    {"id": "G3_1", "pillar": "G", "category": "G3", "text": "Есть ли формализованная антикоррупционная политика?", "type": "scale"},
    {"id": "G3_2", "pillar": "G", "category": "G3", "text": "Публикует ли компания ежегодный ESG/устойчивый отчёт?", "type": "scale"},
    {"id": "G3_3", "pillar": "G", "category": "G3", "text": "Есть ли независимая верификация ESG-отчётности третьей стороной?", "type": "scale"},
]

# ============================================================
# 4. CONTROVERSY OVERLAY — негативные флаги
# ============================================================
CONTROVERSY_FLAGS = [
    {"id": "C1", "text": "Компания вовлечена в производство спорных видов вооружений", "severity": 4},
    {"id": "C2", "text": "Более 30% выручки — тепловой уголь / нефтеносные пески", "severity": 3},
    {"id": "C3", "text": "Доказанные системные нарушения прав человека в цепочке поставок", "severity": 3},
    {"id": "C4", "text": "Крупные штрафы регулятора за экологические нарушения за последние 3 года", "severity": 2},
    {"id": "C5", "text": "Судимость/санкции руководства за коррупцию за последние 5 лет", "severity": 3},
    {"id": "C6", "text": "Крупная утечка персональных данных клиентов за последний год", "severity": 2},
    {"id": "C7", "text": "Массовые трудовые споры / забастовки, связанные с условиями труда", "severity": 1},
    {"id": "C8", "text": "Отсутствие какой-либо экологической политики при высокой материальности E для отрасли", "severity": 1},
]

# Cap на итоговый скор в зависимости от максимальной сработавшей severity
SEVERITY_CAPS = {0: 100, 1: 90, 2: 75, 3: 55, 4: 35}

# ============================================================
# 5. ТИРЫ ЗРЕЛОСТИ
# ============================================================
TIERS = [
    {"min": 85, "max": 100, "label": "Тир 1 — Лидирующий"},
    {"min": 70, "max": 84,  "label": "Тир 2 — Продвинутый"},
    {"min": 55, "max": 69,  "label": "Тир 3 — Развивающийся"},
    {"min": 40, "max": 54,  "label": "Тир 4 — Базовый"},
    {"min": 0,  "max": 39,  "label": "Тир 5 — Отстающий / высокий риск"},
]

# Общий конфиг-объект, если удобнее импортировать одним куском (аналог ESG_CONFIG из JS)
ESG_CONFIG = {
    "sectors": SECTORS,
    "subIndustries": SUB_INDUSTRIES,
    "questions": QUESTIONS,
    "controversyFlags": CONTROVERSY_FLAGS,
    "severityCaps": SEVERITY_CAPS,
    "tiers": TIERS,
}

# Пилар для каждой категории — вычисляется из QUESTIONS автоматически
CATEGORY_PILLAR = {}
for _q in QUESTIONS:
    CATEGORY_PILLAR[_q["category"]] = _q["pillar"]

# Человекочитаемые названия категорий (для текста роадмапа)
CATEGORY_NAMES = {
    "E1": "Ресурсопользование",
    "E2": "Выбросы и отходы",
    "E3": "Экологические инновации",
    "S1": "Персонал",
    "S2": "Права человека и цепочка поставок",
    "S3": "Сообщество",
    "S4": "Ответственность за продукт",
    "G1": "Менеджмент",
    "G2": "Права акционеров",
    "G3": "CSR-стратегия и этика",
}

# Горизонт внедрения по умолчанию для каждой категории (см. раздел 9.3 методологии)
CATEGORY_HORIZON = {
    "E1": "mid",
    "E2": "long",
    "E3": "long",
    "S1": "mid",
    "S2": "mid",
    "S3": "quick",
    "S4": "mid",
    "G1": "long",
    "G2": "long",
    "G3": "quick",
}

HORIZON_LABELS = {
    "quick": "Быстро (недели)",
    "mid": "Средне (месяцы)",
    "long": "Долго / структурно (год+)",
}

# ============================================================
# 6. БИБЛИОТЕКА ШАБЛОНОВ РОАДМАПА
#    Три текста на категорию — в зависимости от диапазона балла
# ============================================================
ROADMAP_TEMPLATES = {
    "E1": {
        "0-25": "Формализуйте политику энергоэффективности и начните систематический учёт потребления энергии, воды и материалов — сейчас практика отсутствует полностью.",
        "25-50": "Переведите план по энергоэффективности из намерения в задокументированную политику с конкретными шагами и ответственными.",
        "50-75": "Существующая программа ресурсоэффективности внедрена частично — усильте её количественными целями (например, % снижения потребления энергии/воды в год).",
    },
    "E2": {
        "0-25": "Начните вести учёт выбросов парниковых газов (Scope 1 и 2) — без базовой линии невозможно ставить цели по снижению.",
        "25-50": "Учёт выбросов есть в зачаточном виде — установите публично заявленную количественную цель по снижению на 3–5 лет.",
        "50-75": "Программа управления выбросами и отходами частично внедрена — добавьте оценку воздействия на биоразнообразие и переработку отходов.",
    },
    "E3": {
        "0-25": "Начните инвестировать в R&D, направленный на снижение экологического воздействия продуктов/услуг.",
        "25-50": "Доля «зелёной» выручки минимальна — определите, какие продукты/услуги можно классифицировать как экологичные, и увеличивайте их долю.",
        "50-75": "Экологические инновации есть, но не систематизированы — оформите отдельную R&D-стратегию с измеримыми целями по зелёной выручке.",
    },
    "S1": {
        "0-25": "Внедрите формализованную систему охраны труда и техники безопасности — это база, без которой остальные S-метрики не имеют смысла.",
        "25-50": "Система охраны труда в начальной стадии — добавьте регулярное обучение персонала и начните публиковать данные по текучести кадров.",
        "50-75": "Практики по персоналу внедрены частично — усильте политику диверсити в найме и расширьте охват обучения.",
    },
    "S2": {
        "0-25": "Разработайте формализованную политику по правам человека и начните due diligence поставщиков — сейчас проверка цепочки поставок не проводится.",
        "25-50": "Политика по правам человека есть, но due diligence поставщиков не систематизирован — внедрите регулярный аудит ключевых поставщиков.",
        "50-75": "Due diligence поставщиков частично внедрён — добавьте механизм подачи жалоб (whistleblowing) для сотрудников и поставщиков.",
    },
    "S3": {
        "0-25": "Начните инвестировать в локальные сообщества — программы, гранты или партнёрства с местными организациями.",
        "25-50": "Взаимодействие с сообществом эпизодическое — сформируйте регулярную программу с измеримым бюджетом.",
        "50-75": "Программы для сообщества есть — добавьте оценку их социального воздействия, чтобы показывать результат, а не только факт участия.",
    },
    "S4": {
        "0-25": "Внедрите систему контроля качества и безопасности продукции, а также политику защиты персональных данных клиентов.",
        "25-50": "Базовые практики есть, но не задокументированы — формализуйте политику защиты данных и контроля качества.",
        "50-75": "Ответственность за продукт внедрена частично — добавьте проверку маркетинговых материалов на предмет вводящих в заблуждение заявлений.",
    },
    "G1": {
        "0-25": "Пересмотрите структуру совета директоров — увеличьте долю независимых директоров и создайте ESG-комитет на уровне совета.",
        "25-50": "Совет директоров частично соответствует практикам управления — увеличьте гендерное разнообразие и независимость состава.",
        "50-75": "Структура управления в целом развита — для дальнейшего роста добавьте формальный ESG-комитет, если его ещё нет.",
    },
    "G2": {
        "0-25": "Обеспечьте равные права голоса для всех акционеров и разработайте прозрачную политику вознаграждения руководства.",
        "25-50": "Права акционеров частично защищены — привяжите вознаграждение руководства к измеримым ESG-показателям.",
        "50-75": "Практики в целом соответствуют стандартам — для лидирующего уровня добавьте более детальное раскрытие политики вознаграждения.",
    },
    "G3": {
        "0-25": "Разработайте формализованную антикоррупционную политику и начните публиковать ежегодный ESG-отчёт.",
        "25-50": "ESG-отчётность существует в базовом виде — добавьте независимую верификацию отчёта третьей стороной.",
        "50-75": "CSR-стратегия развита частично — усильте её независимой верификацией и более детальным раскрытием.",
    },
}

DISCLOSURE_TEMPLATE = (
    "По категории «{name}» недостаточно раскрытых данных в анкете (менее 50% вопросов с содержательным ответом). "
    "Вероятно, часть практик уже существует — начните систематически документировать и раскрывать данные по этой категории, "
    "прежде чем внедрять что-то новое."
)

CONTROVERSY_TEMPLATES = {
    "C1": "Вовлечённость в производство спорных видов вооружений — критический риск, требующий немедленного пересмотра бизнес-модели или сегмента деятельности.",
    "C2": "Более 30% выручки от теплового угля/нефтеносных песков — существенный риск для E-рейтинга; требуется стратегия диверсификации или декарбонизации.",
    "C3": "Системные нарушения прав человека в цепочке поставок — требуется немедленный аудит поставщиков и корректирующие меры.",
    "C4": "Крупные экологические штрафы за последние 3 года — требуется анализ первопричин и программа предотвращения повторных нарушений.",
    "C5": "Коррупционные санкции в отношении руководства — требуется усиление комплаенс-контроля и пересмотр политики этики.",
    "C6": "Крупная утечка персональных данных — требуется аудит систем защиты данных и пересмотр политики кибербезопасности.",
    "C7": "Массовые трудовые споры — требуется анализ условий труда и диалог с представителями сотрудников.",
    "C8": "Отсутствие экологической политики при высокой материальности E для отрасли — приоритетный пробел, требующий немедленной разработки политики.",
}


def _score_bracket(score: float) -> str:
    if score < 25:
        return "0-25"
    if score < 50:
        return "25-50"
    return "50-75"


PILLAR_LABELS = {
    "E": "Environment",
    "S": "Social",
    "G": "Governance",
}


def generate_summary_conclusion(result: dict) -> str:
    """
    Собирает связный текст-вывод (1-2 предложения) по итогам скоринга.
    Полностью rule-based: берёт тир, самый сильный/слабый столп и severity контроверсий
    из уже посчитанного result (calculate_esg_score()), без каких-либо LLM-вызовов.
    """
    pillar_scores = result["pillar_scores"]
    tier = result["tier"]
    esg_final = result["esg_final"]
    severity = result.get("controversy_severity", 0)

    strongest = max(pillar_scores, key=pillar_scores.get)
    weakest = min(pillar_scores, key=pillar_scores.get)

    parts = [
        f"Компания демонстрирует уровень ESG-зрелости «{tier}» (итоговый балл {esg_final})."
    ]

    if pillar_scores[strongest] - pillar_scores[weakest] >= 5:
        parts.append(
            f"Сильнее всего развит столп {PILLAR_LABELS[strongest]} "
            f"({pillar_scores[strongest]:.1f} баллов), наибольшего внимания требует "
            f"{PILLAR_LABELS[weakest]} ({pillar_scores[weakest]:.1f} баллов)."
        )
    else:
        parts.append("Баллы по всем трём столпам (Environment, Social, Governance) примерно на одном уровне.")

    if severity >= 3:
        parts.append(
            "⚠️ Обнаружены серьёзные контроверсии, которые ограничивают итоговую оценку — "
            "их устранение должно быть приоритетом до дальнейшего развития остальных направлений."
        )
    elif severity > 0:
        parts.append(
            "Обнаружены контроверсии с умеренным влиянием на рейтинг — рекомендуется обратить на них внимание."
        )

    return " ".join(parts)


def generate_roadmap(result: dict) -> dict:
    """
    Строит роадмап на основе результата calculate_esg_score().
    Полностью rule-based, без LLM — детерминированный вывод для одинаковых входных данных.
    """
    category_scores = result["category_scores"]
    disclosure_flags = result["disclosure_flags"]
    weights = result["weights"]

    recommendations = []
    for cat_id, score in category_scores.items():
        if score >= 60:
            continue  # категория в порядке, рекомендация не нужна

        pillar = CATEGORY_PILLAR.get(cat_id)
        is_disclosure_gap = disclosure_flags.get(cat_id, False)

        if is_disclosure_gap:
            text = DISCLOSURE_TEMPLATE.format(name=CATEGORY_NAMES.get(cat_id, cat_id))
            horizon = "quick"
        else:
            bracket = _score_bracket(score)
            text = ROADMAP_TEMPLATES.get(cat_id, {}).get(bracket, "")
            horizon = CATEGORY_HORIZON.get(cat_id, "mid")

        priority_score = weights.get(pillar, 0) * (100 - score)

        recommendations.append({
            "category": cat_id,
            "category_name": CATEGORY_NAMES.get(cat_id, cat_id),
            "pillar": pillar,
            "score": round(score, 1),
            "is_disclosure_gap": is_disclosure_gap,
            "horizon": horizon,
            "horizon_label": HORIZON_LABELS.get(horizon, horizon),
            "priority_score": round(priority_score, 2),
            "text": text,
        })

    recommendations.sort(key=lambda r: r["priority_score"], reverse=True)

    controversy_warnings = []
    # Восстанавливаем, какие флаги сработали, из severity — если severity > 0, ищем флаги этой или большей severity.
    # Для точного списка сработавших флагов лучше передавать controversy_answers отдельно (см. generate_roadmap_from_answers).
    grouped_by_horizon = {"quick": [], "mid": [], "long": []}
    for rec in recommendations:
        grouped_by_horizon[rec["horizon"]].append(rec)

    return {
        "summary": {
            "esg_final": result["esg_final"],
            "tier": result["tier"],
            "conclusion": generate_summary_conclusion(result),
        },
        "pillar_breakdown": result["pillar_scores"],
        "controversy_severity": result["controversy_severity"],
        "top_priority_actions": recommendations[:3],
        "recommendations_by_horizon": grouped_by_horizon,
        "all_recommendations": recommendations,
    }


def generate_roadmap_from_answers(result: dict, controversy_answers: dict) -> dict:
    """
    То же самое, что generate_roadmap(), но дополнительно включает точный список
    сработавших controversy-флагов с их текстовыми предупреждениями (раздел 9.1, пункт 3).
    Используй эту функцию вместо generate_roadmap(), если под рукой есть controversy_answers
    (обычно — да, это тот же словарь, что передавался в calculate_esg_score()).
    """
    roadmap = generate_roadmap(result)

    controversy_warnings = []
    for flag in CONTROVERSY_FLAGS:
        if controversy_answers.get(flag["id"]) is True:
            controversy_warnings.append({
                "id": flag["id"],
                "severity": flag["severity"],
                "text": CONTROVERSY_TEMPLATES.get(flag["id"], flag["text"]),
            })
    controversy_warnings.sort(key=lambda w: w["severity"], reverse=True)

    roadmap["controversy_warnings"] = controversy_warnings
    return roadmap


# ============================================================
# ЛОГИКА РАСЧЁТА
# ============================================================

def normalize_answer(question: dict, answer) -> Optional[float]:
    """
    Нормализует ответ на один вопрос анкеты в шкалу 0-100.
    answer: для "scale" — число 0/25/50/75/100 или None (нет данных)
            для "percent" — число (например, 45) или None
    """
    if answer is None or answer == "":
        return None
    if question["type"] == "scale":
        return max(0.0, min(100.0, float(answer)))
    if question["type"] == "percent":
        min_v = question["min"]
        target = question["target"]
        value = float(answer)
        if target == min_v:
            return 100.0 if value >= target else 0.0
        ratio = (value - min_v) / (target - min_v)
        return max(0.0, min(100.0, ratio * 100.0))
    return None


def calculate_category_and_pillar_scores(answers: dict):
    """
    answers: {question_id: raw_answer_value}
    Возвращает (category_scores: dict, pillar_scores: dict, disclosure_flags: dict)
    """
    by_category = {}

    for q in QUESTIONS:
        cat = q["category"]
        if cat not in by_category:
            by_category[cat] = {"pillar": q["pillar"], "scores": [], "answered_count": 0, "total": 0}
        norm = normalize_answer(q, answers.get(q["id"]))
        by_category[cat]["total"] += 1
        if norm is not None:
            by_category[cat]["scores"].append(norm)
            by_category[cat]["answered_count"] += 1

    category_scores = {}
    disclosure_flags = {}

    for cat_id, data in by_category.items():
        avg = sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0.0
        disclosure_ratio = data["answered_count"] / data["total"] if data["total"] else 0.0
        disclosure_multiplier = 0.8 if disclosure_ratio < 0.5 else 1.0
        disclosure_flags[cat_id] = disclosure_ratio < 0.5
        category_scores[cat_id] = avg * disclosure_multiplier

    # Группируем категории по столпам, простое среднее внутри столпа (равные веса категорий)
    pillar_buckets = {"E": [], "S": [], "G": []}
    for cat_id, data in by_category.items():
        pillar_buckets[data["pillar"]].append(category_scores[cat_id])

    pillar_scores = {
        pillar: (sum(scores) / len(scores) if scores else 0.0)
        for pillar, scores in pillar_buckets.items()
    }

    return category_scores, pillar_scores, disclosure_flags


def get_weights(sector_id: str, sub_industry_id: Optional[str] = None) -> dict:
    """Возвращает веса {E,S,G} для выбранного сектора/под-отрасли."""
    if sub_industry_id:
        subs = SUB_INDUSTRIES.get(sector_id, [])
        for sub in subs:
            if sub["id"] == sub_industry_id:
                return sub["weights"]
    for sector in SECTORS:
        if sector["id"] == sector_id:
            return sector["weights"]
    return next(s["weights"] for s in SECTORS if s["id"] == "other")


def calculate_controversy_cap(controversy_answers: dict) -> dict:
    """
    controversy_answers: {flag_id: True/False}
    Возвращает {"severity": int, "cap": float}
    """
    max_severity = 0
    for flag in CONTROVERSY_FLAGS:
        if controversy_answers.get(flag["id"]) is True:
            max_severity = max(max_severity, flag["severity"])
    return {"severity": max_severity, "cap": SEVERITY_CAPS[max_severity]}


def get_tier(score: float) -> str:
    # Проверяем только нижнюю границу (TIERS отсортирован по убыванию min) —
    # раньше проверка "min <= score <= max" создавала разрыв между целыми границами
    # (например, 84.9 не попадал ни в Тир 1 [85-100], ни корректно в Тир 2 из-за max=84),
    # из-за чего дробные баллы (а esg_final почти всегда дробный) проваливались в "Не определён".
    for tier in TIERS:
        if score >= tier["min"]:
            return tier["label"]
    return TIERS[-1]["label"]


def calculate_esg_score(
    answers: dict,
    controversy_answers: dict,
    sector_id: str,
    sub_industry_id: Optional[str] = None,
) -> dict:
    """
    Главная функция — считает всё целиком.
    answers: {question_id: value}
    controversy_answers: {flag_id: True/False}
    sector_id, sub_industry_id: строки id
    """
    category_scores, pillar_scores, disclosure_flags = calculate_category_and_pillar_scores(answers)
    weights = get_weights(sector_id, sub_industry_id)

    esg_raw = (
        weights["E"] * pillar_scores["E"]
        + weights["S"] * pillar_scores["S"]
        + weights["G"] * pillar_scores["G"]
    )

    controversy_result = calculate_controversy_cap(controversy_answers or {})
    severity = controversy_result["severity"]
    cap = controversy_result["cap"]
    esg_final = min(esg_raw, cap)

    return {
        "category_scores": category_scores,
        "pillar_scores": pillar_scores,
        "weights": weights,
        "esg_raw": round(esg_raw, 1),
        "controversy_severity": severity,
        "controversy_cap": cap,
        "esg_final": round(esg_final, 1),
        "tier": get_tier(esg_final),
        "disclosure_flags": disclosure_flags,  # категории со штрафом за нераскрытие — использовать в роадмапе
    }
