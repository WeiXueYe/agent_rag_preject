import { createServerClient } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { hasEnvVars } from "../utils";

export async function updateSession(request: NextRequest) {
  let supabaseResponse = NextResponse.next({
    request,
  });

  // 如果环境变量未设置，跳过代理检查。项目设置完成后可以移除这部分。
  if (!hasEnvVars) {
    return supabaseResponse;
  }

  // 使用 Fluid compute 时，不要将此客户端放在全局环境变量中。
  // 每次请求都要创建一个新的客户端。
  const supabase = createServerClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY!,
    {
      cookies: {
        getAll() {
          return request.cookies.getAll();
        },
        setAll(cookiesToSet) {
          cookiesToSet.forEach(({ name, value }) =>
            request.cookies.set(name, value),
          );
          supabaseResponse = NextResponse.next({
            request,
          });
          cookiesToSet.forEach(({ name, value, options }) =>
            supabaseResponse.cookies.set(name, value, options),
          );
        },
      },
    },
  );

  // 不要在 createServerClient 和 supabase.auth.getClaims() 之间运行代码。
  // 一个简单的错误可能会导致用户随机登出，非常难以调试。

  // 重要提示：如果你移除了 getClaims() 并且使用 Supabase 客户端进行服务端渲染，
  // 你的用户可能会随机登出。
  const { data } = await supabase.auth.getClaims();
  const user = data?.claims;

  if (
    // request.nextUrl.pathname !== "/" &&
    !user &&
    !request.nextUrl.pathname.startsWith("/login") &&
    !request.nextUrl.pathname.startsWith("/auth")
  ) {
    // 没有用户，可能通过将用户重定向到登录页面来响应
    const url = request.nextUrl.clone();
    url.pathname = "/auth/login";
    return NextResponse.redirect(url);
  }

  // 重要提示：你必须原样返回 supabaseResponse 对象。
  // 如果你要使用 NextResponse.next() 创建新的响应对象，请确保：
  // 1. 将请求传递进去，像这样：
  //    const myNewResponse = NextResponse.next({ request })
  // 2. 复制 cookie，像这样：
  //    myNewResponse.cookies.setAll(supabaseResponse.cookies.getAll())
  // 3. 修改 myNewResponse 对象以适应你的需求，但避免修改 cookie！
  // 4. 最后：
  //    return myNewResponse
  // 如果不这样做，可能会导致浏览器和服务器不同步，过早终止用户的会话！

  return supabaseResponse;
}
