import CodeMirror from "@uiw/react-codemirror";
import {json} from "@codemirror/lang-json";
import {markdown} from "@codemirror/lang-markdown";
import React, {useEffect, useRef, useState} from "react";

// 通用头部组件 (WindowHeader)
// 负责窗口的标题栏、图标、动作区以及最大化按钮。
// 它通过 headerClass 属性接收主题背景色。
export const WindowHeader = ({title, icon, actions, isMaximized, setIsMaximized, headerClass}) => {
    // 默认代码图标 SVG
    const DefaultIcon = () => (
        <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" style={{width: '20px', height: '20px'}}
             viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd"
                  d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z"
                  clipRule="evenodd"/>
        </svg>
    );

    return (
        // 使用传入的 headerClass 来定制背景色
        <div className={`p-4 flex justify-between items-center ${headerClass} text-white`}>
            <h3 className="text-lg font-medium flex items-center">
                {/* 如果未传入 icon，则使用 DefaultIcon */}
                {icon || <DefaultIcon/>}
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
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" style={{width: '16px', height: '16px'}}
                         viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd"
                              d={isMaximized ? "M3 7a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm0 6a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1z" : "M3 4a1 1 0 011-1h12a1 1 0 011 1v12a1 1 0 01-1 1H4a1 1 0 01-1-1V4zm2 1v10h10V5H5z"}
                              clipRule="evenodd"/>
                    </svg>
                </button>
            </div>
        </div>
    );
};
// 3.2. 通用标签页组件 (WindowTabs)
// 负责标签页的显示和切换逻辑。
// 通过 accentClass 接收主题强调色，用于激活状态下的文本和边框。
export const WindowTabs = ({activeTab, setActiveTab, darkMode, accentClass}) => {
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
    const [language, setLanguage] = useState('other')
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
export const WindowContent = ({children}) => (
    <div className="p-4">
        {children}
    </div>
);
export const TextBox = ({
                            value,
                            onChange,
                            darkMode,
                            placeholder,
                            maxHeight = 200,
                            isMaximized = false,
                            focusRingClass = "",
                        }) => {
    const editorRef = useRef(null);

    // 动态高度：CodeMirror 默认不会自动高，但我们手动控制外层 div 高度
    const actualMaxHeight = isMaximized ? 600 : maxHeight;

    useEffect(() => {
        if (!editorRef.current) return;
        const editor = editorRef.current;

        // CodeMirror 的 DOM 节点结构比较深
        const el = editor.querySelector(".cm-editor");
        if (!el) return;

        // 自动高度逻辑
        el.style.height = "auto";
        const scrollHeight = el.scrollHeight;

        if (scrollHeight <= actualMaxHeight) {
            el.style.height = `${scrollHeight}px`;
            el.style.overflowY = "hidden";
        } else {
            el.style.height = `${actualMaxHeight}px`;
            el.style.overflowY = "auto";
        }
    }, [value, actualMaxHeight]);

    return (
        <div
            ref={editorRef}
            className={`
        rounded border transition-colors duration-200
        ${darkMode
                ? `bg-gray-700 border-gray-600 text-gray-200 ${focusRingClass}`
                : `bg-white border-gray-300 text-gray-800 ${focusRingClass}`}
      `}
        >
            <CodeMirror
                value={value || ""}
                height="auto"
                basicSetup={{
                    lineNumbers: true,
                    foldGutter: true,
                    highlightActiveLine: true,
                }}
                placeholder={placeholder}
                theme={darkMode ? "dark" : "light"}
                extensions={[
                    json(),
                    markdown(),
                ]}
                onChange={(v) => onChange({target: {value: v}})}
            />
        </div>
    );
};