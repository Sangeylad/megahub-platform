// frontend/src/pages/auth/login.tsx - Login Page selon Standards Leaders 2025

import { useAuth } from '@/hooks/useAuth';
import type { LoginFormData } from '@/types/auth';
import { sanitizeInput } from '@/utils/security/xssProtection';
import { authValidation } from '@/utils/validation/authValidation';
import { createFileRoute } from '@tanstack/react-router';
import React, { useEffect } from 'react';

// ==========================================
// TANSTACK ROUTER - Configuration Route
// ==========================================

export const Route = createFileRoute('/auth/login')({
  component: LoginPage,
});

// ==========================================
// TYPES LOCAUX - TypeScript 5.8.3 Strict
// ==========================================

interface LoginFormState {
  username: string;
  password: string;
  remember_me: boolean;
}

interface LoginFormErrors {
  username?: string;
  password?: string;
}

interface LoginPageState {
  formData: LoginFormState;
  formErrors: LoginFormErrors;
  showPassword: boolean;
  loginAttempts: number;
  isRedirecting: boolean;
}

// ==========================================
// LOGIN PAGE COMPONENT - React 19 Standards
// ==========================================

function LoginPage(): React.JSX.Element {
  // ===== SEARCH PARAMS - TanStack Router =====
  const searchParams = new URLSearchParams(window.location.search);
  const redirectUrl: string = searchParams.get('redirect') ?? '/dashboard';

  // ===== AUTH HOOK - TanStack Query v5 =====
  const {
    login,
    isLoggingIn,
    error: authError,
    isAuthenticated,
  } = useAuth();

  // ===== LOCAL STATE - TypeScript 5.8.3 Strict =====
  const [pageState, setPageState] = React.useState<LoginPageState>({
    formData: {
      username: '',
      password: '',
      remember_me: false,
    },
    formErrors: {},
    showPassword: false,
    loginAttempts: 0,
    isRedirecting: false,
  });

  // ===== REDIRECTION POST-LOGIN - Effect =====
  useEffect(() => {
    if (isAuthenticated && !pageState.isRedirecting) {
      setPageState((prev: LoginPageState) => ({
        ...prev,
        isRedirecting: true
      }));

      if (import.meta.env.MODE === 'development') {
        console.log('✅ [Login] Connexion réussie - Redirection vers:', redirectUrl);
      }

      // Délai pour synchronisation tokens
      setTimeout(() => {
        try {
          window.location.href = redirectUrl;
        } catch (error) {
          console.error('❌ [Login] Erreur navigation:', error);
          window.location.href = '/dashboard';
        }
      }, 150);
    }
  }, [isAuthenticated, pageState.isRedirecting, redirectUrl]);

  // ===== HANDLERS - TypeScript 5.8.3 Strict =====
  const handleInputChange = (field: keyof LoginFormState) => (
    event: React.ChangeEvent<HTMLInputElement>
  ): void => {
    const value: string | boolean = field === 'remember_me' ? event.target.checked : event.target.value;
    const sanitizedValue: string | boolean = typeof value === 'string' ? sanitizeInput(value) : value;

    setPageState((prev: LoginPageState) => ({
      ...prev,
      formData: {
        ...prev.formData,
        [field]: sanitizedValue,
      },
      formErrors: {
        ...prev.formErrors,
        [field]: undefined,
      },
    }));
  };

  const togglePasswordVisibility = (): void => {
    setPageState((prev: LoginPageState) => ({
      ...prev,
      showPassword: !prev.showPassword,
    }));
  };

  const validateForm = (): boolean => {
    const errors: LoginFormErrors = {};

    if (!pageState.formData.username.trim()) {
      errors.username = 'Nom d\'utilisateur requis';
    } else if (pageState.formData.username.length < 3) {
      errors.username = 'Nom d\'utilisateur trop court (minimum 3 caractères)';
    }

    if (!pageState.formData.password) {
      errors.password = 'Mot de passe requis';
    } else if (pageState.formData.password.length < 8) {
      errors.password = 'Mot de passe trop court (minimum 8 caractères)';
    }

    const hasErrors: boolean = Object.keys(errors).length > 0;

    if (hasErrors) {
      setPageState((prev: LoginPageState) => ({
        ...prev,
        formErrors: errors
      }));
    }

    return !hasErrors;
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault();

    if (isLoggingIn || pageState.isRedirecting) {
      return;
    }

    if (!validateForm()) {
      return;
    }

    try {
      if (import.meta.env.MODE === 'development') {
        console.log('🔄 [Login] Début tentative connexion');
      }

      const validatedData: LoginFormData = authValidation.validateLoginForm(pageState.formData);
      await login(validatedData);

      // Reset attempts on success
      setPageState((prev: LoginPageState) => ({
        ...prev,
        loginAttempts: 0
      }));

      if (import.meta.env.MODE === 'development') {
        console.log('✅ [Login] Connexion réussie');
      }

    } catch (error) {
      const newAttempts: number = pageState.loginAttempts + 1;
      setPageState((prev: LoginPageState) => ({
        ...prev,
        loginAttempts: newAttempts
      }));

      console.error('❌ [Login] Erreur:', error);

      // Handle specific error types
      if (error instanceof Error) {
        const errorMessage: string = error.message.toLowerCase();
        const errors: LoginFormErrors = {};

        if (errorMessage.includes('credentials') || errorMessage.includes('invalid')) {
          errors.username = 'Identifiants incorrects';
          errors.password = 'Identifiants incorrects';
        } else if (errorMessage.includes('locked') || errorMessage.includes('attempts')) {
          errors.username = 'Compte temporairement verrouillé';
        } else if (errorMessage.includes('network') || errorMessage.includes('timeout')) {
          errors.username = 'Erreur de connexion, réessayez';
        }

        setPageState((prev: LoginPageState) => ({
          ...prev,
          formErrors: errors
        }));
      }
    }
  };

  // ===== RENDER HELPERS =====
  const renderRedirectingState = (): React.JSX.Element => {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md text-center">
          <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-green-600 animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Connexion réussie !
          </h2>
          <p className="text-gray-600">
            Redirection en cours...
          </p>
        </div>
      </div>
    );
  };

  const renderRedirectInfo = (): React.JSX.Element | null => {
    if (redirectUrl === '/dashboard') {
      return null;
    }

    return (
      <div className="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-700">
          Vous serez redirigé vers la page demandée après connexion
        </p>
      </div>
    );
  };

  const renderGlobalError = (): React.JSX.Element | null => {
    if (!authError) {
      return null;
    }

    return (
      <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
        <div className="flex items-center">
          <svg className="w-5 h-5 text-red-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-sm text-red-700">
            {authError instanceof Error ? authError.message : String(authError)}
          </p>
        </div>
      </div>
    );
  };

  const renderAttemptsWarning = (): React.JSX.Element | null => {
    if (pageState.loginAttempts < 3) {
      return null;
    }

    return (
      <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-center">
          <svg className="w-5 h-5 text-yellow-400 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
          <p className="text-sm text-yellow-700">
            Plusieurs tentatives échouées. Vérifiez vos identifiants.
          </p>
        </div>
      </div>
    );
  };

  const renderFieldError = (fieldName: keyof LoginFormErrors): React.JSX.Element | null => {
    const error: string | undefined = pageState.formErrors[fieldName];
    if (!error) {
      return null;
    }

    return (
      <p className="mt-1 text-sm text-red-600">{error}</p>
    );
  };

  // ===== EARLY RETURNS - Loading States =====
  if (pageState.isRedirecting) {
    return renderRedirectingState();
  }

  // ===== MAIN RENDER - Login Form =====
  return (
    <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">

        {/* Header Section */}
        <div className="text-center mb-8">
          <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            </svg>
          </div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">MegaHub</h1>
          <p className="text-gray-600">Connectez-vous à votre compte</p>
          {renderRedirectInfo()}
        </div>

        {/* Alerts */}
        {renderGlobalError()}
        {renderAttemptsWarning()}

        {/* Login Form */}
        <form onSubmit={handleSubmit} className="space-y-6">

          {/* Username Field */}
          <div>
            <label htmlFor="username" className="block text-sm font-medium text-gray-700 mb-2">
              Nom d'utilisateur
            </label>
            <input
              id="username"
              type="text"
              value={pageState.formData.username}
              onChange={handleInputChange('username')}
              className={`
                w-full px-4 py-3 border-2 rounded-lg 
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-300
                transition-colors duration-200
                ${pageState.formErrors.username
                  ? 'border-red-300 bg-red-50'
                  : 'border-gray-200 bg-white hover:border-gray-300'
                }
              `}
              placeholder="Entrez votre nom d'utilisateur"
              disabled={isLoggingIn}
              autoComplete="username"
              autoFocus
            />
            {renderFieldError('username')}
          </div>

          {/* Password Field */}
          <div>
            <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
              Mot de passe
            </label>
            <div className="relative">
              <input
                id="password"
                type={pageState.showPassword ? 'text' : 'password'}
                value={pageState.formData.password}
                onChange={handleInputChange('password')}
                className={`
                  w-full px-4 py-3 border-2 rounded-lg pr-12
                  focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-300
                  transition-colors duration-200
                  ${pageState.formErrors.password
                    ? 'border-red-300 bg-red-50'
                    : 'border-gray-200 bg-white hover:border-gray-300'
                  }
                `}
                placeholder="Entrez votre mot de passe"
                disabled={isLoggingIn}
                autoComplete="current-password"
              />
              <button
                type="button"
                onClick={togglePasswordVisibility}
                className="absolute inset-y-0 right-0 pr-3 flex items-center hover:text-gray-600 transition-colors"
                disabled={isLoggingIn}
              >
                {pageState.showPassword ? (
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                )}
              </button>
            </div>
            {renderFieldError('password')}
          </div>

          {/* Remember Me Checkbox */}
          <div className="flex items-center justify-between">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={pageState.formData.remember_me}
                onChange={handleInputChange('remember_me')}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                disabled={isLoggingIn}
              />
              <span className="ml-2 text-sm text-gray-700">Se souvenir de moi</span>
            </label>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoggingIn || !pageState.formData.username || !pageState.formData.password}
            className={`
              w-full py-3 px-4 rounded-lg font-medium transition-all duration-200
              ${isLoggingIn || !pageState.formData.username || !pageState.formData.password
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 text-white hover:bg-blue-700 hover:shadow-lg active:transform active:scale-[0.98] focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2'
              }
            `}
          >
            {isLoggingIn ? (
              <div className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Connexion en cours...
              </div>
            ) : (
              'Se connecter'
            )}
          </button>
        </form>

        {/* Development Debug Info */}
        {import.meta.env.MODE === 'development' && (
          <div className="mt-8 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 className="text-sm font-medium text-gray-700 mb-2">🔧 Debug Info</h3>
            <div className="text-xs text-gray-600 space-y-1">
              <p>Loading: {isLoggingIn ? '⏳ Oui' : '✅ Non'}</p>
              <p>Redirecting: {pageState.isRedirecting ? '🔄 Oui' : '❌ Non'}</p>
              <p>Attempts: {pageState.loginAttempts}</p>
              <p>Username: "{pageState.formData.username}"</p>
              <p>Remember: {pageState.formData.remember_me ? '✅ Oui' : '❌ Non'}</p>
              <p>Authenticated: {isAuthenticated ? '✅ Oui' : '❌ Non'}</p>
              <p>Redirect URL: {redirectUrl}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

// ===== EXPORT DEFAULT - Standards Leaders =====
export default LoginPage;