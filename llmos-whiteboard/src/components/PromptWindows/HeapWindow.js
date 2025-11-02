import React  from 'react';
import {BaseWindow} from "./BaseWindow";
const HeapWindow = ({ data, onUpdate, darkMode,windowConfig }) => {
  return (
    <BaseWindow
      data={data}
      onUpdate={onUpdate}
      darkMode={darkMode}
      windowConfig={windowConfig}
    />
  )
};

export default HeapWindow;

