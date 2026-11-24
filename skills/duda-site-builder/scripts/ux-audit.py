"""Auditoria rápida de UX (checklist do ui-ux-pro-max): alvos de toque < 44px, texto < 12px,
imagens sem alt, rolagem horizontal e contraste aproximado (cores com alfa dão falso positivo: confira à mão).

Uso: python3 ux-audit.py <url>   (roda em 1440 e 390 px)
"""
import sys
import asyncio,json
from playwright.async_api import async_playwright
JS=r"""
()=>{
 const lum=c=>{const m=c.match(/[\d.]+/g).map(Number);const [r,g,b]=m.slice(0,3).map(v=>{v/=255;return v<=.03928?v/12.92:((v+.055)/1.055)**2.4});return .2126*r+.7152*g+.0722*b};
 const bg=el=>{while(el){const c=getComputedStyle(el).backgroundColor;if(c&&!c.includes('0)')&&c!=='transparent')return c;el=el.parentElement}return 'rgb(243,245,238)'};
 const out={lowContrast:[],small:[],tinyText:[],noAlt:[],hscroll:document.documentElement.scrollWidth>innerWidth};
 const seen=new Set();
 document.querySelectorAll('body *').forEach(el=>{
  const t=[...el.childNodes].filter(n=>n.nodeType==3&&n.textContent.trim()).map(n=>n.textContent.trim()).join(' ');
  if(t){const cs=getComputedStyle(el);if(cs.visibility=='hidden'||el.closest('[hidden]'))return;
   const fg=cs.color,b=bg(el);const a=(fg.match(/[\d.]+/g)||[])[3];
   let L1=lum(fg),L2=lum(b);const r=(Math.max(L1,L2)+.05)/(Math.min(L1,L2)+.05);
   const fs=parseFloat(cs.fontSize);const need=(fs>=24||(fs>=18.66&&+cs.fontWeight>=700))?3:4.5;
   const eff=a&&+a<1? 'alpha'+a:'';
   if(r<need){const k=t.slice(0,40);if(!seen.has(k)){seen.add(k);out.lowContrast.push(k+' | '+r.toFixed(2)+' '+eff)}}
   if(fs<12)out.tinyText.push(t.slice(0,30)+' '+fs)}
 });
 document.querySelectorAll('a,button,summary').forEach(el=>{const r=el.getBoundingClientRect();if(r.width&&r.height&&(r.height<44||r.width<44))out.small.push((el.innerText||el.getAttribute('aria-label')||'').trim().slice(0,30)+' '+Math.round(r.width)+'x'+Math.round(r.height))});
 document.querySelectorAll('img').forEach(i=>{if(!i.hasAttribute('alt'))out.noAlt.push(i.src)});
 return JSON.stringify(out,null,1)}
"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch()
    for w in (1440,390):
      pg=await b.new_page(viewport={"width":w,"height":900})
      await pg.goto(sys.argv[1],wait_until="load"); await pg.wait_for_timeout(2000)
      print('=== ',w); print(await pg.evaluate(JS))
    await b.close()
asyncio.run(main())
