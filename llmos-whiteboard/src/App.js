import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import EditorTab from './components/EditorTab';
import VisualizerTab from './components/VisualizerTab';
import MonitorTab from './components/MonitorTab';

const App = () => {
  const [darkMode, setDarkMode] = useState(false);
  const [activeTab, setActiveTab] = useState('editor'); // 'editor', 'visualizer', 'monitor'
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
  };

  return (
    <div className={`${darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-800'} min-h-screen transition-colors duration-300`}>
      <Navbar 
        darkMode={darkMode} 
        toggleDarkMode={toggleDarkMode} 
        activeTab={activeTab}
        setActiveTab={setActiveTab}
      />
      
      <div className="container mx-auto px-4 py-6">
        <h1 className="text-3xl font-bold mb-4">LLM OS 增强界面</h1>
        <p className="mb-6">数据已通过后端实时推送。当您在任何一个浏览器窗口修改模块文本时，所有窗口都会同步更新。</p>
        
        {activeTab === 'editor' && (
          <EditorTab
            darkMode={darkMode}
          />
        )}
        
        {activeTab === 'visualizer' && (
          <VisualizerTab
            windows={''}
            llmOutput={''}
            darkMode={darkMode}
          />
        )}
        
        {activeTab === 'monitor' && (
          <MonitorTab darkMode={darkMode} />
        )}
      </div>
    </div>
  );
};

// 使用Tailwind CSS，不再需要内联样式

export default App;