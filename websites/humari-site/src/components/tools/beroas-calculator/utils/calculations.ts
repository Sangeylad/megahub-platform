// src/components/tools/beroas-calculator/utils/calculations.ts
import type { BeroasState, BeroasResults, VolumeProjections, ExtendedProjections, MatrixCell } from '../types';

export class BeroasCalculator {
  static calculateMetrics(state: BeroasState): BeroasResults {
    const { sellingPrice, productCost, shippingCost, packagingCost, paymentFees, 
            platformFees, storageCost, returnsRate, otherCosts, vatRate } = state;

    const sellingPriceHT = sellingPrice;
    const sellingPriceTTC = sellingPriceHT * (1 + vatRate / 100);
    
    const paymentFeesAmount = (sellingPriceHT * paymentFees) / 100;
    const platformFeesAmount = (sellingPriceHT * (platformFees || 0)) / 100;
    const returnsImpact = (sellingPriceHT * returnsRate) / 100;
    
    // ✅ Formule complète comme dans les templates
    const totalCosts = productCost + shippingCost + (packagingCost || 0) + (storageCost || 0) + 
                      paymentFeesAmount + platformFeesAmount + otherCosts + returnsImpact;
    
    const unitMargin = sellingPriceHT - totalCosts;
    const marginPercent = sellingPriceHT > 0 ? (unitMargin / sellingPriceHT) * 100 : 0;
    const calculatedBeroas = unitMargin > 0 ? sellingPriceHT / unitMargin : 0;

    return {
      sellingPriceHT,
      sellingPriceTTC,
      totalCosts,
      unitMargin,
      marginPercent,
      calculatedBeroas,
      paymentFeesAmount,
      platformFeesAmount,
      returnsImpact,
      isRentable: calculatedBeroas > 0 && unitMargin > 0
    };
  }

  static calculateVolumeProjections(state: BeroasState, results: BeroasResults): VolumeProjections {
    const { monthlyOrders, conversionRate, trafficCost } = state;
    
    const monthlyRevenue = results.sellingPriceHT * monthlyOrders;
    const requiredTraffic = conversionRate > 0 ? Math.ceil(monthlyOrders / (conversionRate / 100)) : 0;
    const recommendedBudget = results.unitMargin * monthlyOrders; // Break-even budget
    const actualTrafficCost = requiredTraffic * trafficCost;
    const grossProfit = results.unitMargin * monthlyOrders;
    const netProfit = grossProfit - actualTrafficCost;
    const roi = actualTrafficCost > 0 ? (netProfit / actualTrafficCost) * 100 : 0;

    return {
      monthlyRevenue,
      requiredTraffic,
      recommendedBudget,
      actualTrafficCost,
      netProfit,
      roi
    };
  }

  static calculateExtendedProjections(
    monthlyOrders: number, 
    growthRate: number, 
    sellingPrice: number, 
    unitMargin: number
  ): ExtendedProjections {
    const growthFactor = 1 + (growthRate / 100);
    
    // Q1 calculations (3 months with growth)
    let q1Orders = 0;
    let currentOrders = monthlyOrders;
    
    for (let month = 0; month < 3; month++) {
      q1Orders += currentOrders;
      currentOrders *= growthFactor;
    }
    
    // Yearly calculations (12 months with compound growth)
    let yearlyOrders = 0;
    currentOrders = monthlyOrders;
    
    for (let month = 0; month < 12; month++) {
      yearlyOrders += currentOrders;
      currentOrders *= growthFactor;
    }
    
    return {
      q1: {
        orders: Math.round(q1Orders),
        revenue: q1Orders * sellingPrice,
        profit: q1Orders * unitMargin
      },
      yearly: {
        orders: Math.round(yearlyOrders),
        revenue: yearlyOrders * sellingPrice,
        profit: yearlyOrders * unitMargin
      }
    };
  }

  static generateMatrix(
    priceMin: number,
    priceMax: number,
    costMin: number,
    costMax: number,
    paymentFees: number,
    otherCosts: number,
    targetBeroas: number
  ): MatrixCell[] {
    const priceSteps = 12;
    const costSteps = 10;
    const matrix: MatrixCell[] = [];
    
    const priceRange = this.generateRange(priceMin, priceMax, priceSteps);
    const costRange = this.generateRange(costMin, costMax, costSteps);
    
    priceRange.forEach(price => {
      costRange.forEach(cost => {
        const paymentFeesAmount = (price * paymentFees) / 100;
        const totalCosts = cost + paymentFeesAmount + otherCosts;
        const margin = price - totalCosts;
        const beroas = margin > 0 ? price / margin : 0;
        const isRentable = margin > 0 && beroas <= targetBeroas;
        
        matrix.push({ price, cost, beroas, margin, isRentable });
      });
    });
    
    return matrix;
  }

  private static generateRange(min: number, max: number, steps: number): number[] {
    const range: number[] = [];
    const step = (max - min) / (steps - 1);
    
    for (let i = 0; i < steps; i++) {
      range.push(min + (step * i));
    }
    
    return range;
  }

  static generateScenarios(state: BeroasState, results: BeroasResults) {
    const scenarios = [
      { id: 'conservative', name: 'Prudente', multiplier: 0.5, emoji: '🐌', badge: '-50% volume' },
      { id: 'current', name: 'Actuelle', multiplier: 1.0, emoji: '🎯', badge: 'Volume cible' },
      { id: 'aggressive', name: 'Ambitieuse', multiplier: 2.0, emoji: '🚀', badge: '+100% volume' }
    ];

    return scenarios.map(scenario => {
      const orders = Math.round(state.monthlyOrders * scenario.multiplier);
      const revenue = orders * results.sellingPriceHT;
      const budget = orders * results.unitMargin;
      const traffic = Math.ceil(orders / (state.conversionRate / 100));
      const actualCost = traffic * state.trafficCost;
      const profit = (orders * results.unitMargin) - actualCost;

      return {
        ...scenario,
        orders,
        revenue,
        budget,
        traffic,
        profit
      };
    });
  }

  static generateRecommendations(state: BeroasState, results: BeroasResults) {
    const recommendations = [];
    
    if (results.calculatedBeroas <= 2 && results.marginPercent > 30) {
      recommendations.push({
        type: 'success',
        icon: '🚀',
        text: `BEROAS exceptionnel (${results.calculatedBeroas.toFixed(2)}) ! Vous pouvez investir massivement en publicité avec confiance.`
      });
    } else if (results.calculatedBeroas <= 3) {
      recommendations.push({
        type: 'success',
        icon: '✅',
        text: `Excellent BEROAS (${results.calculatedBeroas.toFixed(2)}) - Configuration idéale pour la croissance publicitaire.`
      });
    } else if (results.calculatedBeroas <= 4) {
      recommendations.push({
        type: 'warning',
        icon: '👍',
        text: `BEROAS correct (${results.calculatedBeroas.toFixed(2)}) mais il y a de la marge d'amélioration.`
      });
    } else {
      recommendations.push({
        type: 'error',
        icon: '⚠️',
        text: `BEROAS élevé (${results.calculatedBeroas.toFixed(2)}) - Difficile d'être rentable en publicité.`
      });
    }

    if (results.marginPercent < 15) {
      recommendations.push({
        type: 'error',
        icon: '🔴',
        text: 'Marge critique (<15%) - Votre produit n\'est pas viable sans optimisations majeures.'
      });
    } else if (results.marginPercent >= 50) {
      recommendations.push({
        type: 'success',
        icon: '💎',
        text: `Marge excellente (${results.marginPercent.toFixed(1)}%) - Vous avez une grande flexibilité tarifaire.`
      });
    }

    if (state.paymentFees > 3.5) {
      recommendations.push({
        type: 'warning',
        icon: '💳',
        text: 'Frais bancaires élevés (>3.5%) - Négociez avec votre processeur ou changez de solution.'
      });
    }

    if (state.platformFees > 12) {
      recommendations.push({
        type: 'warning',
        icon: '🏪',
        text: 'Commission plateforme élevée (>12%) - Considérez vendre sur votre propre site.'
      });
    }

    if (state.returnsRate > 15) {
      recommendations.push({
        type: 'warning',
        icon: '📦',
        text: 'Taux de retour élevé (>15%) - Améliorez vos descriptions produit et photos.'
      });
    }

    return recommendations;
  }

  static generateROIInsights(state: BeroasState, projections: VolumeProjections) {
    const insights = [];
    const actions = [];

    // ROI Analysis
    if (projections.roi > 300) {
      insights.push({
        icon: '🚀',
        text: `ROI exceptionnel (${Math.round(projections.roi)}%) : chaque euro de pub génère ${(projections.roi/100).toFixed(1)}€ de profit net.`
      });
      actions.push({
        type: 'success',
        text: 'Augmentez massivement votre budget publicitaire - votre modèle est très rentable'
      });
    } else if (projections.roi > 150) {
      insights.push({
        icon: '💰',
        text: `ROI solide (${Math.round(projections.roi)}%) : modèle économique viable et rentable.`
      });
      actions.push({
        type: 'success',
        text: 'Scaling progressif recommandé - testez une augmentation de 50% du budget'
      });
    } else if (projections.roi > 50) {
      insights.push({
        icon: '📈',
        text: `ROI modéré (${Math.round(projections.roi)}%) : rentable mais perfectible.`
      });
      actions.push({
        type: 'warning',
        text: 'Optimisez votre taux de conversion ou réduisez le CPC avant de scaler'
      });
    } else if (projections.netProfit > 0) {
      insights.push({
        icon: '⚠️',
        text: `ROI faible (${Math.round(projections.roi)}%) : rentabilité très limitée.`
      });
      actions.push({
        type: 'warning',
        text: 'Priorité : améliorer la conversion et négocier de meilleurs CPC'
      });
    } else {
      insights.push({
        icon: '🔴',
        text: `Perte de ${Math.abs(projections.netProfit).toLocaleString('fr-FR', { style: 'currency', currency: 'EUR' })} par mois avec ces paramètres.`
      });
      actions.push({
        type: 'error',
        text: 'Modèle non viable : augmentez prix/conversion ou réduisez drastiquement les coûts'
      });
    }

    // Conversion insights
    if (state.conversionRate >= 5) {
      actions.push({
        type: 'info',
        text: 'Diversifiez vos canaux d\'acquisition - votre site convertit déjà très bien'
      });
    } else if (state.conversionRate < 2) {
      insights.push({
        icon: '📉',
        text: `Taux de conversion faible (${state.conversionRate}%) : forte marge d'amélioration.`
      });
      actions.push({
        type: 'warning',
        text: 'Priorité absolue : optimisation du tunnel de conversion (+1% = +40% de profits)'
      });
    }

    return { insights, actions };
  }
}