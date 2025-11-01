import React, { useState, useEffect } from 'react';
import PromptDisplay from './components/PromptDisplay';
import LLMOutputWindow from './components/LLMOutputWindow';
import HistoryWindow from './components/HistoryWindow';
import ToolVisualizer from './components/ToolVisualizer';
import SystemMonitor from './components/SystemMonitor';
import Navbar from './components/Navbar';
import DataFlowDiagram from './components/DataFlowDiagram';
import DynamicWindowFactory from './components/DynamicWindowFactory';
import { validateBackendConfig } from './components/ComponentRegistry';
const API_BASE_URL = 'http://localhost:3001/api';

const App = () => {
  const [windows, setWindows] = useState({});
  const [windowConfigs, setWindowConfigs] = useState([]); // 后端配置的窗口列表
  const [fullPrompt, setFullPrompt] = useState('');
  const [loading, setLoading] = useState(true);
  const [llmOutput, setLlmOutput] = useState("");
  const [history, setHistory] = useState([]);
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState('editor'); // 'editor', 'visualizer', 'monitor'
  // **核心改动：使用 useEffect 来设置 SSE 连接**
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
  }, []); // 依赖数组为空，只在组件首次加载时建立连接

  // 这个 useEffect 根据窗口数据和配置组装提示词
  useEffect(() => {
    if (Object.keys(windows).length === 0 || windowConfigs.length === 0) return;

    const assemblePrompt = () => {
      let promptString = `# LLM OS 提示词组装\n\n`;

      // 根据配置顺序组装提示词
      const sortedConfigs = [...windowConfigs].sort((a, b) => (a.order || 0) - (b.order || 0));
      
      sortedConfigs.forEach((config) => {
        const windowData = windows[config.type];
        if (!windowData) return;

        let moduleData = windowData;
        if (typeof moduleData === 'object') {
          moduleData = JSON.stringify(moduleData, null, 2);
        } else {
          moduleData = moduleData.replace(/\n/g, '\\n');
        }

        const moduleName = config.title || config.type;
        const moduleDescription = config.description || `说明文档: ${config.type} 模块`;

        promptString += `### ${moduleName}\n` +
                        `${moduleDescription}\n` +
                        `数据段:\n` +
                        `\`\`\`json\n${moduleData}\n\`\`\`\n\n`;
      });

      promptString += `### 用户输入\n用户: 帮我找一下最近的AI技术突破。`;

      return promptString;
    };

    setFullPrompt(assemblePrompt());
  }, [windows, windowConfigs]);


  // handleUpdate 函数保持不变，它仍然会发送 POST 请求，但现在后端会负责更新所有前端
  const handleUpdate = async (args, kwargs) => {
    try {
      const data = { args, kwargs };
      const res = await fetch(`${API_BASE_URL}/windows/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });
      return res; // 关键：返回响应对象
    } catch (error) {
      console.error("Failed to update data on the server:", error);
      throw error;
    }
  };


  const handleLLMCall = async () => {
    try {
      setLoading(true);
      const res = await fetch(`${API_BASE_URL}/llm/call`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ prompt: fullPrompt })
      });
      const result = await res.json();
      setLlmOutput(result);
      
      // 添加到历史记录
      const timestamp = new Date().toLocaleString();
      setHistory(prev => [...prev, {
        id: Date.now(),
        timestamp,
        prompt: fullPrompt,
        response: result,
        modules: {...windows}
      }]);
    } catch (error) {
      console.error("Failed to call LLM API:", error);
      setLlmOutput("调用失败，请检查后端。");
    } finally {
      setLoading(false);
    }
  };
  
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };
  

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
    <div className={`${darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-800'} min-h-screen transition-colors duration-300`}>
      <Navbar 
        darkMode={darkMode} 
        toggleDarkMode={toggleDarkMode} 
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />
      
      <div className="container mx-auto px-4 py-6">
        <h1 className="text-3xl font-bold mb-4">LLM OS 增强界面</h1>
        <p className="mb-6">数据已通过后端实时推送。当您在任何一个浏览器窗口修改模块文本时，所有窗口都会同步更新。</p>
        
        {activeTab === 'editor' && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="space-y-6">
              <DynamicWindowFactory
                windowConfigs={windowConfigs}
                windowsData={windows}
                onUpdate={handleUpdate}
                darkMode={darkMode}
              />
            </div>
            
            <div className="space-y-6">
              <PromptDisplay prompt={fullPrompt} darkMode={darkMode} />
              
              <div className="flex justify-center">
                <button 
                  onClick={handleLLMCall}
                  disabled={loading}
                  className={`
                    px-6 py-3 rounded-lg font-medium text-white 
                    ${loading ? 'bg-gray-500' : 'bg-blue-600 hover:bg-blue-700'} 
                    transition-colors duration-200 flex items-center
                  `}
                >
                  {loading ? (
                    <>
                      <span className="animate-spin h-5 w-5 mr-2 border-t-2 border-b-2 border-white rounded-full"></span>
                      处理中...
                    </>
                  ) : (
                    <>🚀 调用大模型</>
                  )}
                </button>
              </div>
              
              <LLMOutputWindow result={llmOutput} darkMode={darkMode} />
              
              <HistoryWindow history={history} darkMode={darkMode} />
            </div>
          </div>
        )}
        
        {activeTab === 'visualizer' && (
          <div className="space-y-6">
            <DataFlowDiagram modules={windows} darkMode={darkMode} />
            <ToolVisualizer llmOutput={llmOutput} darkMode={darkMode} />
          </div>
        )}
        
        {activeTab === 'monitor' && (
          <SystemMonitor darkMode={darkMode} />
        )}
      </div>
    </div>
  );
};

// 使用Tailwind CSS，不再需要内联样式

export default App;