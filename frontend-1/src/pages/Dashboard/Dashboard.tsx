import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { companyAPI, assessmentAPI } from '../../api/client';
import type { AssessmentResult } from '../../types';
import './Dashboard.css';

interface Profile {
  name: string;
  industry: string;
  current_result?: AssessmentResult;
}

const ESG_BLOCKS = ['E', 'S', 'G'] as const;
type EsgBlock = (typeof ESG_BLOCKS)[number];

const BLOCK_LABELS: Record<EsgBlock, string> = {
  E: 'Environmental',
  S: 'Social',
  G: 'Governance',
};

const LEVEL_COLORS: Record<string, string> = {
  'Начальный': '#EF4444',
  'Развивающийся': '#F59E0B',
  'Продвинутый': '#3B82F6',
  'Лидер': '#10B981',
};
const DEFAULT_LEVEL_COLOR = '#6B7280';

function getLevelColor(level: string): string {
  return LEVEL_COLORS[level] ?? DEFAULT_LEVEL_COLOR;
}
