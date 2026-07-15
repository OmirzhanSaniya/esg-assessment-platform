export interface User {
    id: number;
    email: string;
    role: 'company' | 'admin';
  }
  
  export interface Company {
    id: number;
    name: string;
    industry: string;
  }
  
  export interface AssessmentResult {
    id: number;
    score_e: number;
    score_s: number;
    score_g: number;
    score_total: number;
    level: string;
    created_at: string;
  }
  
  export interface Question {
    id: number;
    text: string;
    block: 'E' | 'S' | 'G';
    question_type: 'yes_no' | 'single_choice' | 'scale';
    weight: number;
    order: number;
  }
  export interface Sector {
    sector_id: string;
    sector_name: string;
    has_subindustries: boolean;
  }
  
  export interface SubIndustry {
    sector_id: string;
    sub_industry_id: string | null;
    sub_industry_name: string;
  }