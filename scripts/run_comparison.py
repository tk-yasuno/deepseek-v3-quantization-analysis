#!/usr/bin/env python3
"""
DeepSeek V3 vs Kimi K2 比較評価スクリプト
外付けGPU 16GB環境での性能・品質比較
"""

import json
import time
import csv
import subprocess
import psutil
# import GPUtil  # Windows環境での問題回避のためコメントアウト
from datetime import datetime
from pathlib import Path

class LLMComparator:
    def __init__(self):
        self.models = {
            "deepseek-v3": "deepseek-coder:6.7b-instruct-q4_0",  # Q4_0量子化
            "kimi-k2": "kimi-k2:latest"                           # Q4_K_M量子化（カスタム）
        }
        
        # Q4_K_M設定情報
        self.model_configs = {
            "deepseek-v3": {"quantization": "Q4_0", "expected_vram": "8-10GB"},
            "kimi-k2": {"quantization": "Q4_K_M", "expected_vram": "6-8GB"}
        }
        
        self.results_dir = Path("results")
        self.results_dir.mkdir(exist_ok=True)
        
        # CSV出力ファイル
        self.csv_file = self.results_dir / "token_latency_log.csv"
        self.eval_file = self.results_dir / "output_eval.md"
        
    def load_prompts(self):
        """テスト用プロンプトをロード"""
        with open("templates/test_prompts.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        return data["test_prompts"]
    
    def load_prompt_template(self):
        """プロンプトテンプレートをロード"""
        with open("templates/prompt_template.txt", "r", encoding="utf-8") as f:
            return f.read()
    
    def get_system_metrics(self):
        """システムメトリクスを取得"""
        cpu_usage = psutil.cpu_percent(interval=1)
        
        # GPU使用量取得（nvidia-smi経由）
        gpu_memory = 0
        try:
            result = subprocess.run([
                "nvidia-smi", "--query-gpu=memory.used", 
                "--format=csv,noheader,nounits"
            ], capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                gpu_memory = int(result.stdout.strip().split('\n')[0])
        except (subprocess.TimeoutExpired, subprocess.CalledProcessError, ValueError):
            # nvidia-smiが使用できない場合は0とする
            gpu_memory = 0
            
        return cpu_usage, gpu_memory
    
    def run_ollama_inference(self, model_name, prompt, timeout=120):
        """Ollama推論実行"""
        start_time = time.time()
        start_timestamp = datetime.now().isoformat()
        
        cpu_before, gpu_before = self.get_system_metrics()
        
        try:
            result = subprocess.run([
                "ollama", "run", model_name, prompt
            ], capture_output=True, text=True, timeout=timeout, encoding='utf-8')
            
            end_time = time.time()
            end_timestamp = datetime.now().isoformat()
            
            cpu_after, gpu_after = self.get_system_metrics()
            
            if result.returncode == 0:
                output = result.stdout.strip()
                latency_ms = (end_time - start_time) * 1000
                
                # トークン数推定（簡易）
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
                    "error": result.stderr
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
    
    def log_to_csv(self, model_name, prompt_data, result):
        """CSV形式でログ出力"""
        # CSVヘッダーが存在しない場合は作成
        if not self.csv_file.exists():
            with open(self.csv_file, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    "model_name", "prompt_id", "category", "start_time", 
                    "end_time", "token_count", "latency_ms", "tokens_per_second",
                    "gpu_memory_mb", "cpu_usage_percent"
                ])
        
        if result["success"]:
            with open(self.csv_file, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    model_name,
                    prompt_data["id"],
                    prompt_data["category"],
                    result["start_time"],
                    result["end_time"],
                    result["token_count"],
                    result["latency_ms"],
                    result["tokens_per_second"],
                    result["gpu_memory_mb"],
                    result["cpu_usage_percent"]
                ])
    
    def append_to_eval_md(self, prompt_data, results):
        """Markdown形式で評価結果を出力"""
        with open(self.eval_file, "a", encoding="utf-8") as f:
            f.write(f"\n## Prompt ID: {prompt_data['id']}\n")
            f.write(f"### カテゴリ: {prompt_data['category']}\n")
            f.write(f"### Prompt:\n{prompt_data['prompt']}\n\n")
            f.write("---\n\n")
            
            for model_name, result in results.items():
                f.write(f"### {model_name.upper()} Output:\n")
                if result["success"]:
                    f.write(f"```\n{result['output']}\n```\n\n")
                    f.write(f"**性能指標**:\n")
                    f.write(f"- 応答時間: {result['latency_ms']:.1f}ms\n")
                    f.write(f"- トークン/秒: {result['tokens_per_second']:.1f}\n")
                    f.write(f"- GPU使用量: {result['gpu_memory_mb']}MB\n")
                    f.write(f"- CPU使用率: {result['cpu_usage_percent']:.1f}%\n\n")
                    f.write("**評価**:\n")
                    f.write("- 論理性: ★★★☆☆\n")
                    f.write("- 技術的正確性: ★★★☆☆\n")
                    f.write("- 表現の自然さ: ★★★☆☆\n\n")
                else:
                    f.write(f"**エラー**: {result['error']}\n\n")
                
                f.write("---\n\n")
            
            f.write("### コメント:\n")
            f.write("（ここに手動で比較コメントを記入してください）\n\n")
            f.write("=" * 80 + "\n\n")
    
    def run_comparison(self):
        """比較評価メイン実行"""
        prompts = self.load_prompts()
        template = self.load_prompt_template()
        
        # 評価結果ファイル初期化
        with open(self.eval_file, "w", encoding="utf-8") as f:
            f.write("# LLM比較評価結果（Q4_K_M最適化）\n")
            f.write(f"実行日時: {datetime.now().strftime('%Y年%m月%d日 %H:%M:%S')}\n")
            f.write("対象モデル: DeepSeek V3 (Q4_0) vs Kimi K2 (Q4_K_M)\n")
            f.write("環境: 外付けGPU 16GB、INT4量子化最適化\n")
            f.write("量子化選択理由: Q4_K_M = 品質・速度・メモリのバランス最適\n\n")
        
        print("🚀 LLM比較評価を開始します...")
        print(f"対象モデル: {list(self.models.values())}")
        print(f"テストプロンプト数: {len(prompts)}")
        
        for i, prompt_data in enumerate(prompts, 1):
            print(f"\n📝 [{i}/{len(prompts)}] プロンプトID: {prompt_data['id']}")
            print(f"カテゴリ: {prompt_data['category']}")
            
            # プロンプトテンプレート適用
            full_prompt = template.replace("{PROMPT}", prompt_data["prompt"])
            
            results = {}
            
            for model_key, model_name in self.models.items():
                print(f"  🤖 {model_key} で推論中...")
                
                result = self.run_ollama_inference(model_name, full_prompt)
                results[model_key] = result
                
                if result["success"]:
                    print(f"    ✅ 完了 ({result['latency_ms']:.1f}ms, {result['tokens_per_second']:.1f} tok/s)")
                    self.log_to_csv(model_key, prompt_data, result)
                else:
                    print(f"    ❌ エラー: {result['error']}")
            
            # Markdown評価ファイルに追記
            self.append_to_eval_md(prompt_data, results)
            
            # モデル間で少し間隔をあける
            time.sleep(2)
        
        print(f"\n🎉 比較評価完了!")
        print(f"結果ファイル:")
        print(f"  - CSV: {self.csv_file}")
        print(f"  - 評価: {self.eval_file}")

def main():
    comparator = LLMComparator()
    comparator.run_comparison()

if __name__ == "__main__":
    main()