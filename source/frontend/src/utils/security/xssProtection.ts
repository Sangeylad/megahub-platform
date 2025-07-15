// frontend/src/utils/security/xssProtection.ts
const XSS_PATTERNS = {
  htmlTags: /<[^>]*>/g,
  scriptTags: /<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi,
  onEventAttributes: /\s*on\w+\s*=\s*["'][^"']*["']/gi,
  javascript: /javascript:/gi,
  xssVectors: /(alert\s*\(|confirm\s*\(|prompt\s*\(|eval\s*\()/gi,
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

interface SanitizeOptions {
  allowHtml?: boolean;
  allowedTags?: string[];
  maxLength?: number;
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

class XSSProtection {
  private defaultOptions: Required<SanitizeOptions> = {
    allowHtml: false,
    allowedTags: [],
    maxLength: 10000,
    strictMode: true,
    logViolations: true,
  };

  sanitizeInput(input: string, options: SanitizeOptions = {}): string {
    if (typeof input !== 'string') {
      return String(input || '');
    }

    const config = { ...this.defaultOptions, ...options };
    let sanitized = input;

    if (sanitized.length > config.maxLength) {
      sanitized = sanitized.substring(0, config.maxLength);
    }

    if (config.strictMode) {
      sanitized = this.aggressiveSanitize(sanitized);
    }

    if (!config.allowHtml) {
      sanitized = this.stripHtml(sanitized);
    }

    return sanitized.trim().replace(/\s+/g, ' ');
  }

  private aggressiveSanitize(input: string): string {
    let sanitized = input;

    sanitized = sanitized.replace(XSS_PATTERNS.scriptTags, '');
    sanitized = sanitized.replace(XSS_PATTERNS.onEventAttributes, '');
    sanitized = sanitized.replace(XSS_PATTERNS.javascript, '');
    sanitized = sanitized.replace(XSS_PATTERNS.xssVectors, '');

    return sanitized;
  }

  private stripHtml(input: string): string {
    return input.replace(XSS_PATTERNS.htmlTags, '');
  }

  sanitizeEmail(email: string): string {
    return this.sanitizeInput(email, {
      allowHtml: false,
      maxLength: 254,
      strictMode: true,
    });
  }

  sanitizeUsername(username: string): string {
    return this.sanitizeInput(username, {
      allowHtml: false,
      maxLength: 30,
      strictMode: true,
    });
  }

  isInputSafe(input: string): boolean {
    const patterns = Object.values(XSS_PATTERNS);
    return !patterns.some(pattern => pattern.test(input));
  }
}

const xssProtection = new XSSProtection();

export const sanitizeInput = (input: string, options?: SanitizeOptions): string => {
  return xssProtection.sanitizeInput(input, options);
};

export const sanitizeEmail = (email: string): string => {
  return xssProtection.sanitizeEmail(email);
};

export const sanitizeUsername = (username: string): string => {
  return xssProtection.sanitizeUsername(username);
};

export const isInputSafe = (input: string): boolean => {
  return xssProtection.isInputSafe(input);
};

export { XSSProtection };
export type { SanitizeOptions, ValidationResult };
export default xssProtection;
