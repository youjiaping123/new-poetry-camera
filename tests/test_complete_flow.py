#!/usr/bin/env python3
"""
完整流程测试 - 模拟按钮触发完整流程
（不等待真实按钮，直接测试一次完整流程）
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.config import config
from src.camera import Camera
from src.printer import ThermalPrinter
from src.ai_service import AIService


def test_complete_flow():
    """测试完整流程：拍照 → AI处理 → 打印"""
    
    print("=" * 60)
    print("诗歌相机完整流程测试")
    print("=" * 60)
    
    # 1. 验证配置
    print("\n1. 验证配置...")
    is_valid, errors = config.validate()
    if not is_valid:
        print("❌ 配置验证失败:")
        for error in errors:
            print(f"  - {error}")
        return False
    print("✅ 配置验证通过")
    
    # 2. 初始化相机
    print("\n2. 初始化相机...")
    camera = Camera()
    if not camera.initialize():
        print("❌ 相机初始化失败")
        return False
    print("✅ 相机初始化成功")
    
    # 3. 初始化打印机
    print("\n3. 初始化打印机...")
    printer = ThermalPrinter()
    if not printer.initialize():
        print("❌ 打印机初始化失败")
        camera.close()
        return False
    print("✅ 打印机初始化成功")
    
    # 4. 初始化AI服务
    print("\n4. 初始化AI服务...")
    ai_service = AIService()
    print("✅ AI服务已准备")
    
    try:
        # 5. 拍照
        print("\n5. 拍照...")
        print("   (3秒后拍照，请准备)")
        import time
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        image_path = camera.capture()
        if not image_path:
            print("❌ 拍照失败")
            return False
        print(f"✅ 拍照成功: {image_path}")
        
        # 6. AI处理
        print("\n6. AI处理图像...")
        print("   (这可能需要一些时间...)")
        
        poem = ai_service.process_image_to_poem(image_path)
        if not poem:
            print("❌ 诗歌生成失败")
            return False
        
        print("✅ 诗歌生成成功:")
        print("\n" + "─" * 40)
        print(poem)
        print("─" * 40 + "\n")
        
        # 7. 打印
        print("7. 打印诗歌...")
        printer.print_poem(poem)
        print("✅ 打印完成")
        
        print("\n" + "=" * 60)
        print("✅ 完整流程测试成功！")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # 清理
        print("\n清理资源...")
        camera.close()
        printer.close()
        print("✅ 清理完成")


def main():
    print("\n这个测试将执行完整的诗歌相机流程：")
    print("  1. 拍照")
    print("  2. AI识别图像")
    print("  3. 生成诗歌")
    print("  4. 打印诗歌")
    
    try:
        input("\n按回车键开始测试...")
    except KeyboardInterrupt:
        print("\n\n测试已取消")
        return
    
    success = test_complete_flow()
    
    if success:
        print("\n✅ 测试成功！你的诗歌相机已经可以正常工作了。")
        print("\n下一步：")
        print("  运行 'python main.py' 启动诗歌相机")
        print("  短按按钮：拍照并打印")
        print("  长按按钮(2秒)：退出程序")
    else:
        print("\n❌ 测试失败，请检查错误信息")


if __name__ == "__main__":
    main()
