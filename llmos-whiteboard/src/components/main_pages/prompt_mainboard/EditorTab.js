import React, {useEffect, useState} from 'react';
import DynamicWindowFactory from './PromptWindows/DynamicWindowFactory';
import PromptDisplay from './Panel/PromptDisplay';
import LLMControlPanel from './Panel/LLMControlPanel';

import {API_BASE_URL} from "../../../config/api";

const EditorTab = ({
  darkMode
}) => {
  const [windows, setWindows] = useState([]); // 后端配置的窗口列表
  const [fullPrompt, setFullPrompt] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    // 使用 EventSource 监听 SSE 接口
    const eventSource = new EventSource(`${API_BASE_URL}/sse`);

    // 监听 'message' 事件，这是后端推送数据时触发的事件
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // 检查是否是动态配置数据（新式格式）
        if (data.windows && Array.isArray(data.windows)) {
          setWindows(data.windows);
        }
        setLoading(false);
      } catch (error) {
        console.error("Failed to parse SSE data:", error);
      }
    };

    // 监听连接错误
    eventSource.onerror = (error) => {
      console.error("SSE connection error:", error);
      eventSource.close(); // 关闭连接以避免重试
      setLoading(false);
    };

    // 组件卸载时关闭连接，防止内存泄漏
    return () => {
      eventSource.close();
      console.log('SSE connection closed.');
    };
  }, [setWindows]); // 只在组件首次加载时建立连接

    // 根据配置顺序组装提示词
  useEffect(() => {
  if (windows.length === 0) return;

  const promptString = windows
    .sort((a, b) => (a.order || 0) - (b.order || 0))
    .map(win => `
<WINDOW START: ${win.windowTitle}>
META:
${win.data?.meta || ""}
STATE:
${typeof win.data?.state === 'object' ? JSON.stringify(win.data.state, null, 2) : (win.data?.state || "")}
<WINDOW END: ${win.windowTitle}>`)
    .join('\n');

  setFullPrompt(promptString);
}, [windows]);

  if (loading && Object.keys(windows).length === 0) {
    return (
      <div className={`${darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-800'} min-h-screen flex items-center justify-center`}>
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-xl">连接到后端中...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div className="space-y-6">
        <DynamicWindowFactory
          windows={windows}
          darkMode={darkMode}
        />
      </div>
      
      <div className="space-y-6">
        <PromptDisplay prompt={fullPrompt} darkMode={darkMode} />
        
        <LLMControlPanel
          darkMode={darkMode}
          fullPrompt={fullPrompt}
        />
      </div>
    </div>
  );
};

export default EditorTab;