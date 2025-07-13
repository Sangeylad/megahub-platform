// src/components/layout/headers/variants/DefaultHeader.tsx - VERSION CORRIGÉE

'use client'

import Link from 'next/link'
import Image from 'next/image'
import { useState } from 'react'
import type { HeaderComponentProps, MenuItem } from '../types'

export function DefaultHeader({ config }: HeaderComponentProps) {
  const [isMenuOpen, setIsMenuOpen] = useState(false)
  
  const {
    logo_url = '/logo.svg',
    logo_alt = 'Logo',
    navigation = [],
    cta_text,
    cta_url,
    show_contact_info = false,
    contact_phone,
    contact_email
  } = config

  return (
    <header className="sticky top-0 z-50 bg-white/95 backdrop-blur-sm border-b border-neutral-200">
      {/* Barre contact optionnelle */}
      {show_contact_info && (contact_phone || contact_email) && (
        <div className="bg-dark-900 text-white">
          <div className="container-section">
            <div className="flex justify-end items-center h-10 text-sm">
              {contact_phone && (
                <a 
                  href={`tel:${contact_phone}`}
                  className="hover:text-brand-400 transition-colors mr-6"
                >
                  📞 {contact_phone}
                </a>
              )}
              {contact_email && (
                <a 
                  href={`mailto:${contact_email}`}
                  className="hover:text-brand-400 transition-colors"
                >
                  ✉️ {contact_email}
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Navigation principale */}
      <nav className="container-section">
        <div className="flex justify-between items-center h-20">
          
          {/* Logo - Garde le prefetch pour l'accueil */}
          <Link href="/" className="flex items-center">
            <Image 
              src={logo_url} 
              alt={logo_alt}
              width={120}
              height={40}
              className="h-10 w-auto"
            />
          </Link>

          {/* Navigation desktop */}
          <div className="hidden md:flex items-center space-x-8">
            {navigation.map((item, index) => (
              <NavigationItem key={index} item={item} />
            ))}
          </div>

          {/* CTA + Menu mobile */}
          <div className="flex items-center space-x-4">
            {/* CTA Desktop - PREFETCH DÉSACTIVÉ */}
            {cta_text && cta_url && (
              <Link
                href={cta_url}
                prefetch={false}
                className="hidden md:inline-flex items-center px-6 py-2.5 bg-brand-500 text-white font-medium rounded-xl hover:bg-brand-600 transition-colors"
              >
                {cta_text}
              </Link>
            )}

            {/* Burger menu */}
            <button
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="md:hidden p-2 text-neutral-600 hover:text-neutral-900"
              aria-label="Toggle menu"
            >
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>

        {/* Menu mobile */}
        {isMenuOpen && (
          <div className="md:hidden border-t border-neutral-200 bg-white">
            <div className="py-4 space-y-2">
              {navigation.map((item, index) => (
                <MobileNavigationItem 
                  key={index} 
                  item={item} 
                  onClose={() => setIsMenuOpen(false)}
                />
              ))}
              
              {/* CTA Mobile - PREFETCH DÉSACTIVÉ */}
              {cta_text && cta_url && (
                <div className="pt-4 border-t border-neutral-200">
                  <Link
                    href={cta_url}
                    prefetch={false}
                    className="block w-full text-center px-4 py-3 bg-brand-500 text-white font-medium rounded-xl hover:bg-brand-600 transition-colors"
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {cta_text}
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}

// ✅ NAVIGATION ITEM AVEC PREFETCH DÉSACTIVÉ
function NavigationItem({ item }: { item: MenuItem }) {
  const hasChildren = item.children && item.children.length > 0

  if (!hasChildren) {
    return (
      <Link
        href={item.href}
        prefetch={false}
        className="text-neutral-700 hover:text-brand-500 font-medium transition-colors"
      >
        {item.label}
      </Link>
    )
  }

  return (
    <div className="relative group">
      {/* Link parent + flèche - PREFETCH DÉSACTIVÉ */}
      <div className="flex items-center">
        <Link
          href={item.href}
          prefetch={false}
          className="text-neutral-700 hover:text-brand-500 font-medium transition-colors"
        >
          {item.label}
        </Link>
        <svg className="ml-1 w-4 h-4 text-neutral-700 group-hover:text-brand-500 transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {/* Dropdown - PREFETCH DÉSACTIVÉ SUR TOUS LES ENFANTS */}
      <div className="navigation-dropdown absolute top-full left-0 mt-1 w-56 bg-white rounded-xl shadow-lg border border-neutral-200 py-2 z-50">
        {item.children?.map((child, index) => (
          <Link
            key={index}
            href={child.href}
            prefetch={false}
            className="block px-4 py-3 text-neutral-600 hover:text-brand-500 hover:bg-neutral-50 transition-colors"
          >
            {child.label}
          </Link>
        ))}
      </div>
    </div>
  )
}

// Navigation mobile - PREFETCH DÉSACTIVÉ
function MobileNavigationItem({ item, onClose }: { item: MenuItem; onClose: () => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const hasChildren = item.children && item.children.length > 0

  if (!hasChildren) {
    return (
      <Link
        href={item.href}
        prefetch={false}
        className="block px-4 py-3 text-neutral-700 hover:text-brand-500 font-medium"
        onClick={onClose}
      >
        {item.label}
      </Link>
    )
  }

  return (
    <div>
      <div className="flex items-center">
        <Link
          href={item.href}
          prefetch={false}
          className="flex-1 block px-4 py-3 text-neutral-700 hover:text-brand-500 font-medium"
          onClick={onClose}
        >
          {item.label}
        </Link>
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="px-4 py-3 text-neutral-500 hover:text-brand-500"
          aria-label={`Toggle ${item.label} submenu`}
        >
          <svg 
            className={`w-4 h-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            fill="none" 
            stroke="currentColor" 
            viewBox="0 0 24 24"
          >
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </button>
      </div>

      {isOpen && item.children && (
        <div className="bg-neutral-50 border-l-2 border-brand-500 ml-4">
          {item.children.map((child, index) => (
            <Link
              key={index}
              href={child.href}
              prefetch={false}
              className="block px-4 py-2 text-neutral-600 hover:text-brand-500"
              onClick={onClose}
            >
              {child.label}
            </Link>
          ))}
        </div>
      )}
    </div>
  )
}