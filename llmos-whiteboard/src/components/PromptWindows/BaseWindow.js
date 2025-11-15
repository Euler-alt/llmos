import React, {useEffect, useRef, useState} from "react";
import {useThemeClasses} from "./Theme";
import {ByteCount, TextBox, WindowContent, WindowHeader, WindowTabs} from "./structure";

import {event_call} from "../../api/api";
/**
 * BaseWindow 组件，通过 theme 属性接收预制的主题名称。
 */
export const BaseWindow = ({ data, darkMode, windowConfig}) => {
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
  const meta = typeof data?.meta === 'string' ? data.meta : JSON.stringify(data?.meta || {}, null, 2);
  const state = typeof data?.state === 'string' ? data.state : JSON.stringify(data?.state || {}, null, 2);
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
            onChange={(e) => event_call('code', { ...data, meta: e.target.value })}
            darkMode={darkMode}
            placeholder="输入代码窗口的meta信息..."
            rows={isMaximized ? 20 : 6}
            focusRingClass={focusRingClass} // 传入 focusRingClass
            isMaximized={isMaximized} // 传递放大状态
          />
        )}

        {activeTab === 'state' && (
          <TextBox
            value={state}
            onChange={(e) => event_call('code', { ...data, state: e.target.value })}
            darkMode={darkMode}
            placeholder={`输入代码...`}
            rows={isMaximized ? 20 : 8}
            focusRingClass={focusRingClass} // 传入 focusRingClass
            isMaximized={isMaximized} // 传递放大状态
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


// ---  App 演示主题切换 (根组件) ---

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
