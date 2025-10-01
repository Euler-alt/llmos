import React, { useState, useEffect, useRef } from 'react';

const StackWindow = ({ data, onUpdate, darkMode }) => {
  const [isUpdated, setIsUpdated] = useState(false);
  const [isExpanded, setIsExpanded] = useState(true);
  const [showMeta, setShowMeta] = useState(true);
  const [showState, setShowState] = useState(true);
  const metaTextareaRef = useRef(null);
  const stateTextareaRef = useRef(null);
  const { meta, state } = data || {};

  // 监听 data 变化，高亮一下
  useEffect(() => {
    if (!data) return;
    setIsUpdated(true);
    const timer = setTimeout(() => setIsUpdated(false), 500);
    return () => clearTimeout(timer);
  }, [data]);
  
  // 自动调整文本区域高度
  useEffect(() => {
    [metaTextareaRef, stateTextareaRef].forEach(ref => {
      if (ref.current) {
        ref.current.style.height = 'auto';
        ref.current.style.height = `${ref.current.scrollHeight}px`;
      }
    });
  }, [data]);
  
  return (
    <div className={`
      rounded-xl overflow-hidden transition-all duration-300
      ${darkMode ? 'bg-gray-800 text-gray-200' : 'bg-yellow-50 text-gray-800'}
      ${isUpdated ? (darkMode ? 'ring-2 ring-yellow-500' : 'ring-2 ring-orange-500') : ''}
      shadow-lg border ${darkMode ? 'border-gray-700' : 'border-yellow-200'}
    `}>
      {/* 主头部 */}
      <div className={`
        p-4 flex justify-between items-center
        ${darkMode ? 'bg-yellow-900 hover:bg-yellow-800' : 'bg-yellow-600 hover:bg-yellow-500'} 
        text-white transition-colors duration-200
      `}>
        <div className="flex items-center space-x-3 cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
            <path d="M7 3a1 1 0 000 2h6a1 1 0 100-2H7zM4 7a1 1 0 011-1h10a1 1 0 110 2H5a1 1 0 01-1-1zM2 11a2 2 0 012-2h12a2 2 0 012 2v4a2 2 0 01-2 2H4a2 2 0 01-2-2v-4z" />
          </svg>
          <div>
            <h4 className="font-semibold text-lg">栈模块 (Stack)</h4>
            <p className="text-yellow-100 text-xs opacity-80">临时工作区域</p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          {/* Meta 开关按钮 */}
          <button 
            className={`
              p-2 rounded-full transition-all duration-200
              ${showMeta 
                ? (darkMode ? 'bg-green-600 hover:bg-green-500' : 'bg-green-500 hover:bg-green-400')
                : (darkMode ? 'bg-gray-600 hover:bg-gray-500' : 'bg-gray-400 hover:bg-gray-300')
              }
            `}
            onClick={(e) => {
              e.stopPropagation();
              setShowMeta(!showMeta);
            }}
            title={showMeta ? "隐藏Meta信息" : "显示Meta信息"}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
            </svg>
          </button>
          
          {/* State 开关按钮 */}
          <button 
            className={`
              p-2 rounded-full transition-all duration-200
              ${showState 
                ? (darkMode ? 'bg-purple-600 hover:bg-purple-500' : 'bg-purple-500 hover:bg-purple-400')
                : (darkMode ? 'bg-gray-600 hover:bg-gray-500' : 'bg-gray-400 hover:bg-gray-300')
              }
            `}
            onClick={(e) => {
              e.stopPropagation();
              setShowState(!showState);
            }}
            title={showState ? "隐藏State信息" : "显示State信息"}
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
              <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z" />
            </svg>
          </button>
          
          <span className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full font-medium">
            {data?.length || 0} 字节
          </span>
          <div className="cursor-pointer" onClick={() => setIsExpanded(!isExpanded)}>
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 transition-transform duration-200" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d={isExpanded ? "M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" : "M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"} clipRule="evenodd" />
            </svg>
          </div>
        </div>
      </div>
      
      {/* 可展开内容 */}
      {isExpanded && (
        <div className="space-y-4 p-4">
          {/* Meta 信息子框 */}
          <div className={`
            rounded-lg overflow-hidden border
            ${darkMode ? 'border-gray-600 bg-gray-750' : 'border-yellow-200 bg-yellow-100'}
          `}>
            <div className={`
              p-3 flex justify-between items-center cursor-pointer
              ${darkMode ? 'bg-yellow-800 hover:bg-yellow-700' : 'bg-yellow-500 hover:bg-yellow-400'}
              text-white transition-colors duration-200
            `} onClick={() => setShowMeta(!showMeta)}>
              <div className="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                </svg>
                <span className="font-medium">Meta 信息</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full">
                  {meta?.length || 0} 字符
                </span>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 transition-transform duration-200" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d={showMeta ? "M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" : "M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"} clipRule="evenodd" />
                </svg>
              </div>
            </div>
            
            {showMeta && (
              <div className="p-3">
                <textarea
                  ref={metaTextareaRef}
                  className={`
                    w-full p-3 rounded border font-mono text-sm resize-none
                    focus:outline-none focus:ring-2 transition-colors duration-200
                    ${darkMode 
                      ? 'bg-gray-700 text-gray-200 border-gray-600 focus:ring-yellow-500' 
                      : 'bg-white text-gray-800 border-gray-300 focus:ring-yellow-400'
                    }
                  `}
                  value={meta || ''}
                  onChange={(e) => onUpdate('stack', { ...data, meta: e.target.value })}
                  rows="3"
                  placeholder="输入栈窗口的meta信息..."
                />
              </div>
            )}
          </div>

          {/* State 信息子框 */}
          <div className={`
            rounded-lg overflow-hidden border
            ${darkMode ? 'border-gray-600 bg-gray-750' : 'border-yellow-200 bg-yellow-100'}
          `}>
            <div className={`
              p-3 flex justify-between items-center cursor-pointer
              ${darkMode ? 'bg-yellow-800 hover:bg-yellow-700' : 'bg-yellow-500 hover:bg-yellow-400'}
              text-white transition-colors duration-200
            `} onClick={() => setShowState(!showState)}>
              <div className="flex items-center space-x-2">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
                  <path d="M13 6a3 3 0 11-6 0 3 3 0 016 0zM18 8a2 2 0 11-4 0 2 2 0 014 0zM14 15a4 4 0 00-8 0v3h8v-3z" />
                </svg>
                <span className="font-medium">State 信息</span>
              </div>
              <div className="flex items-center space-x-2">
                <span className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full">
                  {state?.length || 0} 字符
                </span>
                <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 transition-transform duration-200" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d={showState ? "M14.707 12.707a1 1 0 01-1.414 0L10 9.414l-3.293 3.293a1 1 0 01-1.414-1.414l4-4a1 1 0 011.414 0l4 4a1 1 0 010 1.414z" : "M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z"} clipRule="evenodd" />
                </svg>
              </div>
            </div>
            
            {showState && (
              <div className="p-3">
                <textarea
                  ref={stateTextareaRef}
                  className={`
                    w-full p-3 rounded border font-mono text-sm resize-none
                    focus:outline-none focus:ring-2 transition-colors duration-200
                    ${darkMode 
                      ? 'bg-gray-700 text-gray-200 border-gray-600 focus:ring-yellow-500' 
                      : 'bg-white text-gray-800 border-gray-300 focus:ring-yellow-400'
                    }
                  `}
                  value={state || ''}
                  onChange={(e) => onUpdate('stack', { ...data, state: e.target.value })}
                  rows="4"
                  placeholder="输入栈窗口的state信息..."
                />
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default StackWindow;