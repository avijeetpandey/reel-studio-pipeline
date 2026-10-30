import re,sys,os
C=__import__("os").path.dirname(__import__("os").path.abspath(__file__))+"/../"
tests={
 "kinetic-type-3d":('buildKinetic3D(tl,{el:"#kt",words:[{t:"Your",at:0.3},{t:"type",at:0.6},{t:"isn\'t",at:0.9},{t:"boring.",at:1.3,accent:true,br:true},{t:"Your",at:2.3},{t:"timing",at:2.6,accent:true},{t:"is.",at:2.9,br:true},{t:"Land",at:3.3},{t:"every",at:3.5},{t:"word",at:3.7,accent:true}],pullBackAt:3.8,end:6});',[0.5,1.6,3.0,4.8],"#e9e4d8"),
 "sound-strip":('buildSoundStrip(tl,{el:"#ss",clips:[{label:"Typing",at:0.8,dur:1.0},{label:"Whoosh",at:2.1,dur:0.7},{label:"Riser",at:3.2,dur:1.2},{label:"Glitch",at:4.8,dur:0.6}],start:0.2,end:6.5});',[0.9,2.3,3.8,5.0],"#0c0d10"),
 "sfx-chip":('buildSfxChip(tl,{el:"#chip",name:"Deep woosh",dur:"00:03",at:0.6,hold:2,x:60,y:700});',[0.2,1.2,2.8],"#14161c"),
 "select-caption":('buildSelectCaption(tl,{el:"#sc",y:200,lines:[[{w:"Hand",at:0.3},{w:"that",at:0.55},{w:"folder",at:0.8},{w:"to",at:1.0},{w:"Claude,",at:1.2,sel:true}],[{w:"it",at:2.4},{w:"starts",at:2.6},{w:"editing",at:2.9,sel:true}]]});',[0.9,1.8,3.2],"#0b1120"),
 "stamp-slap":('buildStampSlap(tl,{el:"#st",text:"CHEAP?",at:0.6,x:540,y:700,hold:2});',[0.5,0.72,1.5,3.0],"#3a4256"),
 "loading-hook":('buildLoadingHook(tl,{el:"#lh",start:0.2,dur:4,y:900});',[0.3,2.2,4.1],"#2b2f3a"),
 "dm-toast":('buildDmToast(tl,{el:"#dm",name:"yourbrand",msg:"Would you trust AI with your resume? YES / NO",at:0.4,rows:[{u:"meera.codes",t:"YES"},{u:"rahul.dev",t:"NO 😅"}]});',[0.9,1.6,2.4],"#6b7a99"),
 "stopwatch":('buildStopwatch(tl,{el:"#sw",at:0.3,dur:1.6,from:4,to:20,unit:"days",x:380,y:600,size:300});',[0.4,1.1,2.0],"#0b1120"),
 "ab-header":('buildAbHeader(tl,{el:"#ab",left:"WITHOUT SFX",right:"WITH SFX",y:200,swaps:[{at:0.3,side:"left"},{at:1.6,side:"right"}]});',[0.5,1.8],"#14161c"),
}
for name,(call,times,bg) in tests.items():
    src=open(C+name+".html").read()
    body=re.sub(r'<!--.*?-->','',src,flags=re.S)
    html=f'''<!doctype html><meta charset=utf-8><style>@import url("https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600;700;800;900&family=JetBrains+Mono:wght@500;600&display=swap");
html,body{{margin:0;background:#000}} #stage{{position:relative;width:1080px;height:1920px;background:{bg};overflow:hidden;transform-origin:0 0;transform:scale(.3)}}
:root{{--accent:#d7261e}}</style><div id=stage>{body}</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.5/gsap.min.js"></script>
<script>const tl=gsap.timeline({{paused:true}});{call}window.TL=tl;window.times={times};</script>'''
    open(name+".html","w").write(html)
print("ok")
