import { NextResponse } from "next/server";
import { createServerClient } from "@supabase/ssr";

/**
 * Shikshak AI — Supabase Auth callback.
 * Exchanges the OAuth code for a session and redirects to /dashboard.
 */
export async function GET(request: Request) {
  const requestUrl = new URL(request.url);
  const code = requestUrl.searchParams.get("code");

  if (code) {
    const supabase = createServerClient(
      process.env.NEXT_PUBLIC_SUPABASE_URL ?? "",
      process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "",
      {
        cookies: {
          getAll() {
            const cookie = request.headers.get("cookie") ?? "";
            return cookie
              .split(";")
              .map((c) => c.trim())
              .filter(Boolean)
              .map((c) => {
                const [name, ...rest] = c.split("=");
                return { name, value: rest.join("=") };
              });
          },
          setAll() {
            // Server route handler — we just redirect; the browser cookie is
            // set by Supabase's server-side exchange.
          },
        },
      },
    );
    await supabase.auth.exchangeCodeForSession(code);
  }

  return NextResponse.redirect(`${requestUrl.origin}/dashboard`);
}
