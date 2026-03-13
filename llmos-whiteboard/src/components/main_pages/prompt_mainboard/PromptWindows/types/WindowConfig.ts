import {WindowIcon, WindowTheme} from "../Theme";
import {ComponentType} from "react";

export interface WindowConfig {
  windowType: string;
  windowId: string;
  windowTitle: string;
  description?: string;
  windowTheme: WindowTheme;
  icon: WindowIcon;
  tabs: string[];
  [key: string]: any; // 允许后端扩展其他自定义字段
}

export interface WindowProps<T = {}> {
  data: any
  darkMode: boolean
  windowConfig: WindowConfig
  onUpdate?: any
  isUpdated?: boolean
  extra?: T  // 扩展字段
}

export type WindowComponent = ComponentType<WindowProps>

export interface RegistryEntry {
  component: WindowComponent; // 接受任何 React 组件
  defaultConfig: WindowConfig;
}