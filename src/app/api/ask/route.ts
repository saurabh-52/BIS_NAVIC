import { NextResponse } from "next/server";

export async function POST(req: Request) {
  try {
    const body = await req.json();
    const { query } = body;

    if (!query) {
      return NextResponse.json({ error: "Query is required" }, { status: 400 });
    }

    console.log(`[API /api/ask] Forwarding query to FastAPI backend: "${query}"`);

    const resp = await fetch("http://127.0.0.1:8001/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query }),
    });

    if (!resp.ok) {
      const errText = await resp.text();
      console.error(`[API /api/ask] Backend error ${resp.status}:`, errText);
      return NextResponse.json({ error: `FastAPI error: ${errText}` }, { status: resp.status });
    }

    const data = await resp.json();
    console.log(`[API /api/ask] Successfully received answer with ${data.contexts_used?.length || 0} contexts`);
    return NextResponse.json(data);
  } catch (err: any) {
    console.error("[API /api/ask] Connection failed:", err.message);
    return NextResponse.json(
      { error: "Could not connect to FastAPI backend at http://127.0.0.1:8001" },
      { status: 502 }
    );
  }
}
