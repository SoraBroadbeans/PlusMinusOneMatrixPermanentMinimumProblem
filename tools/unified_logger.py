#!/usr/bin/env python3
"""
Unified Logging Utility for Toeplitz Permanent Calculation

タイムスタンプ付きで複数の並列プロセスからログを1つのファイルに集約する。
既存の個別ファイル出力と共存可能。
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
import threading


class UnifiedLogger:
    """
    タイムスタンプ付きで複数プロセスからのログを単一ファイルに集約

    使用例:
        logger = UnifiedLogger('logs/execution_log.txt')
        logger.log_session_start(n=20, num_processes=10)
        logger.log_process_event(process_id=0, event='completed', data={...})
        logger.log_session_end()
    """

    def __init__(self, log_file_path: str):
        """
        ロガーを初期化

        Args:
            log_file_path: ログファイルのパス（相対パス or 絶対パス）
        """
        self.log_file = Path(log_file_path)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)

        # スレッドセーフティ用のロック
        self._lock = threading.Lock()

        # セッション情報を保持
        self.session_info = {}

    def _get_timestamp(self) -> str:
        """ISO 8601形式のタイムスタンプを取得"""
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    def _safe_append(self, log_entry: str):
        """
        ファイルにスレッドセーフに追記

        Args:
            log_entry: ログエントリ（改行なし）
        """
        with self._lock:
            try:
                with open(self.log_file, 'a', encoding='utf-8') as f:
                    f.write(log_entry + '\n')
            except IOError as e:
                print(f"Error writing to log file: {e}", file=sys.stderr)

    def log(self, level: str, message: str, data: Optional[Dict[str, Any]] = None):
        """
        一般的なログエントリを追記

        Args:
            level: ログレベル ('INFO', 'WARN', 'ERROR')
            message: ログメッセージ
            data: 補足データ（辞書）
        """
        timestamp = self._get_timestamp()
        log_entry = f"[{timestamp}] {level}: {message}"

        if data:
            data_str = " | ".join(f"{k}={v}" for k, v in data.items())
            log_entry += f" | {data_str}"

        self._safe_append(log_entry)

    def log_session_start(self, n: int, num_processes: int, num_divisions: int = None):
        """
        セッション開始をログに記録

        Args:
            n: 行列サイズ
            num_processes: 並列プロセス数
            num_divisions: rate分割数（オプション）
        """
        self.session_info = {
            'n': n,
            'num_processes': num_processes,
            'num_divisions': num_divisions,
            'start_time': datetime.now()
        }

        timestamp = self._get_timestamp()
        header = f"\n{'='*80}\n[{timestamp}] SESSION START\n{'='*80}"
        self._safe_append(header)

        data = {
            'n': n,
            'num_processes': num_processes,
        }
        if num_divisions:
            data['num_divisions'] = num_divisions

        self.log('INFO', 'Session initialized', data)

    def log_process_start(self, process_id: int, rate_lower: float, rate_upper: float):
        """
        プロセス開始を記録

        Args:
            process_id: プロセスID
            rate_lower: rate範囲下限
            rate_upper: rate範囲上限
        """
        self.log(
            'INFO',
            f'Process {process_id} started',
            {
                'rate_range': f'{rate_lower:.4f}-{rate_upper:.4f}'
            }
        )

    def log_process_completed(self, process_id: int, data: Dict[str, Any]):
        """
        プロセス完了を記録

        Args:
            process_id: プロセスID
            data: プロセス統計情報
                - elapsed_time: 経過時間（秒）
                - total_calculations: 計算回数
                - positive_found: 正値発見数
                - best_permanent: 最小正値
                - etc.
        """
        log_data = {'process_id': process_id}
        log_data.update(data)

        self.log('INFO', 'Process completed', log_data)

    def log_process_error(self, process_id: int, error_message: str):
        """
        プロセスエラーを記録

        Args:
            process_id: プロセスID
            error_message: エラーメッセージ
        """
        self.log('ERROR', f'Process {process_id} failed', {'error': error_message})

    def log_session_end(self, summary: Optional[Dict[str, Any]] = None):
        """
        セッション終了を記録

        Args:
            summary: セッション統計情報（オプション）
        """
        if self.session_info and 'start_time' in self.session_info:
            elapsed = (datetime.now() - self.session_info['start_time']).total_seconds()
            summary = summary or {}
            summary['elapsed_time_sec'] = f"{elapsed:.2f}"

        self.log('INFO', 'Session ended', summary)

        timestamp = self._get_timestamp()
        footer = f"{'='*80}\n[{timestamp}] SESSION END\n{'='*80}\n"
        self._safe_append(footer)

    def log_memory_info(self, process_id: int, memory_data: Dict[str, Any]):
        """
        プロセスのメモリ情報を記録

        Args:
            process_id: プロセスID
            memory_data: メモリ情報
                - rss_mb: RSS（物理メモリ）
                - vms_mb: VMS（仮想メモリ）
                - percent: メモリ使用率
                - etc.
        """
        log_data = {'process_id': process_id}
        log_data.update(memory_data)

        self.log('INFO', 'Memory snapshot', log_data)

    def log_progress(self, process_id: int, progress_data: Dict[str, Any]):
        """
        プロセスの進捗情報を記録

        Args:
            process_id: プロセスID
            progress_data: 進捗情報
                - total_calculations: 計算回数
                - iteration: 記録回数
                - positive_rate: 正値率（%）
                - current_best: 現在の最小値
                - elapsed_time: 経過時間（秒）
                - etc.
        """
        log_data = {'process_id': process_id}
        log_data.update(progress_data)

        self.log('PROGRESS', 'Progress update', log_data)

    def log_exception(self, process_id: int, exception_msg: str, traceback_str: str = None):
        """
        例外情報を詳細に記録

        Args:
            process_id: プロセスID
            exception_msg: 例外メッセージ
            traceback_str: トレースバック（オプション）
        """
        self.log('ERROR', f'Process {process_id} raised exception', {'error': exception_msg})
        if traceback_str:
            self._safe_append(f"  Traceback:\n{traceback_str}")


def parse_log_file(log_file_path: str) -> Dict[str, Any]:
    """
    ログファイルを解析してセッション情報を抽出

    Args:
        log_file_path: ログファイルのパス

    Returns:
        セッション情報の辞書：
        {
            'session_info': {...},
            'processes': [
                {'process_id': 0, 'start': ..., 'end': ..., 'status': ..., ...},
                ...
            ],
            'total_time': ...,
            'raw_log': ...
        }
    """
    if not os.path.exists(log_file_path):
        return {'error': f'Log file not found: {log_file_path}'}

    with open(log_file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    session_info = {}
    processes = {}  # process_id -> info
    summary = {
        'total_calculations': 0,
        'total_iterations': 0,
        'total_positive': 0,
        'success_count': 0,
        'error_count': 0,
        'completed_count': 0
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # パターンマッチングで各イベントを抽出
        if 'SESSION START' in line:
            # セッション開始を記録
            session_info['start_time'] = line.split('[')[1].split(']')[0]
        elif 'Session initialized' in line and 'n=' in line:
            # セッション情報抽出（簡易版）
            pass
        elif 'Process' in line and 'started' in line:
            # プロセス開始
            if 'process_id=' in line:
                # Process 0 started | rate_range=...
                try:
                    process_id = int(line.split('Process ')[1].split(' ')[0])
                    if process_id not in processes:
                        processes[process_id] = {'process_id': process_id}
                    processes[process_id]['start_time'] = line.split('[')[1].split(']')[0]
                except (IndexError, ValueError):
                    pass

        elif 'Process' in line and 'completed' in line:
            # プロセス完了
            try:
                process_id = int(line.split('Process ')[1].split(' ')[0])
                if process_id not in processes:
                    processes[process_id] = {'process_id': process_id}
                processes[process_id]['end_time'] = line.split('[')[1].split(']')[0]
                processes[process_id]['status'] = 'completed'
                summary['completed_count'] += 1
                summary['success_count'] += 1

                # 統計情報を抽出
                if 'elapsed_time' in line:
                    parts = line.split('elapsed_time=')
                    if len(parts) > 1:
                        elapsed = parts[1].split(',')[0] if ',' in parts[1] else parts[1].split(' ')[0]
                        try:
                            processes[process_id]['elapsed_time'] = float(elapsed)
                        except ValueError:
                            pass

                if 'total_calculations=' in line:
                    parts = line.split('total_calculations=')
                    if len(parts) > 1:
                        count = parts[1].split(',')[0] if ',' in parts[1] else parts[1].split(' ')[0]
                        try:
                            calc_count = int(count)
                            processes[process_id]['total_calculations'] = calc_count
                            summary['total_calculations'] += calc_count
                        except ValueError:
                            pass

            except (IndexError, ValueError):
                pass

        elif 'Process' in line and ('ERROR' in line or 'raised exception' in line or 'failed' in line):
            # プロセスエラー
            try:
                process_id = int(line.split('Process ')[1].split(' ')[0])
                if process_id not in processes:
                    processes[process_id] = {'process_id': process_id}
                processes[process_id]['end_time'] = line.split('[')[1].split(']')[0]
                processes[process_id]['status'] = 'error'
                summary['error_count'] += 1

                if 'error=' in line:
                    error_msg = line.split('error=')[1].split('|')[0].strip() if '|' in line else 'Unknown error'
                    processes[process_id]['error'] = error_msg

            except (IndexError, ValueError):
                pass

        elif 'SESSION END' in line:
            session_info['end_time'] = line.split('[')[1].split(']')[0]

    # プロセス情報をソート
    process_list = sorted(processes.values(), key=lambda x: x.get('process_id', 0))

    return {
        'session_info': session_info,
        'processes': process_list,
        'summary': summary,
        'raw_log': log_file_path
    }


def generate_md_from_log(log_file_path: str, output_md_path: str, n: int = None, num_processes: int = None):
    """
    ログファイルからMDレポートを生成

    Args:
        log_file_path: ログファイルのパス
        output_md_path: 出力MDファイルのパス
        n: 行列サイズ（オプション）
        num_processes: 並列プロセス数（オプション）
    """
    log_data = parse_log_file(log_file_path)

    if 'error' in log_data:
        print(f"Error: {log_data['error']}")
        return None

    session_info = log_data.get('session_info', {})
    processes = log_data.get('processes', [])
    summary = log_data.get('summary', {})

    # MDファイル生成
    md_content = []
    md_content.append("# Parallel Execution Progress Report\n")
    md_content.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    md_content.append(f"**Log Source:** `{log_file_path}`\n\n")

    if n:
        md_content.append(f"**Matrix Size:** n = {n}\n")
    if num_processes:
        md_content.append(f"**Parallel Processes:** {num_processes}\n")

    md_content.append("\n---\n\n")

    # セッション情報
    md_content.append("## Session Information\n\n")
    if session_info.get('start_time'):
        md_content.append(f"- **Start Time:** {session_info['start_time']}\n")
    if session_info.get('end_time'):
        md_content.append(f"- **End Time:** {session_info['end_time']}\n")

    md_content.append("\n## Summary\n\n")
    md_content.append(f"- **Total Processes:** {len(processes)}\n")
    md_content.append(f"- **Completed:** {summary.get('completed_count', 0)}\n")
    md_content.append(f"- **Failed:** {summary.get('error_count', 0)}\n")
    md_content.append(f"- **Total Calculations:** {summary.get('total_calculations', 0):,}\n")

    md_content.append("\n## Process Details\n\n")

    for proc in processes:
        process_id = proc.get('process_id', 'Unknown')
        status = proc.get('status', 'unknown')

        md_content.append(f"### Process {process_id}\n\n")
        md_content.append(f"**Status:** {status.upper()}\n\n")

        if proc.get('start_time'):
            md_content.append(f"- **Start Time:** {proc['start_time']}\n")
        if proc.get('end_time'):
            md_content.append(f"- **End Time:** {proc['end_time']}\n")

        if status == 'completed':
            if proc.get('elapsed_time'):
                md_content.append(f"- **Elapsed Time:** {proc['elapsed_time']:.2f} seconds\n")
            if proc.get('total_calculations'):
                md_content.append(f"- **Total Calculations:** {proc['total_calculations']:,}\n")
        elif status == 'error':
            if proc.get('error'):
                md_content.append(f"- **Error:** `{proc['error']}`\n")

        md_content.append("\n")

    # ログファイルリンク
    md_content.append("---\n\n")
    md_content.append(f"**Log File:** `{os.path.basename(log_file_path)}`\n")

    # ファイルに書き込み
    os.makedirs(os.path.dirname(output_md_path), exist_ok=True)
    with open(output_md_path, 'w', encoding='utf-8') as f:
        f.writelines(md_content)

    return output_md_path


def get_logger(log_dir: str = 'logs') -> UnifiedLogger:
    """
    デフォルトのロガーを取得

    Args:
        log_dir: ログディレクトリ（デフォルト: 'logs'）

    Returns:
        UnifiedLogger インスタンス
    """
    log_file = os.path.join(log_dir, 'execution_log.txt')
    return UnifiedLogger(log_file)


# ============================================================================
# 使用例とテストコード
# ============================================================================

if __name__ == '__main__':
    """
    使用例: スタンドアロン実行テスト

    実行方法:
        python tools/unified_logger.py
    """

    # テストログディレクトリ作成
    test_log_dir = '/tmp/test_unified_logger'
    os.makedirs(test_log_dir, exist_ok=True)

    logger = UnifiedLogger(os.path.join(test_log_dir, 'test_execution.log'))

    print("=== Unified Logger Test ===\n")

    # セッション開始
    logger.log_session_start(n=20, num_processes=4, num_divisions=100)

    # プロセス1: 成功
    logger.log_process_start(0, 0.0, 0.01)
    logger.log_memory_info(0, {'rss_mb': 45.2, 'vms_mb': 38.1, 'percent': 0.3})
    logger.log_process_completed(
        0,
        {
            'elapsed_time': 94.3,
            'total_calculations': 1048576,
            'positive_found': 1234,
            'best_permanent': 16,
        }
    )

    # プロセス2: エラー
    logger.log_process_start(1, 0.01, 0.02)
    logger.log_process_error(1, 'Memory allocation failed')

    # プロセス3: 実行中
    logger.log_process_start(2, 0.02, 0.03)
    logger.log_memory_info(2, {'rss_mb': 156.8, 'vms_mb': 145.2, 'percent': 1.0})

    # セッション終了
    logger.log_session_end({
        'total_processes': 4,
        'completed': 1,
        'failed': 1,
        'running': 2,
        'total_time_hr': 1.5
    })

    # ログファイル内容を表示
    print(f"Log file: {logger.log_file}\n")
    if logger.log_file.exists():
        with open(logger.log_file, 'r', encoding='utf-8') as f:
            print("Log contents:")
            print(f.read())
    else:
        print("Log file not created (check permissions)")
