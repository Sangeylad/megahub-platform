'use client';

import { useState } from 'react';
import { getActivityDescription } from '../utils/formulas';
import { GOAL_CONFIG, DIET_PRESETS, DIET_INTENSITY_CONFIG, getOptimalDiet } from '../types';
import type { Goal, CalorieCalculatorHook, DietType, DietIntensity } from '../types';

interface ResultsDisplayProps {
  calculator: CalorieCalculatorHook;
}

export function ResultsDisplay({ calculator }: ResultsDisplayProps) {
  const { userData, results, resetCalculator, changeDietType, changeGoal, changeDietIntensity, adjustMacro, selectedDiet, macroLocks, toggleMacroLock } = calculator;
  const [showDietPanel, setShowDietPanel] = useState(false);
  const [showGoalPanel, setShowGoalPanel] = useState(false);
  const [showIntensityPanel, setShowIntensityPanel] = useState(false);
  const [showCalculationDetails, setShowCalculationDetails] = useState(false);

  if (!results) {
    return (
      <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-8 text-center">
        <div className="text-6xl mb-4">🤔</div>
        <h3 className="text-xl font-semibold text-neutral-800 mb-2">
          Aucun résultat disponible
        </h3>
        <p className="text-neutral-600 mb-6">
          Veuillez d&apos;abord effectuer un calcul pour voir vos résultats
        </p>
        <button
          onClick={() => calculator.setActiveTab('calculator')}
          className="bg-brand-500 hover:bg-brand-600 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200"
        >
          Commencer le calcul
        </button>
      </div>
    );
  }

  const goal = userData.goal as Goal;
  const goalConfig = GOAL_CONFIG[goal];
  const currentDiet = DIET_PRESETS[selectedDiet];
  const optimalDiet = getOptimalDiet(goal);
  const currentIntensity = DIET_INTENSITY_CONFIG[userData.dietIntensity];

  return (
    <div className="space-y-8">
      {/* Header avec objectif */}
      <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-8 text-center">
        <div className="text-6xl mb-4">🎯</div>
        <h3 className="text-2xl font-bold text-neutral-800 mb-4">
          Vos Besoins Caloriques Personnalisés
        </h3>
        
        {/* Objectif */}
        <div className="flex items-center justify-center gap-4 mb-4">
          <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full border-2 ${goalConfig.color} font-semibold`}>
            <span>{goalConfig.emoji}</span>
            <span>Objectif: {goalConfig.label}</span>
          </div>
          <button
            onClick={() => setShowGoalPanel(!showGoalPanel)}
            className="bg-neutral-500 hover:bg-neutral-600 text-white px-3 py-2 rounded-lg font-medium transition-colors text-sm"
          >
            {showGoalPanel ? 'Fermer' : 'Changer'}
          </button>
        </div>

        {/* Intensité */}
        {userData.goal !== 'maintain' && (
          <div className="flex items-center justify-center gap-4 mb-4">
            <div className="inline-flex items-center gap-2 px-3 py-2 rounded-lg bg-neutral-100 border border-neutral-300 text-sm font-medium">
              <span>{currentIntensity.emoji}</span>
              <span>Intensité: {currentIntensity.label}</span>
              <span className="text-xs text-neutral-500">({currentIntensity.weeklyTarget})</span>
            </div>
            <button
              onClick={() => setShowIntensityPanel(!showIntensityPanel)}
              className="bg-neutral-400 hover:bg-neutral-500 text-white px-3 py-1 rounded-lg font-medium transition-colors text-xs"
            >
              {showIntensityPanel ? 'Fermer' : 'Ajuster'}
            </button>
          </div>
        )}

        {/* Panels de changement */}
        {showGoalPanel && (
          <div className="border-t border-neutral-200 pt-6 mt-6">
            <div className="grid md:grid-cols-3 gap-4">
              {Object.entries(GOAL_CONFIG).map(([goalKey, config]) => {
                const isSelected = goal === goalKey;
                
                return (
                  <button
                    key={goalKey}
                    onClick={() => {
                      changeGoal(goalKey as Goal);
                      setShowGoalPanel(false);
                    }}
                    className={`p-4 rounded-lg border-2 text-center transition-all duration-200 ${
                      isSelected
                        ? `border-current ${config.color}`
                        : 'border-neutral-200 hover:border-neutral-300'
                    }`}
                  >
                    <div className="text-3xl mb-2">{config.emoji}</div>
                    <h5 className="font-semibold text-neutral-800 mb-2">{config.label}</h5>
                    <p className="text-xs text-neutral-600">{config.description}</p>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        {showIntensityPanel && userData.goal !== 'maintain' && (
          <div className="border-t border-neutral-200 pt-6 mt-6">
            <div className="grid md:grid-cols-2 gap-4 max-w-md mx-auto">
              {Object.entries(DIET_INTENSITY_CONFIG).map(([intensityKey, config]) => {
                const isSelected = userData.dietIntensity === intensityKey;
                
                return (
                  <button
                    key={intensityKey}
                    onClick={() => {
                      changeDietIntensity(intensityKey as DietIntensity);
                      setShowIntensityPanel(false);
                    }}
                    className={`p-4 rounded-lg border-2 text-center transition-all duration-200 ${
                      isSelected
                        ? 'border-brand-500 bg-brand-50'
                        : 'border-neutral-200 hover:border-neutral-300'
                    }`}
                  >
                    <div className="text-3xl mb-2">{config.emoji}</div>
                    <h5 className="font-semibold text-neutral-800 mb-2">{config.label}</h5>
                    <p className="text-xs text-neutral-600 mb-2">{config.description}</p>
                    <p className="text-sm font-medium text-brand-600">{config.weeklyTarget}</p>
                  </button>
                );
              })}
            </div>
          </div>
        )}

        <div className="mt-4 text-sm text-neutral-600">
          <span className="font-medium">Protéines: {results.proteinPerKg}g/kg</span> de poids de corps
        </div>
      </div>

      {/* Résultats principaux */}
      <div className="grid md:grid-cols-3 gap-6">
        <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-6">
          <div className="text-center">
            <div className="text-3xl mb-3">🫀</div>
            <h4 className="font-semibold text-neutral-800 mb-2">Métabolisme de Base</h4>
            <div className="text-2xl font-bold text-neutral-800">{results.bmr}</div>
            <div className="text-sm text-neutral-600">cal/jour</div>
            <p className="text-xs text-neutral-500 mt-3">
              Calories brûlées au repos
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-6">
          <div className="text-center">
            <div className="text-3xl mb-3">⚡</div>
            <h4 className="font-semibold text-neutral-800 mb-2">Dépense Totale</h4>
            <div className="text-2xl font-bold text-neutral-800">{results.tdee}</div>
            <div className="text-sm text-neutral-600">cal/jour</div>
            <p className="text-xs text-neutral-500 mt-3">
              Avec votre activité
            </p>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-6">
          <div className="text-center">
            <div className="text-3xl mb-3">🍽️</div>
            <h4 className="font-semibold text-neutral-800 mb-2">Calories Objectif</h4>
            <div className="text-2xl font-bold text-brand-600">{results.goalCalories}</div>
            <div className="text-sm text-neutral-600">cal/jour</div>
            <p className="text-xs text-neutral-500 mt-3">
              Pour atteindre votre objectif
            </p>
          </div>
        </div>
      </div>

      {/* Type de régime */}
      <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-8">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h4 className="text-xl font-bold text-neutral-800 mb-2">
              🍽️ Type de Régime Alimentaire
            </h4>
            <p className="text-neutral-600">
              Régime actuel: <span className="font-semibold text-brand-600">{currentDiet.name}</span>
              {selectedDiet === optimalDiet && (
                <span className="ml-2 text-xs bg-yellow-100 text-yellow-700 px-2 py-1 rounded-full">
                  ⭐ Optimal pour votre objectif
                </span>
              )}
            </p>
            <p className="text-sm text-neutral-500 mt-1">{currentDiet.description}</p>
          </div>
          <button
            onClick={() => setShowDietPanel(!showDietPanel)}
            className="bg-brand-500 hover:bg-brand-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            {showDietPanel ? 'Fermer' : 'Changer'}
          </button>
        </div>

        {showDietPanel && (
          <div className="border-t border-neutral-200 pt-6">
            <div className="grid md:grid-cols-3 gap-4">
              {Object.entries(DIET_PRESETS).map(([dietKey, preset]) => {
                const isSelected = selectedDiet === dietKey;
                const isOptimal = dietKey === optimalDiet;
                
                return (
                  <button
                    key={dietKey}
                    onClick={() => {
                      changeDietType(dietKey as DietType);
                      setShowDietPanel(false);
                    }}
                    className={`p-4 rounded-lg border-2 text-left transition-all duration-200 relative ${
                      isSelected
                        ? 'border-brand-500 bg-brand-50'
                        : 'border-neutral-200 hover:border-neutral-300'
                    }`}
                  >
                    {isOptimal && (
                      <div className="absolute -top-2 -right-2 bg-yellow-500 text-white text-xs px-2 py-1 rounded-full">
                        ⭐ Optimal
                      </div>
                    )}
                    <h5 className="font-semibold text-neutral-800 mb-2">{preset.name}</h5>
                    <p className="text-xs text-neutral-600 mb-3">{preset.description}</p>
                    <div className="text-xs space-y-1 mb-3">
                      <div><strong>Protéines:</strong> {preset.proteinGPerKg}g/kg</div>
                      <div><strong>Glucides:</strong> {preset.carbPercentage}% calories</div>
                      <div><strong>Lipides:</strong> Reste</div>
                    </div>
                    <div className="space-y-1">
                      {preset.benefits.slice(0, 2).map((benefit, idx) => (
                        <div key={idx} className="text-xs text-green-600">
                          ✓ {benefit}
                        </div>
                      ))}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>
        )}
      </div>

      {/* Macronutriments avec sliders */}
      <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-8">
        <h4 className="text-xl font-bold text-neutral-800 mb-6 text-center">
          🥗 Répartition des Macronutriments
        </h4>
        
        <div className="mb-6 bg-blue-50 rounded-lg p-4 border border-blue-200">
          <div className="flex items-start gap-3">
            <span className="text-xl">🔒</span>
            <div>
              <h5 className="font-semibold text-blue-800 mb-1">Verrouillage des macros</h5>
              <p className="text-sm text-blue-700">
                Cliquez sur le cadenas pour fixer un macro. Max 2 macros verrouillés en même temps.
              </p>
            </div>
          </div>
        </div>
        
        <div className="grid md:grid-cols-3 gap-8">
          <MacroSlider
            title="Protéines"
            emoji="🥩"
            macro={results.macros.protein}
            color="red"
            isLocked={macroLocks.protein}
            onAdjust={(percentage) => adjustMacro('protein', percentage)}
            onToggleLock={() => toggleMacroLock('protein')}
          />

          <MacroSlider
            title="Glucides"
            emoji="🍞"
            macro={results.macros.carbs}
            color="blue"
            isLocked={macroLocks.carbs}
            onAdjust={(percentage) => adjustMacro('carbs', percentage)}
            onToggleLock={() => toggleMacroLock('carbs')}
          />

          <MacroSlider
            title="Lipides"
            emoji="🥑"
            macro={results.macros.fats}
            color="green"
            isLocked={macroLocks.fats}
            onAdjust={(percentage) => adjustMacro('fats', percentage)}
            onToggleLock={() => toggleMacroLock('fats')}
          />
        </div>

        <div className="mt-8 bg-green-50 rounded-lg p-4 border border-green-200">
          <div className="flex items-start gap-3">
            <span className="text-xl">💡</span>
            <div>
              <h5 className="font-semibold text-green-800 mb-1">Base protéique optimale</h5>
              <p className="text-sm text-green-700">
                <strong>2g de protéines par kg</strong> de poids de corps pour optimiser la composition corporelle. 
                Votre apport actuel: <strong>{results.proteinPerKg}g/kg</strong>.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Détails des calculs */}
      <div className="bg-neutral-50 rounded-xl border border-neutral-200">
        <button
          onClick={() => setShowCalculationDetails(!showCalculationDetails)}
          className="w-full p-6 text-left hover:bg-neutral-100 transition-colors duration-200 flex items-center justify-between"
        >
          <div>
            <h4 className="font-semibold text-neutral-800">🔬 Détails des Calculs</h4>
            <p className="text-sm text-neutral-600 mt-1">
              {showCalculationDetails ? 'Masquer les formules utilisées' : 'Voir comment nous avons calculé vos besoins'}
            </p>
          </div>
          <div className={`transform transition-transform duration-200 ${showCalculationDetails ? 'rotate-180' : ''}`}>
            <svg className="w-5 h-5 text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
            </svg>
          </div>
        </button>

        {showCalculationDetails && (
          <div className="border-t border-neutral-200 p-6 space-y-6">
            {/* Étape 1: BMR */}
            <div className="bg-white rounded-lg p-4 border border-neutral-200">
              <h5 className="font-semibold text-neutral-800 mb-3 flex items-center gap-2">
                <span className="bg-blue-100 text-blue-800 text-sm px-2 py-1 rounded-full">1</span>
                Calcul du Métabolisme de Base (BMR)
              </h5>
              <div className="space-y-2">
                <p className="text-sm text-neutral-600">
                  <strong>Formule {results.calculationDetails.formulaUsed}:</strong>
                </p>
                <code className="block bg-neutral-100 p-3 rounded text-sm font-mono">
                  {results.calculationDetails.bmrFormula}
                </code>
                <p className="text-sm text-neutral-600">
                  <strong>Résultat:</strong> {results.bmr} calories/jour
                </p>
              </div>
            </div>

            {/* Étape 2: TDEE */}
            <div className="bg-white rounded-lg p-4 border border-neutral-200">
              <h5 className="font-semibold text-neutral-800 mb-3 flex items-center gap-2">
                <span className="bg-green-100 text-green-800 text-sm px-2 py-1 rounded-full">2</span>
                Dépense Énergétique Totale (TDEE)
              </h5>
              <div className="space-y-2">
                <p className="text-sm text-neutral-600">
                  <strong>Calcul:</strong> BMR × Facteur d&apos;activité {userData.useAdvancedMode ? '+ Ajustement entraînement' : ''}
                </p>
                <div className="bg-neutral-100 p-3 rounded text-sm space-y-1">
                  <div>BMR: {results.bmr} cal/jour</div>
                  <div>× Facteur d&apos;activité ({getActivityDescription(userData.activityLevel)}): {results.calculationDetails.activityMultiplier}</div>
                  {userData.useAdvancedMode && results.calculationDetails.workoutAdjustment > 0 && (
                    <div>+ Ajustement entraînement: +{Math.round(results.calculationDetails.workoutAdjustment)} cal/jour</div>
                  )}
                  <hr className="my-2" />
                  <div className="font-semibold">= {results.tdee} cal/jour</div>
                </div>
              </div>
            </div>

            {/* Étape 3: Calories objectif */}
            <div className="bg-white rounded-lg p-4 border border-neutral-200">
              <h5 className="font-semibold text-neutral-800 mb-3 flex items-center gap-2">
                <span className="bg-brand-100 text-brand-800 text-sm px-2 py-1 rounded-full">3</span>
                Calories pour Votre Objectif
              </h5>
              <div className="space-y-2">
                <p className="text-sm text-neutral-600">
                  <strong>Ajustement selon objectif:</strong>
                </p>
                <div className="bg-neutral-100 p-3 rounded text-sm space-y-1">
                  <div>TDEE: {results.tdee} cal/jour</div>
                  <div>
                    {results.calculationDetails.goalAdjustment >= 0 ? '+' : ''}{results.calculationDetails.goalAdjustment} cal/jour 
                    ({userData.goal === 'cut' ? 'déficit' : userData.goal === 'bulk' ? 'surplus' : 'maintien'} {currentIntensity.label.toLowerCase()})
                  </div>
                  <hr className="my-2" />
                  <div className="font-semibold text-brand-600">= {results.goalCalories} cal/jour</div>
                </div>
              </div>
            </div>

            {/* Profil utilisé */}
            <div className="bg-white rounded-lg p-4 border border-neutral-200">
              <h5 className="font-semibold text-neutral-800 mb-3">📋 Profil Utilisé</h5>
              <div className="grid md:grid-cols-2 gap-4 text-sm">
                <div>
                  <h6 className="font-medium text-neutral-700 mb-2">Informations personnelles</h6>
                  <ul className="space-y-1 text-neutral-600">
                    <li>• {userData.gender === 'male' ? 'Homme' : 'Femme'}, {userData.age} ans</li>
                    <li>• {userData.weight} kg, {userData.height} cm</li>
                    <li>• {getActivityDescription(userData.activityLevel)}</li>
                    {userData.bodyFat && <li>• Masse grasse: {userData.bodyFat}%</li>}
                  </ul>
                </div>
                <div>
                  <h6 className="font-medium text-neutral-700 mb-2">Paramètres avancés</h6>
                  <ul className="space-y-1 text-neutral-600">
                    <li>• Formule: {results.calculationDetails.formulaUsed.charAt(0).toUpperCase() + results.calculationDetails.formulaUsed.slice(1)}</li>
                    <li>• Objectif: {goalConfig.label}</li>
                    <li>• Intensité: {currentIntensity.label}</li>
                    <li>• Régime: {currentDiet.name}</li>
                    {userData.useAdvancedMode && (
                      <>
                        <li>• Entraînement: {userData.workoutDays}j/semaine</li>
                        {userData.hasCardio && <li>• Cardio: {userData.cardioMinutes}min/semaine</li>}
                      </>
                    )}
                  </ul>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Actions */}
      <div className="flex flex-wrap justify-center gap-4">
        <button
          onClick={() => calculator.setActiveTab('calculator')}
          className="bg-neutral-500 hover:bg-neutral-600 text-white px-6 py-3 rounded-lg font-semibold transition-all duration-200"
        >
          Modifier le calcul
        </button>
        <button
          onClick={resetCalculator}
          className="border-2 border-neutral-300 hover:border-neutral-400 text-neutral-700 px-6 py-3 rounded-lg font-semibold transition-all duration-200"
        >
          Nouveau calcul
        </button>
      </div>
    </div>
  );
}

// Composant MacroSlider (identique)
interface MacroSliderProps {
  title: string;
  emoji: string;
  macro: { grams: number; calories: number; percentage: number };
  color: 'red' | 'blue' | 'green';
  isLocked: boolean;
  onAdjust: (percentage: number) => void;
  onToggleLock: () => void;
}

function MacroSlider({ title, emoji, macro, color, isLocked, onAdjust, onToggleLock }: MacroSliderProps) {
  const colorClasses = {
    red: {
      bg: 'bg-red-100',
      bar: 'bg-red-500',
      text: 'text-red-600',
      slider: 'accent-red-500'
    },
    blue: {
      bg: 'bg-blue-100',
      bar: 'bg-blue-500',
      text: 'text-blue-600',
      slider: 'accent-blue-500'
    },
    green: {
      bg: 'bg-green-100',
      bar: 'bg-green-500',
      text: 'text-green-600',
      slider: 'accent-green-500'
    }
  };

  const colors = colorClasses[color];

  return (
    <div className="text-center space-y-4">
      <div className="flex items-center justify-center gap-3 mb-3">
        <div className="text-4xl">{emoji}</div>
        <button
          onClick={onToggleLock}
          className={`p-2 rounded-lg border-2 transition-all duration-200 ${
            isLocked 
              ? 'border-yellow-500 bg-yellow-50 text-yellow-700' 
              : 'border-neutral-300 hover:border-neutral-400 text-neutral-500'
          }`}
          title={isLocked ? 'Déverrouiller' : 'Verrouiller'}
        >
          {isLocked ? '🔒' : '🔓'}
        </button>
      </div>
      
      <h5 className="font-semibold text-neutral-800">{title}</h5>
      
      <div className={`text-2xl font-bold ${colors.text}`}>
        {macro.grams}g
      </div>
      <div className="text-sm text-neutral-600">
        {macro.calories} cal
      </div>
      <div className="text-xs text-neutral-500">
        {macro.percentage}% des calories
      </div>
      
      <div className={`${colors.bg} rounded-full h-3`}>
        <div 
          className={`${colors.bar} h-3 rounded-full transition-all duration-300`}
          style={{ width: `${macro.percentage}%` }}
        />
      </div>

      <div className="px-2">
        <input
          type="range"
          min="5"
          max="60"
          step="1"
          value={macro.percentage}
          onChange={(e) => onAdjust(parseInt(e.target.value))}
          disabled={isLocked}
          className={`w-full h-2 rounded-lg appearance-none cursor-pointer ${
            isLocked ? 'opacity-50 cursor-not-allowed' : colors.slider
          }`}
        />
        <div className="flex justify-between text-xs text-neutral-400 mt-1">
          <span>5%</span>
          <span>60%</span>
        </div>
        {isLocked && (
          <p className="text-xs text-yellow-600 mt-2">🔒 Verrouillé</p>
        )}
      </div>
    </div>
  );
}