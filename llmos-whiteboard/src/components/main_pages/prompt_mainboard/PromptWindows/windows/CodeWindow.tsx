import React, { useState } from 'react';
import { BaseWindow } from "./BaseWindow";
import { WindowProps } from "../types/WindowConfig";

const CodeWindow = (props: WindowProps) => {
  const [language, setLanguage] = useState('python');

  // 渲染头部右侧的动作元素 (语言选择)
  const HeaderActions = (
    <select
      className="text-xs bg-white bg-opacity-20 px-2 py-1 rounded-full border-none focus:outline-none text-white"
      value={language}
      onChange={(e) => setLanguage(e.target.value)}
      onClick={(e) => e.stopPropagation()}
    >
      <option value="python" className="text-gray-800">Python</option>
      <option value="javascript" className="text-gray-800">JavaScript</option>
      <option value="java" className="text-gray-800">Java</option>
      <option value="other" className="text-gray-800">其他</option>
    </select>
  );

  return (
    <BaseWindow
      {...props}
      actions={HeaderActions}
    />
  );
};

export default CodeWindow;
