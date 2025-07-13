export type TabType = 'calculator' | 'results';
export type Gender = 'male' | 'female';
export type ActivityLevel = 'sedentary' | 'light' | 'moderate' | 'high' | 'extreme';
export type Goal = 'maintain' | 'cut' | 'bulk';
export type Formula = 'mifflin' | 'harris' | 'katch';
export type DietType = 'equilibre' | 'low_carb' | 'keto';
export type DietIntensity = 'moderate' | 'intensive';

export interface DietPreset {
  name: string;
  description: string;
  proteinGPerKg: number;
  carbPercentage: number;
  benefits: string[];
  isOptimal?: boolean;
}

export interface BasicUserData {
  age: number;
  gender: Gender;
  weight: number;
  height: number;
  activityLevel: ActivityLevel;
  goal: Goal;
}

export interface AdvancedUserData extends BasicUserData {
  bodyFat?: number | undefined;
  workoutDays: number;
  workoutIntensity: 'low' | 'moderate' | 'high';
  workoutDuration: number;
  hasCardio: boolean;
  cardioMinutes: number;
  formula: Formula;
  dietIntensity: DietIntensity;
  useAdvancedMode: boolean; // 🆕 Toggle mode avancé
}

export interface MacroLocks {
  protein: boolean;
  carbs: boolean;
  fats: boolean;
}

export interface CalorieResults {
  bmr: number;
  tdee: number;
  goalCalories: number;
  macros: {
    protein: { grams: number; calories: number; percentage: number };
    carbs: { grams: number; calories: number; percentage: number };
    fats: { grams: number; calories: number; percentage: number };
  };
  weeklyWeightChange: number;
  dietType: DietType;
  dietIntensity: DietIntensity;
  proteinPerKg: number;
  macroLocks: MacroLocks;
  // 🆕 Détails des calculs
  calculationDetails: {
    bmrFormula: string;
    activityMultiplier: number;
    workoutAdjustment: number;
    goalAdjustment: number;
    formulaUsed: Formula;
  };
}

export interface CalorieCalculatorState {
  activeTab: TabType;
  userData: AdvancedUserData;
  results: CalorieResults | null;
  isCalculated: boolean;
  selectedDiet: DietType;
  macroLocks: MacroLocks;
  showAdvanced: boolean; // 🆕 État accordéon
}

export interface CalorieCalculatorProps {
  className?: string;
  initialTab?: TabType;
  showExport?: boolean;
  variant?: 'full' | 'embedded' | 'minimal';
}

export interface CalorieCalculatorHook {
  activeTab: TabType;
  userData: AdvancedUserData;
  results: CalorieResults | null;
  isCalculated: boolean;
  selectedDiet: DietType;
  macroLocks: MacroLocks;
  showAdvanced: boolean; // 🆕
  setActiveTab: (tab: TabType) => void;
  updateUserData: (updates: Partial<AdvancedUserData>) => void;
  calculateCalories: () => void;
  resetCalculator: () => void;
  isBasicDataValid: boolean;
  isAdvancedDataValid: boolean;
  canCalculate: boolean;
  getExportData: () => ExportData | null;
  changeDietType: (dietType: DietType) => void;
  changeGoal: (goal: Goal) => void;
  changeDietIntensity: (intensity: DietIntensity) => void;
  adjustMacro: (macroType: 'protein' | 'carbs' | 'fats', percentage: number) => void;
  toggleMacroLock: (macroType: 'protein' | 'carbs' | 'fats') => void;
  toggleAdvancedMode: () => void; // 🆕
}

export interface ExportData {
  userData: AdvancedUserData;
  results: CalorieResults;
  calculatedAt: Date;
  formula: string;
}

export interface GoalConfig {
  label: string;
  emoji: string;
  color: string;
  description: string;
}

export interface DietIntensityConfig {
  label: string;
  description: string;
  weeklyTarget: string;
  emoji: string;
}

export const GOAL_CONFIG: Record<Goal, GoalConfig> = {
  cut: {
    label: 'Perte de poids',
    emoji: '📉',
    color: 'text-red-600 bg-red-50 border-red-200',
    description: 'Déficit calorique pour perdre du gras'
  },
  bulk: {
    label: 'Prise de masse',
    emoji: '📈',
    color: 'text-green-600 bg-green-50 border-green-200',
    description: 'Surplus calorique pour prendre du muscle'
  },
  maintain: {
    label: 'Maintien du poids',
    emoji: '⚖️',
    color: 'text-blue-600 bg-blue-50 border-blue-200',
    description: 'Équilibre pour maintenir sa composition'
  }
};

export const DIET_INTENSITY_CONFIG: Record<DietIntensity, DietIntensityConfig> = {
  moderate: {
    label: 'Modérée',
    description: 'Progression douce et durable',
    weeklyTarget: '0.5 kg/semaine',
    emoji: '🐌'
  },
  intensive: {
    label: 'Intensive',
    description: 'Progression rapide et marquée',
    weeklyTarget: '1.0 kg/semaine',
    emoji: '🚀'
  }
};

export const DIET_PRESETS: Record<DietType, DietPreset> = {
  equilibre: {
    name: 'Équilibré',
    description: 'Régime polyvalent avec glucides modérés (35%)',
    proteinGPerKg: 2.0,
    carbPercentage: 35,
    benefits: [
      'Facile à suivre au quotidien',
      'Performance sportive maintenue', 
      'Flexibilité alimentaire maximale',
      'Adapté à tous les objectifs'
    ]
  },
  low_carb: {
    name: 'Low Carb',
    description: 'Glucides réduits pour contrôle glycémique (15%)',
    proteinGPerKg: 2.0,
    carbPercentage: 15,
    benefits: [
      'Satiété élevée et durable',
      'Contrôle de la glycémie',
      'Perte de graisse facilitée',
      'Réduction des fringales'
    ],
    isOptimal: true
  },
  keto: {
    name: 'Cétogène',
    description: 'Très faible en glucides pour cétose (5%)',
    proteinGPerKg: 2.0,
    carbPercentage: 5,
    benefits: [
      'Cétose métabolique',
      'Clarté mentale accrue',
      'Stabilité énergétique',
      'Perte de poids rapide'
    ]
  }
};

export function getOptimalDiet(goal: Goal): DietType {
  switch (goal) {
    case 'cut':
      return 'low_carb';
    case 'bulk':
      return 'equilibre';
    case 'maintain':
    default:
      return 'low_carb';
  }
}