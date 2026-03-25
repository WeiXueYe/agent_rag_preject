# 测试导入脚本
print("Testing imports...")

try:
    from fastapi import FastAPI
    print("✓ FastAPI imported successfully")
except Exception as e:
    print(f"✗ Failed to import FastAPI: {e}")

try:
    from fastapi.middleware.cors import CORSMiddleware
    print("✓ CORSMiddleware imported successfully")
except Exception as e:
    print(f"✗ Failed to import CORSMiddleware: {e}")

try:
    from backend.chat import router as memory_text_router
    print("✓ memory_text router imported successfully")
except Exception as e:
    print(f"✗ Failed to import memory_text router: {e}")

print("Import test completed.")