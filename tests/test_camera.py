#!/usr/bin/env python3
"""
测试相机功能
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.camera import Camera
from src.config import config


def main():
    print("=" * 50)
    print("相机测试")
    print("=" * 50)
    
    camera = Camera()
    
    # 初始化
    print("\n1. 初始化相机...")
    if not camera.initialize():
        print("❌ 初始化失败")
        return
    print("✅ 初始化成功")
    
    # 拍照
    print("\n2. 拍摄照片...")
    image_path = camera.capture()
    if image_path:
        print(f"✅ 照片已保存: {image_path}")
    else:
        print("❌ 拍照失败")
    
    # 关闭
    print("\n3. 关闭相机...")
    camera.close()
    print("✅ 相机已关闭")
    
    print("\n" + "=" * 50)
    print("测试完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
