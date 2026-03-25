import { createClient } from "@/lib/supabase/client";

export async function getJwtToken() {
  const supabase = createClient();
  
  try {
    // 获取当前会话
    const { data, error } = await supabase.auth.getSession();
    
    if (error) {
      console.error("获取会话失败:", error);
      return null;
    }
    
    // 返回访问令牌
    return data.session?.access_token || null;
  } catch (error) {
    console.error("获取JWT令牌时出错:", error);
    return null;
  }
}

export async function getUserInfo() {
  const supabase = createClient();
  
  try {
    // 获取当前用户信息
    const { data, error } = await supabase.auth.getUser();
    
    if (error) {
      console.error("获取用户信息失败:", error);
      return null;
    }
    
    return data.user;
  } catch (error) {
    console.error("获取用户信息时出错:", error);
    return null;
  }
}