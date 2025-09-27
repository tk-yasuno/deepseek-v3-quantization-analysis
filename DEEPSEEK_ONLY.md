# DeepSeek V3 評価プロジェクト（Takato専用）

## 🎯 プロジェクト目標
外付けGPU 16GB環境でのDeepSeek V3 (6.7B Q4_0) の性能・品質評価

## 🚀 すぐに開始（5分セットアップ）

### Step 1: モデル確認
```powershell
ollama list
# deepseek-coder:6.7b-instruct-q4_0 があることを確認
```

### Step 2: クイックテスト実行
```powershell
cd takato-llm-comparison
python scripts/deepseek_quick_test.py
```

### Step 3: 詳細評価実行
```powershell
python scripts/deepseek_evaluation.py
```

## 📊 評価内容

### テストカテゴリ（6項目）
1. **技術解説** - Transformerアーキテクチャ説明
2. **コード生成** - Webスクレイピングコード作成
3. **問題解決** - データサイエンス課題解決
4. **デバッグ** - Pythonコードエラー修正
5. **アルゴリズム** - バブルソート実装と解説
6. **応用** - クロスバリデーション解説と実装

### 評価指標
- **応答時間** (ms)
- **生成速度** (tokens/sec)
- **GPU使用量** (MB)
- **CPU使用率** (%)
- **品質評価** (5段階)

## 📁 結果ファイル
- `results/deepseek_performance_log.csv` - 数値データ
- `results/deepseek_evaluation.md` - 詳細評価
- `results/output_eval.md` - 総合まとめ

## 🔧 16GB GPU最適化設定
- **量子化**: Q4_0（速度重視）
- **VRAM使用**: 約8-10GB
- **コンテキスト**: 4096トークン
- **並列処理**: 1セッション推奨

## 💡 期待される結果
- **応答速度**: 30-50 tokens/sec
- **成功率**: 85%以上
- **品質**: 技術系タスクで高評価
- **実用性**: プログラミング学習・研究向け

---

**注意**: Kimi K2の比較は技術的問題により中断。DeepSeek V3単体評価に集中。