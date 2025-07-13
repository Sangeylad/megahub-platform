'use client';

import { useState, useCallback, useMemo } from 'react';
import type { CalorieCalculatorState, TabType, AdvancedUserData, DietType, MacroLocks, Goal, DietIntensity } from '../types';
import { calculateResults, getDietRecommendation, calculateMacrosWithLocks } from '../utils/formulas';

const defaultUserData: AdvancedUserData = {
  age: 30,
  gender: 'male',
  weight: 75,
  height: 175,
  activityLevel: 'moderate',
  goal: 'maintain',
  bodyFat: undefined,
  workoutDays: 4,
  workoutIntensity: 'moderate',
  workoutDuration: 60,
  hasCardio: false,
  cardioMinutes: 0,
  formula: 'mifflin',
  dietIntensity: 'moderate',
  useAdvancedMode: false
};

const defaultMacroLocks: MacroLocks = {
  protein: false,
  carbs: false,
  fats: false
};

export function useCalorieCalculator() {
  const [state, setState] = useState<CalorieCalculatorState>({
    activeTab: 'calculator',
    userData: defaultUserData,
    results: null,
    isCalculated: false,
    selectedDiet: 'low_carb',
    macroLocks: defaultMacroLocks,
    showAdvanced: false
  });

  const setActiveTab = useCallback((tab: TabType) => {
    setState(prev => ({
      ...prev,
      activeTab: tab
    }));
  }, []);

  const updateUserData = useCallback((updates: Partial<AdvancedUserData>) => {
    setState(prev => {
      const newUserData = { ...prev.userData, ...updates };
      
      let newSelectedDiet = prev.selectedDiet;
      if (updates.goal) {
        newSelectedDiet = getDietRecommendation(updates.goal);
      }
      
      return {
        ...prev,
        userData: newUserData,
        selectedDiet: newSelectedDiet,
        isCalculated: false,
        results: null,
        macroLocks: defaultMacroLocks
      };
    });
  }, []);

  const calculateCalories = useCallback(() => {
    try {
      // 🎯 LOGIQUE SIMPLE VS AVANCÉ CLARIFIÉE
      const calculationData = { ...state.userData };
      
      if (!state.showAdvanced) {
        // MODE SIMPLE : Ignore les paramètres avancés
        calculationData.useAdvancedMode = false;
        calculationData.bodyFat = undefined; // Force undefined pour ignorer
        calculationData.formula = 'mifflin'; // Formule par défaut
        // Les paramètres workout/cardio sont gardés mais useAdvancedMode=false les ignore
      } else {
        // MODE AVANCÉ : Utilise tout
        calculationData.useAdvancedMode = true;
      }
      
      const results = calculateResults(calculationData, state.selectedDiet, state.macroLocks);
      setState(prev => ({
        ...prev,
        results,
        isCalculated: true,
        activeTab: 'results'
      }));
    } catch (error) {
      console.error('Erreur calcul calories:', error);
    }
  }, [state.userData, state.selectedDiet, state.macroLocks, state.showAdvanced]);

  const resetCalculator = useCallback(() => {
    setState({
      activeTab: 'calculator',
      userData: defaultUserData,
      results: null,
      isCalculated: false,
      selectedDiet: 'low_carb',
      macroLocks: defaultMacroLocks,
      showAdvanced: false
    });
  }, []);

  const changeDietType = useCallback((dietType: DietType) => {
    setState(prev => {
      if (!prev.results) return prev;
      
      const calculationData = { ...prev.userData };
      if (!prev.showAdvanced) {
        calculationData.useAdvancedMode = false;
        calculationData.bodyFat = undefined;
        calculationData.formula = 'mifflin';
      } else {
        calculationData.useAdvancedMode = true;
      }
      
      const newResults = calculateResults(calculationData, dietType, defaultMacroLocks);
      
      return {
        ...prev,
        selectedDiet: dietType,
        results: newResults,
        macroLocks: defaultMacroLocks
      };
    });
  }, []);

  const changeGoal = useCallback((goal: Goal) => {
    setState(prev => {
      if (!prev.results) return prev;
      
      const newUserData = { ...prev.userData, goal };
      const optimalDiet = getDietRecommendation(goal);
      
      const calculationData = { ...newUserData };
      if (!prev.showAdvanced) {
        calculationData.useAdvancedMode = false;
        calculationData.bodyFat = undefined;
        calculationData.formula = 'mifflin';
      } else {
        calculationData.useAdvancedMode = true;
      }
      
      const newResults = calculateResults(calculationData, optimalDiet, defaultMacroLocks);
      
      return {
        ...prev,
        userData: newUserData,
        selectedDiet: optimalDiet,
        results: newResults,
        macroLocks: defaultMacroLocks
      };
    });
  }, []);

  const changeDietIntensity = useCallback((intensity: DietIntensity) => {
    setState(prev => {
      if (!prev.results) return prev;
      
      const newUserData = { ...prev.userData, dietIntensity: intensity };
      
      const calculationData = { ...newUserData };
      if (!prev.showAdvanced) {
        calculationData.useAdvancedMode = false;
        calculationData.bodyFat = undefined;
        calculationData.formula = 'mifflin';
      } else {
        calculationData.useAdvancedMode = true;
      }
      
      const newResults = calculateResults(calculationData, prev.selectedDiet, prev.macroLocks);
      
      return {
        ...prev,
        userData: newUserData,
        results: newResults
      };
    });
  }, []);

  const toggleAdvancedMode = useCallback(() => {
    setState(prev => ({
      ...prev,
      showAdvanced: !prev.showAdvanced,
      // Reset results pour forcer recalcul avec nouveau mode
      results: null,
      isCalculated: false
    }));
  }, []);

  const toggleMacroLock = useCallback((macroType: 'protein' | 'carbs' | 'fats') => {
    setState(prev => {
      const newLocks = {
        ...prev.macroLocks,
        [macroType]: !prev.macroLocks[macroType]
      };
      
      const lockedCount = Object.values(newLocks).filter(Boolean).length;
      if (lockedCount > 2) {
        return prev;
      }
      
      return {
        ...prev,
        macroLocks: newLocks
      };
    });
  }, []);

  const adjustMacro = useCallback((macroType: 'protein' | 'carbs' | 'fats', percentage: number) => {
    setState(prev => {
      if (!prev.results) return prev;
      
      const goalCalories = prev.results.goalCalories;
      const weight = prev.userData.weight;
      
      const newMacros = calculateMacrosWithLocks(
        goalCalories,
        weight,
        prev.results.macros,
        prev.macroLocks,
        macroType,
        percentage
      );
      
      return {
        ...prev,
        results: {
          ...prev.results,
          macros: {
            protein: newMacros.protein,
            carbs: newMacros.carbs,
            fats: newMacros.fats
          },
          dietType: 'equilibre',
          proteinPerKg: newMacros.proteinPerKg
        },
        selectedDiet: 'equilibre'
      };
    });
  }, []);

  const isBasicDataValid = useMemo(() => {
    const { age, weight, height } = state.userData;
    return age >= 15 && age <= 100 &&
            weight >= 30 && weight <= 300 &&
            height >= 100 && height <= 250;
  }, [state.userData]);

  const isAdvancedDataValid = useMemo(() => {
    const { workoutDays, workoutDuration, cardioMinutes, bodyFat } = state.userData;
    return isBasicDataValid &&
           workoutDays >= 0 && workoutDays <= 7 &&
           workoutDuration >= 0 && workoutDuration <= 300 &&
           cardioMinutes >= 0 && cardioMinutes <= 500 &&
           (bodyFat === undefined || (bodyFat >= 5 && bodyFat <= 50));
  }, [state.userData, isBasicDataValid]);

  const canCalculate = useMemo(() => {
    return state.showAdvanced ? isAdvancedDataValid : isBasicDataValid;
  }, [state.showAdvanced, isBasicDataValid, isAdvancedDataValid]);

  const getExportData = useCallback(() => {
    if (!state.results) return null;

    return {
      userData: state.userData,
      results: state.results,
      calculatedAt: new Date(),
      formula: state.userData.formula
    };
  }, [state.userData, state.results]);

  return {
    activeTab: state.activeTab,
    userData: state.userData,
    results: state.results,
    isCalculated: state.isCalculated,
    selectedDiet: state.selectedDiet,
    macroLocks: state.macroLocks,
    showAdvanced: state.showAdvanced,
    setActiveTab,
    updateUserData,
    calculateCalories,
    resetCalculator,
    isBasicDataValid,
    isAdvancedDataValid,
    canCalculate,
    getExportData,
    changeDietType,
    changeGoal,
    changeDietIntensity,
    adjustMacro,
    toggleMacroLock,
    toggleAdvancedMode
  };
}