import { NextRequest, NextResponse } from 'next/server';

// API routes работают на сервере и проксируют запросы к Django API
// В продакшене должен быть установлен NEXT_PUBLIC_API_URL
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

export async function GET(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  if (!API_BASE_URL) {
    return NextResponse.json({ error: 'API URL not configured' }, { status: 500 });
  }

  const path = params.path.join('/');
  // Убеждаемся, что путь заканчивается на / для Django
  const apiPath = path.endsWith('/') ? path : `${path}/`;
  const url = new URL(request.url);
  const queryString = url.search;

  try {
    const response = await fetch(`${API_BASE_URL}/booking/${apiPath}${queryString}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
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

export async function POST(
  request: NextRequest,
  { params }: { params: { path: string[] } }
) {
  if (!API_BASE_URL) {
    return NextResponse.json({ error: 'API URL not configured' }, { status: 500 });
  }

  const path = params.path.join('/');
  // Убеждаемся, что путь заканчивается на / для Django
  const apiPath = path.endsWith('/') ? path : `${path}/`;
  const body = await request.json();

  try {
    const response = await fetch(`${API_BASE_URL}/booking/${apiPath}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(body),
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ error: 'Unknown error' }));
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

