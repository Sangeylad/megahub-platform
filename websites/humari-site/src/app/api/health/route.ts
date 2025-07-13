import { NextResponse } from 'next/server'

const MEGAHUB_API_URL = process.env.MEGAHUB_API_URL!

export async function GET() {
  try {
    // Test local Next.js
    const nextjsHealth = true

    // Test backend MEGAHUB
    let megahubHealth = false
    try {
      const response = await fetch(`${MEGAHUB_API_URL}/seo/public/health/status/`, {
        method: 'GET',
        cache: 'no-store'
      })
      megahubHealth = response.ok && (await response.json())?.status === 'healthy'
    } catch {
      megahubHealth = false
    }

    const overallHealth = nextjsHealth && megahubHealth

    return NextResponse.json(
      {
        status: overallHealth ? 'healthy' : 'degraded',
        services: {
          nextjs: nextjsHealth ? 'healthy' : 'error',
          megahub: megahubHealth ? 'healthy' : 'error'
        },
        timestamp: new Date().toISOString()
      },
      { 
        status: overallHealth ? 200 : 503,
        headers: {
          'Cache-Control': 'no-cache'
        }
      }
    )

  } catch (err) {
    console.error('Health check failed:', err)
    return NextResponse.json(
      {
        status: 'error',
        error: 'Health check failed',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    )
  }
}