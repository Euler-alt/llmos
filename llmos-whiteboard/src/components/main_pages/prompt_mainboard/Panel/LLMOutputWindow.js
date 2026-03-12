import React, { useState, useEffect } from 'react';

const LLMOutputWindow = ({ result, darkMode }) => {
  const [isUpdated, setIsUpdated] = useState(false);
  const [activeTab, setActiveTab] = useState('raw');
  const [isCopied, setIsCopied] = useState(false);

  useEffect(() => {
    if (!result) return;
    setIsUpdated(true);
    setActiveTab('raw'); // 新结果时默认显示答案标签页
    const timer = setTimeout(() => setIsUpdated(false), 500); // 500ms 高亮
    return () => clearTimeout(timer);
  }, [result]);
  
  const handleCopy = (text) => {
    if (!text) return;
    
    navigator.clipboard.writeText(text).then(() => {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    });
  };
  
  const getTabClass = (tab) => {
    const baseClass = "px-4 py-2 font-medium rounded-t-lg transition-colors duration-200";
    const activeClass = darkMode 
      ? "bg-gray-700 text-white border-b-2 border-green-500" 
      : "bg-white text-gray-800 border-b-2 border-green-500";
    const inactiveClass = darkMode 
      ? "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-300" 
      : "bg-gray-100 text-gray-600 hover:bg-gray-200";
    
    return `${baseClass} ${activeTab === tab ? activeClass : inactiveClass}`;
  };

  return (
    <div className={`
      rounded-lg overflow-hidden shadow-lg transition-all duration-300
      ${darkMode ? 'bg-gray-800 text-gray-200' : 'bg-white text-gray-800'}
      ${isUpdated ? (darkMode ? 'ring-2 ring-yellow-500' : 'ring-2 ring-orange-500') : ''}
    `}>
      <div className={`
        p-4 flex justify-between items-center
        ${darkMode ? 'bg-green-900' : 'bg-green-600'} text-white
      `}>
        <h3 className="text-lg font-medium flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-8-3a1 1 0 00-.867.5 1 1 0 11-1.731-1A3 3 0 0113 8a3.001 3.001 0 01-2 2.83V11a1 1 0 11-2 0v-1a1 1 0 011-1 1 1 0 100-2zm0 8a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
          </svg>
          大模型输出 (LLM Output)
        </h3>
        
        <div className="flex items-center">
          {result && (
            <button
              onClick={() => handleCopy(
                activeTab === 'answer' 
                  ? result?.answer 
                  : activeTab === 'raw' 
                    ? result?.raw_response 
                    : JSON.stringify(result?.parsed_calls, null, 2)
              )}
              className={`
                px-3 py-1 rounded text-sm flex items-center
                ${darkMode 
                  ? 'bg-green-800 hover:bg-green-700' 
                  : 'bg-green-500 hover:bg-green-400'
                }
                transition-colors duration-200
              `}
            >
              {isCopied ? (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                  已复制
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
                    <path d="M8 2a1 1 0 000 2h2a1 1 0 100-2H8z" />
                    <path d="M3 5a2 2 0 012-2 3 3 0 003 3h2a3 3 0 003-3 2 2 0 012 2v6h-4.586l1.293-1.293a1 1 0 00-1.414-1.414l-3 3a1 1 0 000 1.414l3 3a1 1 0 001.414-1.414L10.414 13H15v3a2 2 0 01-2 2H5a2 2 0 01-2-2V5zM15 11h2a1 1 0 110 2h-2v-2z" />
                  </svg>
                  复制
                </>
              )}
            </button>
          )}
        </div>
      </div>
      
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        <button 
          className={getTabClass('answer')}
          onClick={() => setActiveTab('answer')}
        >
          答案
        </button>
        <button 
          className={getTabClass('raw')}
          onClick={() => setActiveTab('raw')}
        >
          原始响应
        </button>
        <button 
          className={getTabClass('calls')}
          onClick={() => setActiveTab('calls')}
        >
          工具调用
        </button>
      </div>
      
      <div className="p-4">
        {activeTab === 'answer' && (
          <div className={`
            rounded border p-4 min-h-[200px] max-h-96 overflow-y-auto
            ${darkMode 
              ? 'bg-gray-700 border-gray-600 text-gray-200' 
              : 'bg-gray-50 border-gray-200 text-gray-800'
            }
          `}>
            {result?.answer ? (
              <div className="font-mono whitespace-pre-wrap text-sm">{result.answer}</div>
            ) : (
              <div className="flex flex-col items-center justify-center h-full py-8 text-center">
                <svg xmlns="http://www.w3.org/2000/svg" className={`h-12 w-12 ${darkMode ? 'text-gray-600' : 'text-gray-300'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                </svg>
                <p className="mt-4 text-lg">暂无输出</p>
                <p className={`mt-2 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>
                  点击"调用大模型"按钮获取回答
                </p>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'raw' && (
          <div className={`
            rounded border p-4 min-h-[200px] max-h-96 overflow-y-auto
            ${darkMode 
              ? 'bg-gray-700 border-gray-600 text-gray-200' 
              : 'bg-gray-50 border-gray-200 text-gray-800'
            }
          `}>
            {result?.raw_response ? (
              <pre className="font-mono text-sm whitespace-pre-wrap">{result.raw_response}</pre>
            ) : (
              <div className="flex flex-col items-center justify-center h-full py-8 text-center">
                <svg xmlns="http://www.w3.org/2000/svg" className={`h-12 w-12 ${darkMode ? 'text-gray-600' : 'text-gray-300'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <p className="mt-4 text-lg">暂无原始输出</p>
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'calls' && (
          <div className={`
            rounded border p-4 min-h-[200px] max-h-96 overflow-y-auto
            ${darkMode 
              ? 'bg-gray-700 border-gray-600 text-gray-200' 
              : 'bg-gray-50 border-gray-200 text-gray-800'
            }
          `}>
            {result?.parsed_calls && result.parsed_calls.length > 0 ? (
              <pre className="font-mono text-sm whitespace-pre-wrap">
                {JSON.stringify(result.parsed_calls, null, 2)}
              </pre>
            ) : (
              <div className="flex flex-col items-center justify-center h-full py-8 text-center">
                <svg xmlns="http://www.w3.org/2000/svg" className={`h-12 w-12 ${darkMode ? 'text-gray-600' : 'text-gray-300'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                </svg>
                <p className="mt-4 text-lg">暂无工具调用信息</p>
              </div>
            )}
          </div>
        )}
        
        <div className="mt-3 flex justify-between text-sm">
          <div>
            <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>
              {result ? '响应时间: 0.8秒' : '等待响应...'}
            </span>
          </div>
          <div>
            <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>
              {result?.answer 
                ? `输出长度: ${result.answer.length} 字符` 
                : ''}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LLMOutputWindow;
