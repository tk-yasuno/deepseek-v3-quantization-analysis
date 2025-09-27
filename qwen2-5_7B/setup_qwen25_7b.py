#!/usr/bin/env python3
"""
Qwen2.5-7B セットアップスクリプト（16GB GPU環境用）
INT4量子化モデルを使用してOllamaに登録
"""

import os
import subprocess
import requests
from pathlib import Path
import time

class Qwen25Setup:
    def __init__(self):
        self.models_dir = Path("models")
        self.models_dir.mkdir(exist_ok=True)
        self.qwen_dir = self.models_dir / "qwen25"
        self.qwen_dir.mkdir(exist_ok=True)
        
    def download_qwen25_model(self):
        """Qwen2.5-7B GGUFモデル（Q4_K_M）をダウンロード"""
        print("🔄 Qwen2.5-7B モデルをダウンロード中...")
        print("📊 INT4量子化（Q4_K_M）- VRAM約10GB使用予定")
        
        # HuggingFaceからQwen2.5-7B Q4_K_Mモデルを取得
        model_url = "https://huggingface.co/bartowski/Qwen2.5-7B-Instruct-GGUF/resolve/main/Qwen2.5-7B-Instruct-Q4_K_M.gguf"
        model_path = self.qwen_dir / "Qwen2.5-7B-Instruct-Q4_K_M.gguf"
        
        if model_path.exists():
            print(f"✅ モデルは既にダウンロード済み: {model_path}")
            file_size = model_path.stat().st_size / (1024**3)
            print(f"📁 ファイルサイズ: {file_size:.1f}GB")
            return str(model_path)
            
        try:
            print(f"📥 ダウンロード URL: {model_url}")
            print("⏳ ファイルサイズ約4.2GB - 数分かかります...")
            
            response = requests.get(model_url, stream=True)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            start_time = time.time()
            
            with open(model_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size > 0:
                            progress = (downloaded / total_size) * 100
                            elapsed = time.time() - start_time
                            speed = downloaded / (1024**2) / elapsed if elapsed > 0 else 0
                            print(f"\r⏳ ダウンロード進行状況: {progress:.1f}% ({speed:.1f}MB/s)", end='')
                            
            print(f"\n✅ モデルダウンロード完了: {model_path}")
            file_size = model_path.stat().st_size / (1024**3)
            print(f"📁 最終ファイルサイズ: {file_size:.1f}GB")
            return str(model_path)
            
        except Exception as e:
            print(f"❌ モデルダウンロードに失敗: {e}")
            print("💡 代替手段: Ollama直接pullを試行中...")
            return self.try_ollama_pull()
    
    def try_ollama_pull(self):
        """Ollama経由でQwen2.5を直接ダウンロード"""
        try:
            print("🔄 Ollama経由でqwen2.5:7b-instruct-q4_K_Mをダウンロード中...")
            cmd = ["ollama", "pull", "qwen2.5:7b-instruct-q4_K_M"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)  # 30分タイムアウト
            
            if result.returncode == 0:
                print("✅ Ollama経由でダウンロード完了")
                return "qwen2.5:7b-instruct-q4_K_M"
            else:
                print(f"❌ Ollama pullに失敗: {result.stderr}")
                return None
                
        except subprocess.TimeoutExpired:
            print("⏰ Ollama pullがタイムアウトしました")
            return None
        except Exception as e:
            print(f"❌ Ollama pull中にエラー: {e}")
            return None
    
    def create_ollama_modelfile(self, model_path):
        """16GB GPU環境用に最適化されたOllama Modelfileを作成"""
        print("📝 16GB GPU環境用 Ollama Modelfile を作成中...")
        
        # 16GB GPU環境に最適化されたパラメータ
        modelfile_lines = [
            f"FROM {model_path}",
            "",
            "# 16GB GPU環境用最適化パラメータ",
            "PARAMETER num_gpu 35",           # レイヤー数（7Bモデル用）
            "PARAMETER num_ctx 4096",         # コンテキスト長
            "PARAMETER temperature 0.7",     # 創造性のバランス
            "PARAMETER top_p 0.9",           # 語彙選択の多様性
            "PARAMETER top_k 40",            # トークン選択範囲
            "PARAMETER repeat_penalty 1.1",  # 繰り返し抑制
            "PARAMETER num_thread 8",        # CPU スレッド数
            "",
            "# システムプロンプト（多言語対応）",
            "SYSTEM You are Qwen2.5, a helpful AI assistant created by Alibaba Cloud. You can communicate fluently in multiple languages including Japanese, Chinese, and English. Please provide accurate, helpful, and well-structured responses.",
            "",
        ]
        
        modelfile_content = "\n".join(modelfile_lines)
        
        modelfile_path = self.qwen_dir / "Modelfile"
        with open(modelfile_path, 'w', encoding='utf-8') as f:
            f.write(modelfile_content)
            
        print(f"✅ Modelfile作成完了: {modelfile_path}")
        print("🔧 GPU最適化設定:")
        print("   - GPU層数: 35 (7Bモデル用)")
        print("   - コンテキスト: 4096トークン")
        print("   - VRAM使用予定: 約10-12GB")
        return modelfile_path
    
    def register_with_ollama(self, modelfile_path):
        """OllamaにQwen2.5を登録"""
        print("🚀 Ollama にQwen2.5-7Bを登録中...")
        print("⏳ 初回登録は数分かかる場合があります...")
        
        try:
            # Ollama createコマンドを実行
            cmd = ["ollama", "create", "qwen25-7b", "-f", str(modelfile_path)]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)  # 10分タイムアウト
            
            if result.returncode == 0:
                print("✅ Qwen2.5-7BがOllamaに正常に登録されました！")
                print("🧪 テスト実行例:")
                print("   ollama run qwen25-7b 'Pythonでリストを逆順にする方法を教えて'")
                print("   ollama run qwen25-7b 'Explain transformer attention mechanism'")
                return True
            else:
                print(f"❌ Ollama登録に失敗: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ Ollama登録がタイムアウトしました")
            return False
        except Exception as e:
            print(f"❌ Ollama登録中にエラー: {e}")
            return False
    
    def verify_setup(self):
        """セットアップ確認とGPU使用状況チェック"""
        print("🔍 セットアップ確認中...")
        
        try:
            # ollamaでモデル一覧を確認
            result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
            
            if "qwen25-7b" in result.stdout:
                print("✅ Qwen2.5-7Bが正常に登録されています")
                
                # 簡単なテスト実行
                print("🧪 簡易動作テスト中...")
                test_cmd = ["ollama", "run", "qwen25-7b", "Hello! Please respond in one sentence."]
                test_result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=30)
                
                if test_result.returncode == 0:
                    print("✅ 動作テスト成功")
                    print(f"🤖 テスト応答: {test_result.stdout.strip()[:100]}...")
                    return True
                else:
                    print("⚠️ 動作テストでエラーが発生しました")
                    return False
            else:
                print("❌ Qwen2.5-7Bが見つかりません")
                return False
                
        except subprocess.TimeoutExpired:
            print("⏰ テストがタイムアウトしました")
            return False
        except Exception as e:
            print(f"❌ セットアップ確認中にエラー: {e}")
            return False

def main():
    print("🌟 Qwen2.5-7B セットアップ開始")
    print("🎯 対象環境: RTX 4060 Ti 16GB + Ollama")
    print("📊 量子化: INT4 (Q4_K_M) - 精度と速度のバランス")
    print("-" * 60)
    
    setup = Qwen25Setup()
    
    # Step 1: モデルダウンロード
    model_path = setup.download_qwen25_model()
    if not model_path:
        print("❌ セットアップ中断：モデル取得失敗")
        return
    
    # Step 2: Modelfile作成
    if model_path.startswith("qwen2.5:"):
        print("🔄 Ollama直接pullが成功 - カスタマイズをスキップ")
        final_success = True
    else:
        modelfile_path = setup.create_ollama_modelfile(model_path)
        
        # Step 3: Ollama登録
        final_success = setup.register_with_ollama(modelfile_path)
    
    # Step 4: 確認
    if final_success and setup.verify_setup():
        print("\n🎉 Qwen2.5-7B セットアップ完了！")
        print("=" * 60)
        print("📊 性能期待値（16GB GPU環境）:")
        print("   - VRAM使用量: 約10-12GB")
        print("   - トークン生成速度: 30-50 tok/sec")
        print("   - 日本語対応: 良好")
        print("   - 技術文書処理: 強い")
        print("\n🧪 テストコマンド例:")
        print("   ollama run qwen25-7b 'DeepSeekとQwen2.5の違いを説明して'")
        print("   ollama run qwen25-7b 'Write a Python function to reverse a list'")
        print("\n🔄 比較分析準備完了！")
    else:
        print("❌ セットアップに失敗しました")
        print("💡 トラブルシューティング:")
        print("   1. GPU VRAM を確認: nvidia-smi")
        print("   2. Ollama が起動中か確認: ollama list")
        print("   3. ディスク容量を確認（5GB以上必要）")

if __name__ == "__main__":
    main()