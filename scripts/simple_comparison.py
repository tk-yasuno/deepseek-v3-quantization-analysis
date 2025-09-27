#!/usr/bin/env python3
"""
代替案：既存モデルでの比較評価
Kimi K2の代わりに利用可能なモデルを使用
"""

import subprocess
import json
import time
import csv
import psutil
from datetime import datetime
from pathlib import Path

class SimpleLLMComparator:
    def __init__(self):
        # 現在利用可能なモデルを使用
        self.models = {
            "llama3": "llama3:8b",          # DeepSeek V3の代替
            "mistral": "mistral:latest"      # Kimi K2の代替
        }
        
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        self.csv_file = self.results_dir / "simple_comparison_log.csv"
        self.eval_file = self.results_dir / "simple_eval.md"

    def get_system_metrics(self):
        """簡単なシステムメトリクス"""
        cpu_usage = psutil.cpu_percent(interval=0.1)
        return cpu_usage, 0  # GPUは後で手動確認

    def run_ollama_inference(self, model_name, prompt, timeout=60):
        """Ollama推論実行（簡素版）"""
        start_time = time.time()
        start_timestamp = datetime.now().isoformat()
        
        try:
            result = subprocess.run([
                "ollama", "run", model_name, prompt
            ], capture_output=True, text=True, timeout=timeout, encoding='utf-8')
            
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            if result.returncode == 0:
                output = result.stdout.strip()
                token_count = len(output.split())
                tokens_per_second = token_count / (latency_ms / 1000) if latency_ms > 0 else 0
                
                return {
                    "success": True,
                    "output": output,
                    "latency_ms": latency_ms,
                    "tokens_per_second": tokens_per_second
                }
            else:
                return {"success": False, "error": result.stderr}
                
        except Exception as e:
            return {"success": False, "error": str(e)}

    def run_simple_test(self):
        """簡単な比較テスト"""
        test_prompts = [
            "こんにちは！自己紹介をお願いします。",
            "Pythonでリストを逆順にする方法を教えてください。",
            "機械学習とは何ですか？簡潔に説明してください。"
        ]
        
        print("🚀 簡単な比較テストを開始します...")
        
        # CSVヘッダー作成
        with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["model", "prompt_id", "latency_ms", "tokens_per_second", "success"])
        
        # Markdown初期化
        with open(self.eval_file, "w", encoding="utf-8") as f:
            f.write("# 簡単LLM比較結果\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write("対象: Llama3:8B vs Mistral:latest\n\n")
        
        for i, prompt in enumerate(test_prompts, 1):
            print(f"\n📝 テスト {i}: {prompt}")
            
            with open(self.eval_file, "a", encoding="utf-8") as f:
                f.write(f"\n## テスト {i}\n")
                f.write(f"**プロンプト**: {prompt}\n\n")
            
            for model_key, model_name in self.models.items():
                print(f"  🤖 {model_key} で実行中...")
                
                result = self.run_ollama_inference(model_name, prompt)
                
                if result["success"]:
                    print(f"    ✅ 完了 ({result['latency_ms']:.1f}ms)")
                    
                    # CSV記録
                    with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            model_key, i, result["latency_ms"], 
                            result["tokens_per_second"], True
                        ])
                    
                    # Markdown記録
                    with open(self.eval_file, "a", encoding="utf-8") as f:
                        f.write(f"### {model_key.upper()}の回答:\n")
                        f.write(f"```\n{result['output']}\n```\n")
                        f.write(f"**応答時間**: {result['latency_ms']:.1f}ms\n")
                        f.write(f"**速度**: {result['tokens_per_second']:.1f} tok/s\n\n")
                else:
                    print(f"    ❌ エラー: {result['error']}")
                    
                    with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow([model_key, i, 0, 0, False])
            
            time.sleep(1)  # 少し間隔をあける
        
        print(f"\n🎉 簡単テスト完了！")
        print(f"結果: {self.csv_file} と {self.eval_file}")

def main():
    comparator = SimpleLLMComparator()
    comparator.run_simple_test()

if __name__ == "__main__":
    main()