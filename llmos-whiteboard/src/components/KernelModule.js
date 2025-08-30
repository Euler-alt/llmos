import React from 'react';

const KernelModule = ({ data, onUpdate }) => {
  return (
    <div style={moduleStyle}>
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
  backgroundColor: '#f8f8f8'
};

const textAreaStyle = {
  width: '100%',
  resize: 'none',
  fontFamily: 'monospace',
  fontSize: '14px'
};

export default KernelModule;