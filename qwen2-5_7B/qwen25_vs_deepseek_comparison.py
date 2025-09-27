#!/usr/bin/env python3
"""
Qwen2.5-7B vs DeepSeek V3 性能比較分析
量子化レベル別パフォーマンス・品質評価
"""

import subprocess
import time
import psutil
import json
import os
from datetime import datetime
from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd

class Qwen25vsDeepSeekComparison:
    def __init__(self):
        self.results = []
        self.test_prompts = [
            {
                "category": "プログラミング",
                "prompt": "Pythonでフィボナッチ数列を生成する効率的な方法を3つ説明してください。再帰、反復、ジェネレータの違いも含めて。",
                "expected_elements": ["再帰", "反復", "ジェネレータ", "効率性"]
            },
            {
                "category": "技術解説", 
                "prompt": "Transformerアーキテクチャにおけるself-attentionメカニズムの動作原理を、数式を使わずに分かりやすく説明してください。",
                "expected_elements": ["self-attention", "Query", "Key", "Value", "重み"]
            },
            {
                "category": "問題解決",
                "prompt": "16GB GPUで7Bパラメータのモデルを効率的に実行するための最適化戦略を5つ提案してください。",
                "expected_elements": ["量子化", "バッチサイズ", "勾配蓄積", "混合精度", "メモリ効率"]
            },
            {
                "category": "日本語理解",
                "prompt": "「量子化」という用語が、物理学、機械学習、デジタル信号処理でそれぞれ異なる意味を持つことを説明してください。",
                "expected_elements": ["物理学", "機械学習", "信号処理", "離散化", "精度"]
            },
            {
                "category": "創造的思考",
                "prompt": "AIモデルの性能評価において、単純な精度指標だけでは不十分な理由と、より包括的な評価方法を提案してください。",
                "expected_elements": ["バイアス", "公平性", "解釈可能性", "ロバスト性", "効率性"]
            }
        ]
        
        # テスト対象モデル
        self.models = [
            {
                "name": "deepseek-coder:6.7b-instruct-q4_0",
                "display_name": "DeepSeek Coder 6.7B (Q4_0)",
                "quantization": "Q4_0",
                "expected_vram": "3.8GB"
            },
            {
                "name": "deepseek-coder:6.7b-instruct-q8_0", 
                "display_name": "DeepSeek Coder 6.7B (Q8_0)",
                "quantization": "Q8_0",
                "expected_vram": "7.2GB"
            },
            {
                "name": "qwen2.5:7b",
                "display_name": "Qwen2.5-7B (Default)",
                "quantization": "Default",
                "expected_vram": "4-6GB"
            }
        ]

    def get_gpu_memory(self):
        """GPU メモリ使用量を取得"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if result.returncode == 0:
                return int(result.stdout.strip())
        except:
            pass
        return 0

    def measure_model_performance(self, model_config):
        """個別モデルの性能測定"""
        model_name = model_config["name"]
        display_name = model_config["display_name"]
        
        print(f"\n🔍 {display_name} 性能測定開始...")
        print(f"   量子化: {model_config['quantization']}")
        print(f"   予想VRAM: {model_config['expected_vram']}")
        
        model_results = {
            "model": model_name,
            "display_name": display_name,
            "quantization": model_config["quantization"],
            "expected_vram": model_config["expected_vram"],
            "test_results": [],
            "avg_response_time": 0,
            "avg_tokens_per_sec": 0,
            "total_tokens": 0,
            "gpu_memory_mb": 0,
            "quality_score": 0
        }
        
        total_response_time = 0
        total_tokens = 0
        successful_tests = 0
        total_quality_score = 0
        
        # GPU メモリ測定
        gpu_before = self.get_gpu_memory()
        
        for i, test_case in enumerate(self.test_prompts):
            print(f"  📝 {test_case['category']} テスト ({i+1}/5)")
            print(f"     プロンプト: {test_case['prompt'][:80]}...")
            
            start_time = time.time()
            
            try:
                # Ollamaでモデル実行
                cmd = ["ollama", "run", model_name, test_case["prompt"]]
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=180,  # 3分タイムアウト
                    encoding='utf-8'
                )
                
                end_time = time.time()
                response_time = end_time - start_time
                
                if result.returncode == 0:
                    response_text = result.stdout.strip()
                    
                    # トークン数推定（日本語・英語混在対応）
                    estimated_tokens = len(response_text) / 3.5  # 日本語調整
                    tokens_per_sec = estimated_tokens / response_time if response_time > 0 else 0
                    
                    # 品質評価（キーワード含有率）
                    quality_score = self.evaluate_response_quality(response_text, test_case["expected_elements"])
                    
                    test_result = {
                        "category": test_case["category"],
                        "prompt": test_case["prompt"][:100] + "...",
                        "response": response_text[:300] + "..." if len(response_text) > 300 else response_text,
                        "response_time": response_time,
                        "estimated_tokens": estimated_tokens,
                        "tokens_per_sec": tokens_per_sec,
                        "quality_score": quality_score
                    }
                    
                    model_results["test_results"].append(test_result)
                    
                    total_response_time += response_time
                    total_tokens += estimated_tokens
                    total_quality_score += quality_score
                    successful_tests += 1
                    
                    print(f"     ✅ 完了: {response_time:.1f}秒, {tokens_per_sec:.1f} tok/s, 品質: {quality_score:.2f}")
                    
                else:
                    print(f"     ❌ エラー: {result.stderr[:100]}")
                    
            except subprocess.TimeoutExpired:
                print(f"     ⏰ タイムアウト (180秒)")
            except Exception as e:
                print(f"     ❌ 実行エラー: {str(e)[:100]}")
        
        # 統計計算
        if successful_tests > 0:
            model_results["avg_response_time"] = total_response_time / successful_tests
            model_results["avg_tokens_per_sec"] = total_tokens / total_response_time if total_response_time > 0 else 0
            model_results["total_tokens"] = total_tokens
            model_results["quality_score"] = total_quality_score / successful_tests
        
        # GPU メモリ測定
        gpu_after = self.get_gpu_memory()
        model_results["gpu_memory_mb"] = max(gpu_after - gpu_before, gpu_after)
        
        print(f"  📊 {display_name} 測定完了:")
        print(f"     平均応答時間: {model_results['avg_response_time']:.1f}秒")
        print(f"     平均速度: {model_results['avg_tokens_per_sec']:.1f} tok/s")
        print(f"     品質スコア: {model_results['quality_score']:.2f}/1.0")
        print(f"     GPU使用: {model_results['gpu_memory_mb']:.0f}MB")
        
        return model_results

    def evaluate_response_quality(self, response, expected_elements):
        """応答品質を評価（キーワード含有率）"""
        response_lower = response.lower()
        found_elements = 0
        
        for element in expected_elements:
            if element.lower() in response_lower:
                found_elements += 1
        
        return found_elements / len(expected_elements)

    def run_comprehensive_comparison(self):
        """包括的比較分析実行"""
        print("🚀 Qwen2.5-7B vs DeepSeek V3 包括的比較開始")
        print("=" * 70)
        print("🎯 比較対象:")
        for model in self.models:
            print(f"   - {model['display_name']} ({model['quantization']})")
        print("💻 環境: RTX 4060 Ti 16GB")
        print("📊 評価項目: 速度、メモリ効率、応答品質")
        print("-" * 70)
        
        # 各モデルを順次測定
        for i, model_config in enumerate(self.models):
            if i > 0:
                print(f"\n⏳ GPU メモリクリア中...")
                time.sleep(10)  # GPUメモリクリア待機
            
            model_results = self.measure_model_performance(model_config)
            self.results.append(model_results)
        
        return self.results

    def generate_comprehensive_report(self):
        """包括的比較レポート生成"""
        if len(self.results) < 2:
            print("❌ 比較に必要なデータが不足しています")
            return None
            
        print("\n📊 包括的比較レポート生成中...")
        
        # 結果ディレクトリ作成
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)
        
        # データフレーム作成
        df_data = []
        for result in self.results:
            df_data.append({
                "Model": result["display_name"],
                "Quantization": result["quantization"], 
                "Avg Response Time (s)": result["avg_response_time"],
                "Tokens/sec": result["avg_tokens_per_sec"],
                "Quality Score": result["quality_score"],
                "GPU Memory (MB)": result["gpu_memory_mb"],
                "Total Tokens": result["total_tokens"],
                "Expected VRAM": result["expected_vram"]
            })
        
        df = pd.DataFrame(df_data)
        
        # 効率性指標追加
        df["Efficiency (tok/s per GB)"] = df["Tokens/sec"] / (df["GPU Memory (MB)"] / 1000)
        df["Quality-Speed Balance"] = df["Quality Score"] * df["Tokens/sec"] / 10
        
        # ファイル出力
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # CSV保存
        csv_path = results_dir / f"qwen25_vs_deepseek_comparison_{timestamp}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8')
        print(f"✅ CSV保存: {csv_path}")
        
        # 詳細JSON保存
        json_path = results_dir / f"qwen25_vs_deepseek_detailed_{timestamp}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)
        print(f"✅ JSON保存: {json_path}")
        
        # 比較チャート生成
        self.create_comprehensive_charts(df, results_dir, timestamp)
        
        # コンソール出力
        print("\n" + "="*90)
        print("📊 Qwen2.5-7B vs DeepSeek V3 比較結果")
        print("="*90)
        print(df.to_string(index=False, float_format='%.2f'))
        
        print("\n🏆 パフォーマンス順位:")
        
        # 速度ランキング
        speed_ranking = df.nlargest(3, 'Tokens/sec')[['Model', 'Tokens/sec']]
        print("\n⚡ トークン生成速度:")
        for i, (_, row) in enumerate(speed_ranking.iterrows(), 1):
            print(f"   {i}位: {row['Model']} - {row['Tokens/sec']:.1f} tok/s")
        
        # 品質ランキング
        quality_ranking = df.nlargest(3, 'Quality Score')[['Model', 'Quality Score']]
        print("\n🎯 応答品質:")
        for i, (_, row) in enumerate(quality_ranking.iterrows(), 1):
            print(f"   {i}位: {row['Model']} - {row['Quality Score']:.2f}/1.0")
        
        # 効率性ランキング
        efficiency_ranking = df.nlargest(3, 'Efficiency (tok/s per GB)')[['Model', 'Efficiency (tok/s per GB)']]
        print("\n💎 メモリ効率:")
        for i, (_, row) in enumerate(efficiency_ranking.iterrows(), 1):
            print(f"   {i}位: {row['Model']} - {row['Efficiency (tok/s per GB)']:.1f} tok/s/GB")
        
        # 総合バランス
        balance_ranking = df.nlargest(3, 'Quality-Speed Balance')[['Model', 'Quality-Speed Balance']]
        print("\n⚖️ 品質・速度バランス:")
        for i, (_, row) in enumerate(balance_ranking.iterrows(), 1):
            print(f"   {i}位: {row['Model']} - {row['Quality-Speed Balance']:.1f}")
        
        return df

    def create_comprehensive_charts(self, df, output_dir, timestamp):
        """包括的比較チャート作成"""
        print("📈 包括的比較チャート作成中...")
        
        # 日本語フォント設定
        plt.rcParams['font.family'] = ['DejaVu Sans', 'Hiragino Sans', 'Yu Gothic', 'Meiryo', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('Qwen2.5-7B vs DeepSeek V3 包括的性能比較', fontsize=16, fontweight='bold')
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
        
        # 1. トークン生成速度
        bars1 = ax1.bar(range(len(df)), df['Tokens/sec'], color=colors[:len(df)])
        ax1.set_title('トークン生成速度 (tokens/sec)')
        ax1.set_ylabel('Tokens/sec')
        ax1.set_xticks(range(len(df)))
        ax1.set_xticklabels(df['Model'], rotation=45, ha='right')
        
        # 数値ラベル追加
        for i, bar in enumerate(bars1):
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}', ha='center', va='bottom')
        
        # 2. 応答品質スコア
        bars2 = ax2.bar(range(len(df)), df['Quality Score'], color=colors[:len(df)])
        ax2.set_title('応答品質スコア (0-1)')
        ax2.set_ylabel('Quality Score')
        ax2.set_xticks(range(len(df)))
        ax2.set_xticklabels(df['Model'], rotation=45, ha='right')
        ax2.set_ylim(0, 1)
        
        for i, bar in enumerate(bars2):
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.2f}', ha='center', va='bottom')
        
        # 3. GPU メモリ使用量
        bars3 = ax3.bar(range(len(df)), df['GPU Memory (MB)'], color=colors[:len(df)])
        ax3.set_title('GPU メモリ使用量 (MB)')
        ax3.set_ylabel('Memory (MB)')
        ax3.set_xticks(range(len(df)))
        ax3.set_xticklabels(df['Model'], rotation=45, ha='right')
        
        for i, bar in enumerate(bars3):
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 50,
                    f'{height:.0f}', ha='center', va='bottom')
        
        # 4. 効率性（tok/s per GB）
        bars4 = ax4.bar(range(len(df)), df['Efficiency (tok/s per GB)'], color=colors[:len(df)])
        ax4.set_title('メモリ効率性 (tok/s per GB)')
        ax4.set_ylabel('Efficiency (tok/s/GB)')
        ax4.set_xticks(range(len(df)))
        ax4.set_xticklabels(df['Model'], rotation=45, ha='right')
        
        for i, bar in enumerate(bars4):
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        
        # チャート保存
        chart_path = output_dir / f"qwen25_vs_deepseek_charts_{timestamp}.png"
        plt.savefig(chart_path, dpi=300, bbox_inches='tight')
        print(f"✅ チャート保存: {chart_path}")
        
        # 表示
        plt.show()

def main():
    print("🌟 Qwen2.5-7B vs DeepSeek V3 包括的性能比較ツール")
    print("-" * 70)
    
    # 前提条件確認
    print("🔍 前提条件確認中...")
    
    # Ollama確認
    try:
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ Ollamaが起動していません")
            return
        print("✅ Ollama動作確認")
        
        # 必要なモデルの確認
        model_list = result.stdout
        required_models = ["deepseek-coder:6.7b-instruct-q4_0", "deepseek-coder:6.7b-instruct-q8_0", "qwen2.5:7b"]
        missing_models = []
        
        for model in required_models:
            if model not in model_list:
                missing_models.append(model)
        
        if missing_models:
            print(f"⚠️ 不足モデル: {', '.join(missing_models)}")
            print("続行しますか？ (不足モデルはスキップされます)")
        else:
            print("✅ 必要モデル確認完了")
            
    except Exception as e:
        print(f"❌ Ollama確認エラー: {e}")
        return
    
    # GPU確認
    try:
        result = subprocess.run(["nvidia-smi"], capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ GPU動作確認")
        else:
            print("⚠️ GPU確認失敗")
    except:
        print("⚠️ nvidia-smiが見つかりません")
    
    print("-" * 70)
    
    # 比較分析実行
    comparator = Qwen25vsDeepSeekComparison()
    results = comparator.run_comprehensive_comparison()
    
    if results:
        df = comparator.generate_comprehensive_report()
        
        print(f"\n🎉 包括的比較分析完了！")
        print(f"📁 結果ファイルは results/ フォルダに保存されました")
        print(f"\n💡 次のステップ:")
        print(f"   - GitHub リポジトリに結果を追加")
        print(f"   - README.md に比較結果セクションを追加")
        print(f"   - 技術ブログや論文での活用")
    else:
        print("❌ 比較分析に失敗しました")

if __name__ == "__main__":
    main()