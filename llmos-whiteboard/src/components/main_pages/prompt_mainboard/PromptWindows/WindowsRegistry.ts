/**
 * 动态组件注册表
 * 支持后端配置驱动的动态窗口生成
 */

import KernelWindow from './windows/KernelWindow';
import HeapWindow from './windows/HeapWindow';
import StackWindow from './windows/StackWindow';
import CodeWindow from './windows/CodeWindow';
import TextWindow from "./windows/TextWindow";
import ChatWindow from "./windows/ChatWindow";

import {RegistryEntry, WindowComponent, WindowConfig} from "./types/WindowConfig";

// 利用 Partial，这样你调用时只传想要修改的字段就行
function createWindowConfig(config: Partial<WindowConfig> = {}): WindowConfig {
  return {
    windowType: 'text', // 默认值
    windowId: '0',
    windowTitle: '未命名窗口',
    windowTheme: 'gray',
    icon: 'unknown',
    tabs: ['meta', 'state'],
    ...config, // 只有在这里覆盖传入的 config
  };
}

// 组件注册表 - 前端声明可用的组件类型
const WindowsRegistry:Record<string,RegistryEntry> = {
  ChatWindow:{
    component:ChatWindow,
    defaultConfig: createWindowConfig({
      windowTitle: '对话窗口',
      description: '对话交互',
      windowTheme: 'orange',
      icon: 'text',
      tabs: ['meta', 'state','chat']
    })
  },
  TextWindow:{
    component: TextWindow,
    defaultConfig:createWindowConfig({
      windowTitle: '通用文本窗口',
      description: '通用展示一段文本',
      windowTheme: 'blue',
      icon: 'text',
      tabs: ['meta', 'state']
    })
  },
  KernelWindow: {
    component: KernelWindow,
    defaultConfig: createWindowConfig({
      windowTitle: '内核窗口 (Kernel)',
      description: '系统规则和工作流程',
      windowTheme: 'blue',
      icon: 'kernel',
      tabs: ['meta', 'state']
    })
  },
  HeapWindow: {
    component: HeapWindow,
    defaultConfig: createWindowConfig({
      windowTitle: '堆窗口 (Heap)',
      description: '持久化存储区域',
      windowTheme: 'green',
      icon: 'heap',
      tabs: ['meta', 'state']
    })
  },
  StackWindow: {
    component: StackWindow,
    defaultConfig: createWindowConfig({
      windowTitle: '栈模块 (Stack)',
      description: '临时工作区域',
      windowTheme: 'yellow',
      icon: 'stack',
      tabs: ['meta', 'state']
    })
  },
  CodeWindow: {
    component: CodeWindow,
    defaultConfig: createWindowConfig({
      windowTitle: '代码窗口 (Code)',
      description: '代码编辑和执行区域',
      windowTheme: 'red',
      icon: 'code',
      tabs: ['meta', 'state']
    })
  }
};

export type WindowType = keyof typeof WindowsRegistry

/**
 * 获取组件配置
 * @param {string} type - 组件类型
 * @param {Partial<WindowConfig>} backendConfig - 后端提供的配置（覆盖默认配置）
 * @returns {WindowConfig} 合并后的配置
 */
export const getWindowsConfig = (type: string, backendConfig: Partial<WindowConfig> = {}): WindowConfig => {
  const baseConfig = WindowsRegistry[type]?.defaultConfig || createWindowConfig({
    windowTitle: type,
    description: '未知组件',
    windowTheme: 'gray',
    icon: 'unknown',
    tabs: ['meta', 'state']
  });
  
  return {
    ...baseConfig,
    ...backendConfig,
    type: type // 确保类型标识始终存在
  };
};

/**
 * 获取组件实例
 * @param {string} type - 组件类型
 * @returns {WindowComponent|null} 组件类
 */
export const getWindow = (type:WindowType): WindowComponent | null => {
  return WindowsRegistry[type]?.component || null;
};

export default WindowsRegistry;