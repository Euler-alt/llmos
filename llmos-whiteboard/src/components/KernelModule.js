import React, { useState, useEffect } from 'react';

const KernelModule = ({ data, onUpdate }) => {
  const [isUpdated, setIsUpdated] = useState(false);
    // 监听 data 变化，高亮一下
  useEffect(() => {
    if (!data) return;
    setIsUpdated(true);
    const timer = setTimeout(() => setIsUpdated(false), 500); // 500ms 后消失
    return () => clearTimeout(timer);
  }, [data]);
  return (
     <div style={{ ...moduleStyle, backgroundColor: isUpdated ? '#ff8c00' : '#9cd7d7' }}>
      <h4>内核模块 (Kernel)</h4>
      <textarea
        style={textAreaStyle}
        value={data}
        onChange={(e) => onUpdate('kernel', e.target.value)}
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
  backgroundColor: '#9cd7d7'
};

const textAreaStyle = {
  width: '100%',
  resize: 'none',
  fontFamily: 'monospace',
  fontSize: '14px'
};

export default KernelModule;