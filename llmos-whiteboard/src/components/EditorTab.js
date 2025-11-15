import React, {useEffect, useState} from 'react';
import DynamicWindowFactory from './PromptWindows/DynamicWindowFactory';
import PromptDisplay from './PromptDisplay';
import LLMControlPanel from './LLMControlPanel';
import {validateBackendConfig} from "./PromptWindows/ComponentRegistry";

import {API_BASE_URL} from "../config/api";

const EditorTab = ({
  darkMode
}) => {
  const [windowConfigs, setWindowConfigs] = useState([]); // 后端配置的窗口列表
  const [fullPrompt, setFullPrompt] = useState('');
  const [loading, setLoading] = useState(true);
  const [windows, setWindows] = useState({});

  useEffect(() => {
    setLoading(true);
    // 使用 EventSource 监听 SSE 接口
    const eventSource = new EventSource(`${API_BASE_URL}/sse`);

    // 监听 'message' 事件，这是后端推送数据时触发的事件
    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // 检查是否是动态配置数据（新式格式）
        if (data.windows && validateBackendConfig(data)) {
          // 后端推送了窗口配置（新式格式）
          setWindowConfigs(data.windows);
          // 提取模块数据（排除 windows 配置数组）
          const moduleData = {...data};
          delete moduleData.windows;
          setWindows(moduleData);
        } else {
          // 传统数据格式，保持向后兼容
          setWindows(data);
          // 如果没有配置，使用默认的窗口顺序（只在首次设置）
          setWindowConfigs(prevConfigs => {
            if (prevConfigs.length === 0) {
              return Object.keys(data).map((type, index) => ({
                id: `${type}-${index}`,
                type: type,
                title: type.charAt(0).toUpperCase() + type.slice(1),
                order: index
              }));
            }
            return prevConfigs;
          });
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
  }, [setWindows]); // 依赖数组为空，只在组件首次加载时建立连接

    // 根据配置顺序组装提示词
  const sortedWindowConfigs = [...windowConfigs].sort((a, b) => (a.order || 0) - (b.order || 0));
  // 这个 useEffect 根据窗口数据和配置组装提示词
  useEffect(() => {
    if (Object.keys(windows).length === 0 || sortedWindowConfigs.length === 0) return;

    const assemblePrompt = () => {
      let promptString = "";
      sortedWindowConfigs.forEach((config) => {
        const windowData = windows[config.windowTitle];
        if (!windowData) return;

        const metaText = windowData?.meta || "";
        const stateText = windowData?.state || "";

        promptString += `
<WINDOW START: ${config.windowTitle}>
META:
${metaText}
STATE:
${stateText}
<WINDOW END: ${config.windowTitle}>
`;
      });

    return promptString;
  };

    setFullPrompt(assemblePrompt());
  }, [windows, sortedWindowConfigs]);

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
          windowConfigs={windowConfigs}
          windowsData={windows}
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