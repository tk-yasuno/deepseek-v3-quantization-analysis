#!/usr/bin/env python3
"""
DeepSeek V3 量子化比較スクリプト
Q4_0 vs Q8_0 の性能・品質・GPU使用量比較
"""

import json
import time
import csv
import subprocess
import psutil
from datetime import datetime
from pathlib import Path

class QuantizationComparator:
    def __init__(self):
        # 比較対象のモデル（3つの量子化レベル）
        self.models = {
            "deepseek-fp16": {
                "name": "deepseek-coder:6.7b-instruct",
                "quantization": "FP16",
                "expected_vram": "12-16GB",
                "expected_speed": "3-8 tok/s"
            },
            "deepseek-q8": {
                "name": "deepseek-coder:6.7b-instruct-q8_0", 
                "quantization": "Q8_0",
                "expected_vram": "10-12GB",
                "expected_speed": "5-10 tok/s"
            },
            "deepseek-q4": {
                "name": "deepseek-coder:6.7b-instruct-q4_0",
                "quantization": "Q4_0",
                "expected_vram": "6-8GB",
                "expected_speed": "10-15 tok/s"
            }
        }
        
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # 結果ファイル
        self.csv_file = self.results_dir / "quantization_comparison_log.csv"
        self.eval_file = self.results_dir / "quantization_evaluation.md"
        
    def load_test_prompts(self):
        """量子化比較用テストプロンプト"""
        return [
            {
                "id": "quant_001",
                "category": "コード生成",
                "prompt": "Pythonでクイックソートを実装してください。コメントも含めてください。"
            },
            {
                "id": "quant_002",
                "category": "技術解説", 
                "prompt": "機械学習における過学習とは何ですか？対策も含めて説明してください。"
            },
            {
                "id": "quant_003",
                "category": "数学・論理",
                "prompt": "フィボナッチ数列の10番目の値を計算し、その過程を説明してください。"
            },
            {
                "id": "quant_004",
                "category": "問題解決",
                "prompt": "Webアプリケーションが遅い場合の調査手順を5つのステップで説明してください。"
            }
        ]
    
    def get_gpu_memory_usage(self):
        """GPU使用量をnvidia-smiで取得"""
        try:
            result = subprocess.run([
                "nvidia-smi", "--query-gpu=memory.used,memory.total,utilization.gpu",
                "--format=csv,noheader,nounits"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                data = result.stdout.strip().split(', ')
                return {
                    "memory_used_mb": int(data[0]),
                    "memory_total_mb": int(data[1]), 
                    "gpu_utilization": int(data[2])
                }
        except:
            pass
        return {"memory_used_mb": 0, "memory_total_mb": 16380, "gpu_utilization": 0}
    
    def run_model_inference(self, model_info, prompt, timeout=60):
        """指定モデルでの推論実行"""
        start_time = time.time()
        start_timestamp = datetime.now().isoformat()
        
        # 推論前のGPU使用量
        gpu_before = self.get_gpu_memory_usage()
        cpu_before = psutil.cpu_percent(interval=0.1)
        
        try:
            # プロンプトテンプレート適用
            full_prompt = f"""### Instruction:
あなたは優秀なプログラミングアシスタントです。以下の質問に対して正確で詳細な回答を提供してください。

### Input:
{prompt}

### Response:"""

            result = subprocess.run([
                "ollama", "run", model_info["name"], full_prompt
            ], capture_output=True, text=True, timeout=timeout, encoding='utf-8')
            
            end_time = time.time()
            end_timestamp = datetime.now().isoformat()
            
            # 推論後のシステムメトリクス
            gpu_after = self.get_gpu_memory_usage()
            cpu_after = psutil.cpu_percent(interval=0.1)
            
            if result.returncode == 0:
                output = result.stdout.strip()
                latency_ms = (end_time - start_time) * 1000
                
                # トークン数と速度計算
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
                    "gpu_memory_used_mb": gpu_after["memory_used_mb"],
                    "gpu_memory_peak_mb": max(gpu_before["memory_used_mb"], gpu_after["memory_used_mb"]),
                    "gpu_utilization": gpu_after["gpu_utilization"],
                    "cpu_usage_percent": (cpu_before + cpu_after) / 2,
                    "quantization": model_info["quantization"]
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr or "推論エラー",
                    "quantization": model_info["quantization"]
                }
                
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"タイムアウト ({timeout}秒)",
                "quantization": model_info["quantization"]
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "quantization": model_info["quantization"]
            }
    
    def log_comparison_csv(self, model_key, prompt_data, result):
        """比較結果をCSV記録"""
        if not self.csv_file.exists():
            with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "model", "quantization", "prompt_id", "category", 
                    "latency_ms", "tokens_per_second", "token_count",
                    "gpu_memory_used_mb", "gpu_peak_mb", "gpu_utilization",
                    "cpu_usage_percent", "success"
                ])
        
        with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if result["success"]:
                writer.writerow([
                    model_key, result["quantization"], prompt_data["id"],
                    prompt_data["category"], result["latency_ms"],
                    result["tokens_per_second"], result["token_count"],
                    result["gpu_memory_used_mb"], result["gpu_memory_peak_mb"],
                    result["gpu_utilization"], result["cpu_usage_percent"], True
                ])
            else:
                writer.writerow([
                    model_key, result["quantization"], prompt_data["id"],
                    prompt_data["category"], 0, 0, 0, 0, 0, 0, 0, False
                ])
    
    def append_comparison_md(self, prompt_data, results):
        """比較結果をMarkdown記録"""
        with open(self.eval_file, "a", encoding="utf-8") as f:
            f.write(f"\n## {prompt_data['category']} (ID: {prompt_data['id']})\n")
            f.write(f"### プロンプト:\n```\n{prompt_data['prompt']}\n```\n\n")
            
            for model_key, result in results.items():
                model_info = self.models[model_key]
                f.write(f"### {model_info['quantization']} 結果:\n")
                
                if result["success"]:
                    f.write(f"**出力** ({result['token_count']}トークン):\n")
                    f.write(f"```\n{result['output'][:300]}{'...' if len(result['output']) > 300 else ''}\n```\n\n")
                    
                    f.write(f"**性能指標**:\n")
                    f.write(f"- 応答時間: {result['latency_ms']:.1f}ms\n")
                    f.write(f"- トークン/秒: {result['tokens_per_second']:.1f}\n")
                    f.write(f"- GPU使用量: {result['gpu_memory_used_mb']}MB\n")
                    f.write(f"- GPU利用率: {result['gpu_utilization']}%\n")
                    f.write(f"- CPU使用率: {result['cpu_usage_percent']:.1f}%\n\n")
                else:
                    f.write(f"**エラー**: {result['error']}\n\n")
                
                f.write("---\n\n")
    
    def run_quantization_comparison(self):
        """量子化比較メイン実行"""
        prompts = self.load_test_prompts()
        
        # 評価ファイル初期化
        with open(self.eval_file, "w", encoding="utf-8") as f:
            f.write("# DeepSeek V3 量子化比較結果\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write("比較対象: Q4_0 vs Q8_0 量子化\n")
            f.write("環境: 外付けGPU 16GB (RTX 4060 Ti)\n")
            f.write("目的: 量子化による性能・品質・メモリ使用量の違い分析\n\n")
            
            # 期待値表
            f.write("## 期待される特性比較\n")
            f.write("| 量子化 | メモリ使用 | 推論速度 | 品質 | 用途 |\n")
            f.write("|--------|-----------|----------|------|------|\n")
            f.write("| Q4_0 | 6-8GB | 高速 | 実用的 | 一般用途 |\n")
            f.write("| Q8_0 | 10-12GB | 中速 | 高品質 | 品質重視 |\n\n")
        
        print("🚀 DeepSeek V3 量子化比較を開始します...")
        print(f"比較モデル: Q4_0 vs Q8_0")
        print(f"テストプロンプト数: {len(prompts)}")
        
        for i, prompt_data in enumerate(prompts, 1):
            print(f"\n📝 [{i}/{len(prompts)}] {prompt_data['category']} (ID: {prompt_data['id']})")
            print(f"プロンプト: {prompt_data['prompt'][:60]}...")
            
            results = {}
            
            for model_key, model_info in self.models.items():
                print(f"  🤖 {model_info['quantization']} で推論中...")
                
                result = self.run_model_inference(model_info, prompt_data["prompt"])
                results[model_key] = result
                
                if result["success"]:
                    print(f"    ✅ 完了 ({result['latency_ms']:.1f}ms, {result['tokens_per_second']:.1f} tok/s, {result['gpu_memory_used_mb']}MB)")
                else:
                    print(f"    ❌ エラー: {result['error']}")
                
                # CSV記録
                self.log_comparison_csv(model_key, prompt_data, result)
                
                # モデル間で間隔をあける
                time.sleep(3)
            
            # Markdown記録
            self.append_comparison_md(prompt_data, results)
        
        print(f"\n🎉 量子化比較完了!")
        print(f"結果ファイル:")
        print(f"  - 数値データ: {self.csv_file}")
        print(f"  - 詳細比較: {self.eval_file}")

def main():
    # 両方のモデルが利用可能かチェック
    try:
        result = subprocess.run(["ollama", "list"], 
                              capture_output=True, text=True, encoding='utf-8')
        
        if "deepseek-coder:6.7b-instruct-q4_0" not in result.stdout:
            print("❌ Q4_0モデルが見つかりません")
            return
        
        if "deepseek-coder:6.7b-instruct-q8_0" not in result.stdout:
            print("❌ Q8_0モデルが見つかりません")
            print("ダウンロード中の場合は完了まで待機してください...")
            return
            
        print("✅ 両方のモデル確認済み")
    except Exception as e:
        print(f"❌ Ollama接続エラー: {e}")
        return
    
    comparator = QuantizationComparator()
    comparator.run_quantization_comparison()

if __name__ == "__main__":
    main()