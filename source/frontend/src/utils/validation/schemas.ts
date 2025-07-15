// frontend/src/utils/validation/schemas.ts
import { z } from 'zod';

// Schémas de base sécurisés
export const emailSchema = z
  .string()
  .email('Email invalide')
  .min(5, 'Email trop court')
  .max(255, 'Email trop long')
  .toLowerCase()
  .trim();

export const passwordSchema = z
  .string()
  .min(12, 'Le mot de passe doit contenir au moins 12 caractères')
  .max(128, 'Le mot de passe ne peut pas dépasser 128 caractères')
  .regex(/^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/, 
    'Le mot de passe doit contenir au moins : 1 minuscule, 1 majuscule, 1 chiffre, 1 caractère spécial');

export const slugSchema = z
  .string()
  .min(1, 'Le slug est requis')
  .max(200, 'Le slug ne peut pas dépasser 200 caractères')
  .regex(/^[a-z0-9-]+$/, 'Le slug ne peut contenir que des lettres minuscules, chiffres et tirets')
  .trim();

// Schémas auth
export const loginSchema = z.object({
  email: emailSchema,
  password: z.string().min(1, 'Le mot de passe est requis'),
  rememberMe: z.boolean().optional().default(false),
});

export const registerSchema = z.object({
  firstName: z.string().min(1, 'Le prénom est requis').max(50, 'Prénom trop long').trim(),
  lastName: z.string().min(1, 'Le nom est requis').max(50, 'Nom trop long').trim(),
  email: emailSchema,
  password: passwordSchema,
  confirmPassword: z.string(),
}).refine((data) => data.password === data.confirmPassword, {
  message: 'Les mots de passe ne correspondent pas',
  path: ['confirmPassword'],
});

// Types inférés TypeScript 5.8.3
export type LoginFormData = z.infer<typeof loginSchema>;
export type RegisterFormData = z.infer<typeof registerSchema>;
