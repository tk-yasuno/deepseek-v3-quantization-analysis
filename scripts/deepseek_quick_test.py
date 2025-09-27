#!/usr/bin/env python3
"""
DeepSeek V3 クイックテスト
簡単な動作確認とベンチマーク
"""

import subprocess
import time
from datetime import datetime

def check_deepseek_availability():
    """DeepSeek V3の利用可能性チェック"""
    print("🔍 DeepSeek V3 利用可能性チェック...")
    
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if "deepseek-coder" in result.stdout:
            print("✅ DeepSeek V3 モデル利用可能")
            return True
        else:
            print("❌ DeepSeek V3 モデルが見つかりません")
            print("ダウンロードコマンド: ollama pull deepseek-coder:6.7b-instruct-q4_0")
            return False
    except Exception as e:
        print(f"❌ Ollama接続エラー: {e}")
        return False

def quick_inference_test():
    """クイック推論テスト"""
    test_prompts = [
        "こんにちは！自己紹介をお願いします。",
        "Pythonでリストの長さを取得する方法を教えてください。",
        "1+1の答えは何ですか？理由も説明してください。"
    ]
    
    print("\n🧪 DeepSeek V3 クイック推論テスト")
    print("=" * 50)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n📝 テスト {i}: {prompt}")
        
        start_time = time.time()
        
        try:
            result = subprocess.run([
                "ollama", "run", "deepseek-coder:6.7b-instruct-q4_0", prompt
            ], capture_output=True, text=True, timeout=60, encoding='utf-8')
            
            end_time = time.time()
            latency = (end_time - start_time) * 1000
            
            if result.returncode == 0:
                output = result.stdout.strip()
                token_count = len(output.split())
                tokens_per_sec = token_count / (latency / 1000) if latency > 0 else 0
                
                print(f"✅ 成功 ({latency:.1f}ms, {tokens_per_sec:.1f} tok/s)")
                print("回答:")
                print("-" * 30)
                print(output[:200] + ("..." if len(output) > 200 else ""))
                print("-" * 30)
            else:
                print(f"❌ エラー: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("❌ タイムアウト（60秒）")
        except Exception as e:
            print(f"❌ 例外エラー: {e}")

def performance_benchmark():
    """基本性能ベンチマーク"""
    print("\n🏁 DeepSeek V3 性能ベンチマーク")
    print("=" * 50)
    
    benchmark_prompt = """### Instruction:
あなたは優秀なプログラミングアシスタントです。以下の課題を解決してください。

### Input:
Pythonで、1から100までの整数の中で素数を全て見つけて表示するプログラムを書いてください。効率的なアルゴリズムを使用してください。

### Response:"""

    print("📋 ベンチマーク課題: Python素数検索プログラム生成")
    print("⏱️ 実行中...")
    
    start_time = time.time()
    
    try:
        result = subprocess.run([
            "ollama", "run", "deepseek-coder:6.7b-instruct-q4_0", benchmark_prompt
        ], capture_output=True, text=True, timeout=120, encoding='utf-8')
        
        end_time = time.time()
        total_time = end_time - start_time
        
        if result.returncode == 0:
            output = result.stdout.strip()
            
            # 基本統計
            char_count = len(output)
            word_count = len(output.split())
            line_count = output.count('\n') + 1
            
            # 推定性能
            tokens_per_sec = word_count / total_time if total_time > 0 else 0
            chars_per_sec = char_count / total_time if total_time > 0 else 0
            
            print(f"\n📊 ベンチマーク結果:")
            print(f"  総実行時間: {total_time:.2f}秒")
            print(f"  出力文字数: {char_count:,}")
            print(f"  出力単語数: {word_count:,}")
            print(f"  出力行数: {line_count}")
            print(f"  推定速度: {tokens_per_sec:.1f} トークン/秒")
            print(f"  文字生成速度: {chars_per_sec:.1f} 文字/秒")
            
            # 品質チェック（簡易）
            code_indicators = ["def ", "for ", "if ", "import ", "print(", "return"]
            code_score = sum(1 for indicator in code_indicators if indicator in output)
            
            print(f"  コード品質指標: {code_score}/6")
            
            print(f"\n📄 生成されたコード（先頭200文字）:")
            print("-" * 50)
            print(output[:200] + ("..." if len(output) > 200 else ""))
            print("-" * 50)
            
            # 総合評価
            if total_time < 10 and tokens_per_sec > 20 and code_score >= 4:
                print("🎉 優秀: DeepSeek V3は16GB環境で高性能動作中")
            elif total_time < 20 and tokens_per_sec > 10 and code_score >= 3:
                print("👍 良好: DeepSeek V3は実用的な性能で動作中")
            else:
                print("⚠️ 注意: 性能または品質に改善の余地あり")
                
        else:
            print(f"❌ ベンチマーク失敗: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("❌ ベンチマークタイムアウト（120秒）")
    except Exception as e:
        print(f"❌ ベンチマーク例外: {e}")

def main():
    print("🚀 DeepSeek V3 クイックテスト開始")
    print(f"実行時刻: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: 利用可能性チェック
    if not check_deepseek_availability():
        return
    
    # Step 2: クイック推論テスト
    quick_inference_test()
    
    # Step 3: 性能ベンチマーク
    performance_benchmark()
    
    print(f"\n✅ DeepSeek V3 クイックテスト完了")
    print("次のステップ: python scripts/deepseek_evaluation.py で詳細評価を実行")

if __name__ == "__main__":
    main()