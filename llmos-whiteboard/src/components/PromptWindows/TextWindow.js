import React from 'react';
import {BaseWindow} from "./BaseWindow";
const TextWindow = ({ data, onUpdate, darkMode ,windowConfig}) => {
  return (<BaseWindow
  data={data}
  onUpdate={onUpdate}
  darkMode={darkMode}
  windowConfig={windowConfig}
  />)
};

export default TextWindow;

