// frontend/src/utils/validation/authValidation.ts
import { z } from 'zod';
import { sanitizeInput } from '@/utils/security/xssProtection';
import type {
  LoginFormData,
  RegisterFormData,
  UserUpdateData,
  PasswordChangeData,
} from '@/types/auth';

const emailSchema = z
  .string()
  .min(1, 'Email requis')
  .email('Format email invalide')
  .max(254, 'Email trop long')
  .transform((email) => sanitizeInput(email.toLowerCase().trim()));

const usernameSchema = z
  .string()
  .min(3, 'Nom d\'utilisateur minimum 3 caractères')
  .max(30, 'Nom d\'utilisateur maximum 30 caractères')
  .regex(
    /^[a-zA-Z0-9_]+$/,
    'Nom d\'utilisateur: lettres, chiffres et _ uniquement'
  )
  .transform((username) => sanitizeInput(username.trim()));

const passwordSchema = z
  .string()
  .min(8, 'Mot de passe minimum 8 caractères')
  .max(128, 'Mot de passe maximum 128 caractères')
  .regex(
    /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?":{}|<>])/,
    'Mot de passe: 1 minuscule, 1 majuscule, 1 chiffre, 1 caractère spécial'
  );

const nameSchema = z
  .string()
  .min(1, 'Nom requis')
  .max(150, 'Nom trop long')
  .regex(
    /^[a-zA-ZÀ-ÿ\s\-']+$/,
    'Nom: lettres, espaces, tirets et apostrophes uniquement'
  )
  .transform((name) => sanitizeInput(name.trim()));

const phoneSchema = z
  .string()
  .regex(
    /^(\+33|0)[1-9](\d{8})$/,
    'Numéro de téléphone français invalide'
  )
  .optional()
  .or(z.literal(''))
  .transform((phone) => phone ? sanitizeInput(phone.trim()) : '');

const positionSchema = z
  .string()
  .max(100, 'Poste maximum 100 caractères')
  .optional()
  .or(z.literal(''))
  .transform((position) => position ? sanitizeInput(position.trim()) : '');

export const loginFormSchema = z.object({
  username: z
    .string()
    .min(1, 'Identifiant requis')
    .transform((input) => sanitizeInput(input.trim())),
  password: z
    .string()
    .min(1, 'Mot de passe requis'),
  remember_me: z.boolean().optional().default(false),
});

export const registerFormSchema = z.object({
  username: usernameSchema,
  email: emailSchema,
  password: passwordSchema,
  password_confirm: z.string().min(1, 'Confirmation mot de passe requise'),
  first_name: nameSchema,
  last_name: nameSchema,
  phone: phoneSchema,
  position: positionSchema,
  accept_terms: z.literal(true, {
    errorMap: () => ({ message: 'Vous devez accepter les conditions' }),
  }),
}).refine(
  (data) => data.password === data.password_confirm,
  {
    message: 'Les mots de passe ne correspondent pas',
    path: ['password_confirm'],
  }
);

export const userUpdateSchema = z.object({
  email: emailSchema.optional(),
  first_name: nameSchema.optional(),
  last_name: nameSchema.optional(),
  phone: phoneSchema.optional(),
  position: positionSchema.optional(),
}).partial();

export const passwordChangeSchema = z.object({
  current_password: z
    .string()
    .min(1, 'Mot de passe actuel requis'),
  new_password: passwordSchema,
  new_password_confirm: z
    .string()
    .min(1, 'Confirmation nouveau mot de passe requise'),
}).refine(
  (data) => data.new_password === data.new_password_confirm,
  {
    message: 'Les nouveaux mots de passe ne correspondent pas',
    path: ['new_password_confirm'],
  }
).refine(
  (data) => data.current_password !== data.new_password,
  {
    message: 'Le nouveau mot de passe doit être différent de l\'actuel',
    path: ['new_password'],
  }
);

class AuthValidation {
  validateLoginForm(data: unknown): LoginFormData {
    try {
      return loginFormSchema.parse(data);
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(this.formatZodErrors(error));
      }
      throw error;
    }
  }

  validateRegisterForm(data: unknown): RegisterFormData {
    try {
      return registerFormSchema.parse(data);
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(this.formatZodErrors(error));
      }
      throw error;
    }
  }

  validateProfileUpdate(data: unknown): UserUpdateData {
    try {
      return userUpdateSchema.parse(data);
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(this.formatZodErrors(error));
      }
      throw error;
    }
  }

  validatePasswordChange(data: unknown): PasswordChangeData {
    try {
      return passwordChangeSchema.parse(data);
    } catch (error) {
      if (error instanceof z.ZodError) {
        throw new Error(this.formatZodErrors(error));
      }
      throw error;
    }
  }

  validateEmail(email: string): boolean {
    try {
      emailSchema.parse(email);
      return true;
    } catch {
      return false;
    }
  }

  validateUsername(username: string): boolean {
    try {
      usernameSchema.parse(username);
      return true;
    } catch {
      return false;
    }
  }

  validatePassword(password: string): { 
    valid: boolean; 
    errors: string[];
    strength: 'weak' | 'medium' | 'strong';
  } {
    const errors: string[] = [];
    let score = 0;

    if (password.length < 8) {
      errors.push('Minimum 8 caractères');
    } else {
      score += password.length >= 12 ? 2 : 1;
    }

    if (!/[a-z]/.test(password)) {
      errors.push('Au moins une minuscule');
    } else {
      score += 1;
    }

    if (!/[A-Z]/.test(password)) {
      errors.push('Au moins une majuscule');
    } else {
      score += 1;
    }

    if (!/\d/.test(password)) {
      errors.push('Au moins un chiffre');
    } else {
      score += 1;
    }

    if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
      errors.push('Au moins un caractère spécial');
    } else {
      score += 1;
    }

    if (/(.)\1{2,}/.test(password)) {
      score -= 1;
    }

    if (password.length > 15) {
      score += 1;
    }

    if (/[àâäéèêëîïôöùûüçñ]/i.test(password)) {
      score += 1;
    }

    let strength: 'weak' | 'medium' | 'strong';
    if (score < 4) {
      strength = 'weak';
    } else if (score < 7) {
      strength = 'medium';
    } else {
      strength = 'strong';
    }

    return {
      valid: errors.length === 0,
      errors,
      strength,
    };
  }

  private formatZodErrors(error: z.ZodError): string {
    return error.errors
      .map((err) => `${err.path.join('.')}: ${err.message}`)
      .join(', ');
  }

  sanitizeUserInput(input: string): string {
    return sanitizeInput(input.trim());
  }
}

export const authValidation = new AuthValidation();
export default authValidation;

export {
  emailSchema,
  usernameSchema,
  passwordSchema,
};
