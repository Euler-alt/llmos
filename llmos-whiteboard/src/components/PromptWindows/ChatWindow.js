import React, { useState, useEffect, useRef } from 'react';
import {event_call} from "../../api/api";

const chatWindow_func = 'user_response' //魔法字符串，和后端chat_window对应
const ChatWindow = ({ data, windowConfig,darkMode }) => {
  const [isUpdated, setIsUpdated] = useState(false);
  // activeTab 现在只用于 Meta/State 的切换
  const [activeTab, setActiveTab] = useState('state');
  const [isMaximized, setIsMaximized] = useState(false);

  const metaTextareaRef = useRef(null);
  const stateTextareaRef = useRef(null);

  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");

  const chatEndRef = useRef(null);
  const chatInputTextareaRef = useRef(null);

  const { meta, state } = data || {};

  // 滚动到底部
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  // 发送消息
  const handleSendMessage = async () => {
    if (!input.trim()) return;
    const userMsg = { role: "user", text: input.trim() };

    // 1. 立即清空输入框
    setInput("");

    // 2. 将用户消息添加到聊天记录中 (这是本次交互的唯一消息)
    // 注意：如果 data 里面包含了 messages 历史记录，您可能需要从 data 中读取并更新。
    // 但是在当前设计中，messages 是组件内部状态，我们仅更新它。
    setMessages(prev => [...prev, userMsg]);

    // 3. 通知父组件/后端进行状态更新 (不再期望返回值)
    try {
      await event_call(chatWindow_func, { text: userMsg.text });
    } catch (err) {
      console.error("发送消息到 event_call 失败:", err);
      // 即使发送失败，用户消息仍然保留在界面上，但我们可以添加一个系统提示
      setMessages(prev => [...prev, {
          role: "system",
          text: `⚠️ 上下文同步失败: ${err.message || '未知错误'}`
      }]);
    }
  };

  // 监听 Enter 键发送消息
  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault(); // 阻止默认的换行行为
      handleSendMessage();
    }
  };


  // 视觉更新效果
  useEffect(() => {
    if (!data) return;
    setIsUpdated(true);
    const timer = setTimeout(() => setIsUpdated(false), 500);
    return () => clearTimeout(timer);
  }, [data]);

  // Textarea 高度自适应
  useEffect(() => {
    [metaTextareaRef, stateTextareaRef].forEach(ref => {
      if (ref.current) {
        ref.current.style.height = 'auto';
        ref.current.style.height = `${ref.current.scrollHeight}px`;
      }
    });
  }, [data, activeTab]);

  // 标签页样式辅助函数 (与第一版一致，去掉了 'chat' 标签)
  const getTabClass = (tab) => {
    const baseClass = "px-4 py-2 font-medium rounded-t-lg transition-colors duration-200 cursor-pointer";
    const activeClass = darkMode
      ? "bg-gray-700 text-white border-b-2 border-blue-500"
      : "bg-white text-gray-800 border-b-2 border-blue-500";
    const inactiveClass = darkMode
      ? "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-300"
      : "bg-gray-100 text-gray-600 hover:bg-gray-200";

    return `${baseClass} ${activeTab === tab ? activeClass : inactiveClass}`;
  };

  // ************************** 渲染 **************************

  return (
    <div
      className={`
        rounded-xl overflow-hidden transition-all duration-300 flex flex-col 
        ${darkMode ? 'bg-gray-800 text-gray-200' : 'bg-indigo-50 text-gray-800'}
        ${isUpdated ? (darkMode ? 'ring-2 ring-blue-500' : 'ring-2 ring-blue-400') : ''}
        shadow-lg border ${darkMode ? 'border-gray-700' : 'border-indigo-200'}
        ${isMaximized ? 'fixed z-50 !rounded-lg' : 'relative'}
      `}
      onDoubleClick={() => setIsMaximized(!isMaximized)}
      style={isMaximized ? {
        position: 'fixed',
        top: '5%',
        left: '5%',
        right: '5%',
        bottom: '5%',
        zIndex: 50,
        borderRadius: '0.5rem'
      } : {}}
    >
      {/* 头部 - 保持不变 */}
      <div className={`
        p-4 flex-shrink-0 flex justify-between items-center
        ${darkMode ? 'bg-blue-900' : 'bg-blue-600'} text-white
      `}>
        <h3 className="text-lg font-medium flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
          </svg>
          {windowConfig.windowTitle}
        </h3>

        <div className="flex items-center space-x-3">
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

      {/* 核心内容区 */}
      <div className="flex-grow flex flex-col min-h-0">

        {/* 1. Meta/State 上下文面板 (Context Panel) */}
        <div className={`p-4 flex-shrink-0 border-b ${darkMode ? 'border-gray-700 bg-gray-900' : 'border-gray-200 bg-gray-100'}`}>
            {/* 标签页导航 */}
            <div className="flex border-b border-gray-200 dark:border-gray-700">
                <button className={getTabClass('meta')} onClick={() => setActiveTab('meta')}>
                Meta 信息
                </button>
                <button className={getTabClass('state')} onClick={() => setActiveTab('state')}>
                State 信息
                </button>
            </div>

            {/* 标签页内容 */}
            <div className="pt-4">
              {/* Meta 内容 */}
              {activeTab === 'meta' && (
                <div className={`
                  rounded-lg border p-2 min-h-[120px] max-h-48 overflow-y-auto
                  ${darkMode 
                    ? 'bg-gray-700 border-gray-600 text-gray-200' 
                    : 'bg-white border-gray-200 text-gray-800'
                  }
                `}>
                  <textarea
                    ref={metaTextareaRef}
                    className={`
                      w-full p-2 rounded border-none font-mono text-sm resize-none
                      focus:outline-none h-auto
                      ${darkMode 
                        ? 'bg-gray-700 text-gray-200' 
                        : 'bg-white text-gray-800'
                      }
                    `}
                    value={meta || ''}
                    onChange={(e) => event_call('text', { ...data, meta: e.target.value })}
                    rows="4"
                    placeholder="输入文本窗口的meta信息..."
                    spellCheck="false"
                  />
                </div>
              )}

              {/* State 内容 */}
              {activeTab === 'state' && (
                <div className={`
                  rounded-lg border p-2 min-h-[120px] max-h-48 overflow-y-auto
                  ${darkMode 
                    ? 'bg-gray-700 border-gray-600 text-gray-200' 
                    : 'bg-white border-gray-200 text-gray-800'
                  }
                `}>
                  <textarea
                    ref={stateTextareaRef}
                    className={`
                      w-full p-2 rounded border-none font-mono text-sm resize-none
                      focus:outline-none h-auto
                      ${darkMode 
                        ? 'bg-gray-700 text-gray-200' 
                        : 'bg-white text-gray-800'
                      }
                    `}
                    value={state || ''}
                    onChange={(e) => event_call('text', { ...data, state: e.target.value })}
                    rows="4"
                    placeholder="输入文本窗口的state信息..."
                    spellCheck="false"
                  />
                </div>
              )}

              <div className="mt-2 flex justify-end text-xs">
                <span className={darkMode ? 'text-gray-500' : 'text-gray-400'}>
                    {activeTab === 'meta' ? 'Meta' : 'State'} 字符数: {activeTab === 'meta' ? (meta?.length || 0) : (state?.length || 0)}
                </span>
              </div>
            </div>
        </div>


        {/* 2. 聊天对话区域 (占据中间剩余空间) */}
        <div
          className={`flex-grow overflow-y-auto p-4 space-y-3 
            ${darkMode ? 'bg-gray-800' : 'bg-white'} 
            min-h-[150px]
          `}
        >
          {messages.map((m, i) => (
            <div
              key={i}
              className={`p-3 rounded-xl max-w-[90%] md:max-w-[75%] shadow-sm break-words whitespace-pre-wrap ${
                m.role === 'user'
                  ? (darkMode ? 'bg-blue-600 ml-auto text-white' : 'bg-blue-500 ml-auto text-white')
                  : (darkMode ? 'bg-gray-700 text-gray-100' : 'bg-gray-100 text-gray-800')
              }`}
            >
              {m.text}
            </div>
          ))}
          <div ref={chatEndRef}></div>
        </div>

        {/* 3. 聊天输入框 (Chat Input) */}
        <div className={`p-4 flex-shrink-0 border-t ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="flex space-x-2 items-end">
            <textarea
              ref={chatInputTextareaRef}
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows="1"
              className={`flex-1 p-3 rounded-xl border-2 resize-none text-base 
                ${darkMode 
                  ? 'bg-gray-900 text-gray-200 border-gray-700 focus:border-blue-500' 
                  : 'bg-white text-gray-800 border-gray-300 focus:border-blue-400'
                }
                transition-all duration-200
              `}
              placeholder="输入消息... (Enter 发送, Shift+Enter 换行)"
              style={{ maxHeight: '150px', minHeight: '40px' }}
            />
            <button
              onClick={handleSendMessage}
              disabled={!input.trim()}
              className={`
                px-4 py-2.5 rounded-xl font-semibold transition-colors duration-200 h-fit
                ${!input.trim() 
                    ? 'opacity-50 cursor-not-allowed' 
                    : (darkMode ? 'bg-blue-600 hover:bg-blue-700 text-white' : 'bg-blue-500 hover:bg-blue-600 text-white')
                }
              `}
            >
              发送
            </button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ChatWindow;