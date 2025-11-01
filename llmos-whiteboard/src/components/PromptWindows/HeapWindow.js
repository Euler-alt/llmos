import React  from 'react';
import {BaseWindow,SUPPORTED_THEMES} from "./BaseWindow";
const HeapWindow = ({ data, onUpdate, darkMode }) => {
  return (
    <BaseWindow
      data={data}
      onUpdate={onUpdate}
      darkMode={darkMode}
      theme={SUPPORTED_THEMES[0]}
    />
  )
};

export default HeapWindow;

