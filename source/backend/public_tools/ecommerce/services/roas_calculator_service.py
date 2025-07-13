# backend/public_tools/ecommerce/services/roas_calculator_service.py
import math
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Optional, Union

class ROASCalculatorService:
    """
    Service de calcul ROAS basé sur le template Excel consolidé
    Implémente les 4 modules : Sourcing, Publicité, Performance quotidienne, Allocation multi-canaux
    """
    
    # Constantes par défaut (répliquent le template Excel)
    DEFAULT_SAFETY_MARGIN = Decimal('0.07')  # 7%
    DEFAULT_TARGET_ROAS = Decimal('2.0')     # ROAS cible 2.0
    DEFAULT_CURRENCY = 'EUR'
    
    def __init__(self):
        self.currency = self.DEFAULT_CURRENCY
        
    def _to_decimal(self, value: Union[str, int, float, Decimal]) -> Decimal:
        """Convertit une valeur en Decimal pour calculs précis"""
        if isinstance(value, Decimal):
            return value
        if isinstance(value, str):
            # Nettoyer les caractères monétaires
            cleaned = value.replace('€', '').replace('$', '').replace(',', '.').strip()
            return Decimal(cleaned)
        return Decimal(str(value))
    
    def _round_currency(self, value: Decimal, places: int = 2) -> Decimal:
        """Arrondit une valeur monétaire"""
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def _round_percentage(self, value: Decimal, places: int = 2) -> Decimal:
        """Arrondit un pourcentage"""
        return value.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def calculate_sourcing_costs(self, data: Dict) -> Dict:
        """
        Module 1 : Calcul des coûts de sourcing
        Réplique les formules Excel de l'onglet "Calcul des couts de sourcing"
        """
        try:
            # Inputs
            product_price = self._to_decimal(data.get('product_price', 0))
            shipping_direct = self._to_decimal(data.get('shipping_direct', 0))
            shipping_to_3pl = self._to_decimal(data.get('shipping_to_3pl', 0))
            shipping_3pl_to_client = self._to_decimal(data.get('shipping_3pl_to_client', 0))
            
            # Calculs COGS selon logistique (formules Excel)
            cogs_direct = product_price + shipping_direct  # =B5+C5
            cogs_3pl = product_price + shipping_to_3pl + shipping_3pl_to_client  # =B5+D5+E5
            
            return {
                'product_price': float(self._round_currency(product_price)),
                'shipping_costs': {
                    'direct': float(self._round_currency(shipping_direct)),
                    'to_3pl': float(self._round_currency(shipping_to_3pl)),
                    '3pl_to_client': float(self._round_currency(shipping_3pl_to_client))
                },
                'cogs': {
                    'direct_shipping': float(self._round_currency(cogs_direct)),
                    '3pl_shipping': float(self._round_currency(cogs_3pl)),
                    'difference': float(self._round_currency(abs(cogs_direct - cogs_3pl)))
                },
                'recommendations': {
                    'optimal_shipping': 'direct' if cogs_direct <= cogs_3pl else '3pl',
                    'cost_saving': float(self._round_currency(abs(cogs_direct - cogs_3pl)))
                }
            }
            
        except Exception as e:
            raise ValueError(f"Erreur calcul sourcing: {str(e)}")
    
    def calculate_advertising_costs(self, data: Dict) -> Dict:
        """
        Module 2 : Calcul des coûts publicitaires  
        Réplique les formules Excel de l'onglet "Calcul des couts publicitaires"
        """
        try:
            # Inputs
            cogs = self._to_decimal(data.get('cogs', 0))
            selling_price = self._to_decimal(data.get('selling_price', 0))
            shipping_cost_customer = self._to_decimal(data.get('shipping_cost_customer', 0))
            safety_margin = self._to_decimal(data.get('safety_margin', self.DEFAULT_SAFETY_MARGIN))
            target_roas = self._to_decimal(data.get('target_roas', self.DEFAULT_TARGET_ROAS))
            
            # Calculs Excel (cellules E5, G5, H5, I5, K5, L5, M5, O5)
            total_selling_price = selling_price + shipping_cost_customer  # =C5+D5
            gross_margin_decimal = 1 - (cogs / total_selling_price)  # =1-B5/E5
            gross_margin_percentage = gross_margin_decimal * 100
            
            # CPA Breakeven avec marge de sécurité
            cpa_breakeven_safe = total_selling_price - cogs - (safety_margin * total_selling_price)  # =E5-B5-$H$2*E5
            
            # ROAS nécessaire pour être breakeven
            roas_breakeven = total_selling_price / cpa_breakeven_safe  # =E5/H5
            
            # CPA maximum selon ROAS cible
            cpa_max_target = total_selling_price / target_roas  # =E5/$L$2
            
            # Marge nette avec ROAS cible
            net_margin_target_decimal = (total_selling_price - cogs - cpa_max_target) / total_selling_price  # =(E5-B5-K5)/E5
            net_margin_target_percentage = net_margin_target_decimal * 100
            
            # Profit avec ROAS cible
            profit_target = total_selling_price - cogs - cpa_max_target  # =E5-B5-K5
            
            # Seuil de rentabilité (sans marge de sécurité)
            breakeven_threshold = total_selling_price - (safety_margin * total_selling_price)  # =E5-($P$2*E5)
            
            return {
                'inputs': {
                    'cogs': float(self._round_currency(cogs)),
                    'selling_price': float(self._round_currency(selling_price)),
                    'shipping_cost': float(self._round_currency(shipping_cost_customer)),
                    'total_selling_price': float(self._round_currency(total_selling_price)),
                    'safety_margin': float(self._round_percentage(safety_margin * 100)),
                    'target_roas': float(target_roas)
                },
                'margins': {
                    'gross_margin_percentage': float(self._round_percentage(gross_margin_percentage)),
                    'gross_margin_amount': float(self._round_currency(total_selling_price - cogs)),
                    'net_margin_target_percentage': float(self._round_percentage(net_margin_target_percentage)),
                    'net_margin_target_amount': float(self._round_currency(profit_target))
                },
                'cpa_analysis': {
                    'cpa_breakeven_safe': float(self._round_currency(cpa_breakeven_safe)),
                    'cpa_max_target': float(self._round_currency(cpa_max_target)),
                    'cpa_difference': float(self._round_currency(abs(cpa_breakeven_safe - cpa_max_target)))
                },
                'roas_analysis': {
                    'roas_breakeven': float(self._round_percentage(roas_breakeven, 3)),
                    'target_roas': float(target_roas),
                    'roas_safety_buffer': float(self._round_percentage(target_roas - roas_breakeven, 3))
                },
                'profitability': {
                    'profit_target': float(self._round_currency(profit_target)),
                    'breakeven_threshold': float(self._round_currency(breakeven_threshold)),
                    'is_profitable': profit_target > 0
                },
                'recommendations': self._generate_advertising_recommendations(
                    roas_breakeven, target_roas, gross_margin_percentage, profit_target
                )
            }
            
        except Exception as e:
            raise ValueError(f"Erreur calcul publicité: {str(e)}")
    
    def calculate_daily_performance(self, data: Dict) -> Dict:
        """
        Module 3 : Calcul de performance quotidienne
        Réplique les formules Excel de l'onglet "Résultats journaliers"
        """
        try:
            daily_entries = data.get('daily_entries', [])
            
            if not daily_entries:
                return {'error': 'Aucune donnée quotidienne fournie'}
            
            results = []
            totals = {
                'total_revenue': Decimal('0'),
                'total_spend': Decimal('0'),
                'total_conversions': 0,
                'avg_roas': Decimal('0')
            }
            
            for entry in daily_entries:
                date = entry.get('date')
                shopify_revenue = self._to_decimal(entry.get('shopify_revenue', 0))
                facebook_spend = self._to_decimal(entry.get('facebook_spend', 0))
                google_spend = self._to_decimal(entry.get('google_spend', 0))
                influencer_spend = self._to_decimal(entry.get('influencer_spend', 0))
                other_spend = self._to_decimal(entry.get('other_spend', 0))
                
                # Calculs quotidiens (formules Excel)
                total_daily_spend = facebook_spend + google_spend + influencer_spend + other_spend
                daily_roas = shopify_revenue / total_daily_spend if total_daily_spend > 0 else Decimal('0')
                
                # Accumulation pour totaux
                totals['total_revenue'] += shopify_revenue
                totals['total_spend'] += total_daily_spend
                if shopify_revenue > 0:
                    totals['total_conversions'] += 1
                
                results.append({
                    'date': date,
                    'revenue': float(self._round_currency(shopify_revenue)),
                    'spend_breakdown': {
                        'facebook': float(self._round_currency(facebook_spend)),
                        'google': float(self._round_currency(google_spend)),
                        'influencer': float(self._round_currency(influencer_spend)),
                        'other': float(self._round_currency(other_spend)),
                        'total': float(self._round_currency(total_daily_spend))
                    },
                    'roas': float(self._round_percentage(daily_roas, 2)),
                    'profit_loss': float(self._round_currency(shopify_revenue - total_daily_spend))
                })
            
            # Moyennes globales
            avg_roas = totals['total_revenue'] / totals['total_spend'] if totals['total_spend'] > 0 else Decimal('0')
            avg_daily_revenue = totals['total_revenue'] / len(daily_entries) if daily_entries else Decimal('0')
            avg_daily_spend = totals['total_spend'] / len(daily_entries) if daily_entries else Decimal('0')
            
            return {
                'daily_results': results,
                'summary': {
                    'total_revenue': float(self._round_currency(totals['total_revenue'])),
                    'total_spend': float(self._round_currency(totals['total_spend'])),
                    'total_profit': float(self._round_currency(totals['total_revenue'] - totals['total_spend'])),
                    'avg_roas': float(self._round_percentage(avg_roas, 2)),
                    'avg_daily_revenue': float(self._round_currency(avg_daily_revenue)),
                    'avg_daily_spend': float(self._round_currency(avg_daily_spend)),
                    'profitable_days': totals['total_conversions'],
                    'total_days': len(daily_entries)
                },
                'performance_metrics': self._calculate_performance_metrics(results)
            }
            
        except Exception as e:
            raise ValueError(f"Erreur calcul performance quotidienne: {str(e)}")
    
    def calculate_channel_allocation(self, data: Dict) -> Dict:
        """
        Module 4 : Allocation multi-canaux
        Réplique les formules Excel de l'onglet "Plusieurs Canaux Publicitaires"
        """
        try:
            channels = data.get('channels', [])
            total_shopify_revenue = self._to_decimal(data.get('total_shopify_revenue', 0))
            
            if not channels:
                return {'error': 'Aucun canal publicitaire fourni'}
            
            # Calculs par canal
            total_budget = Decimal('0')
            total_conversion_value = Decimal('0')
            channel_results = []
            
            for channel in channels:
                name = channel.get('name', 'Canal')
                budget = self._to_decimal(channel.get('budget', 0))
                roas_per_channel = self._to_decimal(channel.get('roas', 0))
                
                # Formules Excel (D3, E3, F3, G3)
                conversion_value = budget * roas_per_channel  # =B3*C3
                
                total_budget += budget
                total_conversion_value += conversion_value
                
                channel_results.append({
                    'name': name,
                    'budget': float(self._round_currency(budget)),
                    'roas': float(self._round_percentage(roas_per_channel, 2)),
                    'conversion_value': float(self._round_currency(conversion_value)),
                    'budget_percentage': 0,  # Calculé après
                    'conversion_percentage': 0,  # Calculé après
                    'estimated_roas': 0  # Calculé après
                })
            
            # Calculs globaux et pourcentages
            global_roas = total_conversion_value / total_budget if total_budget > 0 else Decimal('0')
            estimated_global_roas = total_shopify_revenue / total_budget if total_budget > 0 else Decimal('0')
            
            # Mise à jour des pourcentages par canal
            for i, result in enumerate(channel_results):
                if total_budget > 0:
                    result['budget_percentage'] = float(self._round_percentage(
                        (self._to_decimal(result['budget']) / total_budget) * 100, 2
                    ))
                
                if total_shopify_revenue > 0:
                    result['conversion_percentage'] = float(self._round_percentage(
                        (self._to_decimal(result['conversion_value']) / total_shopify_revenue) * 100, 2
                    ))
                
                # ROAS estimé pondéré (formule Excel E3)
                result['estimated_roas'] = float(self._round_percentage(
                    estimated_global_roas / global_roas * self._to_decimal(result['roas']) if global_roas > 0 else 0, 2
                ))
            
            return {
                'channels': channel_results,
                'global_metrics': {
                    'total_budget': float(self._round_currency(total_budget)),
                    'total_conversion_value': float(self._round_currency(total_conversion_value)),
                    'global_roas': float(self._round_percentage(global_roas, 2)),
                    'estimated_roas': float(self._round_percentage(estimated_global_roas, 2)),
                    'shopify_revenue': float(self._round_currency(total_shopify_revenue)),
                    'performance_gap': float(self._round_currency(abs(total_shopify_revenue - total_conversion_value)))
                },
                'optimization_suggestions': self._generate_channel_optimization(channel_results, global_roas)
            }
            
        except Exception as e:
            raise ValueError(f"Erreur calcul allocation canaux: {str(e)}")
    
    def calculate_complete_scenario(self, data: Dict) -> Dict:
        """
        Calcul complet intégrant les 4 modules
        """
        try:
            results = {}
            
            # Module 1 : Sourcing
            if 'sourcing' in data:
                results['sourcing'] = self.calculate_sourcing_costs(data['sourcing'])
            
            # Module 2 : Publicité
            if 'advertising' in data:
                results['advertising'] = self.calculate_advertising_costs(data['advertising'])
            
            # Module 3 : Performance quotidienne
            if 'daily_performance' in data:
                results['daily_performance'] = self.calculate_daily_performance(data['daily_performance'])
            
            # Module 4 : Allocation canaux
            if 'channel_allocation' in data:
                results['channel_allocation'] = self.calculate_channel_allocation(data['channel_allocation'])
            
            # Synthèse globale
            results['global_summary'] = self._generate_global_summary(results)
            
            return results
            
        except Exception as e:
            raise ValueError(f"Erreur calcul scénario complet: {str(e)}")
    
    def _generate_advertising_recommendations(self, roas_breakeven, target_roas, gross_margin, profit) -> List[str]:
        """Génère des recommandations basées sur les métriques publicitaires"""
        recommendations = []
        
        if roas_breakeven > target_roas:
            recommendations.append("⚠️ ROAS breakeven supérieur au ROAS cible - Revoir la stratégie tarifaire")
        
        if gross_margin < 70:
            recommendations.append("💡 Marge brute faible (<70%) - Optimiser les coûts ou augmenter les prix")
        
        if profit <= 0:
            recommendations.append("🔴 Scénario non rentable - Réduire les coûts ou augmenter le ROAS")
        
        if len(recommendations) == 0:
            recommendations.append("✅ Configuration profitable - Surveiller les performances réelles")
        
        return recommendations
    
    def _calculate_performance_metrics(self, daily_results) -> Dict:
        """Calcule des métriques de performance avancées"""
        if not daily_results:
            return {}
        
        roas_values = [entry['roas'] for entry in daily_results if entry['roas'] > 0]
        
        return {
            'best_roas_day': max(roas_values) if roas_values else 0,
            'worst_roas_day': min(roas_values) if roas_values else 0,
            'roas_volatility': float(self._round_percentage(
                Decimal(str(max(roas_values) - min(roas_values))) if len(roas_values) > 1 else Decimal('0'), 2
            )),
            'consistent_days': len([r for r in roas_values if r >= 2.0])
        }
    
    def _generate_channel_optimization(self, channels, global_roas) -> List[str]:
        """Génère des suggestions d'optimisation pour l'allocation des canaux"""
        suggestions = []
        
        # Identifier le canal le plus performant
        best_channel = max(channels, key=lambda x: x['roas']) if channels else None
        worst_channel = min(channels, key=lambda x: x['roas']) if channels else None
        
        if best_channel and worst_channel and best_channel['roas'] > worst_channel['roas'] * 1.5:
            suggestions.append(f"📈 Augmenter le budget sur {best_channel['name']} (ROAS: {best_channel['roas']})")
            suggestions.append(f"📉 Réduire le budget sur {worst_channel['name']} (ROAS: {worst_channel['roas']})")
        
        high_budget_low_roas = [c for c in channels if c['budget_percentage'] > 20 and c['roas'] < 2.0]
        if high_budget_low_roas:
            suggestions.append("⚡ Optimiser les canaux à gros budget mais faible ROAS")
        
        return suggestions or ["💡 Allocation équilibrée - Tester l'augmentation du budget sur les meilleurs canaux"]
    
    def _generate_global_summary(self, results) -> Dict:
        """Génère une synthèse globale de tous les modules"""
        summary = {
            'modules_calculated': list(results.keys()),
            'overall_health': 'good',
            'key_insights': [],
            'action_items': []
        }
        
        # Analyser chaque module pour des insights
        if 'advertising' in results:
            ad_data = results['advertising']
            if ad_data.get('profitability', {}).get('is_profitable'):
                summary['key_insights'].append("✅ Configuration publicitaire rentable")
            else:
                summary['key_insights'].append("⚠️ Configuration publicitaire à optimiser")
                summary['overall_health'] = 'warning'
        
        if 'channel_allocation' in results:
            channel_data = results['channel_allocation']
            best_roas = max([c['roas'] for c in channel_data.get('channels', [])], default=0)
            if best_roas > 3.0:
                summary['key_insights'].append(f"🚀 Excellent canal identifié (ROAS: {best_roas})")
        
        return summary