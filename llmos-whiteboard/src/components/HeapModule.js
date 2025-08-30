import React from 'react';

const HeapModule = ({ data, onUpdate }) => {
  return (
    <div style={moduleStyle}>
      <h4>堆模块 (Heap)</h4>
      <textarea
        style={textAreaStyle}
        value={data}
        onChange={(e) => onUpdate('heap', e.target.value)}
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
  backgroundColor: '#e6f3ff'
};

const textAreaStyle = {
  width: '100%',
  resize: 'none',
  fontFamily: 'monospace',
  fontSize: '14px'
};

export default HeapModule;