@echo off
REM Takato向け LLM比較環境セットアップバッチファイル
REM Windows PowerShell用

echo ========================================
echo Takato向け LLM比較環境セットアップ
echo DeepSeek V3 vs Kimi K2 (外付けGPU 16GB)
echo ========================================
echo.

echo 1. Python仮想環境作成中...
python -m venv venv
if errorlevel 1 (
    echo エラー: Python仮想環境の作成に失敗しました
    pause
    exit /b 1
)

echo 2. 仮想環境をアクティベート中...
call venv\Scripts\activate.bat

echo 3. Python依存関係インストール中...
pip install --upgrade pip
pip install -r requirements.txt
if errorlevel 1 (
    echo エラー: 依存関係のインストールに失敗しました
    pause
    exit /b 1
)

echo 4. Ollamaインストール確認...
ollama --version >nul 2>&1
if errorlevel 1 (
    echo Ollamaがインストールされていません
    echo 以下のコマンドでインストールしてください:
    echo   winget install Ollama.Ollama
    pause
    exit /b 1
) else (
    echo Ollama バージョン確認OK
)

echo 5. DeepSeek V3 モデルダウンロード...
ollama pull deepseek-coder:6.7b-instruct-q4_0
if errorlevel 1 (
    echo 警告: DeepSeek V3のダウンロードに失敗しました
)

echo 6. Kimi K2 セットアップ実行...
python scripts\setup_kimi_k2.py
if errorlevel 1 (
    echo 警告: Kimi K2のセットアップに失敗しました
    echo 手動でセットアップを行ってください
)

echo.
echo ========================================
echo セットアップ完了!
echo ========================================
echo.
echo 次のステップ:
echo 1. 比較評価実行: python scripts\run_comparison.py
echo 2. 結果確認: results\ フォルダを参照
echo 3. 個別テスト: ollama run deepseek-coder:6.7b-instruct-q4_0
echo              ollama run kimi-k2:latest
echo.
pause