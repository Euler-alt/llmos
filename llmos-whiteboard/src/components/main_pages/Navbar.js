import React from 'react';

const Navbar = ({ darkMode, toggleDarkMode, activeTab, setActiveTab }) => {
  return (
    <nav className={`${darkMode ? 'bg-gray-800' : 'bg-blue-600'} text-white shadow-lg transition-colors duration-300`}>
      <div className="container mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center">
            <span className="text-xl font-bold">LLMOS</span>
          </div>
          
          <div className="flex space-x-1">
            <button 
              onClick={() => setActiveTab('editor')}
              className={`px-4 py-2 rounded-lg transition-colors duration-200 ${
                activeTab === 'editor' 
                  ? (darkMode ? 'bg-gray-700' : 'bg-blue-700') 
                  : 'hover:bg-opacity-20 hover:bg-white'
              }`}
            >
              编辑器
            </button>
            
            <button 
              onClick={() => setActiveTab('visualizer')}
              className={`px-4 py-2 rounded-lg transition-colors duration-200 ${
                activeTab === 'visualizer' 
                  ? (darkMode ? 'bg-gray-700' : 'bg-blue-700') 
                  : 'hover:bg-opacity-20 hover:bg-white'
              }`}
            >
              可视化
            </button>
            
            <button 
              onClick={() => setActiveTab('monitor')}
              className={`px-4 py-2 rounded-lg transition-colors duration-200 ${
                activeTab === 'monitor' 
                  ? (darkMode ? 'bg-gray-700' : 'bg-blue-700') 
                  : 'hover:bg-opacity-20 hover:bg-white'
              }`}
            >
              系统监控
            </button>
            
            <button 
              onClick={toggleDarkMode}
              className="ml-4 p-2 rounded-full hover:bg-opacity-20 hover:bg-white transition-colors duration-200"
              aria-label="Toggle dark mode"
            >
              {darkMode ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" style={{ width: '20px', height: '20px' }} viewBox="0 0 20 20" fill="currentColor">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              )}
            </button>
          </div>
        </div>
      </div>
    </nav>
  );
};

export default Navbar;