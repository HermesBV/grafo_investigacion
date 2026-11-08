// Desplegable con casillas nativas: funciona con teclado, mouse y pantalla táctil.
export class MultiSelect {
  constructor(root,{id,label,allLabel,plural}) {
    this.root=root;
    this.allLabel=allLabel;
    this.plural=plural;
    this.trigger=document.createElement('button');
    this.trigger.type='button';
    this.trigger.id=id;
    this.trigger.className='multi-trigger';
    this.trigger.setAttribute('aria-label',label);
    this.trigger.setAttribute('aria-expanded','false');
    this.trigger.setAttribute('aria-controls',id+'-options');
    this.caption=document.createElement('span');
    const arrow=document.createElement('span');arrow.textContent='⌄';arrow.setAttribute('aria-hidden','true');
    this.trigger.append(this.caption,arrow);
    this.popup=document.createElement('div');
    this.popup.id=id+'-options';this.popup.className='multi-popup';this.popup.hidden=true;
    this.popup.setAttribute('role','group');this.popup.setAttribute('aria-label','Opciones de '+label.toLocaleLowerCase('es'));
    const all=document.createElement('button');all.type='button';all.className='multi-all';all.textContent=allLabel;
    this.list=document.createElement('div');this.list.className='multi-list';
    this.popup.append(all,this.list);root.append(this.trigger,this.popup);
    all.addEventListener('click',()=>{this.list.querySelectorAll('input').forEach(c=>c.checked=false);this.refresh();root.dispatchEvent(new Event('input',{bubbles:true}));});
    this.trigger.addEventListener('click',()=>this.setOpen(this.popup.hidden));
    this.list.addEventListener('input',()=>this.refresh());
    document.addEventListener('pointerdown',event=>{if(!root.contains(event.target))this.setOpen(false);});
    root.addEventListener('focusout',event=>{if(!root.contains(event.relatedTarget))this.setOpen(false);});
    root.addEventListener('keydown',event=>{if(event.key==='Escape'&&!this.popup.hidden){event.preventDefault();this.setOpen(false);this.trigger.focus();}});
    this.refresh();
  }
  setOptions(options) {
    this.list.replaceChildren();
    for(const option of options){
      const label=document.createElement('label');label.className='multi-option';
      const input=document.createElement('input');input.type='checkbox';input.value=String(option.value);
      const text=document.createElement('span');text.textContent=option.label;
      label.append(input,text);this.list.append(label);
    }
    this.refresh();
  }
  values(){return [...this.list.querySelectorAll('input:checked')].map(c=>c.value);}
  setValues(values){const selected=new Set(values.map(String));this.list.querySelectorAll('input').forEach(c=>c.checked=selected.has(c.value));this.refresh();}
  refresh(){
    const selected=[...this.list.querySelectorAll('input:checked')];
    this.caption.textContent=selected.length===0?this.allLabel:selected.length===1?selected[0].nextElementSibling.textContent:`${selected.length} ${this.plural}`;
    this.trigger.title=selected.length?selected.map(c=>c.nextElementSibling.textContent).join(' · '):this.allLabel;
  }
  setOpen(open){this.popup.hidden=!open;this.trigger.setAttribute('aria-expanded',String(open));this.root.classList.toggle('multi-open',open);}
}
