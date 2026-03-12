/**
 * 动态组件协议演示
 * 展示如何使用新的动态组件系统
 */

import React, { useState, useEffect } from 'react';
import DynamicWindowFactory from '../components/main_pages/prompt_mainboard/PromptWindows/DynamicWindowFactory';
import { registerWindows, getAvailableWindowsTypes } from '../components/main_pages/prompt_mainboard/PromptWindows/WindowsRegistry';
import { mockBackendSSEData, backendIntegrationHelpers } from '../protocols/BackendIntegrationExample';

// 模拟自定义组件
const CustomAnalyticsWindow = ({ data, onUpdate, darkMode }) => {
  const [activeTab, setActiveTab] = useState('dashboard');
  
  const getTabClass = (tab) => {
    const baseClass = "px-4 py-2 font-medium rounded-t-lg transition-colors duration-200";
    const activeClass = darkMode 
      ? "bg-gray-700 text-white border-b-2 border-purple-500" 
      : "bg-white text-gray-800 border-b-2 border-purple-500";
    const inactiveClass = darkMode 
      ? "bg-gray-800 text-gray-400 hover:bg-gray-700 hover:text-gray-300" 
      : "bg-gray-100 text-gray-600 hover:bg-gray-200";
    
    return `${baseClass} ${activeTab === tab ? activeClass : inactiveClass}`;
  };
  
  return (
    <div className={`
      rounded-xl overflow-hidden transition-all duration-300
      ${darkMode ? 'bg-gray-800 text-gray-200' : 'bg-purple-50 text-gray-800'}
      shadow-lg border ${darkMode ? 'border-gray-700' : 'border-purple-200'}
    `}>
      {/* 头部 */}
      <div className={`
        px-4 py-3 font-semibold flex items-center justify-between
        ${darkMode ? 'bg-purple-900 text-white' : 'bg-purple-600 text-white'}
      `}>
        <div className="flex items-center">
          <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20">
            <path d="M2 10a8 8 0 1116 0 8 8 0 01-16 0zm8-6a6 6 0 00-6 6 6 6 0 006 6 6 6 0 006-6 6 6 0 00-6-6z"/>
          </svg>
          数据分析面板
        </div>
      </div>
      
      {/* 标签页 */}
      <div className="flex border-b border-gray-600">
        <button 
          className={getTabClass('dashboard')}
          onClick={() => setActiveTab('dashboard')}
        >
          仪表板
        </button>
        <button 
          className={getTabClass('metrics')}
          onClick={() => setActiveTab('metrics')}
        >
          指标
        </button>
        <button 
          className={getTabClass('reports')}
          onClick={() => setActiveTab('reports')}
        >
          报告
        </button>
      </div>
      
      {/* 内容区域 */}
      <div className="p-4">
        {activeTab === 'dashboard' && (
          <div>
            <h3 className="text-lg font-medium mb-3">数据分析仪表板</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded">
                <p className="text-sm opacity-75">活跃用户</p>
                <p className="text-2xl font-bold">1,234</p>
              </div>
              <div className="bg-gray-100 dark:bg-gray-700 p-3 rounded">
                <p className="text-sm opacity-75">请求次数</p>
                <p className="text-2xl font-bold">8,567</p>
              </div>
            </div>
          </div>
        )}
        
        {activeTab === 'metrics' && (
          <div>
            <h3 className="text-lg font-medium mb-3">关键指标</h3>
            <textarea
              className="w-full p-2 border rounded bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200"
              rows="6"
              placeholder="指标数据..."
              value={data?.metrics || ''}
              onChange={(e) => onUpdate && onUpdate('custom-analytics', {
                ...data,
                metrics: e.target.value
              })}
            />
          </div>
        )}
        
        {activeTab === 'reports' && (
          <div>
            <h3 className="text-lg font-medium mb-3">分析报告</h3>
            <textarea
              className="w-full p-2 border rounded bg-white dark:bg-gray-700 text-gray-800 dark:text-gray-200"
              rows="6"
              placeholder="报告内容..."
              value={data?.reports || ''}
              onChange={(e) => onUpdate && onUpdate('custom-analytics', {
                ...data,
                reports: e.target.value
              })}
            />
          </div>
        )}
      </div>
    </div>
  );
};

// 注册自定义组件
registerWindows('custom-analytics', CustomAnalyticsWindow, {
  title: '数据分析面板',
  color: 'purple',
  tabs: ['dashboard', 'metrics', 'reports']
});

const DynamicComponentDemo = () => {
  const [demoConfig, setDemoConfig] = useState(null);
  const [windowsData, setWindowsData] = useState({});
  const [darkMode, setDarkMode] = useState(false);
  const [availableComponents, setAvailableComponents] = useState([]);

  useEffect(() => {
    // 获取可用的组件类型
    setAvailableComponents(getAvailableWindowsTypes());
    
    // 模拟后端配置加载
    const loadDemoConfig = () => {
      // 使用动态扩展配置
      const config = backendIntegrationHelpers.normalizeConfig(
        mockBackendSSEData.dynamicExtension
      );
      setDemoConfig(config);
      setWindowsData(config.windows || {});
    };
    
    loadDemoConfig();
  }, []);

  const handleUpdate = (moduleName, newData) => {
    setWindowsData(prev => ({
      ...prev,
      [moduleName]: newData
    }));
    console.log('更新数据:', moduleName, newData);
  };

  const switchDemo = (demoType) => {
    let config;
    switch(demoType) {
      case 'legacy':
        config = backendIntegrationHelpers.normalizeConfig(
          mockBackendSSEData.legacyFormat
        );
        break;
      case 'protocol':
        config = backendIntegrationHelpers.normalizeConfig(
          mockBackendSSEData.protocolFormat
        );
        break;
      case 'dynamic':
        config = backendIntegrationHelpers.normalizeConfig(
          mockBackendSSEData.dynamicExtension
        );
        break;
      default:
        config = backendIntegrationHelpers.generateTestConfig();
    }
    
    setDemoConfig(config);
    setWindowsData(config.windows || {});
  };

  if (!demoConfig) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p>加载演示配置...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={`${darkMode ? 'bg-gray-900 text-white' : 'bg-gray-50 text-gray-800'} min-h-screen p-6`}>
      <div className="max-w-6xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold">动态组件协议演示</h1>
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            {darkMode ? '☀️ 亮色模式' : '🌙 暗色模式'}
          </button>
        </div>

        {/* 演示控制面板 */}
        <div className="bg-white dark:bg-gray-800 rounded-lg p-4 mb-6 shadow">
          <h2 className="text-xl font-semibold mb-3">演示控制</h2>
          <div className="flex gap-2 mb-4">
            <button 
              onClick={() => switchDemo('legacy')}
              className="px-3 py-2 bg-gray-200 dark:bg-gray-700 rounded hover:bg-gray-300 dark:hover:bg-gray-600"
            >
              传统格式
            </button>
            <button 
              onClick={() => switchDemo('protocol')}
              className="px-3 py-2 bg-blue-200 dark:bg-blue-700 rounded hover:bg-blue-300 dark:hover:bg-blue-600"
            >
              协议格式
            </button>
            <button 
              onClick={() => switchDemo('dynamic')}
              className="px-3 py-2 bg-purple-200 dark:bg-purple-700 rounded hover:bg-purple-300 dark:hover:bg-purple-600"
            >
              动态扩展
            </button>
            <button 
              onClick={() => switchDemo('custom')}
              className="px-3 py-2 bg-green-200 dark:bg-green-700 rounded hover:bg-green-300 dark:hover:bg-green-600"
            >
              自定义配置
            </button>
          </div>
          
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <strong>可用组件类型:</strong>
              <div className="mt-1 flex flex-wrap gap-1">
                {availableComponents.map(type => (
                  <span key={type} className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs">
                    {type}
                  </span>
                ))}
              </div>
            </div>
            <div>
              <strong>当前配置:</strong>
              <div className="mt-1">
                窗口数量: {demoConfig.windowConfigs?.length || 0}
              </div>
            </div>
          </div>
        </div>

        {/* 动态窗口展示 */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="space-y-6">
            <DynamicWindowFactory
              windowConfigs={demoConfig.windowConfigs || []}
              windowsData={windowsData}
              onUpdate={handleUpdate}
              darkMode={darkMode}
            />
          </div>
          
          <div className="space-y-6">
            {/* 配置信息展示 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
              <h3 className="text-lg font-semibold mb-3">配置信息</h3>
              <div className="bg-gray-100 dark:bg-gray-900 p-3 rounded text-sm font-mono overflow-auto max-h-60">
                <pre>{JSON.stringify(demoConfig, null, 2)}</pre>
              </div>
            </div>
            
            {/* 数据状态展示 */}
            <div className="bg-white dark:bg-gray-800 rounded-lg p-4 shadow">
              <h3 className="text-lg font-semibold mb-3">数据状态</h3>
              <div className="bg-gray-100 dark:bg-gray-900 p-3 rounded text-sm font-mono overflow-auto max-h-60">
                <pre>{JSON.stringify(windowsData, null, 2)}</pre>
              </div>
            </div>
          </div>
        </div>

        {/* 协议特性说明 */}
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg p-6 shadow">
          <h2 className="text-xl font-semibold mb-4">协议特性</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="p-4 border-l-4 border-blue-500 bg-blue-50 dark:bg-blue-900">
              <h3 className="font-semibold">动态注册</h3>
              <p className="text-sm mt-1">支持运行时注册新组件类型</p>
            </div>
            <div className="p-4 border-l-4 border-green-500 bg-green-50 dark:bg-green-900">
              <h3 className="font-semibold">配置驱动</h3>
              <p className="text-sm mt-1">后端配置决定前端界面</p>
            </div>
            <div className="p-4 border-l-4 border-purple-500 bg-purple-50 dark:bg-purple-900">
              <h3 className="font-semibold">向后兼容</h3>
              <p className="text-sm mt-1">支持传统数据格式平滑迁移</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DynamicComponentDemo;