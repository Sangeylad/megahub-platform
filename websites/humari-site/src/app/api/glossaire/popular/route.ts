// src/app/api/glossaire/popular/route.ts
import { NextRequest, NextResponse } from 'next/server'

const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL || 'https://backoffice.humari.fr'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const limit = searchParams.get('limit') || '10'
    const lang = searchParams.get('lang') || 'fr'
    
    const response = await fetch(
      `${MEGAHUB_API_URL}/glossaire/terms/popular/?limit=${limit}&lang=${lang}`,
      {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        },
        next: { revalidate: 1800 } // Cache 30min pour les populaires
      }
    )
    
    if (!response.ok) {
      throw new Error(`Backend error: ${response.status}`)
    }
    
    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('Popular terms API error:', error)
    return NextResponse.json(
      { error: 'Erreur de chargement des termes populaires' },
      { status: 500 }
    )
  }
}