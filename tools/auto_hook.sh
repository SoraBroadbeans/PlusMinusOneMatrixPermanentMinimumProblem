#!/bin/bash
# 自動hook実行スクリプト
# Pythonファイルが変更されたときに自動でhookを実行

echo "Python ファイル変更監視を開始します..."
echo "監視ディレクトリ: $(pwd)"
echo "バージョン履歴: version_history.md"
echo ""
echo "使用方法:"
echo "  ./auto_hook.sh                 # 継続監視モード"
echo "  ./auto_hook.sh --check         # 一回だけチェック"
echo "  ./auto_hook.sh --help          # ヘルプ表示"
echo ""

# 引数に応じて実行
if [ "$1" = "--check" ]; then
    python3 tools/file_hook.py --check --dir .. --version-file ../version_history.md
elif [ "$1" = "--help" ]; then
    python3 tools/file_hook.py --help
else
    echo "継続監視モードで開始します (Ctrl+C で停止)"
    python3 tools/file_hook.py --dir .. --version-file ../version_history.md
fi