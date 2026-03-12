import React from 'react';
import {BaseWindow} from "./BaseWindow";
import {WindowProps} from "../types/WindowConfig";

const KernelWindow = ({ data, onUpdate, darkMode,windowConfig }:WindowProps) => {
  return (<BaseWindow
  data={data}
  onUpdate={onUpdate}
  darkMode={darkMode}
  windowConfig={windowConfig}
  />)
};

export default KernelWindow;