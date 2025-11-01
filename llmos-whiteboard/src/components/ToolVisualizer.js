import React, { useState } from 'react';

const ToolVisualizer = ({ llmOutput, darkMode }) => {
  const [isMaximized, setIsMaximized] = useState(false);
  // 如果没有输出或没有解析到工具调用，显示空状态
  if (!llmOutput || !llmOutput.parsed_calls || llmOutput.parsed_calls.length === 0) {
    return (
      <div className={`rounded-lg p-6 ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-white text-gray-700'} shadow-lg transition-colors duration-300`}>
        <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold">工具调用可视化</h3>
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
        <div className="flex flex-col items-center justify-center py-10">
          <svg xmlns="http://www.w3.org/2000/svg" className={`h-16 w-16 ${darkMode ? 'text-gray-600' : 'text-gray-300'}`} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          <p className="mt-4 text-lg">暂无工具调用数据</p>
          <p className={`mt-2 ${darkMode ? 'text-gray-500' : 'text-gray-400'}`}>调用大模型后，工具调用将在此处可视化</p>
        </div>
      </div>
    );
  }

  // 处理工具调用数据
  const toolCalls = llmOutput.parsed_calls;

  return (
    <div 
      className={`
        rounded-lg p-6 shadow-lg transition-all duration-300
        ${darkMode ? 'bg-gray-800 text-gray-300' : 'bg-white text-gray-700'}
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
      <h3 className="text-xl font-semibold mb-4">工具调用可视化</h3>
      
      <div className="space-y-6">
        {toolCalls.map((call, index) => (
          <div 
            key={index}
            className={`border rounded-lg overflow-hidden ${
              darkMode ? 'border-gray-700' : 'border-gray-200'
            }`}
          >
            <div className={`p-3 font-medium ${getToolColor(call.tool, darkMode)}`}>
              {getToolIcon(call.tool)}
              <span className="ml-2">{call.tool}</span>
            </div>
            
            <div className={`p-4 ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
              <h4 className="font-medium mb-2">参数</h4>
              <pre className={`p-3 rounded ${darkMode ? 'bg-gray-800' : 'bg-white'} overflow-x-auto`}>
                {JSON.stringify(call.args, null, 2)}
              </pre>
              
              {call.result && (
                <>
                  <h4 className="font-medium mt-4 mb-2">结果</h4>
                  <pre className={`p-3 rounded ${darkMode ? 'bg-gray-800' : 'bg-white'} overflow-x-auto`}>
                    {typeof call.result === 'object' 
                      ? JSON.stringify(call.result, null, 2)
                      : call.result}
                  </pre>
                </>
              )}
            </div>
          </div>
        ))}
      </div>
      
      <div className="mt-6">
        <h4 className="font-medium mb-2">工具调用流程</h4>
        <div className={`p-4 rounded ${darkMode ? 'bg-gray-700' : 'bg-gray-50'}`}>
          <div className="flex items-center overflow-x-auto pb-2">
            {toolCalls.map((call, index) => (
              <React.Fragment key={index}>
                <div className={`flex-shrink-0 rounded px-3 py-2 ${getToolColor(call.tool, darkMode)}`}>
                  {getToolIcon(call, true)}
                  <span className="ml-1">{call.tool}</span>
                </div>
                
                {index < toolCalls.length - 1 && (
                  <div className="flex-shrink-0 mx-2">
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clipRule="evenodd" />
                    </svg>
                  </div>
                )}
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// 根据工具类型返回不同的颜色
const getToolColor = (toolName, darkMode) => {
  const toolType = toolName.toLowerCase();
  
  if (toolType.includes('search') || toolType.includes('find')) {
    return darkMode ? 'bg-indigo-900 text-indigo-200' : 'bg-indigo-100 text-indigo-800';
  } else if (toolType.includes('read') || toolType.includes('get')) {
    return darkMode ? 'bg-blue-900 text-blue-200' : 'bg-blue-100 text-blue-800';
  } else if (toolType.includes('write') || toolType.includes('create') || toolType.includes('update')) {
    return darkMode ? 'bg-green-900 text-green-200' : 'bg-green-100 text-green-800';
  } else if (toolType.includes('delete') || toolType.includes('remove')) {
    return darkMode ? 'bg-red-900 text-red-200' : 'bg-red-100 text-red-800';
  } else if (toolType.includes('execute') || toolType.includes('run')) {
    return darkMode ? 'bg-yellow-900 text-yellow-200' : 'bg-yellow-100 text-yellow-800';
  } else {
    return darkMode ? 'bg-gray-700 text-gray-200' : 'bg-gray-100 text-gray-800';
  }
};

// 根据工具类型返回不同的图标
const getToolIcon = (toolName, small = false) => {
  const toolType = toolName.toLowerCase();
  const size = small ? 'h-4 w-4' : 'h-5 w-5';
  const display = small ? 'inline' : 'inline-block';
  
  if (toolType.includes('search') || toolType.includes('find')) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" className={`${size} ${display}`} viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M8 4a4 4 0 100 8 4 4 0 000-8zM2 8a6 6 0 1110.89 3.476l4.817 4.817a1 1 0 01-1.414 1.414l-4.816-4.816A6 6 0 012 8z" clipRule="evenodd" />
      </svg>
    );
  } else if (toolType.includes('read') || toolType.includes('get')) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" className={`${size} ${display}`} viewBox="0 0 20 20" fill="currentColor">
        <path d="M9 4.804A7.968 7.968 0 005.5 4c-1.255 0-2.443.29-3.5.804v10A7.969 7.969 0 015.5 14c1.669 0 3.218.51 4.5 1.385A7.962 7.962 0 0114.5 14c1.255 0 2.443.29 3.5.804v-10A7.968 7.968 0 0014.5 4c-1.255 0-2.443.29-3.5.804V12a1 1 0 11-2 0V4.804z" />
      </svg>
    );
  } else if (toolType.includes('write') || toolType.includes('create') || toolType.includes('update')) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" className={`${size} ${display}`} viewBox="0 0 20 20" fill="currentColor">
        <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
      </svg>
    );
  } else if (toolType.includes('delete') || toolType.includes('remove')) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" className={`${size} ${display}`} viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
      </svg>
    );
  } else if (toolType.includes('execute') || toolType.includes('run')) {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" className={`${size} ${display}`} viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M11.3 1.046A1 1 0 0112 2v5h4a1 1 0 01.82 1.573l-7 10A1 1 0 018 18v-5H4a1 1 0 01-.82-1.573l7-10a1 1 0 011.12-.38z" clipRule="evenodd" />
      </svg>
    );
  } else {
    return (
      <svg xmlns="http://www.w3.org/2000/svg" className={`${size} ${display}`} viewBox="0 0 20 20" fill="currentColor">
        <path fillRule="evenodd" d="M11.49 3.17c-.38-1.56-2.6-1.56-2.98 0a1.532 1.532 0 01-2.286.948c-1.372-.836-2.942.734-2.106 2.106.54.886.061 2.042-.947 2.287-1.561.379-1.561 2.6 0 2.978a1.532 1.532 0 01.947 2.287c-.836 1.372.734 2.942 2.106 2.106a1.532 1.532 0 012.287.947c.379 1.561 2.6 1.561 2.978 0a1.533 1.533 0 012.287-.947c1.372.836 2.942-.734 2.106-2.106a1.533 1.533 0 01.947-2.287c1.561-.379 1.561-2.6 0-2.978a1.532 1.532 0 01-.947-2.287c.836-1.372-.734-2.942-2.106-2.106a1.532 1.532 0 01-2.287-.947zM10 13a3 3 0 100-6 3 3 0 000 6z" clipRule="evenodd" />
      </svg>
    );
  }
};

export default ToolVisualizer;