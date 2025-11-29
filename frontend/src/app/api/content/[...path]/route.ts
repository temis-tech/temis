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
  const url = new URL(request.url);
  const queryString = url.search;

  try {
    const response = await fetch(`${API_BASE_URL}/content/${path}${queryString}`, {
      headers: {
        'Content-Type': 'application/json',
      },
    });

    const data = await response.json();
    return NextResponse.json(data, { status: response.status });
  } catch (error) {
    return NextResponse.json({ error: 'Internal Server Error' }, { status: 500 });
  }
}

