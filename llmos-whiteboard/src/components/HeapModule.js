import React,{useState,useEffect} from 'react';

const HeapModule = ({ data, onUpdate }) => {
   const [isUpdated,setIsupdated] = useState(false);
   useEffect(()=>{
       if(!data) return;
       setIsupdated(true);
       const timer = setTimeout(()=>setIsupdated(false),500);
       return ()=>clearTimeout(timer);
   },[data])
   return (
    <div style={{...moduleStyle, backgroundColor: isUpdated ? '#ff8c00' : '#e6f3ff'}}>
      <h4>堆模块 (Heap)</h4>
      <textarea
        style={textAreaStyle}
        value={data}
        onChange={(e) => onUpdate('heap', e.target.value)}
        rows="5"
      />
    </div>
  );
};

const moduleStyle = {
  border: '1px solid #ccc',
  borderRadius: '8px',
  padding: '16px',
  marginBottom: '16px',
  backgroundColor: '#e6f3ff'
};

const textAreaStyle = {
  width: '100%',
  resize: 'none',
  fontFamily: 'monospace',
  fontSize: '14px'
};

export default HeapModule;