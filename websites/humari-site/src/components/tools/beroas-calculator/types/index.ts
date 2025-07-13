// src/components/tools/beroas-calculator/types/index.ts
export interface BeroasState {
  // Pricing
  sellingPrice: number;
  vatRate: number;
  
  // Direct costs
  productCost: number;
  shippingCost: number;
  packagingCost: number;
  
  // Transaction fees
  paymentFees: number;
  platformFees: number;
  
  // Other costs
  storageCost: number;
  returnsRate: number;
  otherCosts: number;
  
  // Targets
  targetBeroas: number;
  targetMargin: number;
  
  // Volume simulation
  monthlyOrders: number;
  conversionRate: number;
  trafficCost: number;
  growthRate: number;
}

export interface BeroasResults {
  sellingPriceHT: number;
  sellingPriceTTC: number;
  totalCosts: number;
  unitMargin: number;
  marginPercent: number;
  calculatedBeroas: number;
  paymentFeesAmount: number;
  platformFeesAmount: number;
  returnsImpact: number;
  isRentable: boolean;
}

export interface VolumeProjections {
  monthlyRevenue: number;
  requiredTraffic: number;
  recommendedBudget: number;
  actualTrafficCost: number;
  netProfit: number;
  roi: number;
}

export interface ExtendedProjections {
  q1: {
    orders: number;
    revenue: number;
    profit: number;
  };
  yearly: {
    orders: number;
    revenue: number;
    profit: number;
  };
}

export interface MatrixCell {
  price: number;
  cost: number;
  beroas: number;
  margin: number;
  isRentable: boolean;
}

export interface ScenarioData {
  id: string;
  name: string;
  multiplier: number;
  emoji: string;
  badge: string;
  orders: number;
  revenue: number;
  budget: number;
  traffic: number;
  profit: number;
}

export interface Recommendation {
  type: 'success' | 'warning' | 'error' | 'info';
  icon: string;
  text: string;
}

export interface Insight {
  icon: string;
  text: string;
}

export interface Action {
  type: 'success' | 'warning' | 'error' | 'info';
  text: string;
}

export type TabType = 'basic' | 'advanced' | 'volume' | 'matrix';

export interface BeroasCalculatorProps {
  className?: string;
  initialTab?: TabType;
  showExport?: boolean;
}

export interface BenchmarkData {
  sector: string;
  range: string;
  description: string;
}