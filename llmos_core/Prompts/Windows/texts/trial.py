class Dispatcher:
    def __init__(self):
        self.windows = {}

        # 根据 call_type 定义不同的处理策略
        self.call_handlers = {
            'action': self._handle_action_call,
            'control': self._handle_control_call,
            'state': self._handle_state_call,
            'query': self._handle_query_call,
            'meta': self._handle_meta_call,
        }

    def execute_calls(self, calls):
        """根据 call_type 分发到不同的处理器"""
        results = []

        for i, call in enumerate(calls):
            call_type = call.get('call_type', 'prompt')  # 兼容旧格式

            # 根据类型分发
            if call_type in self.call_handlers:
                result = self.call_handlers[call_type](call, calls, i)
            else:
                # 默认处理（兼容旧的 "prompt" 类型）
                result = self._dispatch_default(call)

            results.append(result)

        return results

    def _handle_action_call(self, call, all_calls, index):
        """处理环境交互类调用 - 自动记录到栈"""
        func_name = call['func_name']
        kwargs = call['kwargs']

        # 1. 执行动作
        result = self._dispatch_to_window(call)

        # 2. 提取关键信息
        action = kwargs.get('action')
        reasoning = kwargs.get('reasoning')
        observation = result.get('observation', str(result))

        # 3. 检查是否有后续的手动 stack_set_instruction
        has_manual_record = any(
            c['func_name'] == 'stack_set_instruction' and c.get('call_type') == 'control'
            for c in all_calls[index + 1:]
        )

        # 4. 如果没有手动记录，自动记录
        if not has_manual_record:
            self.windows['stack'].auto_record_action(
                instruction=action,
                result=observation,
                reasoning=reasoning
            )
            result['auto_recorded'] = True

        return result

    def _handle_control_call(self, call, all_calls, index):
        """处理控制流调用 - 直接执行，不额外记录"""
        return self._dispatch_to_window(call)

    def _handle_state_call(self, call, all_calls, index):
        """处理状态变更 - 可能加入状态校验"""
        result = self._dispatch_to_window(call)

        # 可选：记录到状态变更日志（不是 action_history）
        if self.enable_state_logging:
            self._log_state_change(call, result)

        return result

    def _handle_query_call(self, call, all_calls, index):
        """处理查询 - 纯读操作"""
        return self._dispatch_to_window(call)

    def _handle_meta_call(self, call, all_calls, index):
        """处理元操作 - 可能记录到思考日志"""
        result = self._dispatch_to_window(call)

        # 可选：记录思考过程到独立日志
        if call['func_name'] == 'new_think':
            self._log_thinking(call['kwargs'].get('content'))

        return result

    def _dispatch_to_window(self, call):
        """实际分发到窗口的函数"""
        func_name = call['func_name']
        kwargs = call['kwargs']

        # 找到对应的窗口和处理函数
        for window in self.windows.values():
            handlers = window.export_handlers()
            if func_name in handlers:
                return handlers[func_name](**kwargs)

        return {"status": "error", "reason": f"Unknown function: {func_name}"}