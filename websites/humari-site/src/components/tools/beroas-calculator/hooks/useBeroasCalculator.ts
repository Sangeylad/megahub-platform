// src/components/tools/beroas-calculator/hooks/useBeroasCalculator.ts
'use client';

import { useState, useCallback, useMemo } from 'react';
import type { BeroasState, TabType } from '../types';
import { BeroasCalculator } from '../utils/calculations';

const initialState: BeroasState = {
  sellingPrice: 29.99,
  vatRate: 20,
  productCost: 12.50,
  shippingCost: 3.50,
  packagingCost: 1.20,
  paymentFees: 2.9,
  platformFees: 0,
  storageCost: 0.50,
  returnsRate: 5,
  otherCosts: 2.00,
  targetBeroas: 3.0,
  targetMargin: 40,
  monthlyOrders: 150,
  conversionRate: 2.5,
  trafficCost: 0.65,
  growthRate: 15
};

export function useBeroasCalculator() {
  const [state, setState] = useState<BeroasState>(initialState);
  const [activeTab, setActiveTab] = useState<TabType>('basic');

  // ✅ Stabiliser setActiveTab avec useCallback
  const stableSetActiveTab = useCallback((tab: TabType) => {
    setActiveTab(tab);
  }, []);

  const updateField = useCallback((field: keyof BeroasState, value: number) => {
    setState(prev => ({ ...prev, [field]: value }));
  }, []);

  const updateMultipleFields = useCallback((updates: Partial<BeroasState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  const results = useMemo(() => 
    BeroasCalculator.calculateMetrics(state), [state]
  );

  const volumeProjections = useMemo(() => 
    BeroasCalculator.calculateVolumeProjections(state, results), [state, results]
  );

  const extendedProjections = useMemo(() => 
    BeroasCalculator.calculateExtendedProjections(
      state.monthlyOrders, 
      state.growthRate, 
      results.sellingPriceHT, 
      results.unitMargin
    ), [state.monthlyOrders, state.growthRate, results.sellingPriceHT, results.unitMargin]
  );

  const generateMatrix = useCallback((
    priceMin: number,
    priceMax: number,
    costMin: number,
    costMax: number
  ) => {
    return BeroasCalculator.generateMatrix(
      priceMin,
      priceMax,
      costMin,
      costMax,
      state.paymentFees,
      state.otherCosts,
      state.targetBeroas
    );
  }, [state.paymentFees, state.otherCosts, state.targetBeroas]);

  const resetToDefaults = useCallback(() => {
    setState(initialState);
  }, []);

  // ✅ Mémoriser l'objet retourné pour éviter les re-renders
  return useMemo(() => ({
    state,
    results,
    volumeProjections,
    extendedProjections,
    activeTab,
    setActiveTab: stableSetActiveTab,
    updateField,
    updateMultipleFields,
    generateMatrix,
    resetToDefaults
  }), [
    state,
    results,
    volumeProjections,
    extendedProjections,
    activeTab,
    stableSetActiveTab,
    updateField,
    updateMultipleFields,
    generateMatrix,
    resetToDefaults
  ]);
}