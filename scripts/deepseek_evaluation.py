#!/usr/bin/env python3
"""
DeepSeek V3 単体評価スクリプト
外付けGPU 16GB環境での性能・品質評価
"""

import json
import time
import csv
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

class DeepSeekEvaluator:
    def __init__(self):
        # DeepSeek V3のみに集中
        self.model = "deepseek-coder:6.7b-instruct-q4_0"
        self.model_name = "deepseek-v3"
        
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # 結果ファイル
        self.csv_file = self.results_dir / "deepseek_performance_log.csv"
        self.eval_file = self.results_dir / "deepseek_evaluation.md"
        
    def load_test_prompts(self):
        """テスト用プロンプトセット"""
        return [
            {
                "id": "001",
                "category": "技術解説",
                "prompt": "Transformerアーキテクチャの仕組みを、初心者にもわかりやすく説明してください。"
            },
            {
                "id": "002", 
                "category": "コード生成",
                "prompt": "Pythonで簡単なWebスクレイピングを行うコードを書いてください。requests とBeautifulSoupを使用してください。"
            },
            {
                "id": "003",
                "category": "問題解決",
                "prompt": "データサイエンスプロジェクトで、モデルの予測精度が低い場合に確認すべき5つのポイントを教えてください。"
            },
            {
                "id": "004",
                "category": "デバッグ",
                "prompt": "以下のPythonコードのエラーを修正してください：\n```python\ndef calculate_average(numbers):\n    total = 0\n    for num in numbers:\n        total += num\n    return total / len(numbers)\n\nresult = calculate_average([])\nprint(result)\n```"
            },
            {
                "id": "005",
                "category": "アルゴリズム",
                "prompt": "バブルソートアルゴリズムをPythonで実装し、時間計算量について説明してください。"
            },
            {
                "id": "006",
                "category": "応用",
                "prompt": "機械学習でよく使われるクロスバリデーションとは何ですか？実装例も含めて説明してください。"
            }
        ]
    
    def get_system_metrics(self):
        """システムメトリクス取得"""
        cpu_usage = psutil.cpu_percent(interval=0.5)
        
        # GPU使用量（nvidia-smi使用）
        gpu_memory = 0
        try:
            result = subprocess.run([
                "nvidia-smi", "--query-gpu=memory.used", 
                "--format=csv,noheader,nounits"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                gpu_memory = int(result.stdout.strip())
        except:
            gpu_memory = 0
            
        return cpu_usage, gpu_memory
    
    def run_deepseek_inference(self, prompt, timeout=120):
        """DeepSeek V3での推論実行"""
        start_time = time.time()
        start_timestamp = datetime.now().isoformat()
        
        cpu_before, gpu_before = self.get_system_metrics()
        
        try:
            # プロンプトテンプレート適用
            full_prompt = f"""### Instruction:
あなたは優秀なAIアシスタントです。以下の質問に対して、簡潔かつ論理的に答えてください。

### Input:
{prompt}

### Response:"""

            result = subprocess.run([
                "ollama", "run", self.model, full_prompt
            ], capture_output=True, text=True, timeout=timeout, encoding='utf-8')
            
            end_time = time.time()
            end_timestamp = datetime.now().isoformat()
            
            cpu_after, gpu_after = self.get_system_metrics()
            
            if result.returncode == 0:
                output = result.stdout.strip()
                latency_ms = (end_time - start_time) * 1000
                
                # トークン数推定
                token_count = len(output.split())
                tokens_per_second = token_count / (latency_ms / 1000) if latency_ms > 0 else 0
                
                return {
                    "success": True,
                    "output": output,
                    "start_time": start_timestamp,
                    "end_time": end_timestamp,
                    "latency_ms": latency_ms,
                    "token_count": token_count,
                    "tokens_per_second": tokens_per_second,
                    "gpu_memory_mb": max(gpu_before, gpu_after),
                    "cpu_usage_percent": (cpu_before + cpu_after) / 2
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or "推論エラー"
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"タイムアウト ({timeout}秒)"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def log_performance_csv(self, prompt_data, result):
        """性能データをCSV記録"""
        if not self.csv_file.exists():
            with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "prompt_id", "category", "start_time", "end_time",
                    "token_count", "latency_ms", "tokens_per_second",
                    "gpu_memory_mb", "cpu_usage_percent", "success"
                ])
        
        if result["success"]:
            with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    prompt_data["id"],
                    prompt_data["category"],
                    result["start_time"],
                    result["end_time"],
                    result["token_count"],
                    result["latency_ms"],
                    result["tokens_per_second"],
                    result["gpu_memory_mb"],
                    result["cpu_usage_percent"],
                    True
                ])
        else:
            with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    prompt_data["id"], prompt_data["category"], "", "",
                    0, 0, 0, 0, 0, False
                ])
    
    def append_evaluation_md(self, prompt_data, result):
        """評価結果をMarkdown記録"""
        with open(self.eval_file, "a", encoding="utf-8") as f:
            f.write(f"\n## Prompt ID: {prompt_data['id']}\n")
            f.write(f"### カテゴリ: {prompt_data['category']}\n")
            f.write(f"### プロンプト:\n```\n{prompt_data['prompt']}\n```\n\n")
            
            if result["success"]:
                f.write("### DeepSeek V3 出力:\n")
                f.write(f"```\n{result['output']}\n```\n\n")
                
                f.write("### 性能指標:\n")
                f.write(f"- **応答時間**: {result['latency_ms']:.1f}ms\n")
                f.write(f"- **トークン/秒**: {result['tokens_per_second']:.1f}\n")
                f.write(f"- **トークン数**: {result['token_count']}\n")
                f.write(f"- **GPU使用量**: {result['gpu_memory_mb']}MB\n")
                f.write(f"- **CPU使用率**: {result['cpu_usage_percent']:.1f}%\n\n")
                
                f.write("### 評価（手動記入用）:\n")
                f.write("- **論理性**: ★★★☆☆\n")
                f.write("- **技術的正確性**: ★★★☆☆\n")
                f.write("- **表現の自然さ**: ★★★☆☆\n")
                f.write("- **実用性**: ★★★☆☆\n\n")
                
                f.write("### コメント:\n")
                f.write("（ここに手動でコメントを記入してください）\n\n")
                
            else:
                f.write(f"### エラー:\n")
                f.write(f"```\n{result['error']}\n```\n\n")
            
            f.write("---\n\n")
    
    def run_evaluation(self):
        """DeepSeek V3評価メイン実行"""
        prompts = self.load_test_prompts()
        
        # 評価ファイル初期化
        with open(self.eval_file, "w", encoding="utf-8") as f:
            f.write("# DeepSeek V3 単体評価結果\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write("モデル: deepseek-coder:6.7b-instruct-q4_0\n")
            f.write("環境: 外付けGPU 16GB、Q4_0量子化\n")
            f.write("目的: DeepSeek V3の性能と品質評価\n\n")
        
        print("🚀 DeepSeek V3 単体評価を開始します...")
        print(f"モデル: {self.model}")
        print(f"テストプロンプト数: {len(prompts)}")
        
        success_count = 0
        total_latency = 0
        total_tokens = 0
        
        for i, prompt_data in enumerate(prompts, 1):
            print(f"\n📝 [{i}/{len(prompts)}] {prompt_data['category']} (ID: {prompt_data['id']})")
            print(f"プロンプト: {prompt_data['prompt'][:50]}...")
            
            result = self.run_deepseek_inference(prompt_data["prompt"])
            
            if result["success"]:
                print(f"✅ 成功 ({result['latency_ms']:.1f}ms, {result['tokens_per_second']:.1f} tok/s)")
                success_count += 1
                total_latency += result['latency_ms']
                total_tokens += result['token_count']
            else:
                print(f"❌ エラー: {result['error']}")
            
            # 結果記録
            self.log_performance_csv(prompt_data, result)
            self.append_evaluation_md(prompt_data, result)
            
            # 少し間隔をあける
            time.sleep(2)
        
        # 最終サマリー
        print(f"\n🎉 DeepSeek V3評価完了!")
        print(f"成功率: {success_count}/{len(prompts)} ({success_count/len(prompts)*100:.1f}%)")
        
        if success_count > 0:
            avg_latency = total_latency / success_count
            avg_tokens = total_tokens / success_count
            avg_speed = avg_tokens / (avg_latency / 1000)
            print(f"平均応答時間: {avg_latency:.1f}ms")
            print(f"平均トークン数: {avg_tokens:.0f}")
            print(f"平均速度: {avg_speed:.1f} tokens/sec")
        
        print(f"\n📊 結果ファイル:")
        print(f"- 性能データ: {self.csv_file}")
        print(f"- 評価詳細: {self.eval_file}")

def main():
    # DeepSeek V3が利用可能かチェック
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if "deepseek-coder" not in result.stdout:
            print("❌ DeepSeek V3が見つかりません")
            print("以下のコマンドでインストールしてください:")
            print("  ollama pull deepseek-coder:6.7b-instruct-q4_0")
            return
        else:
            print("✅ DeepSeek V3モデル確認済み")
    except Exception as e:
        print(f"❌ Ollama接続エラー: {e}")
        return
    
    evaluator = DeepSeekEvaluator()
    evaluator.run_evaluation()

if __name__ == "__main__":
    main()