#!/usr/bin/env python3
"""
Python ファイル変更監視フック
Pythonファイルが変更されるたびに変更内容とバージョンを記録する
"""

import os
import hashlib
import datetime
import json
import subprocess
import sys
from pathlib import Path


class FileChangeHook:
    def __init__(self, watch_dir=None, version_file="version_history.md"):
        self.watch_dir = Path(watch_dir) if watch_dir else Path.cwd()
        self.version_file = Path(version_file)
        self.hash_file = self.watch_dir / ".file_hashes.json"
        self.progress_file = self.watch_dir / "research_progress.md"
        self.current_version = self._load_version()
        
        # 研究進捗のカテゴリ分け
        self.research_categories = {
            'algorithm': 'アルゴリズム実装',
            'optimization': '計算最適化',
            'analysis': '理論解析',
            'tools': '開発ツール',
            'documentation': 'ドキュメント作成',
            'validation': '検証・テスト'
        }
        
    def _load_version(self):
        """現在のバージョンを取得"""
        if self.version_file.exists():
            with open(self.version_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # 最新のバージョン番号を抽出
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('## v'):
                        version_str = line.split()[1].replace('v', '')
                        try:
                            return float(version_str)
                        except ValueError:
                            continue
        return 1.0
    
    def _get_file_hash(self, file_path):
        """ファイルのハッシュ値を計算"""
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    
    def _load_hashes(self):
        """保存されたハッシュ値を読み込み"""
        if self.hash_file.exists():
            with open(self.hash_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_hashes(self, hashes):
        """ハッシュ値を保存"""
        with open(self.hash_file, 'w') as f:
            json.dump(hashes, f, indent=2)
    
    def _analyze_code_changes(self, file_path):
        """コードの変更内容を詳細分析"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            analysis = {
                'line_count': len(content.split('\n')),
                'functions': [],
                'classes': [],
                'imports': [],
                'comments': 0
            }
            
            for line_num, line in enumerate(content.split('\n'), 1):
                stripped = line.strip()
                if stripped.startswith('def '):
                    func_name = stripped.split('(')[0].replace('def ', '')
                    analysis['functions'].append((func_name, line_num))
                elif stripped.startswith('class '):
                    class_name = stripped.split('(')[0].split(':')[0].replace('class ', '')
                    analysis['classes'].append((class_name, line_num))
                elif stripped.startswith('import ') or stripped.startswith('from '):
                    analysis['imports'].append(stripped)
                elif stripped.startswith('#') or '"""' in stripped:
                    analysis['comments'] += 1
            
            return analysis
        except Exception as e:
            return {'error': str(e), 'line_count': 0}
    
    def _get_file_diff(self, file_path, old_hash, new_hash):
        """ファイルの変更内容を詳細に取得"""
        if old_hash is None:
            # 新規ファイル作成の詳細分析
            analysis = self._analyze_code_changes(file_path)
            if 'error' in analysis:
                return f"新規ファイル作成: {file_path} (分析エラー: {analysis['error']})"
            
            desc = f"新規ファイル作成: {file_path} ({analysis['line_count']}行)"
            if analysis['functions']:
                func_names = [name for name, _ in analysis['functions'][:3]]  # 最初の3つの関数
                desc += f" - 主要関数: {', '.join(func_names)}"
                if len(analysis['functions']) > 3:
                    desc += f"など{len(analysis['functions'])}個"
            if analysis['classes']:
                class_names = [name for name, _ in analysis['classes']]
                desc += f" - クラス: {', '.join(class_names)}"
            return desc
        else:
            # ファイル更新の詳細分析
            analysis = self._analyze_code_changes(file_path)
            if 'error' in analysis:
                return f"ファイル更新: {file_path} (分析エラー: {analysis['error']})"
            
            desc = f"ファイル更新: {file_path} ({analysis['line_count']}行)"
            if analysis['functions']:
                desc += f" - 関数{len(analysis['functions'])}個"
            if analysis['classes']:
                desc += f" - クラス{len(analysis['classes'])}個"
            return desc
    
    def _generate_detailed_summary(self, changes):
        """変更内容の詳細サマリーを生成"""
        new_files = [c for c in changes if '新規ファイル作成' in c]
        updated_files = [c for c in changes if 'ファイル更新' in c]
        deleted_files = [c for c in changes if 'ファイル削除' in c]
        
        summary = ""
        
        if new_files:
            summary += "\n**新規実装**:\n"
            for change in new_files:
                if 'calc_permanent' in change:
                    summary += "- パーマネント計算アルゴリズム実装 (愚直法とRyser法)\n"
                elif 'calc_r_n' in change:
                    summary += "- r_n値計算機能実装 ((±1)行列のパーマネント値個数解析)\n"
                elif 'file_hook' in change:
                    summary += "- 自動バージョン管理システム実装\n"
                elif '__init__' in change:
                    summary += "- パッケージ化対応\n"
                else:
                    summary += f"- {change}\n"
        
        if updated_files:
            summary += "\n**機能改善**:\n"
            for change in updated_files:
                if 'calc_' in change:
                    summary += "- 計算アルゴリズムの最適化・バグ修正\n"
                elif 'hook' in change:
                    summary += "- バージョン管理機能の改善\n"
                else:
                    summary += f"- {change}\n"
        
        if deleted_files:
            summary += "\n**リファクタリング**:\n"
            summary += "- ファイル構造の整理・移動\n"
        
        return summary
    
    def _update_version_file(self, changes):
        """バージョンファイルを詳細情報付きで更新"""
        self.current_version += 0.1
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 詳細サマリー生成
        detailed_summary = self._generate_detailed_summary(changes)
        
        version_entry = f"""## v{self.current_version:.1f}
**更新日時**: {timestamp}

**概要**: プロジェクトの進展と機能拡張
{detailed_summary}
**技術詳細**:
"""
        
        for change in changes:
            version_entry += f"- {change}\n"
        
        version_entry += "\n---\n\n"
        
        # 既存のバージョンファイルに追記
        if self.version_file.exists():
            with open(self.version_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            
            # バージョン履歴の先頭に新しいエントリを挿入
            if "# バージョン履歴" in existing_content:
                parts = existing_content.split("# バージョン履歴", 1)
                new_content = parts[0] + "# バージョン履歴\n\n" + version_entry + parts[1]
            else:
                new_content = "# バージョン履歴\n\n" + version_entry + existing_content
        else:
            new_content = "# バージョン履歴\n\n" + version_entry
        
        with open(self.version_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    def _categorize_changes(self, changes):
        """変更を研究カテゴリに分類"""
        categorized = {cat: [] for cat in self.research_categories.keys()}
        
        for change in changes:
            if 'calc_permanent' in change or 'calc_r_n' in change:
                if '新規' in change:
                    categorized['algorithm'].append(change)
                else:
                    categorized['optimization'].append(change)
            elif 'hook' in change or 'auto_' in change:
                categorized['tools'].append(change)
            elif '__init__' in change or 'README' in change:
                categorized['documentation'].append(change)
            elif '削除' in change:
                categorized['optimization'].append(change)  # リファクタリング
            else:
                categorized['analysis'].append(change)  # デフォルト
        
        return categorized
    
    def _update_research_progress(self, changes, summary):
        """研究進捗ファイルを更新"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        categorized = self._categorize_changes(changes)
        
        progress_entry = f"""# 研究進捗レポート v{self.current_version:.1f}
**更新日**: {timestamp}

## 今回の進捗概要
{summary}

## 研究領域別進捗
"""
        
        for category, category_changes in categorized.items():
            if category_changes:
                progress_entry += f"\n### {self.research_categories[category]}\n"
                for change in category_changes:
                    progress_entry += f"- {change}\n"
        
        progress_entry += f"\n## 次のステップ\n"
        progress_entry += "- [ ] パフォーマンス測定\n"
        progress_entry += "- [ ] 理論値との比較検証\n"
        progress_entry += "- [ ] 結果の論文化\n"
        progress_entry += "\n---\n\n"
        
        # 研究進捗ファイルに追記
        if self.progress_file.exists():
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                existing_content = f.read()
            new_content = progress_entry + existing_content
        else:
            new_content = progress_entry
        
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            f.write(new_content)
    
    def check_changes(self):
        """変更をチェックして記録"""
        old_hashes = self._load_hashes()
        new_hashes = {}
        changes = []
        
        # .pyファイルを検索（srcフォルダ内も含む）
        py_files = list(self.watch_dir.glob("*.py")) + list(self.watch_dir.glob("src/*.py"))
        for py_file in py_files:
            if py_file.name.startswith('.'):  # 隠しファイルは除外
                continue
                
            file_path = str(py_file.relative_to(self.watch_dir))
            new_hash = self._get_file_hash(py_file)
            new_hashes[file_path] = new_hash
            
            old_hash = old_hashes.get(file_path)
            
            if old_hash != new_hash:
                change_desc = self._get_file_diff(py_file, old_hash, new_hash)
                changes.append(change_desc)
        
        # 削除されたファイルをチェック
        for file_path in old_hashes:
            if file_path not in new_hashes:
                changes.append(f"ファイル削除: {file_path}")
        
        if changes:
            print(f"検出された変更: {len(changes)}件")
            for change in changes:
                print(f"  - {change}")
            
            self._update_version_file(changes)
            self._save_hashes(new_hashes)
            print(f"バージョン v{self.current_version:.1f} として記録しました")
            print(f"研究進捗レポートも更新されました: {self.progress_file}")
        else:
            print("変更はありませんでした")
        
        return changes
    
    def run_continuous(self, interval=5):
        """継続的に監視"""
        import time
        print(f"ファイル監視を開始します (間隔: {interval}秒)")
        print(f"監視ディレクトリ: {self.watch_dir}")
        print("Ctrl+C で停止")
        
        try:
            while True:
                self.check_changes()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n監視を停止しました")


def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Python ファイル変更監視フック")
    parser.add_argument("--dir", default=".", help="監視するディレクトリ (デフォルト: 現在のディレクトリ)")
    parser.add_argument("--version-file", default="version_history.md", help="バージョン履歴ファイル")
    parser.add_argument("--check", action="store_true", help="一回だけチェックして終了")
    parser.add_argument("--interval", type=int, default=5, help="監視間隔（秒）")
    
    args = parser.parse_args()
    
    hook = FileChangeHook(args.dir, args.version_file)
    
    if args.check:
        hook.check_changes()
    else:
        hook.run_continuous(args.interval)


if __name__ == "__main__":
    main()