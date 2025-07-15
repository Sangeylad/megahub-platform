// frontend/src/utils/xssProtection.ts

// 🛡️ XSS Protection - Sanitization sécurisée selon standards MegaHub

// ==========================================
// CARACTÈRES DANGEREUX & REMPLACEMENTS
// ==========================================

const XSS_PATTERNS = {
  // HTML tags et caractères dangereux
  htmlTags: /<[^>]*>/g,
  scriptTags: /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
  styleTags: /<style\b[^<]*(?:(?!<\/style>)<[^<]*)*<\/style>/gi,
  onEventAttributes: /\s*on\w+\s*=\s*["'][^"']*["']/gi,
  
  // JavaScript patterns
  javascript: /javascript:/gi,
  vbscript: /vbscript:/gi,
  dataUri: /data:/gi,
  
  // SQL injection patterns
  sqlKeywords: /(\b(select|insert|update|delete|drop|union|exec|execute)\b)/gi,
  
  // XSS vectors communs
  xssVectors: /(alert\s*\(|confirm\s*\(|prompt\s*\(|eval\s*\(|setTimeout\s*\(|setInterval\s*\()/gi,
} as const;

const HTML_ENTITIES = {
  '&': '&amp;',
  '<': '&lt;',
  '>': '&gt;',
  '"': '&quot;',
  "'": '&#x27;',
  '/': '&#x2F;',
  '`': '&#96;',
  '=': '&#x3D;',
} as const;

const SAFE_REPLACEMENTS = {
  '<': '[',
  '>': ']',
  '"': "'",
  '&': 'and',
  '%': 'percent',
  '(': '[',
  ')': ']',
} as const;

// ==========================================
// INTERFACE CONFIGURATION
// ==========================================

interface SanitizeOptions {
  allowHtml?: boolean;
  allowedTags?: string[];
  allowedAttributes?: string[];
  maxLength?: number;
  preserveWhitespace?: boolean;
  strictMode?: boolean;
  logViolations?: boolean;
}

interface ValidationResult {
  isValid: boolean;
  sanitized: string;
  violations: string[];
  originalLength: number;
  sanitizedLength: number;
}

// ==========================================
// CLASSE XSS PROTECTION
// ==========================================

class XSSProtection {
  private defaultOptions: Required<SanitizeOptions> = {
    allowHtml: false,
    allowedTags: [],
    allowedAttributes: [],
    maxLength: 10000,
    preserveWhitespace: false,
    strictMode: true,
    logViolations: true,
  };

  // ==========================================
  // SANITIZATION PRINCIPALE
  // ==========================================

  sanitizeInput(input: string, options: SanitizeOptions = {}): string {
    if (typeof input !== 'string') {
      return String(input || '');
    }

    const config = { ...this.defaultOptions, ...options };
    const violations: string[] = [];
    let sanitized = input;

    // Longueur maximale
    if (sanitized.length > config.maxLength) {
      sanitized = sanitized.substring(0, config.maxLength);
      violations.push(`Input truncated to ${config.maxLength} characters`);
    }

    // Mode strict - sanitization agressive
    if (config.strictMode) {
      sanitized = this.aggressiveSanitize(sanitized, violations);
    } else {
      sanitized = this.basicSanitize(sanitized, violations);
    }

    // Gestion HTML
    if (!config.allowHtml) {
      sanitized = this.stripHtml(sanitized, violations);
    } else {
      sanitized = this.sanitizeHtml(sanitized, config, violations);
    }

    // Normalisation whitespace
    if (!config.preserveWhitespace) {
      sanitized = sanitized.trim().replace(/\s+/g, ' ');
    }

    // Logging des violations
    if (config.logViolations && violations.length > 0) {
      this.logSecurityViolation(input, sanitized, violations);
    }

    return sanitized;
  }

  // ==========================================
  // SANITIZATION AGRESSIVE (MODE STRICT)
  // ==========================================

  private aggressiveSanitize(input: string, violations: string[]): string {
    let sanitized = input;

    // Supprimer complètement les patterns dangereux
    if (XSS_PATTERNS.scriptTags.test(sanitized)) {
      sanitized = sanitized.replace(XSS_PATTERNS.scriptTags, '');
      violations.push('Script tags removed');
    }

    if (XSS_PATTERNS.styleTags.test(sanitized)) {
      sanitized = sanitized.replace(XSS_PATTERNS.styleTags, '');
      violations.push('Style tags removed');
    }

    if (XSS_PATTERNS.onEventAttributes.test(sanitized)) {
      sanitized = sanitized.replace(XSS_PATTERNS.onEventAttributes, '');
      violations.push('Event attributes removed');
    }

    if (XSS_PATTERNS.javascript.test(sanitized)) {
      sanitized = sanitized.replace(XSS_PATTERNS.javascript, '');
      violations.push('JavaScript protocol removed');
    }

    if (XSS_PATTERNS.vbscript.test(sanitized)) {
      sanitized = sanitized.replace(XSS_PATTERNS.vbscript, '');
      violations.push('VBScript protocol removed');
    }

    if (XSS_PATTERNS.dataUri.test(sanitized)) {
      sanitized = sanitized.replace(XSS_PATTERNS.dataUri, '');
      violations.push('Data URI removed');
    }

    if (XSS_PATTERNS.xssVectors.test(sanitized)) {
      sanitized = sanitized.replace(XSS_PATTERNS.xssVectors, '');
      violations.push('XSS vectors removed');
    }

    if (XSS_PATTERNS.sqlKeywords.test(sanitized)) {
      sanitized = sanitized.replace(XSS_PATTERNS.sqlKeywords, (match) => `[${match}]`);
      violations.push('SQL keywords neutralized');
    }

    return sanitized;
  }

  // ==========================================
  // SANITIZATION BASIQUE
  // ==========================================

  private basicSanitize(input: string, violations: string[]): string {
    let sanitized = input;

    // Remplacer les caractères dangereux par des équivalents sûrs
    for (const [dangerous, safe] of Object.entries(SAFE_REPLACEMENTS)) {
      if (sanitized.includes(dangerous)) {
        sanitized = sanitized.replace(new RegExp(dangerous, 'g'), safe);
        violations.push(`Replaced dangerous character: ${dangerous}`);
      }
    }

    return sanitized;
  }

  // ==========================================
  // GESTION HTML
  // ==========================================

  private stripHtml(input: string, violations: string[]): string {
    if (XSS_PATTERNS.htmlTags.test(input)) {
      violations.push('HTML tags stripped');
      return input.replace(XSS_PATTERNS.htmlTags, '');
    }
    return input;
  }

  private sanitizeHtml(
    input: string, 
    config: Required<SanitizeOptions>,
    violations: string[]
  ): string {
    let sanitized = input;

    // Escape HTML entities
    for (const [char, entity] of Object.entries(HTML_ENTITIES)) {
      sanitized = sanitized.replace(new RegExp(char, 'g'), entity);
    }

    // Autoriser seulement les tags spécifiés
    if (config.allowedTags.length > 0) {
      const allowedTagsRegex = new RegExp(
        `<(?!\/?(?:${config.allowedTags.join('|')})\b)[^>]*>`,
        'gi'
      );
      
      if (allowedTagsRegex.test(sanitized)) {
        sanitized = sanitized.replace(allowedTagsRegex, '');
        violations.push('Disallowed HTML tags removed');
      }
    }

    return sanitized;
  }

  // ==========================================
  // VALIDATION COMPLÈTE
  // ==========================================

  validateAndSanitize(input: string, options: SanitizeOptions = {}): ValidationResult {
    const originalLength = input.length;
    const violations: string[] = [];
    
    const sanitized = this.sanitizeInput(input, {
      ...options,
      logViolations: false, // On gère le logging ici
    });

    const isValid = sanitized === input && violations.length === 0;

    const result: ValidationResult = {
      isValid,
      sanitized,
      violations,
      originalLength,
      sanitizedLength: sanitized.length,
    };

    // Log si nécessaire
    if (!isValid && (options.logViolations ?? true)) {
      this.logSecurityViolation(input, sanitized, violations);
    }

    return result;
  }

  // ==========================================
  // VALIDATION SPÉCIALISÉE
  // ==========================================

  sanitizeEmail(email: string): string {
    return this.sanitizeInput(email, {
      allowHtml: false,
      maxLength: 254,
      strictMode: true,
      preserveWhitespace: false,
    });
  }

  sanitizeUrl(url: string): string {
    let sanitized = this.sanitizeInput(url, {
      allowHtml: false,
      maxLength: 2048,
      strictMode: true,
    });

    // Vérifier que l'URL commence par http/https
    if (sanitized && !sanitized.match(/^https?:\/\//)) {
      sanitized = '';
    }

    return sanitized;
  }

  sanitizeUsername(username: string): string {
    return this.sanitizeInput(username, {
      allowHtml: false,
      maxLength: 30,
      strictMode: true,
      preserveWhitespace: false,
    });
  }

  sanitizeFileName(filename: string): string {
    let sanitized = this.sanitizeInput(filename, {
      allowHtml: false,
      maxLength: 255,
      strictMode: true,
    });

    // Supprimer les caractères dangereux pour les noms de fichiers
    sanitized = sanitized.replace(/[<>:"/\\|?*\x00-\x1f]/g, '');
    
    return sanitized;
  }

  sanitizeSearchQuery(query: string): string {
    return this.sanitizeInput(query, {
      allowHtml: false,
      maxLength: 500,
      strictMode: false, // Moins strict pour la recherche
      preserveWhitespace: true,
    });
  }

  // ==========================================
  // HELPERS & UTILS
  // ==========================================

  isInputSafe(input: string): boolean {
    const patterns = Object.values(XSS_PATTERNS);
    return !patterns.some(pattern => pattern.test(input));
  }

  detectXSSAttempt(input: string): string[] {
    const threats: string[] = [];

    if (XSS_PATTERNS.scriptTags.test(input)) threats.push('Script injection');
    if (XSS_PATTERNS.onEventAttributes.test(input)) threats.push('Event handler injection');
    if (XSS_PATTERNS.javascript.test(input)) threats.push('JavaScript protocol');
    if (XSS_PATTERNS.xssVectors.test(input)) threats.push('XSS function calls');
    if (XSS_PATTERNS.sqlKeywords.test(input)) threats.push('SQL injection attempt');

    return threats;
  }

  // ==========================================
  // LOGGING SÉCURITÉ
  // ==========================================

  private logSecurityViolation(
    original: string, 
    sanitized: string, 
    violations: string[]
  ): void {
    const logEntry = {
      timestamp: new Date().toISOString(),
      type: 'xss_protection',
      original: original.substring(0, 200), // Limiter pour logs
      sanitized: sanitized.substring(0, 200),
      violations,
      userAgent: typeof navigator !== 'undefined' ? navigator.userAgent : '',
      url: typeof window !== 'undefined' ? window.location.href : '',
    };

    // Log développement
    if (process.env.NODE_ENV === 'development') {
      console.warn('🛡️ XSS Protection Violation:', logEntry);
    }

    // Monitoring production
    if (process.env.NODE_ENV === 'production') {
      this.sendSecurityAlert(logEntry);
    }
  }

  private sendSecurityAlert(logEntry: any): void {
    // Envoyer au monitoring (Sentry, LogRocket, etc.)
    try {
      fetch('/api/security/xss-violation/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logEntry),
      }).catch(() => {
        // Fail silently en production
      });
    } catch {
      // Fail silently
    }
  }
}

// ==========================================
// EXPORT SINGLETON & FUNCTIONS
// ==========================================

const xssProtection = new XSSProtection();

// Export fonction principale
export const sanitizeInput = (input: string, options?: SanitizeOptions): string => {
  return xssProtection.sanitizeInput(input, options);
};

// Export fonctions spécialisées
export const sanitizeEmail = (email: string): string => {
  return xssProtection.sanitizeEmail(email);
};

export const sanitizeUrl = (url: string): string => {
  return xssProtection.sanitizeUrl(url);
};

export const sanitizeUsername = (username: string): string => {
  return xssProtection.sanitizeUsername(username);
};

export const sanitizeFileName = (filename: string): string => {
  return xssProtection.sanitizeFileName(filename);
};

export const sanitizeSearchQuery = (query: string): string => {
  return xssProtection.sanitizeSearchQuery(query);
};

// Export utilitaires
export const isInputSafe = (input: string): boolean => {
  return xssProtection.isInputSafe(input);
};

export const detectXSSAttempt = (input: string): string[] => {
  return xssProtection.detectXSSAttempt(input);
};

export const validateAndSanitize = (input: string, options?: SanitizeOptions): ValidationResult => {
  return xssProtection.validateAndSanitize(input, options);
};

// Export classe pour usage avancé
export { XSSProtection };
export type { SanitizeOptions, ValidationResult };

// Export default
export default xssProtection;