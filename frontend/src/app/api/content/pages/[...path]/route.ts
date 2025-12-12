import { NextRequest, NextResponse } from 'next/server';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL 
  || process.env.INTERNAL_API_URL 
  || 'http://127.0.0.1:8001/api';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  if (!API_BASE_URL) {
    return NextResponse.json({ error: 'API URL not configured' }, { status: 500 });
  }

  const path = params.path.join('/');
  const url = new URL(request.url);
  const queryString = url.search;

  // Формируем правильный путь для Django API
  let apiPath = path;
  if (!apiPath.endsWith('/')) {
    apiPath += '/';
  }

  try {
    // API_BASE_URL = https://api.rainbow-say.estenomada.es/api
    // Нужно: https://api.rainbow-say.estenomada.es/api/content/pages/by-slug/uslugi/
    const targetUrl = `${API_BASE_URL}/content/pages/${apiPath}${queryString}`;
    
    const response = await fetch(targetUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      cache: 'no-store',
    });

    if (!response.ok) {
      const errorText = await response.text();
      let errorData;
      try {
        errorData = JSON.parse(errorText);
      } catch {
        errorData = { error: errorText || 'Unknown error' };
      }
      return NextResponse.json(errorData, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error: any) {
    console.error('API route error:', error);
    return NextResponse.json({ 
      error: 'Internal Server Error',
      details: error.message 
    }, { status: 500 });
  }
}

