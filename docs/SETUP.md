# セットアップガイド

## 🛠️ システム要件

### 必須要件
- **GPU**: NVIDIA GPU 16GB以上（RTX 4060 Ti, RTX 4080, A4000等）
- **CPU**: Intel i7 / AMD Ryzen 7 以上
- **RAM**: 16GB以上
- **ストレージ**: 20GB以上の空き容量（モデル + データ）
- **OS**: Windows 10/11 64-bit

### ソフトウェア要件
- **Python**: 3.8以降
- **CUDA**: 11.8以降（nvidia-smi動作確認済み）
- **Git**: バージョン管理用

---

## 📥 インストール手順

### 1. リポジトリのクローン
```powershell
git clone https://github.com/[USERNAME]/takato-llm-quantization-benchmark.git
cd takato-llm-quantization-benchmark
```

### 2. Python環境構築
```powershell
# 仮想環境作成
python -m venv venv

# 仮想環境アクティベート
venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt
```

### 3. Ollamaのインストール
```powershell
# Windows Package Manager使用
winget install Ollama.Ollama

# または手動ダウンロード
# https://ollama.ai/download/windows からインストーラー取得
```

### 4. DeepSeek V3モデルのダウンロード
```powershell
# Q4_0量子化版（約3.8GB）
ollama pull deepseek-coder:6.7b-instruct-q4_0

# Q8_0量子化版（約7.2GB）
ollama pull deepseek-coder:6.7b-instruct-q8_0
```

### 5. GPU設定の確認
```powershell
# CUDA動作確認
nvidia-smi

# Ollama GPU認識確認
$env:CUDA_VISIBLE_DEVICES = "0"
ollama run deepseek-coder:6.7b-instruct-q4_0 "Hello, GPU test"
```

---

## 🧪 動作確認

### クイックテスト
```powershell
# 基本動作確認（約3分）
python scripts/deepseek_quick_test.py
```

期待される出力：
```
🚀 DeepSeek V3 クイックテスト開始
✅ DeepSeek V3 モデル利用可能
✅ 成功 (3000-5000ms, 10-15 tok/s)
👍 良好: DeepSeek V3は実用的な性能で動作中
```

### GPU使用量確認
```powershell
nvidia-smi
```

期待される出力：
```
|  0  NVIDIA GeForce RTX 4060 Ti   |  6000-12000MiB/16380MiB |
|    ollama.exe                    |             GPU Memory |
```

---

## 🔧 トラブルシューティング

### GPU未認識の場合
```powershell
# Ollamaプロセス再起動
taskkill /IM ollama.exe /F
$env:CUDA_VISIBLE_DEVICES = "0"
ollama serve
```

### モデルダウンロード失敗
```powershell
# ネットワーク確認後再試行
ollama pull deepseek-coder:6.7b-instruct-q4_0 --insecure
```

### Python依存関係エラー
```powershell
# 仮想環境再作成
rmdir /s venv
python -m venv venv
venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

### メモリ不足エラー
- 他のアプリケーションを終了
- Q8_0の代わりにQ4_0のみ使用
- バッチサイズを削減

---

## ⚡ 自動セットアップ（Windows）

### setup.bat実行
```powershell
# 管理者権限で実行
setup.bat
```

自動で実行される内容：
1. Python仮想環境作成
2. 依存関係インストール
3. Ollamaインストール確認
4. GPU動作テスト
5. モデルダウンロード

---

## 📊 ベンチマーク実行

### 完全比較テスト
```powershell
# 量子化比較実行（約15分）
python scripts/quantization_comparison.py
```

### 結果確認
```powershell
# CSVデータ確認
type results\quantization_comparison_log.csv

# 詳細レポート確認
notepad results\quantization_evaluation.md
```

---

## 🔍 設定の最適化

### GPU最適化
```powershell
# 環境変数設定
$env:OLLAMA_NUM_PARALLEL = "1"
$env:CUDA_VISIBLE_DEVICES = "0"
```

### メモリ最適化
- Q4_0: 日常利用・並行処理
- Q8_0: 単一タスク・高品質要求

---

## 📞 サポート・FAQ

### よくある質問

**Q: 16GB未満のGPUでも動作しますか？**
A: Q4_0は8GB GPUでも動作可能ですが、Q8_0は困難です。

**Q: AMD GPUは対応していますか？**  
A: 現在NVIDIA CUDA専用です。ROCm対応は今後検討予定。

**Q: 商用利用は可能ですか？**
A: MITライセンスにより商用利用可能です。

### コミュニティ
- GitHub Issues: バグ報告・機能要望
- Discussions: 質問・議論
- Wiki: 詳細文書・FAQ

---

**次のステップ**: [実験実行ガイド](../README_GITHUB.md#🚀-クイックスタート)