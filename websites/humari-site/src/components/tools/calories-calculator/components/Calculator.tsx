'use client';

import type { Gender, ActivityLevel, Goal, Formula, CalorieCalculatorHook } from '../types';
import { getFormulaDescription } from '../utils/formulas';
import { GOAL_CONFIG } from '../types';

interface CalculatorProps {
  calculator: CalorieCalculatorHook;
}

export function Calculator({ calculator }: CalculatorProps) {
  const { userData, updateUserData, calculateCalories, canCalculate, showAdvanced, toggleAdvancedMode } = calculator;

  const handleInputChange = (field: string, value: string | number | boolean | Gender | ActivityLevel | Goal | Formula | undefined) => {
    updateUserData({ [field]: value });
  };

  return (
    <div className="bg-white rounded-xl border border-neutral-200 shadow-sm">
      <div className="p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h3 className="text-2xl font-bold text-neutral-800 mb-3">
            🧮 Calculateur de Besoins Caloriques
          </h3>
          <p className="text-neutral-600 max-w-2xl mx-auto">
            Renseignez vos informations pour obtenir vos besoins caloriques personnalisés
          </p>
        </div>

        {/* Objectif en 3 blocs séparés */}
        <div className="mb-8">
          <h4 className="text-lg font-semibold text-neutral-800 mb-4 text-center">
            🎯 Choisissez votre objectif
          </h4>
          <div className="grid md:grid-cols-3 gap-4">
            {Object.entries(GOAL_CONFIG).map(([goalKey, config]) => {
              const isSelected = userData.goal === goalKey;
              
              return (
                <button
                  key={goalKey}
                  onClick={() => handleInputChange('goal', goalKey as Goal)}
                  className={`p-6 rounded-xl border-2 text-center transition-all duration-200 ${
                    isSelected
                      ? `border-current ${config.color}`
                      : 'border-neutral-200 hover:border-neutral-300'
                  }`}
                >
                  <div className="text-4xl mb-3">{config.emoji}</div>
                  <h5 className="font-semibold text-neutral-800 mb-2">{config.label}</h5>
                  <p className="text-sm text-neutral-600">{config.description}</p>
                </button>
              );
            })}
          </div>
        </div>

        <div className="grid lg:grid-cols-2 gap-8">
          {/* Colonne 1: Informations personnelles */}
          <div className="space-y-6">
            <h4 className="font-semibold text-neutral-800 text-lg mb-4 flex items-center gap-2">
              👤 Informations Personnelles
            </h4>
            
            {/* Âge */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Âge (années)
              </label>
              <input
                type="number"
                min="15"
                max="100"
                value={userData.age}
                onChange={(e) => handleInputChange('age', parseInt(e.target.value) || 0)}
                className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                placeholder="Ex: 30"
              />
            </div>

            {/* Genre */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-3">
                Genre
              </label>
              <div className="grid grid-cols-2 gap-3">
                {[
                  { value: 'male' as Gender, label: '👨 Homme' },
                  { value: 'female' as Gender, label: '👩 Femme' }
                ].map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleInputChange('gender', option.value)}
                    className={`
                      p-4 rounded-lg border-2 text-center transition-all duration-200
                      ${userData.gender === option.value
                        ? 'border-brand-500 bg-brand-50 text-brand-800'
                        : 'border-neutral-200 hover:border-neutral-300 text-neutral-700'
                      }
                    `}
                  >
                    <div className="font-semibold">{option.label}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Poids */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Poids (kg)
              </label>
              <input
                type="number"
                min="30"
                max="300"
                step="0.1"
                value={userData.weight}
                onChange={(e) => handleInputChange('weight', parseFloat(e.target.value) || 0)}
                className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                placeholder="Ex: 75.5"
              />
            </div>

            {/* Taille */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-2">
                Taille (cm)
              </label>
              <input
                type="number"
                min="100"
                max="250"
                value={userData.height}
                onChange={(e) => handleInputChange('height', parseInt(e.target.value) || 0)}
                className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                placeholder="Ex: 175"
              />
            </div>
          </div>

          {/* Colonne 2: Activité uniquement */}
          <div className="space-y-6">
            <h4 className="font-semibold text-neutral-800 text-lg mb-4 flex items-center gap-2">
              🏃 Niveau d&apos;Activité
            </h4>
            
            {/* Niveau d'activité */}
            <div>
              <label className="block text-sm font-medium text-neutral-700 mb-3">
                Niveau d&apos;activité quotidien
              </label>
              <div className="space-y-2">
                {[
                  { value: 'sedentary' as ActivityLevel, label: 'Sédentaire', desc: 'Bureau, peu d&apos;exercice' },
                  { value: 'light' as ActivityLevel, label: 'Léger', desc: 'Exercice 1-3x/semaine' },
                  { value: 'moderate' as ActivityLevel, label: 'Modéré', desc: 'Exercice 3-5x/semaine' },
                  { value: 'high' as ActivityLevel, label: 'Élevé', desc: 'Exercice 6-7x/semaine' },
                  { value: 'extreme' as ActivityLevel, label: 'Extrême', desc: 'Sport quotidien intense' }
                ].map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleInputChange('activityLevel', option.value)}
                    className={`
                      w-full p-4 rounded-lg border-2 text-left transition-all duration-200
                      ${userData.activityLevel === option.value
                        ? 'border-brand-500 bg-brand-50 text-brand-800'
                        : 'border-neutral-200 hover:border-neutral-300 text-neutral-700'
                      }
                    `}
                  >
                    <div className="font-semibold">{option.label}</div>
                    <div className="text-sm opacity-75 mt-1">{option.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Info sur le mode simple */}
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <div className="flex items-start gap-3">
                <span className="text-xl">⚡</span>
                <div>
                  <h6 className="font-semibold text-green-800 mb-1">Calcul rapide</h6>
                  <p className="text-sm text-green-700">
                    Ces informations suffisent pour un calcul précis. 
                    {!showAdvanced && (
                      <span className="font-medium"> Mode simple activé.</span>
                    )}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Options Avancées */}
        <div className="mt-12">
          <button
            onClick={toggleAdvancedMode}
            className="w-full bg-neutral-50 hover:bg-neutral-100 border border-neutral-200 rounded-lg p-4 transition-all duration-200 flex items-center justify-between"
          >
            <div className="flex items-center gap-3">
              <span className="text-2xl">⚙️</span>
              <div className="text-left">
                <h5 className="font-semibold text-neutral-800">Options Avancées</h5>
                <p className="text-sm text-neutral-600">
                  {showAdvanced 
                    ? 'Masquer les paramètres détaillés' 
                    : 'Musculation, cardio, formule de calcul - pour plus de précision'
                  }
                </p>
              </div>
            </div>
            <div className={`transform transition-transform duration-200 ${showAdvanced ? 'rotate-180' : ''}`}>
              <svg className="w-5 h-5 text-neutral-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </button>

          <div className={`overflow-hidden transition-all duration-300 ${showAdvanced ? 'max-h-screen opacity-100 mt-6' : 'max-h-0 opacity-0'}`}>
            <div className="grid lg:grid-cols-3 gap-8 p-6 bg-neutral-50 rounded-lg border border-neutral-200">
              
              {/* Colonne 1: Masse grasse et formule */}
              <div className="space-y-6">
                <h6 className="font-medium text-neutral-700 text-sm uppercase tracking-wide">Précision du calcul</h6>
                
                {/* Masse grasse */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Taux de masse grasse (%) - Optionnel
                  </label>
                  <input
                    type="number"
                    min="5"
                    max="50"
                    step="0.1"
                    value={userData.bodyFat || ''}
                    onChange={(e) => handleInputChange('bodyFat', e.target.value ? parseFloat(e.target.value) : undefined)}
                    className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                    placeholder="Ex: 15.5"
                  />
                  <p className="text-xs text-neutral-500 mt-2">
                    💡 Balance impédancemètre, DEXA, pince
                  </p>
                </div>

                {/* Formule */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-3">
                    Formule de calcul
                  </label>
                  <div className="space-y-2">
                    {[
                      { value: 'mifflin' as Formula, label: 'Mifflin-St Jeor', recommended: true },
                      { value: 'harris' as Formula, label: 'Harris-Benedict', recommended: false },
                      { value: 'katch' as Formula, label: 'Katch-McArdle', recommended: false }
                    ].map((option) => (
                      <button
                        key={option.value}
                        onClick={() => handleInputChange('formula', option.value)}
                        className={`
                          w-full p-3 rounded-lg border-2 text-left transition-all duration-200 relative
                          ${userData.formula === option.value
                            ? 'border-brand-500 bg-brand-50 text-brand-800'
                            : 'border-neutral-200 hover:border-neutral-300 text-neutral-700'
                          }
                        `}
                      >
                        <div className="flex items-center justify-between">
                          <div className="font-semibold">{option.label}</div>
                          {option.recommended && (
                            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded-full">
                              Recommandée
                            </span>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-neutral-500 mt-2">
                    {getFormulaDescription(userData.formula)}
                  </p>
                </div>
              </div>

              {/* Colonne 2: Musculation */}
              <div className="space-y-6">
                <h6 className="font-medium text-neutral-700 text-sm uppercase tracking-wide">Musculation</h6>
                
                {/* Jours d'entraînement */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-3">
                    Séances par semaine
                  </label>
                  <div className="grid grid-cols-4 gap-2">
                    {[0, 1, 2, 3, 4, 5, 6, 7].map((days) => (
                      <button
                        key={days}
                        onClick={() => handleInputChange('workoutDays', days)}
                        className={`
                          p-3 rounded-lg border-2 text-center font-semibold transition-all duration-200
                          ${userData.workoutDays === days
                            ? 'border-brand-500 bg-brand-500 text-white'
                            : 'border-neutral-200 hover:border-neutral-300 text-neutral-700'
                          }
                        `}
                      >
                        {days}
                      </button>
                    ))}
                  </div>
                </div>

                {/* Intensité */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-3">
                    Intensité des séances
                  </label>
                  <div className="space-y-2">
                    {[
                      { value: 'low', label: 'Légère', desc: 'Échauffement, étirements' },
                      { value: 'moderate', label: 'Modérée', desc: 'Séances classiques' },
                      { value: 'high', label: 'Intense', desc: 'Entraînement poussé' }
                    ].map((option) => (
                      <button
                        key={option.value}
                        onClick={() => handleInputChange('workoutIntensity', option.value)}
                        className={`
                          w-full p-3 rounded-lg border-2 text-left transition-all duration-200
                          ${userData.workoutIntensity === option.value
                            ? 'border-brand-500 bg-brand-50 text-brand-800'
                            : 'border-neutral-200 hover:border-neutral-300 text-neutral-700'
                          }
                        `}
                      >
                        <div className="font-semibold">{option.label}</div>
                        <div className="text-sm opacity-75 mt-1">{option.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Durée */}
                <div>
                  <label className="block text-sm font-medium text-neutral-700 mb-2">
                    Durée par séance (min)
                  </label>
                  <input
                    type="number"
                    min="0"
                    max="300"
                    value={userData.workoutDuration}
                    onChange={(e) => handleInputChange('workoutDuration', parseInt(e.target.value) || 0)}
                    className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                    placeholder="60"
                  />
                </div>
              </div>

              {/* Colonne 3: Cardio */}
              <div className="space-y-6">
                <h6 className="font-medium text-neutral-700 text-sm uppercase tracking-wide">Cardio additionnel</h6>
                
                {/* Checkbox cardio */}
                <div>
                  <label className="flex items-center gap-3 mb-4">
                    <input
                      type="checkbox"
                      checked={userData.hasCardio}
                      onChange={(e) => handleInputChange('hasCardio', e.target.checked)}
                      className="w-5 h-5 text-brand-600 border-2 border-neutral-300 rounded focus:ring-brand-500"
                    />
                    <span className="font-medium text-neutral-700">
                      Je fais du cardio en plus
                    </span>
                  </label>

                  {userData.hasCardio && (
                    <div>
                      <label className="block text-sm font-medium text-neutral-700 mb-2">
                        Minutes par semaine
                      </label>
                      <input
                        type="number"
                        min="0"
                        max="500"
                        value={userData.cardioMinutes}
                        onChange={(e) => handleInputChange('cardioMinutes', parseInt(e.target.value) || 0)}
                        className="w-full px-4 py-3 border border-neutral-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                        placeholder="150"
                      />
                      <p className="text-xs text-neutral-500 mt-2">
                        Course, vélo, rameur, etc.
                      </p>
                    </div>
                  )}
                </div>

                {/* Info accuracy */}
                <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
                  <div className="flex items-start gap-3">
                    <span className="text-xl">🎯</span>
                    <div>
                      <h6 className="font-semibold text-blue-800 mb-1">Mode avancé</h6>
                      <p className="text-sm text-blue-700">
                        Ces paramètres permettent un calcul ultra-précis selon votre routine.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Bouton de calcul */}
        <div className="mt-10 text-center">
          <button
            onClick={calculateCalories}
            disabled={!canCalculate}
            className={`
              inline-flex items-center gap-3 px-8 py-4 rounded-xl font-semibold text-lg transition-all duration-300
              ${canCalculate
                ? 'bg-brand-500 hover:bg-brand-600 text-white shadow-lg hover:shadow-xl hover:-translate-y-1'
                : 'bg-neutral-300 text-neutral-500 cursor-not-allowed'
              }
            `}
          >
            🧮 Calculer mes besoins
            {canCalculate && (
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            )}
          </button>
          
          {!canCalculate && (
            <p className="text-sm text-neutral-500 mt-3">
              Veuillez remplir tous les champs obligatoires
            </p>
          )}
        </div>

        {/* Tips */}
        <div className="mt-8 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6 border border-green-200">
          <div className="flex items-start gap-4">
            <span className="text-2xl">💡</span>
            <div>
              <h5 className="font-semibold text-neutral-800 mb-2">Conseils pour un calcul optimal</h5>
              <ul className="text-sm text-neutral-600 space-y-1">
                <li>• Pesez-vous le matin à jeun pour plus de précision</li>
                <li>• {showAdvanced ? 'Mode avancé : calcul ultra-précis avec tous vos paramètres' : 'Mode simple : calcul rapide et fiable pour débuter'}</li>
                <li>• Ajustez selon vos résultats après 2-3 semaines de suivi</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}