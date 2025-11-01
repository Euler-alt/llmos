import React, { useState, useRef } from 'react';

// --- 1. 复合组件子结构定义（Sub-Components / Slots） ---
// 1.1. 头部组件 (CodeWindow.Header)
// 负责标题、图标，并允许通过 'actions' prop 插入自定义元素（如语言选择和最大化按钮）
export const WindowHeader = ({ title, icon, actions, darkMode, isMaximized, setIsMaximized }) => {
  const headerClass = darkMode ? 'bg-red-900' : 'bg-red-600';

  return (
    <div className={`p-4 flex justify-between items-center ${headerClass} text-white`}>
      <h3 className="text-lg font-medium flex items-center">
        {/* 标题图标 - 使用您的SVG */}
        {icon || (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
        )}
        {title}
      </h3>

      {/* 动作区 (Actions Slot) - 允许用户传入按钮、select等 */}
      <div className="flex items-center space-x-3">
        {actions}

        {/* 默认最大化按钮 */}
        <button
          className="p-2 rounded-full transition-all duration-200 hover:bg-white hover:bg-opacity-20"
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
    </div>
  );
};

// 1.2. 标签页组件 (CodeWindow.Tabs)
const CodeWindowTabs = ({ activeTab, setActiveTab, darkMode }) => {
  const getTabClass = (tabName) => {
    const base = "px-4 py-2 text-sm font-medium transition-colors duration-200";
    if (activeTab === tabName) {
      return `${base} ${darkMode ? 'text-white border-red-500' : 'text-red-600 border-red-500'} border-b-2`;
    }
    return `${base} ${darkMode ? 'text-gray-400 hover:text-gray-300' : 'text-gray-500 hover:text-gray-700'}`;
  };

  return (
    <div className="flex border-b border-gray-200 dark:border-gray-700">
      <button className={getTabClass('meta')} onClick={() => setActiveTab('meta')}>
        Meta 信息
      </button>
      <button className={getTabClass('state')} onClick={() => setActiveTab('state')}>
        State 信息
      </button>
    </div>
  );
};

// 1.3. 内容容器 (CodeWindow.Content)
const CodeWindowContent = ({ children, isMaximized, activeTab }) => (
  // 这里的 min-h 和 max-h 可以根据 isMaximized 动态调整，但我们通过 CSS 容器控制
  <div className={`p-4 ${isMaximized ? 'h-[80vh]' : ''}`}>
    {children}
  </div>
);


// --- 2. 主组件 (CodeWindow) - 组合子组件，提供逻辑 ---

const CodeWindow = ({ data, onUpdate, windowConfig, darkMode, isUpdated }) => {
  const [isMaximized, setIsMaximized] = useState(false);
  const [language, setLanguage] = useState('python');
  const [activeTab, setActiveTab] = useState('meta');

  // 解构数据 (简化示例，实际应处理 data?.meta 等)
  const meta = data?.meta || '';
  const state = data?.state || '';

  // 辅助组件：渲染头部右侧的动作元素
  const HeaderActions = (
    <>
      <select
        className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full border-none focus:outline-none"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
        onClick={(e) => e.stopPropagation()}
      >
        <option value="python">Python</option>
        <option value="javascript">JavaScript</option>
        <option value="java">Java</option>
        <option value="other">其他</option>
      </select>
      <span className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full font-medium">
        {(meta?.length || 0) + (state?.length || 0)} 字节
      </span>
    </>
  );

  // 共享的背景和边框样式
  const containerClasses = `
    rounded-xl overflow-hidden transition-all duration-300
    ${darkMode ? 'bg-gray-800 text-gray-200' : 'bg-red-50 text-gray-800'}
    ${isUpdated ? (darkMode ? 'ring-2 ring-red-500' : 'ring-2 ring-red-400') : ''}
    shadow-2xl border ${darkMode ? 'border-gray-700' : 'border-red-200'}
    ${isMaximized ? 'fixed z-50' : 'relative w-full max-w-2xl'}
  `;

  // 最大化时的内联样式
  const maximizedStyle = {
    top: '5vh',
    left: '5vh',
    right: '5vh',
    bottom: '5vh',
  };

  return (
    <div
      className={containerClasses}
      onDoubleClick={() => setIsMaximized(!isMaximized)}
      style={isMaximized ? maximizedStyle : {}}
    >
      {/* 1. 组合：Header 组件 */}
      <WindowHeader
        title="代码窗口 (Code)"
        darkMode={darkMode}
        isMaximized={isMaximized}
        setIsMaximized={setIsMaximized}
        // 关键点：通过 prop 传递自定义动作，而不是硬编码
        actions={HeaderActions}
      />

      {/* 2. 组合：Tabs 组件 */}
      <CodeWindowTabs
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        darkMode={darkMode}
      />

      {/* 3. 组合：Content 组件，在这里注入 Tab 内容 */}
      <CodeWindowContent isMaximized={isMaximized} activeTab={activeTab}>
        {activeTab === 'meta' && (
          <TextAreaBox
            value={meta}
            onChange={(e) => onUpdate('code', { ...data, meta: e.target.value })}
            darkMode={darkMode}
            placeholder="输入代码窗口的meta信息..."
            rows={isMaximized ? 20 : 6}
          />
        )}

        {activeTab === 'state' && (
          <TextAreaBox
            value={state}
            onChange={(e) => onUpdate('code', { ...data, state: e.target.value })}
            darkMode={darkMode}
            placeholder={`输入${language}代码...`}
            rows={isMaximized ? 20 : 8}
          />
        )}
      </CodeWindowContent>

      <div className={`p-3 border-t text-sm ${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-200'} flex justify-between`}>
          <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>Meta: {meta?.length || 0} 字符</span>
          <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>State: {state?.length || 0} 字符</span>
      </div>

    </div>
  );
};

// 辅助组件：通用 Textarea 样式
const TextAreaBox = ({ value, onChange, darkMode, placeholder, rows }) => {
    return (
        <textarea
            className={`
                w-full p-3 rounded border font-mono text-sm resize-none
                focus:outline-none focus:ring-2 transition-colors duration-200
                ${darkMode
                    ? 'bg-gray-700 text-gray-200 border-gray-600 focus:ring-red-500'
                    : 'bg-white text-gray-800 border-gray-300 focus:ring-red-400'
                }
            `}
            value={value || ''}
            onChange={onChange}
            rows={rows}
            placeholder={placeholder}
            spellCheck="false"
        />
    )
}

export default CodeWindow;