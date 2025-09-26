import React, { useState, useEffect } from 'react';

const CodeModule = ({ data, onUpdate }) => {
  const [isUpdated, setIsUpdated] = useState(false);
  // 监听 data 变化，高亮一下
  useEffect(() => {
    if (!data) return;
    setIsUpdated(true);
    const timer = setTimeout(() => setIsUpdated(false), 500); // 500ms 后消失
    return () => clearTimeout(timer);
  }, [data]);
  return (
    <div style={{ ...moduleStyle, backgroundColor: isUpdated ? '#ff8c00' : '#ccffcc' }}>
      <h4>代码模块 (Code)</h4>
      <textarea
        style={textAreaStyle}
        value={data}
        onChange={(e) => onUpdate('code', e.target.value)}
        rows="5"
      />
    </div>
  );
};

const moduleStyle = {
  border: '1px solid #ccc',
  borderRadius: '8px',
  padding: '16px',
  marginBottom: '16px',
  backgroundColor: '#ccffcc' // 为新模块选择一个不同的背景色
};

const textAreaStyle = {
  width: '100%',
  resize: 'none',
  fontFamily: 'monospace',
  fontSize: '14px'
};

export default CodeModule;