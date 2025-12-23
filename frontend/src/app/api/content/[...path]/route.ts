import { NextRequest, NextResponse } from 'next/server';

// API routes работают на сервере и проксируют запросы к Django API
// В продакшене должен быть установлен NEXT_PUBLIC_API_URL
// Используем внутренний URL для запросов от сервера Next.js к Django
const API_BASE_URL = process.env.INTERNAL_API_URL 
  || process.env.NEXT_PUBLIC_API_URL 
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

  // Убеждаемся, что путь заканчивается на / для Django
  const apiPath = path.endsWith('/') ? path : `${path}/`;

  try {
    // Для внутренних запросов используем правильные заголовки
    const isInternal = API_BASE_URL.includes('127.0.0.1') || API_BASE_URL.includes('localhost');
    const fetchHeaders: HeadersInit = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
    
    // Если запрос к внутреннему API, добавляем заголовки для Django
    // В Node.js fetch нельзя установить Host напрямую, но можно использовать URL с правильным host
    let fetchUrl = `${API_BASE_URL}/content/${apiPath}${queryString}`;
    if (isInternal) {
      fetchHeaders['X-Forwarded-Proto'] = 'https';
      fetchHeaders['X-Forwarded-Host'] = 'api.temis.ooo';
      // Используем URL с правильным host для внутренних запросов
      fetchUrl = `http://127.0.0.1:8001/api/content/${apiPath}${queryString}`;
    }
    
    const response = await fetch(fetchUrl, {
      headers: fetchHeaders,
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
      console.error(`API error: ${response.status}`, errorData);
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

