// frontend/src/types/auth/index.ts

// 🔐 Barrel exports types auth - Standards Sécurité TypeScript 5.8.3

// ==========================================
// IMPORTS FIRST
// ==========================================

import type {
  User,
  UserType,
  Company,
  Brand,
  UserPermissionsSummary,
  AccessibleBrandsInfo,
  BrandInfo,
  AdministeredBrandInfo,
  Role,
  RoleType,
  Permission,
  PermissionType,
  UserRole,
  UserRoleContext,
  AuthTokens,
  AuthState,
  AuthContextValue,
  LoginFormData,
  RegisterFormData,
  UserUpdateData,
  PasswordChangeData,
  BrandAssignmentData,
  LoginResponse,
  RegisterResponse,
  RefreshTokenResponse,
  LogoutResponse,
  PasswordChangeResponse,
  BrandAssignmentResponse,
  ValidationError,
  AuthValidationResult,
  AuthError,
  AuthQueryKeys,
  UseAuthOptions,
  UseUserSuspenseOptions,
} from './auth.types';

// ==========================================
// CORE AUTH TYPES RE-EXPORTS
// ==========================================

export type {
  // User & Company types
  User,
  UserType,
  Company,
  Brand,
  UserPermissionsSummary,
  AccessibleBrandsInfo,
  BrandInfo,
  AdministeredBrandInfo,
  
  // Roles & Permissions system
  Role,
  RoleType,
  Permission,
  PermissionType,
  UserRole,
  UserRoleContext,
  
  // Auth tokens & state
  AuthTokens,
  AuthState,
  AuthContextValue,
  
  // Form data types
  LoginFormData,
  RegisterFormData,
  UserUpdateData,
  PasswordChangeData,
  BrandAssignmentData,
  
  // API Response types
  LoginResponse,
  RegisterResponse,
  RefreshTokenResponse,
  LogoutResponse,
  PasswordChangeResponse,
  BrandAssignmentResponse,
  
  // Validation & Error types
  ValidationError,
  AuthValidationResult,
  AuthError,
  
  // Query & Hook types
  AuthQueryKeys,
  UseAuthOptions,
  UseUserSuspenseOptions,
} from './auth.types';

// ==========================================
// TYPE GUARDS FOR AUTH
// ==========================================

export const isUser = (user: unknown): user is User => {
  return (
    typeof user === 'object' &&
    user !== null &&
    'id' in user &&
    'username' in user &&
    'email' in user &&
    'user_type' in user
  );
};

export const isAuthTokens = (tokens: unknown): tokens is AuthTokens => {
  return (
    typeof tokens === 'object' &&
    tokens !== null &&
    'access' in tokens &&
    'refresh' in tokens &&
    'token_type' in tokens
  );
};

export const isAuthError = (error: unknown): error is AuthError => {
  return (
    typeof error === 'object' &&
    error !== null &&
    'message' in error &&
    'code' in error
  );
};

export const isCompanyAdmin = (user: User): boolean => {
  return user.user_type === 'agency_admin' || 
         user.permissions_summary?.is_company_admin === true;
};

export const isBrandAdmin = (user: User): boolean => {
  return user.user_type === 'brand_admin' || 
         user.permissions_summary?.is_brand_admin === true;
};

export const canAccessAnalytics = (user: User): boolean => {
  return user.can_access_analytics || isCompanyAdmin(user) || isBrandAdmin(user);
};

export const canAccessReports = (user: User): boolean => {
  return user.can_access_reports || isCompanyAdmin(user) || isBrandAdmin(user);
};

// ==========================================
// CONSTANTS
// ==========================================

export const USER_TYPES = {
  AGENCY_ADMIN: 'agency_admin',
  BRAND_ADMIN: 'brand_admin', 
  BRAND_MEMBER: 'brand_member',
  CLIENT_READONLY: 'client_readonly',
} as const;

export const ROLE_TYPES = {
  SYSTEM: 'system',
  COMPANY: 'company',
  BRAND: 'brand',
  FEATURE: 'feature',
} as const;

export const PERMISSION_TYPES = {
  READ: 'read',
  WRITE: 'write',
  DELETE: 'delete',
  ADMIN: 'admin',
} as const;

// ==========================================
// DEFAULT VALUES
// ==========================================

export const DEFAULT_AUTH_STATE: AuthState = {
  user: null,
  tokens: null,
  isAuthenticated: false,
  isLoading: true,
  error: null,
  lastActivity: Date.now(),
};

export const DEFAULT_USER_PERMISSIONS: UserPermissionsSummary = {
  is_company_admin: false,
  is_brand_admin: false,
  accessible_brands_count: 0,
  administered_brands_count: 0,
  can_access_analytics: false,
  can_access_reports: false,
};

// ==========================================
// UTILITY FUNCTIONS
// ==========================================

export const getUserDisplayName = (user: User): string => {
  return `${user.first_name} ${user.last_name}`.trim() || user.username;
};

export const getUserInitials = (user: User): string => {
  const firstName = user.first_name?.charAt(0) || '';
  const lastName = user.last_name?.charAt(0) || '';
  return (firstName + lastName).toUpperCase() || user.username.charAt(0).toUpperCase();
};

export const getUserTypeLabel = (userType: UserType): string => {
  const labels: Record<UserType, string> = {
    agency_admin: 'Admin Agence',
    brand_admin: 'Admin Marque',
    brand_member: 'Membre Marque',
    client_readonly: 'Client (Lecture seule)',
  };
  return labels[userType];
};

export const getRoleTypeLabel = (roleType: RoleType): string => {
  const labels: Record<RoleType, string> = {
    system: 'Système',
    company: 'Entreprise',
    brand: 'Marque',
    feature: 'Feature',
  };
  return labels[roleType];
};

export const getPermissionTypeLabel = (permissionType: PermissionType): string => {
  const labels: Record<PermissionType, string> = {
    read: 'Lecture',
    write: 'Écriture',
    delete: 'Suppression',
    admin: 'Administration',
  };
  return labels[permissionType];
};

export const isTokenExpired = (token: string): boolean => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    const exp = payload.exp * 1000; // Convert to milliseconds
    return Date.now() >= exp;
  } catch {
    return true; // Invalid token format
  }
};

export const getTokenExpiration = (token: string): Date | null => {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]));
    return new Date(payload.exp * 1000);
  } catch {
    return null;
  }
};

export const getUserPermissions = (user: User): string[] => {
  // Start with empty array since permissions are computed from roles in backend
  const permissions: Set<string> = new Set();
  
  // Add permissions based on user type
  if (isCompanyAdmin(user)) {
    permissions.add('company.admin');
    permissions.add('users.write');
    permissions.add('brands.write');
  }
  
  if (isBrandAdmin(user)) {
    permissions.add('brand.admin');
    permissions.add('pages.write');
    permissions.add('analytics.read');
  }
  
  if (canAccessAnalytics(user)) {
    permissions.add('analytics.read');
  }
  
  if (canAccessReports(user)) {
    permissions.add('reports.read');
  }
  
  return Array.from(permissions);
};

export const hasPermission = (user: User, permission: string): boolean => {
  const userPermissions = getUserPermissions(user);
  return userPermissions.includes(permission);
};

export const hasAnyPermission = (user: User, permissions: string[]): boolean => {
  const userPermissions = getUserPermissions(user);
  return permissions.some(permission => userPermissions.includes(permission));
};

export const hasAllPermissions = (user: User, permissions: string[]): boolean => {
  const userPermissions = getUserPermissions(user);
  return permissions.every(permission => userPermissions.includes(permission));
};

// ==========================================
// VALIDATION HELPERS
// ==========================================

export const validateEmail = (email: string): boolean => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
};

export const validateUsername = (username: string): boolean => {
  const usernameRegex = /^[a-zA-Z0-9_]{3,30}$/;
  return usernameRegex.test(username);
};

export const validatePassword = (password: string): { 
  valid: boolean; 
  errors: string[] 
} => {
  const errors: string[] = [];
  
  if (password.length < 8) {
    errors.push('Le mot de passe doit contenir au moins 8 caractères');
  }
  
  if (!/[A-Z]/.test(password)) {
    errors.push('Le mot de passe doit contenir au moins une majuscule');
  }
  
  if (!/[a-z]/.test(password)) {
    errors.push('Le mot de passe doit contenir au moins une minuscule');
  }
  
  if (!/\d/.test(password)) {
    errors.push('Le mot de passe doit contenir au moins un chiffre');
  }
  
  if (!/[!@#$%^&*(),.?":{}|<>]/.test(password)) {
    errors.push('Le mot de passe doit contenir au moins un caractère spécial');
  }
  
  return {
    valid: errors.length === 0,
    errors,
  };
};