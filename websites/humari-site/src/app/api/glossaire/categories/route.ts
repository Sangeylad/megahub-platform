// src/app/api/glossaire/categories/route.ts
import { NextResponse } from 'next/server'

const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL || 'https://backoffice.humari.fr'

export async function GET() {
  try {
    const response = await fetch(`${MEGAHUB_API_URL}/glossaire/categories/`, {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      next: { revalidate: 3600 } // Cache 1h pour les catégories
    })
    
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('Categories API error:', error)
    return NextResponse.json(
      { error: 'Erreur de chargement des catégories' },
      { status: 500 }
    )
  }
}