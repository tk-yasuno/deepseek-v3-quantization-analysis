#!/usr/bin/env python3
"""
GitHub用レポート生成スクリプト
量子化比較結果をMarkdown形式でGitHub表示用に整形
"""

import csv
import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
from pathlib import Path

# 日本語フォント設定（文字化け対策）
import matplotlib
matplotlib.rcParams['font.family'] = ['DejaVu Sans', 'Yu Gothic', 'Hiragino Sans', 'Takao', 'IPAexGothic', 'IPAPGothic', 'VL PGothic', 'Noto Sans CJK JP']
plt.rcParams['font.size'] = 10
plt.rcParams['axes.unicode_minus'] = False  # マイナス記号の文字化け対策

class GitHubReportGenerator:
    def __init__(self):
        self.results_dir = Path("results")
        self.csv_file = self.results_dir / "quantization_comparison_log.csv"
        self.github_results = self.results_dir / "RESULTS.md"
        
    def load_csv_data(self):
        """CSVデータを読み込み"""
        if not self.csv_file.exists():
            print("❌ 比較結果CSVファイルが見つかりません")
            print("まず python scripts/quantization_comparison.py を実行してください")
            return None
            
        try:
            df = pd.read_csv(self.csv_file)
            return df
        except Exception as e:
            print(f"❌ CSVファイル読み込みエラー: {e}")
            return None
    
    def generate_performance_chart(self, df):
        """性能比較チャートを生成"""
        try:
            # 成功したデータのみフィルタ
            success_data = df[df['success'] == True]
            
            if success_data.empty:
                print("⚠️ 成功したテストデータが見つかりません")
                return False
            
            # 量子化別に平均値を計算（FP16, Q8_0, Q4_0）
            fp16_data = success_data[success_data['quantization'] == 'FP16'] if 'FP16' in success_data['quantization'].values else None
            q8_data = success_data[success_data['quantization'] == 'Q8_0']
            q4_data = success_data[success_data['quantization'] == 'Q4_0']
            
            quantizations = success_data['quantization'].unique()
            num_quants = len(quantizations)
            
            fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
            title = f'DeepSeek V3 Quantization Comparison ({", ".join(sorted(quantizations))})'
            fig.suptitle(title, fontsize=16, fontweight='bold')
            
            # Color mapping for different quantizations
            color_map = {'FP16': '#2E8B57', 'Q8_0': '#4169E1', 'Q4_0': '#DC143C'}
            colors = [color_map.get(q, '#808080') for q in sorted(quantizations)]
            
            # 1. Inference Speed Comparison
            categories = sorted(success_data['category'].unique())
            x_pos = range(len(categories))
            width = 0.8 / num_quants
            
            for i, quant in enumerate(sorted(quantizations)):
                quant_data = success_data[success_data['quantization'] == quant]
                speeds = [quant_data[quant_data['category'] == cat]['tokens_per_second'].mean() for cat in categories]
                offset = (i - (num_quants - 1) / 2) * width
                ax1.bar([p + offset for p in x_pos], speeds, width, 
                       label=quant, color=color_map.get(quant, '#808080'))
            
            ax1.set_xlabel('Category')
            ax1.set_ylabel('Tokens per Second')
            ax1.set_title('Inference Speed Comparison')
            ax1.set_xticks(x_pos)
            ax1.set_xticklabels(categories, rotation=45)
            ax1.legend()
            
            # 2. GPU Memory Usage Comparison
            for i, quant in enumerate(sorted(quantizations)):
                quant_data = success_data[success_data['quantization'] == quant]
                gpu_usage = [quant_data[quant_data['category'] == cat]['gpu_memory_used_mb'].mean() for cat in categories]
                offset = (i - (num_quants - 1) / 2) * width
                ax2.bar([p + offset for p in x_pos], gpu_usage, width, 
                       label=quant, color=color_map.get(quant, '#808080'))
            
            ax2.set_xlabel('Category')
            ax2.set_ylabel('GPU Memory Usage (MB)')
            ax2.set_title('GPU Memory Usage Comparison')
            ax2.set_xticks(x_pos)
            ax2.set_xticklabels(categories, rotation=45)
            ax2.legend()
            
            # 3. Response Time Comparison
            for i, quant in enumerate(sorted(quantizations)):
                quant_data = success_data[success_data['quantization'] == quant]
                latencies = [quant_data[quant_data['category'] == cat]['latency_ms'].mean() for cat in categories]
                offset = (i - (num_quants - 1) / 2) * width
                ax3.bar([p + offset for p in x_pos], latencies, width, 
                       label=quant, color=color_map.get(quant, '#808080'))
            
            ax3.set_xlabel('Category')
            ax3.set_ylabel('Response Time (ms)')
            ax3.set_title('Response Time Comparison')
            ax3.set_xticks(x_pos)
            ax3.set_xticklabels(categories, rotation=45)
            ax3.legend()
            
            # 4. Token Count Comparison
            for i, quant in enumerate(sorted(quantizations)):
                quant_data = success_data[success_data['quantization'] == quant]
                tokens = [quant_data[quant_data['category'] == cat]['token_count'].mean() for cat in categories]
                offset = (i - (num_quants - 1) / 2) * width
                ax4.bar([p + offset for p in x_pos], tokens, width, 
                       label=quant, color=color_map.get(quant, '#808080'))
            
            ax4.set_xlabel('Category')
            ax4.set_ylabel('Token Count')
            ax4.set_title('Response Token Count Comparison')
            ax4.set_xticks(x_pos)
            ax4.set_xticklabels(categories, rotation=45)
            ax4.legend()
            
            plt.tight_layout()
            chart_path = self.results_dir / "performance_charts.png"
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"✅ Performance chart generated: {chart_path}")
            return True
            
        except Exception as e:
            print(f"❌ Chart generation error: {e}")
            return False
    
    def generate_github_report(self, df):
        """GitHub用詳細レポートを生成"""
        try:
            success_data = df[df['success'] == True]
            
            with open(self.github_results, "w", encoding="utf-8") as f:
                f.write("# DeepSeek V3 Quantization Comparison Results\n\n")
                f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                # Executive Summary
                f.write("## 🎯 Executive Summary\n\n")
                
                if not success_data.empty:
                    quantizations = success_data['quantization'].unique()
                    quant_stats = {}
                    
                    # Calculate average performance for each quantization
                    for quant in quantizations:
                        data = success_data[success_data['quantization'] == quant]
                        quant_stats[quant] = {
                            'speed': data['tokens_per_second'].mean(),
                            'gpu': data['gpu_memory_used_mb'].mean()
                        }
                    
                    f.write(f"### Key Findings\n")
                    for quant in sorted(quantizations):
                        stats = quant_stats[quant]
                        f.write(f"- **{quant}**: {stats['speed']:.1f} tok/s average, {stats['gpu']:.0f}MB GPU usage\n")
                    
                    # Performance comparisons
                    if 'Q4_0' in quant_stats and 'Q8_0' in quant_stats:
                        q4_speed = quant_stats['Q4_0']['speed']
                        q8_speed = quant_stats['Q8_0']['speed']
                        q4_gpu = quant_stats['Q4_0']['gpu']
                        q8_gpu = quant_stats['Q8_0']['gpu']
                        f.write(f"- **Q4_0 vs Q8_0**: {((q4_speed/q8_speed-1)*100):.1f}% speed improvement, {((q8_gpu-q4_gpu)/q8_gpu*100):.1f}% memory reduction\n")
                    
                    if 'FP16' in quant_stats and 'Q4_0' in quant_stats:
                        fp16_speed = quant_stats['FP16']['speed']  
                        fp16_gpu = quant_stats['FP16']['gpu']
                        q4_speed = quant_stats['Q4_0']['speed']
                        q4_gpu = quant_stats['Q4_0']['gpu']
                        f.write(f"- **Q4_0 vs FP16**: {((q4_speed/fp16_speed-1)*100):.1f}% speed change, {((fp16_gpu-q4_gpu)/fp16_gpu*100):.1f}% memory reduction\n")
                    
                    f.write("\n")
                
                # Performance comparison table
                f.write("## 📊 Detailed Performance Data\n\n")
                f.write("### Category-wise Comparison\n\n")
                
                if not success_data.empty:
                    # Calculate average values by quantization and category
                    pivot_speed = success_data.pivot_table(
                        values='tokens_per_second', 
                        index='category', 
                        columns='quantization', 
                        aggfunc='mean'
                    ).round(1)
                    
                    pivot_gpu = success_data.pivot_table(
                        values='gpu_memory_used_mb', 
                        index='category', 
                        columns='quantization', 
                        aggfunc='mean'
                    ).round(0)
                    
                    # Dynamic header based on available quantizations
                    quantizations = sorted(pivot_speed.columns)
                    header = "| Category |"
                    divider = "|----------|"
                    
                    for quant in quantizations:
                        header += f" {quant} Speed | {quant} GPU |"
                        divider += "------------|-----------|"
                    
                    f.write(header + "\n")
                    f.write(divider + "\n")
                    
                    for category in pivot_speed.index:
                        row = f"| {category} |"
                        for quant in quantizations:
                            speed = pivot_speed.loc[category, quant] if quant in pivot_speed.columns else 0
                            gpu = int(pivot_gpu.loc[category, quant]) if quant in pivot_gpu.columns else 0
                            row += f" {speed:.1f} tok/s | {gpu}MB |"
                        f.write(row + "\n")
                
                f.write("\n")
                
                # Chart
                f.write("### Performance Comparison Chart\n\n")
                f.write("![Performance Comparison](performance_charts.png)\n\n")
                
                # Recommendations
                f.write("## 💡 Practical Recommendations\n\n")
                
                # Conditional recommendations based on available quantizations
                quantizations = success_data['quantization'].unique()
                
                if 'FP16' in quantizations:
                    f.write("### FP16 (Full Precision) Recommended Use Cases\n")
                    f.write("- ✅ Maximum quality requirements\n")
                    f.write("- ✅ Research & academic work\n")
                    f.write("- ✅ Production-critical applications\n")
                    f.write("- ✅ When GPU memory is abundant (>12GB)\n\n")
                
                if 'Q8_0' in quantizations:
                    f.write("### Q8_0 Recommended Use Cases\n")
                    f.write("- ✅ High-quality code generation & review\n")
                    f.write("- ✅ Technical documentation writing\n")
                    f.write("- ✅ Balance between quality and efficiency\n")
                    f.write("- ✅ Medium GPU memory systems (8-12GB)\n\n")
                
                if 'Q4_0' in quantizations:
                    f.write("### Q4_0 Recommended Use Cases\n")
                    f.write("- ✅ Daily development & learning assistance\n")
                    f.write("- ✅ Fast iterative tasks\n") 
                    f.write("- ✅ Multi-application concurrent usage\n")
                    f.write("- ✅ Lower GPU memory systems (6-8GB)\n\n")
                
                # Data Quality & Statistics
                f.write("## 📈 Data Quality & Statistics\n\n")
                
                total_tests = len(df)
                success_tests = len(success_data)
                success_rate = (success_tests / total_tests) * 100 if total_tests > 0 else 0
                
                f.write(f"- **Total Tests**: {total_tests}\n")
                f.write(f"- **Successful Tests**: {success_tests}\n")
                f.write(f"- **Success Rate**: {success_rate:.1f}%\n")
                f.write(f"- **Test Categories**: {len(success_data['category'].unique())} types\n\n")
                
                # Raw Data Links
                f.write("## 📄 Raw Data\n\n")
                f.write("- [CSV Numerical Data](quantization_comparison_log.csv)\n")
                f.write("- [Detailed Evaluation Report](quantization_evaluation.md)\n\n")
                
                # Experiment Environment
                quantizations = success_data['quantization'].unique()
                f.write("## 🛠️ Experiment Environment\n\n")
                f.write("- **GPU**: NVIDIA GeForce RTX 4060 Ti 16GB\n")
                f.write("- **OS**: Windows 11\n")
                f.write("- **Inference Engine**: Ollama\n")
                f.write(f"- **Quantization Levels**: {', '.join(sorted(quantizations))}\n")
                f.write("- **Model Format**: GGUF\n")
                f.write("- **Measurement Method**: Single execution per test, nvidia-smi monitoring\n\n")
            
            print(f"✅ GitHub report generated: {self.github_results}")
            return True
            
        except Exception as e:
            print(f"❌ Report generation error: {e}")
            return False

def main():
    print("📊 GitHub report generation started...")
    
    generator = GitHubReportGenerator()
    
    # Load CSV data
    df = generator.load_csv_data()
    if df is None:
        return
    
    print(f"✅ CSV data loaded: {len(df)} rows")
    
    # Generate performance chart
    if generator.generate_performance_chart(df):
        print("✅ Performance chart generated")
    
    # Generate GitHub report
    if generator.generate_github_report(df):
        print("✅ GitHub report generated")
    
    print("🎯 All files generated successfully!")
    print("You can now commit and push to GitHub repository.")
    print("Files ready for GitHub:")
    print("  - results/RESULTS.md")
    print("  - results/performance_charts.png") 
    print("  - results/quantization_comparison_log.csv")

if __name__ == "__main__":
    main()