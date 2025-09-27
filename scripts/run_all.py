#!/usr/bin/env python3
"""
全自動実行スクリプト - 量子化比較からGitHub準備まで
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def check_q8_model():
    """Q8_0モデルの存在確認"""
    print("🔍 Q8_0モデルの確認中...")
    result = subprocess.run(
        ["ollama", "list"],
        capture_output=True, text=True, encoding="utf-8"
    )
    
    if "deepseek-coder:6.7b-instruct-q8_0" in result.stdout:
        print("✅ Q8_0モデル準備完了")
        return True
    else:
        print("❌ Q8_0モデルが見つかりません")
        print("まだダウンロード中の可能性があります")
        return False

def run_quantization_comparison():
    """量子化比較を実行"""
    print("\n📊 量子化比較実行中...")
    
    script_path = Path("scripts/quantization_comparison.py")
    if not script_path.exists():
        print(f"❌ スクリプトが見つかりません: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True, capture_output=False
        )
        print("✅ 量子化比較完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ 量子化比較エラー: {e}")
        return False

def generate_github_report():
    """GitHub用レポート生成"""
    print("\n📝 GitHub用レポート生成中...")
    
    script_path = Path("scripts/generate_github_report.py")
    if not script_path.exists():
        print(f"❌ スクリプトが見つかりません: {script_path}")
        return False
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True, capture_output=False
        )
        print("✅ GitHub用レポート生成完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ レポート生成エラー: {e}")
        return False

def main():
    print("🚀 全自動実行開始: 量子化比較 → GitHub準備")
    print("=" * 50)
    
    # 作業ディレクトリ確認
    if not Path("scripts").exists():
        print("❌ scriptsディレクトリが見つかりません")
        print("takato-llm-comparisonディレクトリで実行してください")
        return
    
    # 必要なパッケージ確認
    try:
        import matplotlib.pyplot as plt
        import pandas as pd
    except ImportError:
        print("❌ 必要なパッケージが不足しています")
        print("pip install matplotlib pandas")
        return
    
    # Q8_0モデル確認
    if not check_q8_model():
        print("\n⏳ Q8_0モデルのダウンロード完了を待機中...")
        print("ダウンロードが完了したら再度実行してください")
        return
    
    # 量子化比較実行
    if not run_quantization_comparison():
        print("❌ 量子化比較に失敗しました")
        return
    
    # GitHub用レポート生成
    if not generate_github_report():
        print("❌ GitHub用レポート生成に失敗しました")
        return
    
    # 最終確認
    print("\n" + "=" * 50)
    print("🎉 全自動実行完了!")
    print("\nGitHub準備完了ファイル:")
    
    files_to_check = [
        "results/RESULTS.md",
        "results/performance_charts.png",
        "results/quantization_comparison_log.csv",
        "README_GITHUB.md",
        "LICENSE",
        "docs/SETUP.md"
    ]
    
    for file_path in files_to_check:
        if Path(file_path).exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
    
    print("\n次のステップ:")
    print("1. git init")
    print("2. git add .")
    print("3. git commit -m 'Initial commit: DeepSeek V3 quantization comparison'")
    print("4. GitHub上でリポジトリ作成")
    print("5. git remote add origin <your-repo-url>")
    print("6. git push -u origin main")

if __name__ == "__main__":
    main()