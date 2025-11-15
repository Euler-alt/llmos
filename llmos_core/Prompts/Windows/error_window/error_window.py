from llmos_core.Prompts.Windows.BaseWindow import BasePromptWindow
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

META_DIR = Path(__file__).parent
META_FILE = META_DIR / 'error_description.json'

@BasePromptWindow.register('error_window', 'ErrorWindow')
class ErrorWindow(BasePromptWindow):
    """
    异常窗口 - 专门记录大模型回复产生的异常信息
    """

    def __init__(self, window_name='ErrorWindow'):
        super().__init__(window_name=window_name)
        self.file_path = META_FILE
        
        # 加载异常窗口的描述文件
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.description = f.read()
        except FileNotFoundError:
            self.description = "异常窗口 - 用于记录和跟踪大模型产生的异常信息"
        
        # 异常记录数据结构
        self.error_records: List[Dict[str, Any]] = []
        self.max_records = 50  # 最大记录数
        
        # 异常统计
        self.error_stats = {
            'total_errors': 0,
            'errors_by_type': {},
            'recent_errors': []
        }

    def export_meta_prompt(self) -> str:
        """异常窗口的元提示词 - 描述窗口功能和使用规范"""
        return f"""
### 异常窗口功能说明 ###
{self.description}

功能:
- 记录大模型回复过程中产生的各种异常
- 提供异常分类和统计信息
- 支持异常查询和过滤
- 提供异常处理建议

可调用的函数:
- error_record(error_type, error_message, context): 记录新异常
- error_query(type_filter="all"): 查询异常记录
- error_clear(before_time=None): 清理异常记录
- error_statistics(): 获取异常统计
- error_suggest_fix(error_id): 获取异常修复建议
"""

    def export_state_prompt(self) -> str:
        """异常窗口的状态提示词 - 显示当前异常状态"""
        if not self.error_records:
            return "### 当前没有异常记录 ###\n"
        
        # 显示最近5个异常
        recent_errors = self.error_records[-5:]
        error_summary = "### 最近异常记录 ###\n"
        
        for i, error in enumerate(recent_errors):
            error_summary += f"[{i+1}] {error['timestamp']} - {error['error_type']}: {error['error_message'][:50]}...\n"
        
        # 添加统计信息
        error_summary += f"\n### 异常统计 ###\n"
        error_summary += f"总异常数: {self.error_stats['total_errors']}\n"
        
        if self.error_stats['errors_by_type']:
            error_summary += f"按类型分布:\n"
            for error_type, count in self.error_stats['errors_by_type'].items():
                error_summary += f"  - {error_type}: {count}\n"
        
        return error_summary

    def forward(self, *args, **kwargs):
        """组合完整提示词"""
        return super().forward()

    # === 异常处理函数 ===

    def _error_record(self, *args, **kwargs):
        """记录新异常"""
        error_type = kwargs.get('error_type', 'unknown')
        error_message = kwargs.get('error_message', '')
        context = kwargs.get('context', {})
        
        # 创建异常记录
        error_record = {
            'id': len(self.error_records),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'error_type': error_type,
            'error_message': error_message,
            'context': context,
            'resolved': False
        }
        
        # 添加到记录列表
        self.error_records.append(error_record)
        
        # 更新统计信息
        self.error_stats['total_errors'] += 1
        
        # 更新类型统计
        if error_type in self.error_stats['errors_by_type']:
            self.error_stats['errors_by_type'][error_type] += 1
        else:
            self.error_stats['errors_by_type'][error_type] = 1
        
        # 维护最大记录数
        if len(self.error_records) > self.max_records:
            self.error_records.pop(0)
        
        return {
            'status': 'recorded',
            'error_id': error_record['id'],
            'error_type': error_type,
            'timestamp': error_record['timestamp']
        }

    def _error_query(self, *args, **kwargs):
        """查询异常记录"""
        type_filter = kwargs.get('type_filter', 'all')
        limit = kwargs.get('limit', 10)
        
        # 过滤异常记录
        if type_filter == 'all':
            filtered_errors = self.error_records
        else:
            filtered_errors = [error for error in self.error_records 
                             if error['error_type'] == type_filter]
        
        # 应用限制
        filtered_errors = filtered_errors[-limit:]
        
        return {
            'status': 'ok',
            'count': len(filtered_errors),
            'errors': filtered_errors
        }

    def _error_clear(self, *args, **kwargs):
        """清理异常记录"""
        before_time = kwargs.get('before_time')
        
        if before_time:
            # 清理指定时间之前的记录
            original_count = len(self.error_records)
            self.error_records = [
                error for error in self.error_records 
                if error['timestamp'] >= before_time
            ]
            cleared_count = original_count - len(self.error_records)
        else:
            # 清理所有记录
            cleared_count = len(self.error_records)
            self.error_records = []
            self.error_stats = {
                'total_errors': 0,
                'errors_by_type': {},
                'recent_errors': []
            }
        
        return {
            'status': 'cleared',
            'cleared_count': cleared_count,
            'remaining_count': len(self.error_records)
        }

    def _error_statistics(self, *args, **kwargs):
        """获取异常统计"""
        return {
            'status': 'ok',
            'statistics': self.error_stats
        }

    def _error_suggest_fix(self, *args, **kwargs):
        """获取异常修复建议"""
        error_id = kwargs.get('error_id')
        
        if error_id is None or error_id >= len(self.error_records):
            return {
                'status': 'error',
                'reason': f'无效的异常ID: {error_id}'
            }
        
        error = self.error_records[error_id]
        error_type = error['error_type']
        
        # 根据异常类型提供建议
        suggestions = {
            'parse_error': '检查大模型输出格式，确保符合JSON规范',
            'timeout_error': '增加超时时间或优化模型调用逻辑',
            'rate_limit': '降低请求频率，添加重试机制',
            'content_filter': '检查输入内容是否包含敏感信息',
            'model_error': '尝试更换模型或检查模型服务状态',
            'unknown': '检查网络连接和API配置'
        }
        
        suggestion = suggestions.get(error_type, '检查系统日志和配置')
        
        return {
            'status': 'ok',
            'error_id': error_id,
            'error_type': error_type,
            'suggestion': suggestion,
            'context': error.get('context', {})
        }

    def export_handlers(self):
        """导出异常处理函数"""
        return {
            'error_record': self._error_record,
            'error_query': self._error_query,
            'error_clear': self._error_clear,
            'error_statistics': self._error_statistics,
            'error_suggest_fix': self._error_suggest_fix
        }