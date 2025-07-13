// src/components/tools/beroas-calculator/components/shared/TabNavigation.tsx
'use client';

import type { TabType } from '../../types';

interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

export function TabNavigation({ activeTab, onTabChange }: TabNavigationProps) {
  const tabs = [
    { id: 'basic' as const, label: '📊 Calculateur Simple', description: 'Calcul de base' },
    { id: 'advanced' as const, label: '🚀 BEROAS Avancé', description: 'Analyse complète' },
    { id: 'volume' as const, label: '📈 Simulateur Volume', description: 'Projections business' },
    { id: 'matrix' as const, label: '🎯 Matrice Interactive', description: 'Scénarios multiples' }
  ];

  return (
    <nav className="flex bg-white rounded-xl p-2 shadow-lg border border-neutral-200 overflow-x-auto">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onTabChange(tab.id)}
          className={`
            flex-1 min-w-40 px-4 py-3 rounded-lg font-semibold text-sm transition-all duration-300
            ${activeTab === tab.id
              ? 'bg-brand-500 text-white shadow-lg transform -translate-y-0.5'
              : 'text-neutral-600 hover:bg-neutral-50 hover:text-neutral-800'
            }
          `}
          aria-selected={activeTab === tab.id}
          role="tab"
        >
          <div className="text-center">
            <div className="font-bold">{tab.label}</div>
            <div className="text-xs opacity-75 mt-1">{tab.description}</div>
          </div>
        </button>
      ))}
    </nav>
  );
}