/**
 * 动态组件注册表
 * 支持后端配置驱动的动态窗口生成
 */

import KernelWindow from './PromptWindows/KernelWindow';
import HeapWindow from './PromptWindows/HeapWindow';
import StackWindow from './PromptWindows/StackWindow';
import CodeWindow from './PromptWindows/CodeWinodw';
import TextWindow from "./PromptWindows/TextWindow";
import ChatWindow from "./PromptWindows/ChatWindow";
// 组件注册表 - 前端声明可用的组件类型
const componentRegistry = {
  chat:{
    component:ChatWindow,
    defaultConfig:{
      title: '对话窗口',
      description: '对话交互',
      theme: 'orange',
      icon: 'text',
      tabs: ['meta', 'state','chat']
    }
  },
  text:{
    component: TextWindow,
    defaultConfig:{
      title: '通用文本窗口',
      description: '通用展示一段文本',
      theme: 'blue',
      icon: 'text',
      tabs: ['meta', 'state']
    }
  },
  kernel: {
    component: KernelWindow,
    defaultConfig: {
      title: '内核窗口 (Kernel)',
      description: '系统规则和工作流程',
      theme: 'blue',
      icon: 'kernel',
      tabs: ['meta', 'state']
    }
  },
  heap: {
    component: HeapWindow,
    defaultConfig: {
      title: '堆窗口 (Heap)',
      description: '持久化存储区域',
      theme: 'green',
      icon: 'heap',
      tabs: ['meta', 'state']
    }
  },
  stack: {
    component: StackWindow,
    defaultConfig: {
      title: '栈模块 (Stack)',
      description: '临时工作区域',
      theme: 'yellow',
      icon: 'stack',
      tabs: ['meta', 'state']
    }
  },
  code: {
    component: CodeWindow,
    defaultConfig: {
      title: '代码窗口 (Code)',
      description: '代码编辑和执行区域',
      theme: 'red',
      icon: 'code',
      tabs: ['meta', 'state']
    }
  }
};

/**
 * 注册新组件类型
 * @param {string} type - 组件类型标识
 * @param {React.Component} component - React组件
 * @param {Object} config - 组件默认配置
 */
export const registerComponent = (type, component, config = {}) => {
  if (componentRegistry[type]) {
    console.warn(`组件类型 "${type}" 已存在，将被覆盖`);
  }
  
  componentRegistry[type] = {
    component,
    defaultConfig: {
      title: type.charAt(0).toUpperCase() + type.slice(1),
      description: '自定义组件',
      theme: 'gray',
      icon: 'custom',
      tabs: ['meta', 'state'],
      ...config
    }
  };
};

/**
 * 获取组件配置
 * @param {string} type - 组件类型
 * @param {Object} backendConfig - 后端提供的配置（覆盖默认配置）
 * @returns {Object} 合并后的配置
 */
export const getComponentConfig = (type, backendConfig = {}) => {
  const baseConfig = componentRegistry[type]?.defaultConfig || {
    title: type,
    description: '未知组件',
    theme: 'gray',
    icon: 'unknown',
    tabs: ['meta', 'state']
  };
  
  return {
    ...baseConfig,
    ...backendConfig,
    type: type // 确保类型标识始终存在
  };
};

/**
 * 获取组件实例
 * @param {string} type - 组件类型
 * @returns {React.Component|null} 组件类
 */
export const getComponent = (type) => {
  return componentRegistry[type]?.component || null;
};

/**
 * 获取所有可用的组件类型
 * @returns {string[]} 组件类型列表
 */
export const getAvailableComponentTypes = () => {
  return Object.keys(componentRegistry);
};

/**
 * 验证后端配置的有效性
 * @param {Object} backendConfig - 后端配置
 * @returns {boolean} 是否有效
 */
export const validateBackendConfig = (backendConfig) => {
  if (!backendConfig || typeof backendConfig !== 'object') {
    return false;
  }
  
  // 检查是否包含 windows 配置数组（新式格式）
  if ('windows' in backendConfig) {
    // 新式格式验证
    if (!Array.isArray(backendConfig.windows)) {
      return false;
    }
    
    // 检查每个窗口配置
    for (const windowConfig of backendConfig.windows) {
      if (!windowConfig.type || !componentRegistry[windowConfig.type]) {
        console.warn(`未知的组件类型: ${windowConfig.type}`);
        return false;
      }
    }
    
    return true;
  }
  
  // 传统格式验证：检查是否包含至少一个已知的模块类型
  const knownTypes = getAvailableComponentTypes();
  for (const key in backendConfig) {
    if (knownTypes.includes(key)) {
      return true;
    }
  }
  
  return false;
};

export default componentRegistry;