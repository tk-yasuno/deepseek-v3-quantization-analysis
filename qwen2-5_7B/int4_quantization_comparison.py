#!/usr/bin/env python3
"""
Multi-Model INT4量子化比較分析
DeepSeek V3 vs Qwen2.5-7B の性能・効率比較（INT4量子化）
"""

import subprocess
import time
import psutil
import json
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

class INT4QuantizationComparison:
    def __init__(self):
        self.results = []
        self.test_prompts = [
            "Pythonでリストを逆順にする3つの方法を説明してください。",
            "機械学習におけるAttentionメカニズムとは何ですか？",
            "量子化がLLMの性能に与える影響について説明してください。",
            "日本語と英語でプログラミングの概念を説明する際の違いは？",
            "分散システムの設計において重要な考慮事項を5つ挙げてください。"
        ]
        
    def measure_model_performance(self, model_name, model_display_name):
        """モデルの性能測定（INT4量子化対応）"""
        print(f"\n🔍 {model_display_name} 性能測定開始...")
        
        model_results = {
            "model": model_name,
            "display_name": model_display_name,
            "quantization": "INT4",
            "responses": [],
            "avg_response_time": 0,
            "avg_tokens_per_sec": 0,
            "memory_usage_mb": 0,
            "gpu_memory_mb": 0
        }
        
        total_response_time = 0
        total_tokens = 0
        
        # GPU メモリ使用量測定開始
        try:
            gpu_before = self.get_gpu_memory()
        except:
            gpu_before = 0
            
        for i, prompt in enumerate(self.test_prompts):
            print(f"  📝 テスト {i+1}/5: {prompt[:50]}...")
            
            start_time = time.time()
            
            try:
                # Ollamaコマンド実行
                cmd = ["ollama", "run", model_name, prompt]
                result = subprocess.run(
                    cmd, 
                    capture_output=True, 
                    text=True, 
                    timeout=120,  # 2分タイムアウト
                    encoding='utf-8'
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if result.returncode == 0:
                    response_text = result.stdout.strip()
                    
                    # トークン数推定（文字数/4の概算）
                    estimated_tokens = len(response_text) / 4
                    tokens_per_sec = estimated_tokens / response_time if response_time > 0 else 0
                    
                    model_results["responses"].append({
                        "prompt": prompt,
                        "response": response_text[:200] + "..." if len(response_text) > 200 else response_text,
                        "response_time": response_time,
                        "estimated_tokens": estimated_tokens,
                        "tokens_per_sec": tokens_per_sec
                    })
                    
                    total_response_time += response_time
                    total_tokens += estimated_tokens
                    
                    print(f"    ✅ 完了: {response_time:.1f}秒, {tokens_per_sec:.1f} tok/s")
                    
                else:
                    print(f"    ❌ エラー: {result.stderr}")
                    
            except subprocess.TimeoutExpired:
                print(f"    ⏰ タイムアウト (120秒)")
            except Exception as e:
                print(f"    ❌ 実行エラー: {e}")
        
        # 平均値計算
        if len(model_results["responses"]) > 0:
            model_results["avg_response_time"] = total_response_time / len(model_results["responses"])
            model_results["avg_tokens_per_sec"] = (total_tokens / total_response_time) if total_response_time > 0 else 0
        
        # メモリ使用量測定
        model_results["memory_usage_mb"] = psutil.virtual_memory().used / (1024**2)
        
        try:
            gpu_after = self.get_gpu_memory()
            model_results["gpu_memory_mb"] = gpu_after
        except:
            model_results["gpu_memory_mb"] = 0
        
        print(f"  📊 {model_display_name} 測定完了:")
        print(f"    - 平均応答時間: {model_results['avg_response_time']:.1f}秒")
        print(f"    - 平均速度: {model_results['avg_tokens_per_sec']:.1f} tok/s")
        print(f"    - GPU メモリ: {model_results['gpu_memory_mb']:.0f}MB")
        
        return model_results
    
    def get_gpu_memory(self):
        """GPU メモリ使用量を取得"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return 0
    
    def run_comparison(self):
        """INT4量子化モデル比較実行"""
        print("🚀 INT4量子化モデル比較分析開始")
        print("=" * 60)
        print("🎯 比較対象:")
        print("  - DeepSeek Coder 6.7B (Q4_0量子化)")
        print("  - Qwen2.5-7B (INT4量子化)")
        print("💻 環境: RTX 4060 Ti 16GB")
        print("-" * 60)
        
        # DeepSeek測定
        deepseek_results = self.measure_model_performance(
            "deepseek-coder:6.7b-instruct-q4_0", 
            "DeepSeek Coder 6.7B (Q4_0)"
        )
        self.results.append(deepseek_results)
        
        # 少し待機（GPU メモリクリア）
        print("\n⏳ GPU メモリクリア中...")
        time.sleep(5)
        
        # Qwen2.5測定
        qwen_results = self.measure_model_performance(
            "qwen2.5:7b",
            "Qwen2.5-7B (INT4)"
        )
        self.results.append(qwen_results)
        
        return self.results
    
    def generate_comparison_report(self):
        """比較レポート生成"""
        if len(self.results) < 2:
            print("❌ 比較に必要なデータが不足しています")
            return
            
        print("\n📊 INT4量子化モデル比較レポート生成中...")
        
        # データフレーム作成
        df_data = []
        for result in self.results:
            df_data.append({
                "Model": result["display_name"],
                "Quantization": result["quantization"],
                "Avg Response Time (s)": result["avg_response_time"],
                "Tokens/sec": result["avg_tokens_per_sec"],
                "GPU Memory (MB)": result["gpu_memory_mb"],
                "RAM Usage (MB)": result["memory_usage_mb"]
            })
        
        df = pd.DataFrame(df_data)
        
        # 結果保存
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        # CSVエクスポート
        csv_path = results_dir / f"int4_quantization_comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ CSV保存完了: {csv_path}")
        
        # JSONエクスポート（詳細データ）
        json_path = results_dir / f"int4_detailed_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON保存完了: {json_path}")
        
        # 比較チャート生成
        self.create_comparison_charts(df, results_dir)
        
        # コンソール出力
        print("\n" + "="*80)
        print("📊 INT4量子化モデル比較結果サマリー")
        print("="*80)
        print(df.to_string(index=False))
        print("\n🏆 パフォーマンス分析:")
        
        # 速度比較
        fastest_model = df.loc[df['Tokens/sec'].idxmax(), 'Model']
        print(f"  ⚡ 最高速度: {fastest_model}")
        
        # メモリ効率比較
        most_efficient = df.loc[df['GPU Memory (MB)'].idxmin(), 'Model']
        print(f"  💾 最小GPU使用: {most_efficient}")
        
        # 応答時間比較
        fastest_response = df.loc[df['Avg Response Time (s)'].idxmin(), 'Model']
        print(f"  🚀 最短応答: {fastest_response}")
        
        return df
    
    def create_comparison_charts(self, df, output_dir):
        """比較チャート作成"""
        print("📈 比較チャート作成中...")
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('INT4量子化モデル比較分析', fontsize=16, fontweight='bold')
        
        # 1. トークン生成速度
        ax1.bar(df['Model'], df['Tokens/sec'], color=['#ff7f0e', '#1f77b4'])
        ax1.set_title('トークン生成速度 (tokens/sec)')
        ax1.set_ylabel('Tokens/sec')
        ax1.tick_params(axis='x', rotation=45)
        
        # 2. GPU メモリ使用量
        ax2.bar(df['Model'], df['GPU Memory (MB)'], color=['#2ca02c', '#d62728'])
        ax2.set_title('GPU メモリ使用量 (MB)')
        ax2.set_ylabel('Memory (MB)')
        ax2.tick_params(axis='x', rotation=45)
        
        # 3. 平均応答時間
        ax3.bar(df['Model'], df['Avg Response Time (s)'], color=['#9467bd', '#8c564b'])
        ax3.set_title('平均応答時間 (秒)')
        ax3.set_ylabel('Response Time (s)')
        ax3.tick_params(axis='x', rotation=45)
        
        # 4. 効率比較（速度/メモリ）
        efficiency = df['Tokens/sec'] / (df['GPU Memory (MB)'] / 1000)  # tokens per sec per GB
        ax4.bar(df['Model'], efficiency, color=['#17becf', '#bcbd22'])
        ax4.set_title('効率性 (tok/s per GB GPU)')
        ax4.set_ylabel('Efficiency')
        ax4.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # チャート保存
        chart_path = output_dir / f"int4_comparison_charts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"✅ チャート保存完了: {chart_path}")
        
        plt.show()

def main():
    print("🌟 INT4量子化モデル比較分析ツール")
    print("🎯 DeepSeek V3 Q4_0 vs Qwen2.5-7B INT4")
    print("-" * 60)
    
    # 前提条件確認
    print("🔍 前提条件確認中...")
    
    # Ollama起動確認
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Ollamaが起動していません")
            return
        print("✅ Ollama動作確認")
    except:
        print("❌ Ollamaが見つかりません")
        return
    
    # GPU確認
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ GPU動作確認")
        else:
            print("⚠️ GPU確認失敗 - CPU実行になる可能性があります")
    except:
        print("⚠️ nvidia-smiが見つかりません")
    
    print("-" * 60)
    
    # 比較分析実行
    comparator = INT4QuantizationComparison()
    results = comparator.run_comparison()
    
    if results:
        df = comparator.generate_comparison_report()
        
        print("\n🎉 INT4量子化比較分析完了！")
        print("📁 結果ファイルはresultsフォルダに保存されました。")
        print("\n💡 次のステップ:")
        print("  - 結果をGitHubリポジトリに追加")
        print("  - README.mdに比較結果を統合")
        print("  - 論文やブログ記事での活用")
    else:
        print("❌ 比較分析に失敗しました")

if __name__ == "__main__":
    main()