// /var/www/megahub/websites/humari-site/src/components/tools/calories-calculator/utils/exportPDF.ts

import type { ExportData } from '../types';
import { DIET_PRESETS, GOAL_CONFIG, DIET_INTENSITY_CONFIG } from '../types';

// Types pour jsPDF
interface JsPDFConstructor {
  new (options?: {
    orientation?: 'portrait' | 'landscape';
    unit?: string;
    format?: string;
    putOnlyUsedFonts?: boolean;
    compress?: boolean;
  }): JsPDFInstance;
}

interface JsPDFInstance {
  setFontSize(size: number): void;
  setFont(fontName: string, fontStyle: string): void;
  setTextColor(color: string): void;
  splitTextToSize(text: string, maxWidth: number): string[];
  text(text: string | string[], x: number, y: number): void;
  addPage(): void;
  output(type: 'blob'): Blob;
  setDrawColor(r: number, g: number, b: number): void;
  setFillColor(r: number, g: number, b: number): void;
  rect(x: number, y: number, width: number, height: number, style?: string): void;
  line(x1: number, y1: number, x2: number, y2: number): void;
  internal: {
    pageSize: {
      getHeight(): number;
      getWidth(): number;
    };
  };
}

// Déclaration TypeScript pour jsPDF
declare global {
  interface Window {
    jspdf?: {
      jsPDF: JsPDFConstructor;
    };
    jsPDF?: JsPDFConstructor;
  }
}

export async function exportToPDF(exportData: ExportData): Promise<void> {
  try {
    console.log('🚀 Début export PDF...');
    
    // Charger jsPDF
    await loadJsPDF();
    console.log('✅ jsPDF chargé');
    
    // Créer le PDF
    const pdfBlob = await generatePDF(exportData);
    console.log('✅ PDF généré');
    
    // Télécharger
    downloadPDF(pdfBlob, exportData);
    console.log('✅ PDF téléchargé');
    
  } catch (error) {
    console.error('❌ Erreur export PDF:', error);
    throw new Error(`Erreur export PDF: ${error instanceof Error ? error.message : 'Erreur inconnue'}`);
  }
}

async function loadJsPDF(): Promise<void> {
  // Vérifier si jsPDF est déjà chargé
  if (window.jsPDF || (window.jspdf?.jsPDF)) {
    console.log('jsPDF déjà disponible');
    return;
  }

  console.log('Chargement de jsPDF...');
  
  try {
    // Charger jsPDF depuis CDN
    await loadScript('https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js');
    
    // Attendre un petit délai pour la disponibilité
    await new Promise(resolve => setTimeout(resolve, 100));
    
    // Vérifier que jsPDF est maintenant disponible
    if (!window.jsPDF && !window.jspdf?.jsPDF) {
      throw new Error('jsPDF non trouvé après chargement');
    }
    
    console.log('jsPDF chargé avec succès');
    
  } catch (error) {
    console.error('Erreur chargement jsPDF:', error);
    throw new Error('Impossible de charger jsPDF');
  }
}

async function generatePDF(exportData: ExportData): Promise<Blob> {
  // Accéder à jsPDF de manière robuste
  let JsPDFConstructor: JsPDFConstructor;
  if (window.jsPDF) {
    JsPDFConstructor = window.jsPDF;
  } else if (window.jspdf?.jsPDF) {
    JsPDFConstructor = window.jspdf.jsPDF;
  } else {
    throw new Error('jsPDF non disponible');
  }

  console.log('Création du document PDF...');

  // Créer le document
  const doc = new JsPDFConstructor({
    orientation: 'portrait',
    unit: 'mm',
    format: 'a4',
    putOnlyUsedFonts: true,
    compress: true
  });

  // Configuration de base
  const margin = 20;
  const pageWidth = 210;
  const pageHeight = 297;
  const contentWidth = pageWidth - (2 * margin);
  let currentY = margin;

  // Récupération des données
  const { userData, results } = exportData;
  const goalConfig = GOAL_CONFIG[userData.goal];
  const dietPreset = DIET_PRESETS[results.dietType];
  const intensityConfig = DIET_INTENSITY_CONFIG[userData.dietIntensity];

  // Helper pour ajouter du texte
  const addText = (text: string, size: number = 12, isBold: boolean = false, color: string = '#000000') => {
    doc.setFontSize(size);
    doc.setFont('helvetica', isBold ? 'bold' : 'normal');
    doc.setTextColor(color);
    
    const lines = doc.splitTextToSize(text, contentWidth);
    doc.text(lines, margin, currentY);
    currentY += lines.length * (size * 0.4) + 2;
  };

  const addSpace = (space: number = 6) => {
    currentY += space;
  };

  const addSection = (title: string) => {
    addSpace(12);
    // Ligne décorative au-dessus du titre
    doc.setDrawColor(254, 0, 73);
    doc.setFillColor(254, 0, 73);
    doc.rect(margin, currentY - 2, 40, 1, 'F');
    addSpace(4);
    addText(title, 16, true, '#374151');
    addSpace(8);
  };

  const addBulletPoint = (text: string, highlight: boolean = false) => {
    if (highlight) {
      addText(`• ${text}`, 12, true, '#059669');
    } else {
      addText(`• ${text}`, 12, false, '#333333');
    }
  };

  const checkPageBreak = (neededSpace: number = 30) => {
    if (currentY + neededSpace > pageHeight - margin) {
      doc.addPage();
      currentY = margin;
    }
  };

  try {
    // En-tête avec logo/branding (garde comme c'était, ça marche bien)
    doc.setFillColor(254, 0, 73);
    doc.rect(0, 0, pageWidth, 25, 'F');
    
    doc.setTextColor('#FFFFFF');
    doc.setFontSize(20);
    doc.setFont('helvetica', 'bold');
    doc.text('RAPPORT BESOINS CALORIQUES', margin, 16);
    
    currentY = 40;

    // Informations principales - mise en forme propre
    addText(`Objectif: ${goalConfig.label}`, 14, true, '#374151');
    addText(`Regime alimentaire: ${dietPreset.name}`, 12, false, '#555555');
    addText(`Intensite: ${intensityConfig.label} (${intensityConfig.weeklyTarget})`, 12, false, '#555555');
    addSpace(4);
    addText(`Calcule le ${exportData.calculatedAt.toLocaleDateString('fr-FR')} a ${exportData.calculatedAt.toLocaleTimeString('fr-FR')}`, 10, false, '#888888');

    // Résultats principaux
    checkPageBreak(80);
    addSection('VOS RESULTATS CALORIQUES');
    
    addBulletPoint(`Metabolisme de base (BMR): ${results.bmr} calories/jour`);
    addBulletPoint(`Depense totale (TDEE): ${results.tdee} calories/jour`);
    addBulletPoint(`CALORIES POUR VOTRE OBJECTIF: ${results.goalCalories} calories/jour`, true);
    addBulletPoint(`Proteines recommandees: ${results.proteinPerKg}g par kg de poids`);
    
    if (userData.goal !== 'maintain') {
      const changeText = userData.goal === 'cut' ? 'perte' : 'gain';
      addBulletPoint(`Objectif hebdomadaire: ${changeText} de ${Math.abs(results.weeklyWeightChange)}kg`);
    }

    // Macronutriments
    checkPageBreak(60);
    addSection('REPARTITION DES MACRONUTRIMENTS');
    
    addBulletPoint(`Proteines: ${results.macros.protein.grams}g (${results.macros.protein.percentage}% des calories)`);
    addBulletPoint(`Glucides: ${results.macros.carbs.grams}g (${results.macros.carbs.percentage}% des calories)`);
    addBulletPoint(`Lipides: ${results.macros.fats.grams}g (${results.macros.fats.percentage}% des calories)`);
    
    addSpace(6);
    const totalCals = results.macros.protein.calories + results.macros.carbs.calories + results.macros.fats.calories;
    addText(`Total: ${totalCals} calories`, 11, false, '#888888');

    // Profil utilisateur
    checkPageBreak(80);
    addSection('VOTRE PROFIL');
    
    addBulletPoint(`${userData.gender === 'male' ? 'Homme' : 'Femme'}, ${userData.age} ans`);
    addBulletPoint(`Poids: ${userData.weight}kg, Taille: ${userData.height}cm`);
    addBulletPoint(`Niveau d'activite: ${getActivityLabel(userData.activityLevel)}`);
    
    if (userData.bodyFat) {
      addBulletPoint(`Taux de masse grasse: ${userData.bodyFat}%`);
    }
    
    if (userData.useAdvancedMode) {
      addBulletPoint(`Entrainement: ${userData.workoutDays} seances/semaine (${userData.workoutDuration}min)`);
      if (userData.hasCardio) {
        addBulletPoint(`Cardio additionnel: ${userData.cardioMinutes}min/semaine`);
      }
    }
    
    addBulletPoint(`Formule utilisee: ${getFormulaLabel(userData.formula)}`);

    // Détails calculs (si mode avancé)
    if (userData.useAdvancedMode) {
      checkPageBreak(120);
      addSection('DETAILS DES CALCULS');
      
      // BMR
      addText('Metabolisme de base (BMR):', 13, true, '#374151');
      addSpace(4);
      addText(results.calculationDetails.bmrFormula, 10, false, '#666666');
      addText(`→ Resultat: ${results.bmr} calories/jour`, 11, true, '#333333');
      
      addSpace(10);
      
      // TDEE
      addText('Depense energetique totale (TDEE):', 13, true, '#374151');
      addSpace(4);
      addText(`BMR x ${results.calculationDetails.activityMultiplier} (facteur d'activite)`, 10, false, '#666666');
      if (results.calculationDetails.workoutAdjustment > 0) {
        addText(`+ ${Math.round(results.calculationDetails.workoutAdjustment)} calories (ajustement entrainement)`, 10, false, '#666666');
      }
      addText(`→ Resultat: ${results.tdee} calories/jour`, 11, true, '#333333');
      
      addSpace(10);
      
      // Calories objectif
      addText('Calories objectif:', 13, true, '#374151');
      addSpace(4);
      const adjustmentText = results.calculationDetails.goalAdjustment >= 0 ? 
        `TDEE + ${results.calculationDetails.goalAdjustment}` : 
        `TDEE ${results.calculationDetails.goalAdjustment}`;
      addText(`${adjustmentText} calories`, 10, false, '#666666');
      addText(`→ Resultat: ${results.goalCalories} calories/jour`, 11, true, '#333333');
    }

    // Footer avec lien - repositionné proprement
    const footerY = pageHeight - 30;
    
    // Ligne de séparation
    doc.setDrawColor(220, 220, 220);
    doc.line(margin, footerY - 5, pageWidth - margin, footerY - 5);
    
    // Texte footer aligné proprement
    doc.setFontSize(9);
    doc.setTextColor('#666666');
    doc.text('Calcule avec Humari - Agence Marketing Digital', margin, footerY + 2);
    
    // URL dynamique
    const currentUrl = typeof window !== 'undefined' ? window.location.href : 'https://humari.fr/outils/calculateur-calories';
    doc.setTextColor('#0066CC');
    doc.text(`Recalculer: ${currentUrl}`, margin, footerY + 9);
    
    doc.setTextColor('#666666');
    doc.text('Rapport 100% gratuit et prive - Aucune donnee transmise', margin, footerY + 16);

    console.log('Document PDF créé');
    return doc.output('blob');
    
  } catch (error) {
    console.error('Erreur création contenu PDF:', error);
    throw new Error(`Erreur génération contenu: ${error instanceof Error ? error.message : 'Erreur inconnue'}`);
  }
}

function downloadPDF(pdfBlob: Blob, exportData: ExportData): void {
  try {
    const url = URL.createObjectURL(pdfBlob);
    const link = document.createElement('a');
    link.href = url;
    
    const dateStr = exportData.calculatedAt.toISOString().split('T')[0];
    const goalStr = exportData.userData.goal === 'cut' ? 'perte' : 
                   exportData.userData.goal === 'bulk' ? 'masse' : 'maintien';
    
    link.download = `besoins-caloriques-${goalStr}-${dateStr}.pdf`;
    
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    // Nettoyer l'URL
    setTimeout(() => URL.revokeObjectURL(url), 1000);
    
  } catch (error) {
    console.error('Erreur téléchargement PDF:', error);
    throw new Error('Erreur lors du téléchargement');
  }
}

// Helpers
function loadScript(src: string): Promise<void> {
  return new Promise((resolve, reject) => {
    // Vérifier si le script est déjà chargé
    if (document.querySelector(`script[src="${src}"]`)) {
      resolve();
      return;
    }

    const script = document.createElement('script');
    script.src = src;
    script.async = true;
    
    script.onload = () => {
      console.log(`✅ Script chargé: ${src}`);
      resolve();
    };
    
    script.onerror = (error) => {
      console.error(`❌ Erreur chargement script: ${src}`, error);
      reject(new Error(`Erreur chargement ${src}`));
    };
    
    document.head.appendChild(script);
  });
}

function getActivityLabel(level: string): string {
  const labels = {
    sedentary: 'Sedentaire',
    light: 'Legerement actif',
    moderate: 'Moderement actif', 
    high: 'Tres actif',
    extreme: 'Extremement actif'
  };
  return labels[level as keyof typeof labels] || level;
}

function getFormulaLabel(formula: string): string {
  const labels = {
    mifflin: 'Mifflin-St Jeor',
    harris: 'Harris-Benedict',
    katch: 'Katch-McArdle'
  };
  return labels[formula as keyof typeof labels] || formula;
}