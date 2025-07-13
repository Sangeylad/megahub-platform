// src/components/tools/beroas-calculator/utils/exportUtils.ts
import jsPDF from 'jspdf';
import type { BeroasState, BeroasResults, MatrixCell } from '../types';

const formatCurrency = (value: number): string => {
 return new Intl.NumberFormat('fr-FR', {
   style: 'currency',
   currency: 'EUR',
   minimumFractionDigits: 0,
   maximumFractionDigits: 2
 }).format(value);
};

export const exportUtils = {
 async exportToPDF(state: BeroasState, results: BeroasResults) {
   const doc = new jsPDF();
   
   // Header
   doc.setFontSize(20);
   doc.setFont('helvetica', 'bold');
   doc.text('Analyse BEROAS - Rapport Complet', 20, 30);
   
   doc.setFontSize(12);
   doc.setFont('helvetica', 'normal');
   doc.text(`Généré le ${new Date().toLocaleDateString('fr-FR')} à ${new Date().toLocaleTimeString('fr-FR')}`, 20, 45);
   
   let yPos = 65;
   
   // Métriques principales
   doc.setFontSize(16);
   doc.setFont('helvetica', 'bold');
   doc.text('📊 Métriques Principales', 20, yPos);
   
   yPos += 15;
   doc.setFontSize(12);
   doc.setFont('helvetica', 'normal');
   
   const metrics = [
     `Prix de vente HT: ${formatCurrency(results.sellingPriceHT)}`,
     `Marge unitaire: ${formatCurrency(results.unitMargin)} (${results.marginPercent.toFixed(1)}%)`,
     `BEROAS calculé: ${results.calculatedBeroas.toFixed(2)}`,
     `Budget publicitaire max: ${formatCurrency(Math.max(0, results.unitMargin))}`,
     `Prix TTC client: ${formatCurrency(results.sellingPriceTTC)}`
   ];
   
   metrics.forEach(metric => {
     doc.text(metric, 20, yPos);
     yPos += 10;
   });
   
   // Détail des coûts
   yPos += 15;
   doc.setFontSize(16);
   doc.setFont('helvetica', 'bold');
   doc.text('💰 Détail des Coûts', 20, yPos);
   
   yPos += 15;
   doc.setFontSize(12);
   doc.setFont('helvetica', 'normal');
   
   const costs = [
     `Coût produit: ${formatCurrency(state.productCost)}`,
     `Frais livraison: ${formatCurrency(state.shippingCost)}`,
     `Emballage: ${formatCurrency(state.packagingCost || 0)}`,
     `Frais bancaires: ${formatCurrency(results.paymentFeesAmount)} (${state.paymentFees}%)`,
     `Commission plateforme: ${formatCurrency(results.platformFeesAmount || 0)} (${state.platformFees || 0}%)`,
     `Autres coûts: ${formatCurrency(state.otherCosts)}`,
     ``,
     `Total des coûts: ${formatCurrency(results.totalCosts)}`
   ];
   
   costs.forEach(cost => {
     if (cost) {
       doc.text(cost, 20, yPos);
     }
     yPos += cost ? 10 : 5;
   });
   
   // Recommandations
   yPos += 15;
   doc.setFontSize(16);
   doc.setFont('helvetica', 'bold');
   doc.text('💡 Recommandations', 20, yPos);
   
   yPos += 15;
   doc.setFontSize(12);
   doc.setFont('helvetica', 'normal');
   
   let recommendation = '';
   if (results.calculatedBeroas <= 2.5) {
     recommendation = '✅ Excellent BEROAS - Investissez massivement en publicité';
   } else if (results.calculatedBeroas <= 4) {
     recommendation = '👍 BEROAS correct - Optimisez vos coûts pour plus de flexibilité';
   } else {
     recommendation = '⚠️ BEROAS élevé - Réduisez vos coûts ou augmentez vos prix';
   }
   
   doc.text(recommendation, 20, yPos);
   yPos += 20;
   
   // Analyse détaillée
   if (state.monthlyOrders > 0) {
     doc.setFontSize(16);
     doc.setFont('helvetica', 'bold');
     doc.text('📈 Projection Mensuelle', 20, yPos);
     
     yPos += 15;
     doc.setFontSize(12);
     doc.setFont('helvetica', 'normal');
     
     const monthlyRevenue = results.sellingPriceHT * state.monthlyOrders;
     const monthlyProfit = results.unitMargin * state.monthlyOrders;
     
     const projections = [
       `Objectif commandes: ${state.monthlyOrders}/mois`,
       `CA mensuel: ${formatCurrency(monthlyRevenue)}`,
       `Profit brut mensuel: ${formatCurrency(monthlyProfit)}`,
       `Marge par commande: ${formatCurrency(results.unitMargin)}`
     ];
     
     projections.forEach(projection => {
       doc.text(projection, 20, yPos);
       yPos += 10;
     });
   }
   
   // Footer
   doc.setFontSize(10);
   doc.setFont('helvetica', 'italic');
   doc.text('Calculateur BEROAS - MEGAHUB | humari.fr', 20, 280);
   
   // Download
   doc.save(`analyse-beroas-${new Date().toISOString().split('T')[0]}.pdf`);
 },

 exportMatrixData(matrixData: MatrixCell[], filename: string = 'matrice-beroas') {
   const headers = ['Prix de vente', 'Coût produit', 'BEROAS', 'Marge unitaire', 'Rentable'];
   const rows = matrixData.map(cell => [
     cell.price.toFixed(2),
     cell.cost.toFixed(2),
     cell.beroas.toFixed(2),
     cell.margin.toFixed(2),
     cell.isRentable ? 'Oui' : 'Non'
   ]);
   
   const csvContent = [headers, ...rows]
     .map(row => row.join(','))
     .join('\n');
   
   const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
   const url = URL.createObjectURL(blob);
   const link = document.createElement('a');
   link.href = url;
   link.download = `${filename}-${new Date().toISOString().split('T')[0]}.csv`;
   document.body.appendChild(link);
   link.click();
   document.body.removeChild(link);
   URL.revokeObjectURL(url);
 }
};