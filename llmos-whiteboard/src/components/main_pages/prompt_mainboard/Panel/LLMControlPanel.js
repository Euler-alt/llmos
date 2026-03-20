import React, {useCallback, useEffect, useState} from 'react';
import {API_BASE_URL} from "../../../../config/api";
import LLMOutputWindow from "./LLMOutputWindow";
import HistoryWindow from "./HistoryWindow";
import {callLLM} from "../../../../api/api";

const LLMControlPanel = ({
  darkMode,
  fullPrompt
}) => {
  const [models, setModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('default'); // 选择的模型
  const [selectedProgram, setSelectedProgram] = useState('ALFworld'); // 选择的程序
  const [manualResponse, setManualResponse] = useState(''); // 手动输入的回复
    // 手动发送回复
  const [history, setHistory] = useState([]);
  const [llmOutput, setLlmOutput] = useState({});
  const [loading, setLoading] = useState(false);
  const [useCache, setUseCache] = useState(true);

  const handleCacheToggle = async (enabled) => {
    setUseCache(enabled);
    try {
      await fetch(`${API_BASE_URL}/llm/config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ use_cache: enabled }),
      });
    } catch (error) {
      console.error("Failed to update cache config:", error);
    }
  };
  
  const handleLLMCall = async () => {
    setLoading(true)
    const result = await callLLM(fullPrompt);
    if (result.ok) {
      setLlmOutput(result.data);
      const timestamp = new Date().toLocaleString();
      setHistory(prev => [
        ...prev,
        {
          id: Date.now(),
          timestamp,
          prompt: fullPrompt,
          response: result.data,
        },
      ]);
    } else {
      setLlmOutput(result.error);
    }
    setLoading(false)
  };

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
        let new_record = {
          id: Date.now(),
          timestamp,
          response: { answer: manualResponse},
        };
        let apillmOutput = {"answer": manualResponse, "raw_response": manualResponse,
        "parsed_calls": res.json()};
        setHistory(prev => [
        ...prev,
        new_record
      ]);
      // 更新输出（和你原来一致）
      setLlmOutput(apillmOutput);
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

  const handleProgramSwitch = async (programName) => {
    if (!programName) return;
    try {
      const res = await fetch(`${API_BASE_URL}/program/set`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ program_name: programName }),
      });
      if (res.ok) {
        setSelectedProgram(programName);
        console.log(`✅ 成功切换到程序: ${programName}`);
      } else {
        alert('切换程序失败');
      }
    } catch (err) {
      console.error("❌ 切换程序错误:", err);
    }
  };

  const handleProgramReset = async () => {
    if (!window.confirm("确定要重置当前程序状态吗？这会清空所有窗口的运行时数据。")) return;
    
    setLoading(true);
    try {
      const res = await fetch(`${API_BASE_URL}/program/reset`, {
        method: 'POST',
      });
      if (res.ok) {
        console.log("✅ 程序重置成功");
        // 清空当前输出
        setLlmOutput({});
      } else {
        alert('重置程序失败');
      }
    } catch (err) {
      console.error("❌ 重置程序错误:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleModelSwitch = useCallback(async (selectedModel) => {
    if (!selectedModel) return;

    try {
      const res = await fetch(`${API_BASE_URL}/model/update`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ modelName: selectedModel }),
      });

      if (!res.ok) {
        console.log("⚠ 后端不支持这个路径或返回错误:", res.status);
        setHistory(prev => [...prev, {
          id: Date.now(),
          timestamp: new Date().toLocaleString(),
          prompt: "切换模型",
          response: { answer: `后端不支持 setmodel (${res.status})`, isManual: true },
        }]);
        return;
      }
      setSelectedModel(selectedModel)
      console.log("✅ 后端成功切换模型");
    } catch (err) {
      console.error("❌ 网络错误:", err);
      setHistory(prev => [...prev, {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        prompt: "切换模型",
        response: { answer: `网络错误：无法连接 setmodel`, isManual: true },
      }]);
    }
  },[setHistory]); // ← deps 空数组 OK

  useEffect(() => {
    const fetchModels = async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/models`);
        if (res.ok) {
          const data = await res.json();
          setModels(data.models || []);
        } else {
          console.error("获取模型列表失败");
        }
      } catch (err) {
        console.error("获取模型列表错误:", err);
      }
    };
    fetchModels();
  }, []);

  return (
    <div className="flex flex-col gap-4">
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
          {/* 程序和模型选择区域 */}
          <div className="flex flex-col sm:flex-row gap-4 items-center">
            <div className="flex-1 max-w-xs">
              <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                选择程序
              </label>
              <select
                value={selectedProgram}
                onChange={(e) => handleProgramSwitch(e.target.value)}
                className={`
                  w-full px-3 py-3 rounded-lg border font-medium
                  ${darkMode 
                    ? 'bg-gray-700 text-gray-200 border-gray-600' 
                    : 'bg-white text-gray-800 border-gray-300'
                  }
                  focus:outline-none focus:ring-2 focus:ring-blue-500
                `}
              >
                <option value="ALFworld">ALFworld (游戏环境)</option>
                <option value="Context">Context (任务上下文)</option>
                <option value="Chat">Chat (通用对话)</option>
              </select>
            </div>

            <div className="flex-1 max-w-xs">
              <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                选择模型
              </label>
              <select
                value={selectedModel}
                onChange={(e) => handleModelSwitch(e.target.value)}
                className={`
                  w-full px-3 py-3 rounded-lg border font-medium
                  ${darkMode 
                    ? 'bg-gray-700 text-gray-200 border-gray-600' 
                    : 'bg-white text-gray-800 border-gray-300'
                  }
                  focus:outline-none focus:ring-2 focus:ring-blue-500
                `}>
                <option value="default">default</option>
                {models.map((model) => (
                  <option key={model} value={model}>
                    {model}
                  </option>
                ))}
              </select>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                checked={useCache}
                onChange={(e) => handleCacheToggle(e.target.checked)}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />
              <label htmlFor="useCache" className="ml-2 block text-sm text-gray-900">
                Use Cache
              </label>
            </div>

            <div className="flex-1 max-w-xs">
              <label className={`block text-sm font-medium mb-2 ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                模型调用
              </label>
              <div className="flex gap-2">
                <button
                  onClick={handleLLMCall}
                  disabled={loading}
                  className={`
                    flex-1 px-4 py-3 rounded-lg font-medium text-white shadow-md
                    ${loading ? 'bg-gray-500' : 'bg-gradient-to-r from-blue-600 to-blue-500 hover:from-blue-700 hover:to-blue-600'} 
                    transition-all duration-300 transform active:scale-95 flex items-center justify-center
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
                
                <button
                  onClick={handleProgramReset}
                  disabled={loading}
                  title="重置当前程序状态"
                  className={`
                    px-4 py-3 rounded-lg font-medium shadow-md transition-all duration-300 transform active:scale-95
                    ${darkMode 
                      ? 'bg-gray-700 text-gray-200 hover:bg-gray-600 border border-gray-600' 
                      : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-300'}
                    ${loading ? 'opacity-50 cursor-not-allowed' : ''}
                  `}
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className={`h-5 w-5 ${loading ? 'animate-spin' : ''}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                </button>
              </div>
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
  );
};

export default LLMControlPanel;