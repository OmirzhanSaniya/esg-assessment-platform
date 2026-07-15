import type { Sector, SubIndustry } from '../types';

export const SECTORS: Sector[] = [
  { sector_id: 'energy', sector_name: 'Энергетика (нефть, газ, уголь)', has_subindustries: true },
  { sector_id: 'mining', sector_name: 'Добывающая промышленность и металлургия', has_subindustries: true },
  { sector_id: 'utilities', sector_name: 'Коммунальные услуги (Utilities)', has_subindustries: true },
  { sector_id: 'manufacturing', sector_name: 'Промышленное производство', has_subindustries: true },
  { sector_id: 'construction', sector_name: 'Строительство и недвижимость', has_subindustries: true },
  { sector_id: 'transport', sector_name: 'Транспорт и логистика', has_subindustries: true },
  { sector_id: 'financial', sector_name: 'Финансовые услуги', has_subindustries: true },
  { sector_id: 'tech', sector_name: 'Технологии и ПО', has_subindustries: true },
  { sector_id: 'telecom', sector_name: 'Телекоммуникации и медиа', has_subindustries: true },
  { sector_id: 'retail', sector_name: 'Ритейл и товары народного потребления', has_subindustries: true },
  { sector_id: 'healthcare', sector_name: 'Здравоохранение и фармацевтика', has_subindustries: true },
  { sector_id: 'agriculture', sector_name: 'Сельское хозяйство и производство продуктов питания', has_subindustries: true },
  { sector_id: 'services', sector_name: 'Профессиональные услуги / образование / консалтинг', has_subindustries: false },
  { sector_id: 'other', sector_name: 'Прочее', has_subindustries: false },
];

export const SUB_INDUSTRIES: SubIndustry[] = [
  // energy
  { sector_id: 'energy', sub_industry_id: 'oil_gas', sub_industry_name: 'Нефть и газ (добыча/переработка)' },
  { sector_id: 'energy', sub_industry_id: 'coal', sub_industry_name: 'Уголь' },
  { sector_id: 'energy', sub_industry_id: 'renewables', sub_industry_name: 'Возобновляемая энергетика' },
  { sector_id: 'energy', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // mining
  { sector_id: 'mining', sub_industry_id: 'metal_mining', sub_industry_name: 'Горнодобыча (металлы/руды)' },
  { sector_id: 'mining', sub_industry_id: 'steel', sub_industry_name: 'Металлургия/сталь' },
  { sector_id: 'mining', sub_industry_id: 'chemicals', sub_industry_name: 'Химическая промышленность' },
  { sector_id: 'mining', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // utilities
  { sector_id: 'utilities', sub_industry_id: 'power', sub_industry_name: 'Электроэнергетика' },
  { sector_id: 'utilities', sub_industry_id: 'water', sub_industry_name: 'Водоснабжение и водоотведение' },
  { sector_id: 'utilities', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // manufacturing
  { sector_id: 'manufacturing', sub_industry_id: 'machinery', sub_industry_name: 'Машиностроение' },
  { sector_id: 'manufacturing', sub_industry_id: 'automotive', sub_industry_name: 'Автомобилестроение' },
  { sector_id: 'manufacturing', sub_industry_id: 'aerospace', sub_industry_name: 'Аэрокосмическая и оборонная промышленность' },
  { sector_id: 'manufacturing', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // construction
  { sector_id: 'construction', sub_industry_id: 'residential', sub_industry_name: 'Девелопмент жилой недвижимости' },
  { sector_id: 'construction', sub_industry_id: 'commercial', sub_industry_name: 'Коммерческое строительство' },
  { sector_id: 'construction', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // transport
  { sector_id: 'transport', sub_industry_id: 'aviation', sub_industry_name: 'Авиаперевозки' },
  { sector_id: 'transport', sub_industry_id: 'shipping', sub_industry_name: 'Морские и железнодорожные перевозки' },
  { sector_id: 'transport', sub_industry_id: 'logistics', sub_industry_name: 'Логистика и курьерские услуги' },
  { sector_id: 'transport', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // financial
  { sector_id: 'financial', sub_industry_id: 'banking', sub_industry_name: 'Банки' },
  { sector_id: 'financial', sub_industry_id: 'insurance', sub_industry_name: 'Страхование' },
  { sector_id: 'financial', sub_industry_id: 'asset_mgmt', sub_industry_name: 'Инвестфонды и управление активами' },
  { sector_id: 'financial', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // tech
  { sector_id: 'tech', sub_industry_id: 'software', sub_industry_name: 'Разработка ПО / SaaS' },
  { sector_id: 'tech', sub_industry_id: 'electronics', sub_industry_name: 'Производство электроники / хардвер' },
  { sector_id: 'tech', sub_industry_id: 'semiconductors', sub_industry_name: 'Полупроводники' },
  { sector_id: 'tech', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // telecom
  { sector_id: 'telecom', sub_industry_id: 'telecom_operators', sub_industry_name: 'Телеком-операторы' },
  { sector_id: 'telecom', sub_industry_id: 'media', sub_industry_name: 'Медиа и контент' },
  { sector_id: 'telecom', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // retail
  { sector_id: 'retail', sub_industry_id: 'retail_general', sub_industry_name: 'Розничная торговля (офлайн/онлайн)' },
  { sector_id: 'retail', sub_industry_id: 'apparel', sub_industry_name: 'Производство одежды и текстиля' },
  { sector_id: 'retail', sub_industry_id: 'food_bev', sub_industry_name: 'Продукты питания и напитки' },
  { sector_id: 'retail', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // healthcare
  { sector_id: 'healthcare', sub_industry_id: 'pharma', sub_industry_name: 'Фармацевтика' },
  { sector_id: 'healthcare', sub_industry_id: 'clinics', sub_industry_name: 'Медицинские услуги / клиники' },
  { sector_id: 'healthcare', sub_industry_id: 'biotech', sub_industry_name: 'Биотехнологии' },
  { sector_id: 'healthcare', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // agriculture
  { sector_id: 'agriculture', sub_industry_id: 'crops', sub_industry_name: 'Растениеводство' },
  { sector_id: 'agriculture', sub_industry_id: 'livestock', sub_industry_name: 'Животноводство' },
  { sector_id: 'agriculture', sub_industry_id: 'fishing', sub_industry_name: 'Рыболовство и аквакультура' },
  { sector_id: 'agriculture', sub_industry_id: null, sub_industry_name: 'Другое / не подходит' },

  // services and other have has_subindustries=false, so no rows needed
];