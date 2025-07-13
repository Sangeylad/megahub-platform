import type { AdvancedUserData, CalorieResults, ActivityLevel, Goal, Formula, DietType, MacroLocks, DietIntensity } from '../types';
import { DIET_PRESETS, getOptimalDiet } from '../types';

export function calculateBMR(userData: AdvancedUserData): number {
  const { age, gender, weight, height, bodyFat, formula } = userData;

  switch (formula) {
    case 'mifflin':
      if (gender === 'male') {
        return 10 * weight + 6.25 * height - 5 * age + 5;
      } else {
        return 10 * weight + 6.25 * height - 5 * age - 161;
      }

    case 'harris':
      if (gender === 'male') {
        return 88.362 + (13.397 * weight) + (4.799 * height) - (5.677 * age);
      } else {
        return 447.593 + (9.247 * weight) + (3.098 * height) - (4.330 * age);
      }

    case 'katch':
      if (bodyFat && bodyFat > 0) {
        const leanMass = weight * (1 - bodyFat / 100);
        return 370 + (21.6 * leanMass);
      }
      return calculateBMR({ ...userData, formula: 'mifflin' });

    default:
      return calculateBMR({ ...userData, formula: 'mifflin' });
  }
}

export function getActivityMultiplier(activityLevel: ActivityLevel): number {
  const multipliers = {
    sedentary: 1.2,
    light: 1.375,
    moderate: 1.55,
    high: 1.725,
    extreme: 1.9
  };
  return multipliers[activityLevel];
}

export function getWorkoutAdjustment(userData: AdvancedUserData): number {
  if (!userData.useAdvancedMode) return 0;

  const { workoutDays, workoutIntensity, workoutDuration, hasCardio, cardioMinutes } = userData;
  let adjustment = 0;

  const intensityMultiplier = {
    low: 0.05,
    moderate: 0.08,
    high: 0.12
  };

  const workoutCalories = workoutDays * workoutDuration * intensityMultiplier[workoutIntensity];
  adjustment += workoutCalories;

  if (hasCardio && cardioMinutes > 0) {
    const cardioCalories = (cardioMinutes * 7) * 0.1;
    adjustment += cardioCalories;
  }

  return adjustment;
}

export function calculateGoalCalories(tdee: number, goal: Goal, intensity: DietIntensity = 'moderate'): number {
  switch (goal) {
    case 'cut':
      return intensity === 'moderate' 
        ? Math.round(tdee - 500)
        : Math.round(tdee - 1000);
    case 'bulk':
      return intensity === 'moderate'
        ? Math.round(tdee + 300)
        : Math.round(tdee + 500);
    case 'maintain':
    default:
      return Math.round(tdee);
  }
}

export function calculateMacros(
  goalCalories: number, 
  weight: number, 
  dietType: DietType = 'equilibre'
): {
  protein: { grams: number; calories: number; percentage: number };
  carbs: { grams: number; calories: number; percentage: number };
  fats: { grams: number; calories: number; percentage: number };
  proteinPerKg: number;
} {
  const dietPreset = DIET_PRESETS[dietType];
  
  const proteinGrams = Math.round(weight * dietPreset.proteinGPerKg);
  const proteinCalories = proteinGrams * 4;
  
  const carbCalories = Math.round(goalCalories * (dietPreset.carbPercentage / 100));
  const carbGrams = Math.round(carbCalories / 4);
  
  const fatCalories = goalCalories - proteinCalories - carbCalories;
  const fatGrams = Math.round(fatCalories / 9);

  return {
    protein: {
      grams: proteinGrams,
      calories: proteinCalories,
      percentage: Math.round((proteinCalories / goalCalories) * 100)
    },
    carbs: {
      grams: carbGrams,
      calories: carbCalories,
      percentage: dietPreset.carbPercentage
    },
    fats: {
      grams: fatGrams,
      calories: fatCalories,
      percentage: Math.round((fatCalories / goalCalories) * 100)
    },
    proteinPerKg: dietPreset.proteinGPerKg
  };
}

interface CurrentMacros {
  protein: { grams: number; calories: number; percentage: number };
  carbs: { grams: number; calories: number; percentage: number };
  fats: { grams: number; calories: number; percentage: number };
}

export function calculateMacrosWithLocks(
  goalCalories: number,
  weight: number,
  currentMacros: CurrentMacros,
  macroLocks: MacroLocks,
  changedMacro?: 'protein' | 'carbs' | 'fats',
  newPercentage?: number
): {
  protein: { grams: number; calories: number; percentage: number };
  carbs: { grams: number; calories: number; percentage: number };
  fats: { grams: number; calories: number; percentage: number };
  proteinPerKg: number;
} {
  const lockedCount = Object.values(macroLocks).filter(Boolean).length;
  
  if (lockedCount >= 3) {
    return {
      ...currentMacros,
      proteinPerKg: Math.round((currentMacros.protein.grams / weight) * 10) / 10
    };
  }
  
  const newMacros = { ...currentMacros };
  
  if (changedMacro && newPercentage !== undefined) {
    const newCalories = (goalCalories * newPercentage) / 100;
    const divisor = changedMacro === 'fats' ? 9 : 4;
    
    newMacros[changedMacro] = {
      calories: Math.round(newCalories),
      grams: Math.round(newCalories / divisor),
      percentage: Math.round(newPercentage)
    };
  }
  
  const usedCalories = Object.keys(macroLocks).reduce((sum, macro) => {
    if (macroLocks[macro as keyof MacroLocks]) {
      return sum + newMacros[macro as keyof typeof newMacros].calories;
    }
    return sum;
  }, 0);
  
  const remainingCalories = goalCalories - usedCalories;
  const unlockedMacros = Object.keys(macroLocks).filter(
    macro => !macroLocks[macro as keyof MacroLocks]
  ) as Array<'protein' | 'carbs' | 'fats'>;
  
  if (unlockedMacros.length === 0) {
    return {
      ...newMacros,
      proteinPerKg: Math.round((newMacros.protein.grams / weight) * 10) / 10
    };
  }
  
  const currentUnlockedTotal = unlockedMacros.reduce(
    (sum, macro) => sum + newMacros[macro].calories, 0
  );
  
  unlockedMacros.forEach(macro => {
    const proportion = currentUnlockedTotal > 0 
      ? newMacros[macro].calories / currentUnlockedTotal 
      : 1 / unlockedMacros.length;
    
    const newMacroCalories = remainingCalories * proportion;
    const divisor = macro === 'fats' ? 9 : 4;
    
    newMacros[macro] = {
      calories: Math.round(newMacroCalories),
      grams: Math.round(newMacroCalories / divisor),
      percentage: Math.round((newMacroCalories / goalCalories) * 100)
    };
  });
  
  return {
    ...newMacros,
    proteinPerKg: Math.round((newMacros.protein.grams / weight) * 10) / 10
  };
}

// ✅ Corrigé : suppression du paramètre tdee inutilisé
export function calculateWeeklyWeightChange(goal: Goal, intensity: DietIntensity): number {
  if (goal === 'maintain') return 0;
  
  const weeklyTarget = goal === 'cut' 
    ? (intensity === 'moderate' ? -0.5 : -1.0)
    : (intensity === 'moderate' ? 0.3 : 0.5);
    
  return weeklyTarget;
}

// 🆕 Fonctions pour détails des calculs
export function getBMRFormulaText(userData: AdvancedUserData): string {
  const { formula, gender, weight, height, age, bodyFat } = userData;
  
  switch (formula) {
    case 'mifflin':
      return gender === 'male' 
        ? `BMR = 10 × ${weight} + 6.25 × ${height} - 5 × ${age} + 5`
        : `BMR = 10 × ${weight} + 6.25 × ${height} - 5 × ${age} - 161`;
    
    case 'harris':
      return gender === 'male'
        ? `BMR = 88.362 + (13.397 × ${weight}) + (4.799 × ${height}) - (5.677 × ${age})`
        : `BMR = 447.593 + (9.247 × ${weight}) + (3.098 × ${height}) - (4.330 × ${age})`;
    
    case 'katch':
      if (bodyFat && bodyFat > 0) {
        const leanMass = Math.round(weight * (1 - bodyFat / 100) * 10) / 10;
        return `BMR = 370 + (21.6 × ${leanMass}) [masse maigre = ${weight} × (1 - ${bodyFat}%)]`;
      }
      return 'Katch-McArdle nécessite le taux de masse grasse, formule Mifflin utilisée';
    
    default:
      return 'Formule non reconnue';
  }
}

export function getGoalAdjustmentText(goal: Goal, intensity: DietIntensity): string {
  switch (goal) {
    case 'cut':
      return intensity === 'moderate' 
        ? 'TDEE - 500 cal (déficit modéré pour -0.5kg/semaine)'
        : 'TDEE - 1000 cal (déficit intensif pour -1kg/semaine)';
    case 'bulk':
      return intensity === 'moderate'
        ? 'TDEE + 300 cal (surplus modéré pour +0.3kg/semaine)'
        : 'TDEE + 500 cal (surplus intensif pour +0.5kg/semaine)';
    case 'maintain':
    default:
      return 'TDEE (calories d\'entretien)';
  }
}

export function calculateResults(
  userData: AdvancedUserData, 
  dietType: DietType = 'equilibre',
  macroLocks: MacroLocks = { protein: false, carbs: false, fats: false }
): CalorieResults {
  const bmr = calculateBMR(userData);
  const activityMultiplier = getActivityMultiplier(userData.activityLevel);
  const workoutAdjustment = getWorkoutAdjustment(userData);
  
  const tdee = Math.round(bmr * activityMultiplier + workoutAdjustment);
  const goalCalories = calculateGoalCalories(tdee, userData.goal, userData.dietIntensity);
  const macrosResult = calculateMacros(goalCalories, userData.weight, dietType);
  const weeklyWeightChange = calculateWeeklyWeightChange(userData.goal, userData.dietIntensity);

  return {
    bmr: Math.round(bmr),
    tdee,
    goalCalories,
    macros: {
      protein: macrosResult.protein,
      carbs: macrosResult.carbs,
      fats: macrosResult.fats
    },
    weeklyWeightChange,
    dietType,
    dietIntensity: userData.dietIntensity,
    proteinPerKg: macrosResult.proteinPerKg,
    macroLocks,
    // 🆕 Détails des calculs
    calculationDetails: {
      bmrFormula: getBMRFormulaText(userData),
      activityMultiplier,
      workoutAdjustment,
      goalAdjustment: goalCalories - tdee,
      formulaUsed: userData.formula
    }
  };
}

export function getDietRecommendation(goal: Goal): DietType {
  return getOptimalDiet(goal);
}

export function getFormulaDescription(formula: Formula): string {
  const descriptions = {
    mifflin: 'Mifflin-St Jeor (recommandée) - Plus précise pour la plupart des gens',
    harris: 'Harris-Benedict - Formule classique, peut surestimer chez les personnes en surpoids',
    katch: 'Katch-McArdle - Plus précise si vous connaissez votre taux de masse grasse'
  };
  return descriptions[formula];
}

export function getActivityDescription(level: ActivityLevel): string {
  const descriptions = {
    sedentary: 'Sédentaire - Travail de bureau, peu d\'activité physique',
    light: 'Légèrement actif - Exercice léger 1-3 fois/semaine',
    moderate: 'Modérément actif - Exercice modéré 3-5 fois/semaine',
    high: 'Très actif - Exercice intense 6-7 fois/semaine',
    extreme: 'Extrêmement actif - Travail physique + sport quotidien'
  };
  return descriptions[level];
}