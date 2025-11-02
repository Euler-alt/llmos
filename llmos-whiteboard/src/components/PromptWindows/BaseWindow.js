import React, {useEffect, useRef, useState} from 'react';

// --- 1. 主题颜色映射表 (THEME_MAP) ---
// 这是核心的主题配置，将主题名称（如 'red'）映射到所需的 Tailwind CSS 类名。
// 每个属性都包含 'light'（浅色模式）和 'dark'（深色模式）两种配置。
const THEME_MAP = {
    // --- 原有主题 ---

    // 红色主题 (Red Theme) - 适合代码/警告窗口
    'red': {
        // header: 窗口头部背景色
        header: { light: 'bg-red-600', dark: 'bg-red-900' },
        // bgAccent: 窗口主体背景色 (浅色模式下带微弱主题色，深色模式下为深灰)
        bgAccent: { light: 'bg-red-50', dark: 'bg-gray-800' },
        // accent: 强调色 (用于标签页激活文本等)
        accent: { light: 'text-red-600', dark: 'text-red-400' },
        // focus: 聚焦环颜色 (用于输入框获得焦点时)
        focus: { light: 'focus:ring-red-400', dark: 'focus:ring-red-500' },
        // ring: 更新提示环颜色 (用于整个窗口有更新时)
        ring: { light: 'ring-red-400', dark: 'ring-red-500' },
        // border: 外部边框颜色
        border: { light: 'border-red-200', dark: 'border-gray-700' },
    },
    // 蓝色主题 (Blue Theme) - 适合聊天/交互窗口
    'blue': {
        header: { light: 'bg-blue-600', dark: 'bg-blue-900' },
        bgAccent: { light: 'bg-blue-50', dark: 'bg-gray-800' },
        accent: { light: 'text-blue-600', dark: 'text-blue-400' },
        focus: { light: 'focus:ring-blue-400', dark: 'focus:ring-blue-500' },
        ring: { light: 'ring-blue-400', dark: 'ring-blue-500' },
        border: { light: 'border-blue-200', dark: 'border-gray-700' },
    },
    // 绿色主题 (Green Theme) - 适合日志/成功窗口
    'green': {
        header: { light: 'bg-green-600', dark: 'bg-green-900' },
        bgAccent: { light: 'bg-green-50', dark: 'bg-gray-800' },
        accent: { light: 'text-green-600', dark: 'text-green-400' },
        focus: { light: 'focus:ring-green-400', dark: 'focus:ring-green-500' },
        ring: { light: 'ring-green-400', dark: 'ring-green-500' },
        border: { light: 'border-green-200', dark: 'border-gray-700' },
    },

    // --- 新增主题 ---

    // 1. 紫色主题 (Purple Theme) - 适合配置/设置窗口
    'purple': {
        header: { light: 'bg-purple-600', dark: 'bg-purple-900' },
        bgAccent: { light: 'bg-purple-50', dark: 'bg-gray-800' },
        accent: { light: 'text-purple-600', dark: 'text-purple-400' },
        focus: { light: 'focus:ring-purple-400', dark: 'focus:ring-purple-500' },
        ring: { light: 'ring-purple-400', dark: 'ring-purple-500' },
        border: { light: 'border-purple-200', dark: 'border-gray-700' },
    },

    // 2. 黄色主题 (Yellow Theme) - 适合待办/提示窗口 (注意：深色模式头部颜色略有调整以提高可读性)
    'yellow': {
        header: { light: 'bg-yellow-600', dark: 'bg-yellow-800' }, // 深色模式下用 800，避免太暗
        bgAccent: { light: 'bg-yellow-50', dark: 'bg-gray-800' },
        accent: { light: 'text-yellow-600', dark: 'text-yellow-400' },
        focus: { light: 'focus:ring-yellow-400', dark: 'focus:ring-yellow-500' },
        ring: { light: 'ring-yellow-400', dark: 'ring-yellow-500' },
        border: { light: 'border-yellow-200', dark: 'border-gray-700' },
    },

    // 3. 青色主题 (Cyan Theme) - 适合通知/信息流窗口
    'cyan': {
        header: { light: 'bg-cyan-600', dark: 'bg-cyan-900' },
        bgAccent: { light: 'bg-cyan-50', dark: 'bg-gray-800' },
        accent: { light: 'text-cyan-600', dark: 'text-cyan-400' },
        focus: { light: 'focus:ring-cyan-400', dark: 'focus:ring-cyan-500' },
        ring: { light: 'ring-cyan-400', dark: 'ring-cyan-500' },
        border: { light: 'border-cyan-200', dark: 'border-gray-700' },
    },

    // 4. 灰色主题 (Gray Theme) - 适合默认/不强调的窗口
    'gray': {
        header: { light: 'bg-gray-600', dark: 'bg-gray-900' },
        bgAccent: { light: 'bg-gray-50', dark: 'bg-gray-800' },
        accent: { light: 'text-gray-600', dark: 'text-gray-400' },
        focus: { light: 'focus:ring-gray-400', dark: 'focus:ring-gray-500' },
        ring: { light: 'ring-gray-400', dark: 'ring-gray-500' },
        border: { light: 'border-gray-200', dark: 'border-gray-700' },
    },
};

export const SUPPORTED_THEMES = Object.keys(THEME_MAP);

// --- 2. 主题 Hook (useThemeClasses) ---
// 这个自定义 Hook 负责根据传入的主题名称和深色模式状态，返回一个包含所有所需 CSS 类名的对象。
export const useThemeClasses = (themeName, darkMode) => {
    // 尝试获取指定主题，如果主题不存在，则默认使用 'red' 主题
    const theme = THEME_MAP[themeName] || THEME_MAP['red'];
    // 确定当前是 'dark' 还是 'light' 模式
    const mode = darkMode ? 'dark' : 'light';

    // 返回一个包含所有解析后的 Tailwind 类名对象
    return {
        // 组合背景色和文本色类
        containerBgTextClass: `${theme.bgAccent[mode]} ${darkMode ? 'text-gray-200' : 'text-gray-800'}`,
        headerClass: theme.header[mode],
        accentClass: theme.accent[mode],
        focusRingClass: theme.focus[mode],
        updateRingClass: theme.ring[mode],
        containerBorderClass: theme.border[mode],
    };
};


// --- 3. 通用结构组件 (子组件) ---

// 3.1. 通用头部组件 (WindowHeader)
// 负责窗口的标题栏、图标、动作区以及最大化按钮。
// 它通过 headerClass 属性接收主题背景色。
export const WindowHeader = ({ title, icon, actions, isMaximized, setIsMaximized, headerClass }) => {
  // 默认代码图标 SVG
  const DefaultIcon = () => (
    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
      <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
    </svg>
  );

  return (
    // 使用传入的 headerClass 来定制背景色
    <div className={`p-4 flex justify-between items-center ${headerClass} text-white`}>
      <h3 className="text-lg font-medium flex items-center">
        {/* 如果未传入 icon，则使用 DefaultIcon */}
        {icon || <DefaultIcon />}
        {title}
      </h3>

      {/* 动作区 (actions slot) 和最大化按钮 */}
      <div className="flex items-center space-x-3">
        {actions}

        {/* 最大化/恢复按钮，调用 setIsMaximized 改变父组件状态 */}
        <button
          className="p-2 rounded-full transition-all duration-200 hover:bg-white hover:bg-opacity-20"
          onClick={(e) => {
            e.stopPropagation();
            setIsMaximized(!isMaximized);
          }}
          title={isMaximized ? "恢复窗口大小" : "最大化窗口"}
        >
          {/* SVG 根据 isMaximized 状态切换图标 */}
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" style={{ width: '16px', height: '16px' }} viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d={isMaximized ? "M3 7a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 6a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" : "M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 1v10h10V5H5z"} clipRule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  );
};

// 3.2. 通用标签页组件 (WindowTabs)
// 负责标签页的显示和切换逻辑。
// 通过 accentClass 接收主题强调色，用于激活状态下的文本和边框。
export const WindowTabs = ({ activeTab, setActiveTab, darkMode, accentClass }) => {
  const getTabClass = (tabName) => {
    const base = "px-4 py-2 text-sm font-medium transition-colors duration-200";
    if (activeTab === tabName) {
      // 激活状态：使用传入的 accentClass 作为文本色，并将其转换为 border 颜色
      const borderClass = accentClass.replace('text-', 'border-');
      return `${base} ${darkMode ? 'text-white' : accentClass} border-b-2 ${borderClass}`;
    }
    // 非激活状态：使用默认灰色
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

export const HeaderActions = () => {
  const [language,setLanguage] = useState('other')
  return (
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
  );
};

export const ByteCount = ({byteCount}) => {
    return (
        <span className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full font-medium">
            {byteCount || 0} 字节
        </span>)
};

// 3.3. 通用内容容器 (WindowContent)
// 仅提供统一的内边距，用于包裹窗口主体内容。
export const WindowContent = ({ children }) => (
  <div className="p-4">
    {children}
  </div>
);


// 3.4. 通用文本框 (TextBox)
// 负责提供统一的输入框样式，通过 focusRingClass 接收主题聚焦环颜色。
export const TextBox = ({ value, onChange, darkMode, placeholder, rows, focusRingClass,maxHeight = 200 }) => {

  const textAreaRef = useRef(null);
  useEffect(() => {
      const el = textAreaRef.current;
      if (!el) return;
      el.style.height = 'auto'; // 每次刷新先重置
      const desired = el.scrollHeight;
      if (desired <= maxHeight) {
      el.style.height = `${desired}px`;
      el.style.overflowY = 'hidden';
    } else {
      el.style.height = `${maxHeight}px`;
      el.style.overflowY = 'auto';
    }
  }, [value, maxHeight]);

  return (
    <textarea
        ref={textAreaRef}
        className={`
            w-full p-3 rounded border font-mono text-sm resize-none
            focus:outline-none focus:ring-2 transition-colors duration-200
            ${darkMode
                // 深色模式样式，使用传入的 focusRingClass
                ? `bg-gray-700 text-gray-200 border-gray-600 ${focusRingClass}`
                // 浅色模式样式，使用传入的 focusRingClass
                : `bg-white text-gray-800 border-gray-300 ${focusRingClass}`
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


// --- 4. 主组件 (BaseWindow) - 组合通用组件并应用主题 ---

/**
 * BaseWindow 组件，通过 theme 属性接收预制的主题名称。
 */
export const BaseWindow = ({ data, onUpdate, darkMode, windowConfig}) => {
  const [isMaximized, setIsMaximized] = useState(false);
  const [activeTab, setActiveTab] = useState('meta');
  const [isUpdated, setIsUpdated] = useState(false);

  const metaTextareaRef = useRef(null);
  const stateTextareaRef = useRef(null);

  const themeName = windowConfig?.windowTheme || 'red'
  // --- 关键点：使用 Hook 获取所有主题相关的类名 ---
  // 只需要传入主题名称和深色模式状态
  const themeClasses = useThemeClasses(themeName, darkMode);

  const {
      containerBgTextClass, // 容器背景和文本色
      headerClass,          // 头部背景色
      accentClass,          // 强调色 (用于 Tab)
      focusRingClass,       // 聚焦环颜色 (用于 TextBox)
      updateRingClass,      // 更新提示环颜色 (用于外部容器)
      containerBorderClass, // 外部边框颜色
  } = themeClasses;

  // 解构数据
  const meta = data?.meta || '';
  const state = data?.state || '';
  const byteCount = <ByteCount byteCount={(meta?.length || 0) + (state?.length || 0)}/>

  // 数据变化时用变量标记一段时间以实现高亮
  useEffect(() => {
    if (!data) return;
    setIsUpdated(true);
    const timer = setTimeout(() => setIsUpdated(false), 500);
    return () => clearTimeout(timer);
  }, [data]);

  useEffect(() => {
    [metaTextareaRef, stateTextareaRef].forEach(ref => {
      if (ref.current) {
        ref.current.style.height = 'auto';
        ref.current.style.height = `${ref.current.scrollHeight}px`;
      }
    });
  }, [data]);

  // 窗口容器的通用样式
  const containerClasses = `
    rounded-xl overflow-hidden transition-all duration-300
    ${containerBgTextClass}
    ${isUpdated ? `ring-2 ${updateRingClass}` : ''} {/* 如果有更新，显示主题色的 Ring */}
    shadow-2xl border ${darkMode ? 'border-gray-700' : containerBorderClass}
    ${/* ${isMaximized ? 'fixed z-50' : 'relative w-full max-w-2xl'} */ ''} // 注释并替换为空字符串
    ${isMaximized ? 'fixed z-50 !rounded-lg' : 'relative'}
  `;

  // 最大化时的固定定位样式
  const maximizedStyle = {
        position: 'fixed',
        top: '10%',
        left: '25%',
        right: '25%',
        bottom: '10%',
        zIndex: 50,
        borderRadius: '0.5rem'
      };

  return (
    <div
      className={containerClasses}
      onDoubleClick={() => setIsMaximized(!isMaximized)}
      style={isMaximized ? maximizedStyle : {}}
    >
      {/* 1. 组合：WindowHeader，传入 headerClass 来定制颜色 */}
      <WindowHeader
        title={windowConfig?.windowTitle || "窗口 (Window)"}
        darkMode={darkMode}
        isMaximized={isMaximized}
        setIsMaximized={setIsMaximized}
        actions={byteCount}
        headerClass={headerClass}
      />

      {/* 2. 组合：WindowTabs，传入 accentClass 来定制激活颜色 */}
      <WindowTabs
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        darkMode={darkMode}
        accentClass={accentClass}
      />

      {/* 3. 组合：WindowContent，注入 Tab 内容 */}
      <WindowContent>
        {activeTab === 'meta' && (
          <TextBox
            value={meta}
            onChange={(e) => onUpdate('code', { ...data, meta: e.target.value })}
            darkMode={darkMode}
            placeholder="输入代码窗口的meta信息..."
            rows={isMaximized ? 20 : 6}
            focusRingClass={focusRingClass} // 传入 focusRingClass
          />
        )}

        {activeTab === 'state' && (
          <TextBox
            value={state}
            onChange={(e) => onUpdate('code', { ...data, state: e.target.value })}
            darkMode={darkMode}
            placeholder={`输入代码...`}
            rows={isMaximized ? 20 : 8}
            focusRingClass={focusRingClass} // 传入 focusRingClass
          />
        )}
      </WindowContent>

      {/* 底部状态栏 */}
      <div className={`p-3 border-t text-sm ${darkMode ? 'bg-gray-700 border-gray-600' : 'bg-gray-100 border-gray-200'} flex justify-between`}>
          <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>Meta: {meta?.length || 0} 字符</span>
          <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>State: {state?.length || 0} 字符</span>
      </div>

    </div>
  );
};


// --- 5. App 演示主题切换 (根组件) ---

const App = () => {
    // 模拟数据和更新函数
    const mockData = {
        meta: "// 元数据信息",
        state: "console.log('应用状态代码');",
    };
    const handleUpdate = (type, newData) => {
        // 实际应用中，这里会调用 Firestore 或其他状态管理更新数据
        console.log(`Updating ${type} with new data:`, newData);
    };

    const [currentTheme, setCurrentTheme] = useState('red');
    const [isDark, setIsDark] = useState(true);

    const themeOptions = ['red', 'blue', 'green'];

    return (
        <div className={`min-h-screen p-8 transition-colors ${isDark ? 'bg-gray-900' : 'bg-gray-100'}`}>
            <h1 className="text-3xl font-bold text-center mb-6" style={{ color: isDark ? 'white' : 'black' }}>
                预制主题切换示例 (Theme: {currentTheme})
            </h1>

            <div className="flex justify-center items-center space-x-4 mb-10">
                {/* 主题选择下拉框 */}
                <select
                    value={currentTheme}
                    onChange={(e) => setCurrentTheme(e.target.value)}
                    className="p-2 border rounded-lg shadow-md bg-white text-gray-800"
                >
                    {themeOptions.map(t => (
                        <option key={t} value={t}>{t} 主题</option>
                    ))}
                </select>
                {/* 模式切换按钮 */}
                <button
                    onClick={() => setIsDark(!isDark)}
                    className={`p-2 rounded-lg font-medium text-white shadow-md transition-colors ${isDark ? 'bg-indigo-700 hover:bg-indigo-600' : 'bg-gray-500 hover:bg-gray-600'}`}
                >
                    切换到 {isDark ? '浅色' : '深色'} 模式
                </button>
            </div>

            <div className="flex justify-center">
                {/* 渲染 BaseWindow，只需要传入主题名即可改变所有颜色 */}
                <BaseWindow
                    data={mockData}
                    onUpdate={handleUpdate}
                    darkMode={isDark}
                    isUpdated={true}
                    theme={currentTheme}
                />
            </div>
        </div>
    );
}

export default App;
