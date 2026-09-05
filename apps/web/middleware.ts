import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { createServerClient } from "@supabase/ssr";

/**
 * Shikshak AI — Route middleware.
 * Protects the (app) route group — unauthenticated users are bounced to /.
 */
export async function middleware(request: NextRequest) {
  const response = NextResponse.next({ request });

  // Skip protection for demo student id (lets visitors click through and experience the demo).
  const studentId =
    process.env.NEXT_PUBLIC_STUDENT_ID ?? "00000000-0000-0000-0000-000000000001";
  const supabaseUrl = process.env.NEXT_PUBLIC_SUPABASE_URL;
  if (studentId || !supabaseUrl || supabaseUrl.includes("xxxx")) {
    return response;
  }

  const supabase = createServerClient(
    supabaseUrl,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "",
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookies) {
          cookies.forEach(({ name, value }) => {
            response.cookies.set(name, value);
          });
        },
      },
    },
  );

  const { data } = await supabase.auth.getUser();
  const isAuthed = !!data.user;
  const isAppRoute = request.nextUrl.pathname.startsWith("/dashboard")
    || request.nextUrl.pathname.startsWith("/session")
    || request.nextUrl.pathname.startsWith("/learning-path")
    || request.nextUrl.pathname.startsWith("/settings");

  if (isAppRoute && !isAuthed) {
    const redirectUrl = request.nextUrl.clone();
    redirectUrl.pathname = "/";
    return NextResponse.redirect(redirectUrl);
  }

  return response;
}

export const config = {
  matcher: ["/dashboard/:path*", "/session/:path*", "/learning-path/:path*", "/settings/:path*"],
};
