#!/usr/bin/env python3
"""
Vision Module Demo - MediaPipe + FER Architecture
演示新架构的使用方法
"""

import sys
import cv2
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from src.perception.vision import VisionPerceptor, detect_emotion_from_image


def demo_real_time_detection():
    """实时摄像头情感检测演示"""
    print("=" * 60)
    print("Real-time Emotion Detection Demo")
    print("=" * 60)
    print("Press 'q' to quit, 's' to save screenshot")
    print()
    
    # 创建检测器（默认使用MediaPipe）
    with VisionPerceptor(camera_id=0, use_mediapipe=True) as vp:
        print(f"Detector initialized: {'MediaPipe' if vp.use_mediapipe else 'Haar Cascade'}")
        
        frame_count = 0
        while True:
            percept = vp.perceive()
            frame_count += 1
            
            if percept:
                # 显示检测结果
                emotion = percept.metadata['dominant_emotion']
                conf = percept.confidence
                v = percept.valence_hint
                a = percept.arousal_hint
                d = percept.dominance_hint
                detector = percept.metadata.get('detector', 'unknown')
                
                print(f"\rFrame {frame_count} | "
                      f"Emotion: {emotion.upper():8s} ({conf:.1%}) | "
                      f"VAD: V={v:+.2f} A={a:.2f} D={d:+.2f} | "
                      f"Detector: {detector:9s}", end='')
            else:
                print(f"\rFrame {frame_count} | No face detected", end='')
            
            # 键盘控制
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s') and percept:
                # 保存截图
                timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"screenshot_{emotion}_{timestamp}.jpg"
                # Note: 实际项目中需要保存带标注的图像
                print(f"\n  Saved: {filename}")
    
    print("\n\nDemo finished!")


def demo_image_detection():
    """图片文件情感检测演示"""
    print("=" * 60)
    print("Image File Emotion Detection Demo")
    print("=" * 60)
    
    # 方法1: 使用便捷函数
    image_path = "test_image.jpg"  # 替换为实际图片路径
    
    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        print("Tip: 请将图片放在当前目录或提供完整路径")
        return
    
    print(f"\nAnalyzing: {image_path}")
    
    # 使用MediaPipe检测
    percept = detect_emotion_from_image(image_path, use_mediapipe=True)
    
    if percept:
        print(f"\n✅ Detection successful!")
        print(f"  Emotion: {percept.metadata['dominant_emotion'].upper()}")
        print(f"  Confidence: {percept.confidence:.1%}")
        print(f"  VAD:")
        print(f"    Valence:   {percept.valence_hint:+.2f} ({'positive' if percept.valence_hint > 0 else 'negative'})")
        print(f"    Arousal:   {percept.arousal_hint:.2f} ({'high' if percept.arousal_hint > 0.6 else 'low'})")
        print(f"    Dominance: {percept.dominance_hint:+.2f}")
        print(f"  Detector: {percept.metadata.get('detector', 'unknown')}")
        
        # 显示所有情感概率
        print(f"\n  All emotions:")
        for emo, prob in sorted(percept.metadata['all_emotions'].items(), key=lambda x: x[1], reverse=True):
            bar = '█' * int(prob * 30)
            print(f"    {emo:10s} {prob:.1%} {bar}")
    else:
        print(f"\n❌ No face detected in image")


def demo_comparison():
    """对比MediaPipe和Haar Cascade检测效果"""
    print("=" * 60)
    print("Detector Comparison: MediaPipe vs Haar Cascade")
    print("=" * 60)
    
    image_path = "test_image.jpg"
    
    if not Path(image_path).exists():
        print(f"❌ Image not found: {image_path}")
        return
    
    print(f"\nAnalyzing: {image_path}")
    
    # 测试MediaPipe
    print("\n[1] MediaPipe Detection:")
    percept_mp = detect_emotion_from_image(image_path, use_mediapipe=True)
    if percept_mp:
        print(f"  ✅ Detected: {percept_mp.metadata['dominant_emotion'].upper()} "
              f"({percept_mp.confidence:.1%})")
        print(f"  Detector: {percept_mp.metadata['detector']}")
    else:
        print(f"  ❌ No face detected")
    
    # 测试Haar Cascade
    print("\n[2] Haar Cascade Detection:")
    percept_haar = detect_emotion_from_image(image_path, use_mediapipe=False)
    if percept_haar:
        print(f"  ✅ Detected: {percept_haar.metadata['dominant_emotion'].upper()} "
              f"({percept_haar.confidence:.1%})")
        print(f"  Detector: {percept_haar.metadata['detector']}")
    else:
        print(f"  ❌ No face detected")
    
    # 对比结果
    if percept_mp and percept_haar:
        print("\n[Comparison]")
        if percept_mp.metadata['dominant_emotion'] == percept_haar.metadata['dominant_emotion']:
            print(f"  ✅ Both detected same emotion: {percept_mp.metadata['dominant_emotion'].upper()}")
        else:
            print(f"  ⚠️  Different results:")
            print(f"     MediaPipe: {percept_mp.metadata['dominant_emotion'].upper()} ({percept_mp.confidence:.1%})")
            print(f"     Haar:      {percept_haar.metadata['dominant_emotion'].upper()} ({percept_haar.confidence:.1%})")


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python demo_vision.py realtime    # 实时摄像头检测")
        print("  python demo_vision.py image       # 图片文件检测")
        print("  python demo_vision.py compare     # 对比不同检测器")
        return
    
    mode = sys.argv[1].lower()
    
    if mode == "realtime":
        demo_real_time_detection()
    elif mode == "image":
        demo_image_detection()
    elif mode == "compare":
        demo_comparison()
    else:
        print(f"❌ Unknown mode: {mode}")
        print("Available modes: realtime, image, compare")


if __name__ == "__main__":
    main()
