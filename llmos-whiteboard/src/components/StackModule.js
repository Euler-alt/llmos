import React from 'react';

const StackModule = ({ data, onUpdate }) => {
  return (
    <div style={moduleStyle}>
      <h4>栈模块 (Stack)</h4>
      <textarea
        style={textAreaStyle}
        value={data}
        onChange={(e) => onUpdate('stack', e.target.value)}
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
  backgroundColor: '#fffbe6'
};

const textAreaStyle = {
  width: '100%',
  resize: 'none',
  fontFamily: 'monospace',
  fontSize: '14px'
};

export default StackModule;