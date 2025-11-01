/**
 * 动态窗口工厂
 * 根据后端配置动态生成窗口组件
 */

import React from 'react';
import { getComponent, getComponentConfig } from './ComponentRegistry';

/**
 * 动态窗口组件
 * @param {Object} props
 * @param {Object} props.config - 窗口配置
 * @param {Object} props.data - 窗口数据
 * @param {Function} props.onUpdate - 更新回调
 * @param {boolean} props.darkMode - 暗黑模式
 */
const DynamicWindow = ({ config, data, onUpdate, darkMode }) => {
  const Component = getComponent(config.type);
  
  if (!Component) {
    return (
      <div className={`
        rounded-xl p-4 border-2 border-dashed
        ${darkMode 
          ? 'bg-gray-800 border-gray-600 text-gray-400' 
          : 'bg-gray-100 border-gray-300 text-gray-600'
        }
      `}>
        <div className="flex items-center justify-center h-32">
          <div className="text-center">
            <svg className="w-12 h-12 mx-auto mb-2 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
            <p className="font-medium">未知组件类型</p>
            <p className="text-sm opacity-75">{config.type}</p>
          </div>
        </div>
      </div>
    );
  }
  
  // 合并配置和数据
  const componentConfig = getComponentConfig(config.type, config);
  return (
    <Component 
      data={data}
      onUpdate={onUpdate}
      darkMode={darkMode}
      windowConfig = {componentConfig}
    />
  );
};

/**
 * 动态窗口工厂
 * @param {Object} props
 * @param {Array} props.windowConfigs - 窗口配置数组
 * @param {Object} props.windowsData - 窗口数据对象
 * @param {Function} props.onUpdate - 更新回调
 * @param {boolean} props.darkMode - 暗黑模式
 */
const DynamicWindowFactory = ({ windowConfigs = [], windowsData = {}, onUpdate, darkMode }) => {
  if (!Array.isArray(windowConfigs) || windowConfigs.length === 0) {
    return (
      <div className={`
        rounded-lg p-6 text-center
        ${darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-100 text-gray-600'}
      `}>
        <svg className="w-16 h-16 mx-auto mb-4 opacity-50" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
        </svg>
        <p className="text-lg font-medium">等待后端配置</p>
        <p className="text-sm">后端将动态推送窗口配置</p>
      </div>
    );
  }
  
  return (
    <div className="space-y-6">
      {windowConfigs.map((windowConfig, index) => (
        <DynamicWindow
          key={windowConfig.id || `${windowConfig.type}-${index}`}
          config={windowConfig}
          data={windowsData[windowConfig.title] || {}}
          onUpdate={onUpdate}
          darkMode={darkMode}
        />
      ))}
    </div>
  );
};

export default DynamicWindowFactory;