import { Badge } from "./ui/badge";
import { Button } from "./ui/button";

export function EnvVarWarning() {
  return (
    <div className="flex gap-4 items-center">
      <Badge variant={"outline"} className="font-normal">
        {/* Supabase environment variables required */}
        supabase 环境变量必填
      </Badge>
      <div className="flex gap-2">
        <Button size="sm" variant={"outline"} disabled>
          登陆 supabase
        </Button>
        <Button size="sm" variant={"default"} disabled>
          注册 supabase
        </Button>
      </div>
    </div>
  );
}
