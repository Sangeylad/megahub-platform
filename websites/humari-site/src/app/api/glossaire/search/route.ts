// src/app/api/glossaire/search/route.ts
import { NextRequest, NextResponse } from 'next/server'

const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL || 'https://backoffice.humari.fr'

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    
    // Construction de l'URL vers le backend MEGAHUB
    const backendUrl = new URL(`${MEGAHUB_API_URL}/glossaire/terms/search/`)
    
    // Forward tous les paramètres de recherche
    searchParams.forEach((value, key) => {
      if (value && value !== '' && value !== 'false') {
        backendUrl.searchParams.append(key, value)
      }
    })
    
    console.log('🔍 Backend API call:', backendUrl.toString())
    
    const response = await fetch(backendUrl.toString(), {
      method: 'GET',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
      },
      cache: 'no-store' // Pas de cache pour les recherches
    })
    
    if (!response.ok) {
      console.error('Backend API error:', response.status, response.statusText)
      return NextResponse.json(
        { error: 'Erreur de recherche', status: response.status },
        { status: response.status }
      )
    }
    
    const data = await response.json()
    return NextResponse.json(data)
    
  } catch (error) {
    console.error('Search API error:', error)
    return NextResponse.json(
      { error: 'Erreur serveur lors de la recherche' },
      { status: 500 }
    )
  }
}