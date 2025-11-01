import React, { useState, useEffect, useRef } from 'react';
import {BaseWindow, SUPPORTED_THEMES} from "./BaseWindow";

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