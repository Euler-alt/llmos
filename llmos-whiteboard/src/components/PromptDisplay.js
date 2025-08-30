import React from 'react';

const PromptDisplay = ({ prompt }) => {
  return (
    <div style={displayStyle}>
      <h3>总组装提示词 (Complete Assembled Prompt)</h3>
      <div style={promptTextStyle}>
        <pre>{prompt}</pre>
      </div>
    </div>
  );
};

const displayStyle = {
  border: '2px solid #333',
  borderRadius: '10px',
  padding: '20px',
  marginTop: '20px',
  backgroundColor: '#f0f0f0'
};

const promptTextStyle = {
  whiteSpace: 'pre-wrap',
  wordWrap: 'break-word',
  maxHeight: '400px',
  overflowY: 'auto',
  fontFamily: 'monospace',
  fontSize: '16px',
  lineHeight: '1.5',
};

export default PromptDisplay;