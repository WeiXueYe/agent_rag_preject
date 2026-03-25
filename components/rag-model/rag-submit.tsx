"use client";

import { useState } from "react";
import { Button } from "../ui/button";
import { Input } from "../ui/input";
import { Label } from "../ui/label";
import { getJwtToken } from "@/app/auth/get-info/get-jwt";
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../ui/card";

interface FileSubmissionFormProps {
  onSuccess?: (response: any) => void;
  onError?: (error: Error) => void;
}

export default function RagSubment({ onSuccess, onError }: FileSubmissionFormProps) {
  const [files, setFiles] = useState<File[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState("");
  
  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setMessage("请选择至少一个文件");
      return;
    }
    
    setIsLoading(true);
    setMessage("");
    
    try {
      const formData = new FormData();
      files.forEach((file) => {
        formData.append('files', file);
      });
      const jwtToken = await getJwtToken();
      if (!jwtToken) {
        throw new Error("无法获取 JWT 令牌，请先登录");
      }
      
      const response = await fetch("http://localhost:8000/receive_files", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${jwtToken}`,
        },
        body: formData,
      });
      
      if (!response.ok) {
        throw new Error(`上传失败: ${response.statusText}`);
      }
      
      const result = await response.json();
      setMessage("文件上传成功");
      setFiles([]);
      onSuccess?.(result);
    } catch (error) {
      console.error("上传错误:", error);
      setMessage(`上传失败: ${error instanceof Error ? error.message : "未知错误"}`);
      onError?.(error instanceof Error ? error : new Error("未知错误"));
    } finally {
      setIsLoading(false);
    }
  };
  
  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>文件上传</CardTitle>
        <CardDescription>支持多种文件格式的提交</CardDescription>
      </CardHeader>
      <form onSubmit={handleSubmit}>
        <CardContent>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="file-upload">选择文件</Label>
              <Input
                id="file-upload"
                type="file"
                multiple
                accept=".pdf,.doc,.docx,.txt,.md,.csv,.json,.xml"
                onChange={handleFileChange}
              />
            </div>
            
            {files.length > 0 && (
              <div className="mt-4">
                <Label>已选择的文件:</Label>
                <ul className="mt-2 space-y-1">
                  {files.map((file, index) => (
                    <li key={index} className="text-sm">
                      {file.name} ({(file.size / 1024).toFixed(2)} KB)
                    </li>
                  ))}
                </ul>
              </div>
            )}
            
            {message && (
              <div className={`mt-4 p-2 rounded ${message.includes("成功") ? "bg-green-50 text-green-700" : "bg-red-50 text-red-700"}`}>
                {message}
              </div>
            )}
          </div>
        </CardContent>
        <CardFooter>
          <Button type="submit" className="w-full" disabled={isLoading}>
            {isLoading ? "上传中..." : "上传文件"}
          </Button>
        </CardFooter>
      </form>
    </Card>
  );
}
