import React, { useState } from 'react';
import ActionRecord from './ActionRecord';

const HistoryItemContent = ({ item, darkMode }) => {
  const [activeTab, setActiveTab] = useState('answer');

  const getTabClass = (tab) => `
    px-3 py-1 text-xs font-medium rounded-t-md transition-all duration-200
    ${activeTab === tab 
      ? (darkMode ? 'bg-gray-700 text-blue-400 border-b-2 border-blue-400' : 'bg-white text-blue-600 border-b-2 border-blue-600')
      : (darkMode ? 'bg-gray-800 text-gray-500 hover:text-gray-300' : 'bg-gray-100 text-gray-400 hover:text-gray-600')
    }
  `;

  const result = item.response;

  return (
    <div className={`p-4 border-t ${darkMode ? 'border-gray-600' : 'border-gray-200'}`}>
      {/* 选项卡头部 */}
      <div className="flex border-b mb-4 gap-1">
        <button 
          className={getTabClass('answer')}
          onClick={() => setActiveTab('answer')}
        >
          行动记录
        </button>
        <button 
          className={getTabClass('raw')}
          onClick={() => setActiveTab('raw')}
        >
          原始响应
        </button>
        <button 
          className={getTabClass('tools')}
          onClick={() => setActiveTab('tools')}
        >
          工具调用
        </button>
      </div>

      {/* 选项卡内容 */}
      <div className="max-h-96 overflow-y-auto custom-scrollbar">
        {activeTab === 'answer' && (
          <div className="space-y-2">
            {result?.parsed_calls && result.parsed_calls.length > 0 ? (
              result.parsed_calls.map((call, idx) => (
                <ActionRecord key={idx} record={call} index={idx} darkMode={darkMode} />
              ))
            ) : (
              <div className="text-center py-8 text-sm opacity-50 italic">暂无行动记录</div>
            )}
          </div>
        )}

        {activeTab === 'raw' && (
          <div className={`p-3 rounded text-sm font-mono whitespace-pre-wrap ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
            {result?.raw_response || "无原始响应"}
          </div>
        )}

        {activeTab === 'tools' && (
          <div className={`p-3 rounded text-sm font-mono whitespace-pre-wrap ${darkMode ? 'bg-gray-900' : 'bg-gray-50'}`}>
            {result?.parsed_calls ? JSON.stringify(result.parsed_calls, null, 2) : "无工具调用数据"}
          </div>
        )}
      </div>

      <div className="mt-4 flex justify-between items-center">
        <div className="text-[10px] opacity-50">
          Prompt 长度: {item.prompt?.length || 0}
        </div>
        <button 
          className={`px-3 py-1 rounded text-sm ${
            darkMode 
              ? 'bg-blue-600 hover:bg-blue-700 text-white' 
              : 'bg-blue-100 hover:bg-blue-200 text-blue-800'
          } transition-colors duration-200`}
          onClick={() => {
            console.log('恢复历史状态', item);
          }}
        >
          恢复此状态
        </button>
      </div>
    </div>
  );
};

const HistoryWindow = ({ history, darkMode }) => {
  const [expandedItem, setExpandedItem] = useState(null);
  const [isMaximized, setIsMaximized] = useState(false);

  if (history.length === 0) {
    return (
      <div className={`rounded-lg p-4 ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-700'} transition-colors duration-300`}>
        <h3 className="text-xl font-semibold mb-2">历史记录</h3>
        <p className="text-center py-4 italic">暂无历史记录</p>
      </div>
    );
  }

  const toggleExpand = (id) => {
    if (expandedItem === id) {
      setExpandedItem(null);
    } else {
      setExpandedItem(id);
    }
  };

  return (
    <div 
      className={`
        rounded-lg p-4 transition-all duration-300
        ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-700'}
        ${isMaximized ? 'fixed z-50 !rounded-lg' : 'relative'}
      `}
      onDoubleClick={() => setIsMaximized(!isMaximized)}
      style={isMaximized ? { 
        position: 'fixed', 
        top: '10%', 
        left: '25%', 
        right: '25%', 
        bottom: '10%', 
        zIndex: 50,
        borderRadius: '0.5rem'
      } : {}}
    >
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold">历史记录</h3>
        <button 
          className="p-2 rounded-full transition-all duration-200 hover:bg-gray-700 hover:bg-opacity-20"
          onClick={(e) => {
            e.stopPropagation();
            setIsMaximized(!isMaximized);
          }}
          title={isMaximized ? "恢复窗口大小" : "最大化窗口"}
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d={isMaximized ? "M3 7a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 6a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" : "M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 1v10h10V5H5z"} clipRule="evenodd" />
          </svg>
        </button>
      </div>
      
      <div className="space-y-3">
        {history.slice().reverse().map((item) => (
          <div 
            key={item.id}
            className={`border rounded-lg overflow-hidden ${
              darkMode ? 'border-gray-700 bg-gray-700' : 'border-gray-300 bg-white'
            } transition-colors duration-300`}
          >
            <div 
              className={`flex justify-between items-center p-3 cursor-pointer ${
                darkMode ? 'hover:bg-gray-600' : 'hover:bg-gray-50'
              }`}
              onClick={() => toggleExpand(item.id)}
            >
              <div>
                <span className="font-medium">会话 #{history.indexOf(item) + 1}</span>
                <span className="ml-3 text-sm opacity-70">{item.timestamp}</span>
              </div>
              <div>
                {expandedItem === item.id ? (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
                  </svg>
                )}
              </div>
            </div>
            
            {expandedItem === item.id && (
              <HistoryItemContent item={item} darkMode={darkMode} />
            )}
          </div>
        ))}
      </div>
    </div>
  );
};

export default HistoryWindow;