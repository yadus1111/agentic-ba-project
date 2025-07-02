import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { businessProblem } = body;

    if (!businessProblem) {
      return NextResponse.json(
        { error: 'Business problem is required' },
        { status: 400 }
      );
    }

    // Call the FastAPI backend
    const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    
    const backendResponse = await fetch(`${backendUrl}/generate-report`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ business_problem: businessProblem }),
    });

    if (!backendResponse.ok) {
      const errorData = await backendResponse.json();
      throw new Error(errorData.detail || 'Backend API error');
    }

    const data = await backendResponse.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Error processing request:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
} 