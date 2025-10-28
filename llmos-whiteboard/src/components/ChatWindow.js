import React, { useState, useEffect, useRef } from 'react';

const ChatWindow = ({ data, onUpdate, darkMode }) => {
  const [isUpdated, setIsUpdated] = useState(false);
  const [activeTab, setActiveTab] = useState('state');
  const [isMaximized, setIsMaximized] = useState(false);
  const metaTextareaRef = useRef(null);
  const stateTextareaRef = useRef(null);
  const [messages, setMessages] = useState([]);  // 🆕 新增对话数据
  const [input, setInput] = useState("");         // 🆕 聊天输入框

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
    const userMsg = { role: "user", text: input };
    setMessages(prev => [...prev, userMsg]);
    setInput("");

    try {
      // 向后端发送
      const res = await onUpdate("user_response", { text: input });

      // 假设 handleUpdate 里返回 fetch 的结果
      const data = await res.json();
      const botMsg = { role: "assistant", text: data.output };

      setMessages(prev => [...prev, botMsg]);
      onUpdate("chat", { messages: [...messages, userMsg, botMsg] });

    } catch (err) {
      console.error(err);
    }
  };

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

  const getTabClass = (tab) => {
    const baseClass = "px-4 py-2 font-medium rounded-t-lg transition-colors duration-200";
    const activeClass = darkMode
      ? "bg-gray-700 text-white border-b-2 border-blue-500"
      : "bg-white text-gray-800 border-b-2 border-blue-500";
    const inactiveClass = darkMode
      ? "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-300"
      : "bg-gray-100 text-gray-600 hover:bg-gray-200";

    return `${baseClass} ${activeTab === tab ? activeClass : inactiveClass}`;
  };

  return (
    <div
      className={`
        rounded-xl overflow-hidden transition-all duration-300
        ${darkMode ? 'bg-gray-800 text-gray-200' : 'bg-indigo-50 text-gray-800'}
        ${isUpdated ? (darkMode ? 'ring-2 ring-blue-500' : 'ring-2 ring-blue-400') : ''}
        shadow-lg border ${darkMode ? 'border-gray-700' : 'border-indigo-200'}
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
      {/* 主头部 */}
      <div className={`
        p-4 flex justify-between items-center
        ${darkMode ? 'bg-blue-900' : 'bg-blue-600'} text-white
      `}>
        <h3 className="text-lg font-medium flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M4 4a2 2 0 012-2h4.586A2 2 0 0112 2.586L15.414 6A2 2 0 0116 7.414V16a2 2 0 01-2 2H6a2 2 0 01-2-2V4zm2 6a1 1 0 011-1h6a1 1 0 110 2H7a1 1 0 01-1-1zm1 3a1 1 0 100 2h6a1 1 0 100-2H7z" clipRule="evenodd" />
          </svg>
          文本窗口 (Text)
        </h3>

        <div className="flex items-center space-x-3">
          <span className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full font-medium">
            {(meta?.length || 0) + (state?.length || 0)} 字节
          </span>
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

      {/* 标签页 */}
      <div className="flex border-b border-gray-200 dark:border-gray-700">
        <button className={getTabClass('meta')} onClick={() => setActiveTab('meta')}>
          Meta 信息
        </button>
        <button className={getTabClass('state')} onClick={() => setActiveTab('state')}>
          State 信息
        </button>
        <button className={getTabClass('chat')} onClick={() => setActiveTab('chat')}>
          Chat 对话
        </button>
      </div>

      {/* 内容区域 */}
      <div className="p-4">
        {activeTab === 'meta' && (
          <div className={`
            rounded border p-4 min-h-[200px] max-h-96 overflow-y-auto
            ${darkMode 
              ? 'bg-gray-700 border-gray-600 text-gray-200' 
              : 'bg-gray-50 border-gray-200 text-gray-800'
            }
          `}>
            <textarea
              ref={metaTextareaRef}
              className={`
                w-full p-3 rounded border font-mono text-sm resize-none
                focus:outline-none focus:ring-2 transition-colors duration-200
                ${darkMode 
                  ? 'bg-gray-700 text-gray-200 border-gray-600 focus:ring-blue-500' 
                  : 'bg-white text-gray-800 border-gray-300 focus:ring-blue-400'
                }
              `}
              value={meta || ''}
              onChange={(e) => onUpdate('text', { ...data, meta: e.target.value })}
              rows="6"
              placeholder="输入文本窗口的meta信息..."
            />
          </div>
        )}

        {activeTab === 'state' && (
          <div className={`
            rounded border p-4 min-h-[200px] max-h-96 overflow-y-auto
            ${darkMode 
              ? 'bg-gray-700 border-gray-600 text-gray-200' 
              : 'bg-gray-50 border-gray-200 text-gray-800'
            }
          `}>
            <textarea
              ref={stateTextareaRef}
              className={`
                w-full p-3 rounded border font-mono text-sm resize-none
                focus:outline-none focus:ring-2 transition-colors duration-200
                ${darkMode 
                  ? 'bg-gray-700 text-gray-200 border-gray-600 focus:ring-blue-500' 
                  : 'bg-white text-gray-800 border-gray-300 focus:ring-blue-400'
                }
              `}
              value={state || ''}
              onChange={(e) => onUpdate('text', { ...data, state: e.target.value })}
              rows="8"
              placeholder="输入文本窗口的state信息..."
              spellCheck="false"
            />
          </div>
        )}
        {activeTab === 'chat' && (
          <div
            className={`rounded border p-4 min-h-[300px] max-h-[500px] flex flex-col
              ${darkMode 
                ? 'bg-gray-700 border-gray-600 text-gray-200' 
                : 'bg-gray-50 border-gray-200 text-gray-800'
              }`}
          >
            <div className="flex-1 overflow-y-auto space-y-3">
              {messages.map((m, i) => (
                <div
                  key={i}
                  className={`p-2 rounded-lg max-w-[80%] ${
                    m.role === 'user'
                      ? (darkMode ? 'bg-blue-600 ml-auto text-white' : 'bg-blue-500 ml-auto text-white')
                      : (darkMode ? 'bg-gray-600 text-gray-100' : 'bg-gray-200 text-gray-800')
                  }`}
                >
                  {m.text}
                </div>
              ))}
              <div ref={chatEndRef}></div>
            </div>

            {/* 输入框 */}
            <div className="mt-3 flex space-x-2">
              <textarea
                ref={chatInputTextareaRef}
                value={input}
                onChange={e => setInput(e.target.value)}
                rows="2"
                className={`flex-1 p-2 rounded border resize-none font-mono text-sm
                  ${darkMode 
                    ? 'bg-gray-800 text-gray-200 border-gray-600 focus:ring-blue-500' 
                    : 'bg-white text-gray-800 border-gray-300 focus:ring-blue-400'
                  }`}
                placeholder="输入消息..."
              />
              <button
                onClick={handleSendMessage}
                className={`px-4 py-2 rounded font-semibold
                  ${darkMode
                    ? 'bg-blue-600 hover:bg-blue-700 text-white'
                    : 'bg-blue-500 hover:bg-blue-600 text-white'
                  }`}
              >
                发送
              </button>
            </div>
          </div>
        )}
        <div className="mt-3 flex justify-between text-sm">
          <div>
            <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>
              Meta: {meta?.length || 0} 字符
            </span>
          </div>
          <div>
            <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>
              State: {state?.length || 0} 字符
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatWindow;

