import React, { useState } from 'react';

const PromptDisplay = ({ prompt, darkMode }) => {
  const [isCopied, setIsCopied] = useState(false);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(prompt).then(() => {
      setIsCopied(true);
      setTimeout(() => setIsCopied(false), 2000);
    });
  };
  
  return (
    <div className={`
      rounded-lg overflow-hidden shadow-lg
      ${darkMode ? 'bg-gray-800 text-gray-200' : 'bg-gray-100 text-gray-800'}
      transition-colors duration-300
    `}>
      <div className={`
        p-4 flex justify-between items-center
        ${darkMode ? 'bg-purple-900' : 'bg-purple-600'} text-white
      `}>
        <h3 className="text-lg font-medium flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
            <path fillRule="evenodd" d="M12.316 3.051a1 1 0 01.633 1.265l-4 12a1 1 0 11-1.898-.632l4-12a1 1 0 011.265-.633zM5.707 6.293a1 1 0 010 1.414L3.414 10l2.293 2.293a1 1 0 11-1.414 1.414l-3-3a1 1 0 010-1.414l3-3a1 1 0 011.414 0zm8.586 0a1 1 0 011.414 0l3 3a1 1 0 010 1.414l-3 3a1 1 0 11-1.414-1.414L16.586 10l-2.293-2.293a1 1 0 010-1.414z" clipRule="evenodd" />
          </svg>
          总组装提示词 (Complete Assembled Prompt)
        </h3>
        <button
          onClick={handleCopy}
          className={`
            px-3 py-1 rounded text-sm flex items-center
            ${darkMode 
              ? 'bg-purple-800 hover:bg-purple-700' 
              : 'bg-purple-500 hover:bg-purple-400'
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
              复制提示词
            </>
          )}
        </button>
      </div>
      
      <div className={`p-4 ${darkMode ? 'bg-gray-800' : 'bg-white'}`}>
        <div className={`
          rounded border p-4 max-h-96 overflow-y-auto font-mono text-sm
          ${darkMode 
            ? 'bg-gray-900 border-gray-700 text-gray-300' 
            : 'bg-gray-50 border-gray-200 text-gray-800'
          }
        `}>
          <pre className="whitespace-pre-wrap">{prompt || '暂无提示词数据'}</pre>
        </div>
        
        <div className="mt-3 flex justify-between text-sm">
          <div>
            <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>
              提示词长度: {prompt?.length || 0} 字符
            </span>
          </div>
          <div>
            <span className={darkMode ? 'text-gray-400' : 'text-gray-500'}>
              估计 Token 数: ~{Math.round((prompt?.length || 0) / 4)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PromptDisplay;