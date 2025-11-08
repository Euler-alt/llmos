import React, { useState, useEffect } from 'react';
import PromptDisplay from './components/PromptDisplay';
import LLMOutputWindow from './components/LLMOutputWindow';
import HistoryWindow from './components/HistoryWindow';
import ToolVisualizer from './components/ToolVisualizer';
import SystemMonitor from './components/SystemMonitor';
import Navbar from './components/Navbar';
import DataFlowDiagram from './components/DataFlowDiagram';
import DynamicWindowFactory from './components/PromptWindows/DynamicWindowFactory';
import { validateBackendConfig } from './components/PromptWindows/ComponentRegistry';
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
  const [selectedModel, setSelectedModel] = useState('default'); // 选择的模型
  const [manualResponse, setManualResponse] = useState(''); // 手动输入的回复
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

  // 根据配置顺序组装提示词
  const sortedWindowConfigs = [...windowConfigs].sort((a, b) => (a.order || 0) - (b.order || 0));

  useEffect(() => {
  if (!selectedModel) return;

  const sendModel = async () => {
    try {
      const res = await fetch(`${API_BASE_URL}/llm/setModel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: selectedModel }),
      });

      if (!res.ok) {
        console.log("⚠ 后端不支持这个路径或返回错误:", res.status);
        // ✅ 前端照样更新提示
        setHistory(prev => [...prev, {
          id: Date.now(),
          timestamp: new Date().toLocaleString(),
          prompt: "切换模型",
          response: { answer: `后端不支持 setmodel (${res.status})`, isManual: true },
        }]);
        return;
      }

      console.log("✅ 后端成功切换模型");
    } catch (err) {
      console.error("❌ 网络错误或后端根本不存在:", err);
      setHistory(prev => [...prev, {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        prompt: "切换模型",
        response: { answer: `网络错误：无法连接 setmodel`, isManual: true },
      }]);
    }
  };

  sendModel();
}, [selectedModel]);

  // 这个 useEffect 根据窗口数据和配置组装提示词
  useEffect(() => {
    if (Object.keys(windows).length === 0 || sortedWindowConfigs.length === 0) return;

    const assemblePrompt = () => {
      let promptString = ``;
      
      sortedWindowConfigs.forEach((config) => {
        const windowData = windows[config.windowTitle];
        if (!windowData) return;
        promptString += `${JSON.stringify(windowData)}`;
      });

      return promptString;
    };

    setFullPrompt(assemblePrompt());
  }, [windows, sortedWindowConfigs]);


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
        body: JSON.stringify({ 
          prompt: fullPrompt
        })
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
        windows: {...windows}
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

  // 手动发送回复到后端
  const handleManualSend = async () => {
    if (!manualResponse.trim()) return;
    
    try {
      const res = await fetch(`${API_BASE_URL}/llm/manual-response`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          response: manualResponse,
        })
      });
      
      if (res.ok) {
        // 添加到历史记录
        const timestamp = new Date().toLocaleString();
        setHistory(prev => [...prev, {
          id: Date.now(),
          timestamp,
          prompt: fullPrompt,
          response: { answer: manualResponse},
          windows: {...windows}
        }]);
        setLlmOutput({"answer":"zero", "raw_response": manualResponse,
        "parsed_calls": res.json()})
        // 清空输入框
        setManualResponse('');
        alert('手动回复已发送到后端');
      } else {
        alert('发送失败，请检查后端连接');
      }
    } catch (error) {
      console.error("Failed to send manual response:", error);
      alert('发送失败，请检查网络连接');
    }
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
                windowConfigs={sortedWindowConfigs}
                windowsData={windows}
                onUpdate={handleUpdate}
                darkMode={darkMode}
              />
            </div>
            
            <div className="space-y-6">
              <PromptDisplay prompt={fullPrompt} darkMode={darkMode} />
              
              {/* 大模型控制面板 - 整合所有相关功能 */}
              <div className={`
                rounded-lg overflow-hidden shadow-lg transition-all duration-300
                ${darkMode ? 'bg-gray-800 text-gray-200' : 'bg-white text-gray-800'}
              `}>
                <div className={`
                  p-4 flex justify-between items-center
                  ${darkMode ? 'bg-blue-900' : 'bg-blue-600'} text-white
                `}>
                  <h3 className="text-lg font-medium flex items-center">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
                      <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3zM6 8a2 2 0 11-4 0 2 2 0 014 0zM16 18v-3a5.972 5.972 0 00-.75-2.906A3.005 3.005 0 0119 15v3h-3zM4.75 12.094A5.973 5.973 0 004 15v3H1v-3a3 3 0 013.75-2.906z" />
                    </svg>
                    大模型控制面板
                  </h3>
                </div>
                
                <div className="p-4 space-y-6">
                  {/* 模型选择和调用区域 */}
                  <div className="flex flex-col sm:flex-row gap-4 items-center">
                    <div className="flex-1 max-w-xs">
                      <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        选择模型
                      </label>
                      <select 
                        value={selectedModel}
                        onChange={(e) => setSelectedModel(e.target.value)}
                        className={`
                          w-full px-3 py-3 rounded-lg border font-medium
                          ${darkMode 
                            ? 'bg-gray-700 text-gray-200 border-gray-600' 
                            : 'bg-white text-gray-800 border-gray-300'
                          }
                          focus:outline-none focus:ring-2 focus:ring-blue-500
                        `}
                      >
                        <option value="default">default</option>
                        <option value="deepseek-chat">deepseek-chat</option>
                        <option value="deepseek-reasoner">deepseek-reasoner</option>
                        <option value="gpt-3.5-turbo">GPT-3.5 Turbo</option>
                        <option value="gpt-4">GPT-4</option>
                        <option value="claude-3-sonnet">Claude 3 Sonnet</option>
                        <option value="claude-3-haiku">Claude 3 Haiku</option>
                        <option value="gemini-pro">Gemini Pro</option>
                      </select>
                    </div>
                    
                    <div className="flex-1 max-w-xs">
                      <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                        模型调用
                      </label>
                      <button 
                        onClick={handleLLMCall}
                        disabled={loading}
                        className={`
                          w-full px-6 py-3 rounded-lg font-medium text-white
                          ${loading ? 'bg-gray-500' : 'bg-blue-600 hover:bg-blue-700'} 
                          transition-colors duration-200 flex items-center justify-center
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
                  </div>
                  
                  {/* 手动输入回复区域 */}
                  <div>
                    <h4 className={`text-md font-medium mb-3 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      手动输入回复
                    </h4>
                    <textarea
                      value={manualResponse}
                      onChange={(e) => setManualResponse(e.target.value)}
                      placeholder="在此输入大模型的回复内容..."
                      className={`
                        w-full p-3 rounded border font-mono text-sm resize-none
                        focus:outline-none focus:ring-2 transition-colors duration-200
                        ${darkMode 
                          ? 'bg-gray-700 text-gray-200 border-gray-600 focus:ring-blue-500' 
                          : 'bg-white text-gray-800 border-gray-300 focus:ring-blue-400'
                        }
                      `}
                      rows="3"
                    />
                    <div className="flex justify-end mt-3">
                      <button
                        onClick={handleManualSend}
                        disabled={!manualResponse.trim()}
                        className={`
                          px-4 py-2 rounded-lg font-medium
                          ${!manualResponse.trim() 
                            ? 'bg-gray-400 text-gray-200 cursor-not-allowed' 
                            : darkMode 
                              ? 'bg-green-600 text-white hover:bg-green-700' 
                              : 'bg-green-500 text-white hover:bg-green-600'
                          }
                          transition-colors duration-200
                        `}
                      >
                        发送到后端
                      </button>
                    </div>
                  </div>
                </div>
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