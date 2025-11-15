import React from 'react';
import DataFlowDiagram from './DataFlowDiagram';
import ToolVisualizer from './ToolVisualizer';

const VisualizerTab = ({ windows, llmOutput, darkMode }) => {
  return (
    <div className="space-y-6">
      <DataFlowDiagram modules={windows} darkMode={darkMode} />
      <ToolVisualizer llmOutput={llmOutput} darkMode={darkMode} />
    </div>
  );
};

export default VisualizerTab;