'use client';

import type { TabType } from '../../types';

interface TabNavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
  showResults: boolean;
}

export function TabNavigation({ activeTab, onTabChange, showResults }: TabNavigationProps) {
  const tabs = [
    {
      id: 'calculator' as TabType,
      label: 'Calculateur',
      emoji: '🧮',
      description: 'Saisir vos informations'
    },
    {
      id: 'results' as TabType,
      label: 'Résultats',
      emoji: '📊',
      description: 'Vos besoins caloriques',
      disabled: !showResults
    }
  ];

  return (
    <div className="flex justify-center">
      <div className="bg-white rounded-xl border border-neutral-200 shadow-sm p-2 inline-flex gap-2">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => !tab.disabled && onTabChange(tab.id)}
            disabled={tab.disabled}
            className={`
              flex items-center gap-3 px-6 py-3 rounded-lg font-semibold transition-all duration-200
              ${activeTab === tab.id
                ? 'bg-brand-500 text-white shadow-lg'
                : tab.disabled
                  ? 'text-neutral-400 cursor-not-allowed'
                  : 'text-neutral-700 hover:bg-neutral-100'
              }
            `}
          >
            <span className="text-lg">{tab.emoji}</span>
            <div className="text-left">
              <div className="text-sm font-semibold">{tab.label}</div>
              <div className={`text-xs ${
                activeTab === tab.id ? 'text-brand-100' : 'text-neutral-500'
              }`}>
                {tab.description}
              </div>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}