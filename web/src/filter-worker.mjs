import {prepareData,filterGraph} from './filter-core.mjs';
let data,index;
self.onmessage=({data:message})=>{
  if(message.type==='init') {
    data=message.data;
    index=prepareData(data);
    self.postMessage({type:'ready'});
  } else if(message.type==='filter') {
    try {
      self.postMessage({type:'result',id:message.id,result:filterGraph(data,message.filters,index)});
    } catch(error) {
      self.postMessage({type:'error',id:message.id,message:error.message});
    }
  }
};
