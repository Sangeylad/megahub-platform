// frontend/src/types/auth/auth.types.ts

// 🔐 Types Auth - Standards Sécurité TypeScript 5.8.3 selon modèles Django backend

// ==========================================
// USER TYPES - Correspondance CustomUser Django
// ==========================================

export type UserType = 'agency_admin' | 'brand_admin' | 'brand_member' | 'client_readonly';

export interface Company {
  readonly id: number;
  readonly name: string;
  readonly is_active: boolean;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface Brand {
  readonly id: number;
  readonly name: string;
  readonly company: number | Company; // ID ou objet complet selon contexte
  readonly url?: string;
  readonly is_active: boolean;
  readonly is_deleted: boolean;
  readonly brand_admin?: number; // ID de l'admin
  readonly users_count?: number;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface User {
  readonly id: number;
  readonly username: string;
  readonly email: string;
  readonly first_name: string;
  readonly last_name: string;
  readonly phone: string;
  readonly position: string;

  // Relations business
  readonly company?: Company | null;
  readonly company_name?: string; // From serializer
  readonly brands?: Brand[];

  // Type et permissions
  readonly user_type: UserType;
  readonly can_access_analytics: boolean;
  readonly can_access_reports: boolean;

  // Statuts
  readonly is_active: boolean;
  readonly is_staff: boolean;
  readonly is_superuser: boolean;
  readonly email_verified?: boolean; // Pour compatibilité frontend

  // Métadonnées
  readonly last_login?: string | null;
  readonly last_login_ip?: string | null;
  readonly date_joined: string;
  readonly created_at: string;
  readonly updated_at: string;

  // Champs calculés (from serializers)
  readonly permissions_summary?: UserPermissionsSummary;
  readonly accessible_brands_info?: AccessibleBrandsInfo;
  readonly is_company_admin_status?: boolean;
  readonly is_brand_admin_status?: boolean;
  readonly brands_list?: BrandInfo[];
  readonly administered_brands_list?: AdministeredBrandInfo[];
}

export interface UserPermissionsSummary {
  readonly is_company_admin: boolean;
  readonly is_brand_admin: boolean;
  readonly accessible_brands_count: number;
  readonly administered_brands_count: number;
  readonly can_access_analytics: boolean;
  readonly can_access_reports: boolean;
}

export interface AccessibleBrandsInfo {
  readonly count: number;
  readonly names: string[]; // Limité à 5 pour UI
}

export interface BrandInfo {
  readonly id: number;
  readonly name: string;
  readonly is_admin: boolean;
  readonly url?: string;
}

export interface AdministeredBrandInfo {
  readonly id: number;
  readonly name: string;
  readonly company: string;
  readonly users_count: number;
}

// ==========================================
// ROLES & PERMISSIONS - Système Django
// ==========================================

export type RoleType = 'system' | 'company' | 'brand' | 'feature';
export type PermissionType = 'read' | 'write' | 'delete' | 'admin';

export interface Role {
  readonly id: number;
  readonly name: string;
  readonly display_name: string;
  readonly description: string;
  readonly role_type: RoleType;
  readonly is_active: boolean;
  readonly is_system: boolean;
  readonly users_count?: number;
  readonly permissions_count?: number;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface Permission {
  readonly id: number;
  readonly name: string;
  readonly display_name: string;
  readonly description: string;
  readonly permission_type: PermissionType;
  readonly resource_type: string;
  readonly is_active: boolean;
  readonly roles_count?: number;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface UserRole {
  readonly id: number;
  readonly user: number;
  readonly user_username?: string;
  readonly user_email?: string;
  readonly role: number;
  readonly role_name?: string;
  readonly role_type?: RoleType;

  // Contexte optionnel
  readonly company?: number | null;
  readonly company_name?: string;
  readonly brand?: number | null;
  readonly brand_name?: string;
  readonly feature?: number | null;
  readonly feature_name?: string;

  // Métadonnées
  readonly granted_by?: number | null;
  readonly granted_by_username?: string;
  readonly granted_at: string;
  readonly expires_at?: string | null;
  readonly is_active_status?: boolean;
  readonly context_summary?: UserRoleContext;
  readonly created_at: string;
  readonly updated_at: string;
}

export interface UserRoleContext {
  readonly company?: string | null;
  readonly brand?: string | null;
  readonly feature?: string | null;
  readonly is_active: boolean;
  readonly expires_at?: string | null;
}

// ==========================================
// AUTH TOKENS & RESPONSES - 🔧 FIX TypeScript
// ==========================================

export interface AuthTokens {
  readonly access: string; // Django SimpleJWT utilise 'access'
  readonly refresh: string; // Django SimpleJWT utilise 'refresh'
  readonly access_expires_in?: number; // Durée en secondes
  readonly refresh_expires_in?: number; // Durée en secondes
  readonly expires_in?: number; // ✅ FIX: Support backend response
  readonly token_type: 'Bearer'; // ✅ FIX: Type littéral strict
}

export interface LoginFormData {
  readonly username: string; // Django utilise username, pas email
  readonly password: string;
  readonly remember_me?: boolean;
}

export interface RegisterFormData {
  readonly username: string;
  readonly email: string;
  readonly password: string;
  readonly password_confirm: string;
  readonly first_name: string;
  readonly last_name: string;
  readonly company?: number;
  readonly user_type?: UserType;
  readonly phone?: string;
  readonly position?: string;
  readonly can_access_analytics?: boolean;
  readonly can_access_reports?: boolean;
  readonly accept_terms: true;
}

export interface LoginResponse {
  readonly access: string;
  readonly refresh: string;
  readonly expires_in?: number; // ✅ FIX: Support backend response
  readonly token_type?: string; // ✅ FIX: Support backend response
  readonly user: User;
  // Données utilisateur intégrées dans la réponse Django
  readonly [key: string]: unknown; // Flexibilité pour données utilisateur
}

export interface RegisterResponse {
  readonly user: User;
  readonly tokens: AuthTokens;
  readonly message?: string;
}

export interface RefreshTokenResponse {
  readonly access: string;
  readonly expires_in?: number; // ✅ FIX: Support backend response
  readonly access_expires_in?: number; // ✅ FIX: Support frontend legacy
}

export interface LogoutResponse {
  readonly message: string;
  readonly success: boolean;
}

export interface UserUpdateData {
  readonly email?: string;
  readonly first_name?: string;
  readonly last_name?: string;
  readonly phone?: string;
  readonly position?: string;
  readonly user_type?: UserType;
  readonly can_access_analytics?: boolean;
  readonly can_access_reports?: boolean;
}

export interface PasswordChangeData {
  readonly current_password: string;
  readonly new_password: string;
  readonly new_password_confirm: string;
}

export interface PasswordChangeResponse {
  readonly message: string;
  readonly user: string;
}

export interface BrandAssignmentData {
  readonly brand_ids: number[];
}

export interface BrandAssignmentResponse {
  readonly message: string;
  readonly user: string;
  readonly assigned_brands: number;
  readonly total_brands: number;
}

// ==========================================
// AUTH STATE & CONTEXT
// ==========================================

export interface AuthState {
  readonly user: User | null;
  readonly tokens: AuthTokens | null;
  readonly isAuthenticated: boolean;
  readonly isLoading: boolean;
  readonly error: string | null;
  readonly lastActivity: number;
}

export interface AuthContextValue extends AuthState {
  readonly login: (credentials: LoginFormData) => Promise<LoginResponse>;
  readonly register: (data: RegisterFormData) => Promise<RegisterResponse>;
  readonly logout: () => Promise<void>;
  readonly refreshToken: () => Promise<string>;
  readonly updateProfile: (data: UserUpdateData) => Promise<User>;
  readonly changePassword: (data: PasswordChangeData) => Promise<void>;
  readonly assignBrands: (userId: number, brandIds: number[]) => Promise<void>;
  readonly clearError: () => void;
  readonly checkPermission: (permission: string) => boolean;
  readonly hasRole: (role: string) => boolean;
  readonly canAccessBrand: (brandId: number) => boolean;
  readonly canAdminBrand: (brandId: number) => boolean;
}

// ==========================================
// VALIDATION SCHEMAS
// ==========================================

export interface ValidationError {
  readonly field: string;
  readonly message: string;
  readonly code: string;
}

export interface AuthValidationResult {
  readonly isValid: boolean;
  readonly errors: ValidationError[];
}

// ==========================================
// API ERROR RESPONSES
// ==========================================

export interface AuthError {
  readonly message: string;
  readonly code: string;
  readonly details?: Record<string, string[]>; // Django form errors
  readonly non_field_errors?: string[];
  readonly timestamp: string;
}

// ==========================================
// QUERY KEYS FACTORY TYPES
// ==========================================

export interface AuthQueryKeys {
  readonly all: readonly ['auth'];
  readonly user: () => readonly ['auth', 'user'];
  readonly profile: (userId: number) => readonly ['auth', 'profile', number];
  readonly permissions: () => readonly ['auth', 'permissions'];
  readonly roles: () => readonly ['auth', 'roles'];
  readonly userRoles: (userId: number) => readonly ['auth', 'userRoles', number];
}

// ==========================================
// HOOK OPTIONS
// ==========================================

export interface UseAuthOptions {
  readonly enabled?: boolean;
  readonly staleTime?: number;
  readonly gcTime?: number;
  readonly retry?: number | boolean;
  readonly refetchOnWindowFocus?: boolean;
  readonly suspense?: boolean; // TanStack Query v5 Suspense
}

export interface UseUserSuspenseOptions extends UseAuthOptions {
  // Pas de propriété suspense requise - géré automatiquement par useSuspenseQuery
}

// ==========================================
// CONSTANTS
// ==========================================

export const USER_TYPES = {
  AGENCY_ADMIN: 'agency_admin' as const,
  BRAND_ADMIN: 'brand_admin' as const,
  BRAND_MEMBER: 'brand_member' as const,
  CLIENT_READONLY: 'client_readonly' as const,
};

export const ROLE_TYPES = {
  SYSTEM: 'system' as const,
  COMPANY: 'company' as const,
  BRAND: 'brand' as const,
  FEATURE: 'feature' as const,
};

export const PERMISSION_TYPES = {
  READ: 'read' as const,
  WRITE: 'write' as const,
  DELETE: 'delete' as const,
  ADMIN: 'admin' as const,
};