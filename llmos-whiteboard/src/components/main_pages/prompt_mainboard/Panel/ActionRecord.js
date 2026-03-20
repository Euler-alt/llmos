import React, { useState } from 'react';

const ActionRecord = ({ record, index, darkMode }) => {
  const isError = record.status === 'error' || record.call_type === 'error';
  const [isFolded, setIsFolded] = useState(true);
  
  const hasParams = record.call_kwargs && Object.keys(record.call_kwargs).length > 0;

  return (
    <div className={`
      mb-4 p-3 rounded-lg border-l-4 shadow-sm
      ${darkMode ? 'bg-gray-800 border-gray-700' : 'bg-white border-gray-200'}
      ${isError ? 'border-l-red-500' : 'border-l-blue-500'}
    `}>
      <div className="flex justify-between items-start mb-2">
        <span className={`
          text-xs font-bold px-2 py-0.5 rounded uppercase
          ${isError ? 'bg-red-100 text-red-700' : 'bg-blue-100 text-blue-700'}
        `}>
          {record.func_name || 'System Call'}
        </span>
        <span className="text-[10px] text-gray-500">Step #{index + 1}</span>
      </div>
      
      {record.reasoning && (
        <div className={`text-xs italic mb-2 ${darkMode ? 'text-gray-400' : 'text-gray-500'}`}>
          💡 Reasoning: {record.reasoning}
        </div>
      )}
      
      <div className={`text-sm font-medium break-words whitespace-pre-wrap ${darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
        {record.summary || record.result || 'Executed successfully'}
      </div>
      
      {hasParams && (
        <div className="mt-2">
          <button 
            onClick={() => setIsFolded(!isFolded)}
            className="text-[10px] text-blue-500 hover:text-blue-600 flex items-center focus:outline-none"
          >
            <svg 
              xmlns="http://www.w3.org/2000/svg" 
              className={`h-3 w-3 mr-1 transform transition-transform ${isFolded ? '' : 'rotate-180'}`} 
              viewBox="0 0 20 20" 
              fill="currentColor"
            >
              <path fillRule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
            {isFolded ? '显示参数' : '隐藏参数'}
          </button>
          
          {!isFolded && (
            <div className="mt-1 text-[10px] font-mono bg-black bg-opacity-5 p-2 rounded overflow-x-auto text-left">
              <pre className="whitespace-pre-wrap">{JSON.stringify(record.call_kwargs, null, 2)}</pre>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ActionRecord;
