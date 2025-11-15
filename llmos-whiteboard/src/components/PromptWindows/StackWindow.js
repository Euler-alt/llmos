import React, { useState, useEffect, useRef } from 'react';
import {BaseWindow} from "./BaseWindow";
import {SUPPORTED_THEMES} from "./Theme";

const StackWindow = ({ data, onUpdate, darkMode,windowConfig }) => {
  return (
    <BaseWindow
      data={data}
      onUpdate={onUpdate}
      darkMode={darkMode}
      windowConfig ={windowConfig}
    />
  )
};

export default StackWindow;