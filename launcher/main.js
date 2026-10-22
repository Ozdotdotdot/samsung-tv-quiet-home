(function(){'use strict';
var apps=[['YouTube','9Ur5IzDKqV.TizenYouTube','01','Videos & subscriptions'],['Netflix','org.tizen.netflix-app','02','Films & series'],['Prime Video','org.tizen.primevideo','03','Films & series'],['Jellyfin','AprZAARz4r.Jellyfin','04','Your library'],['Disney+','MCmYXNxgcu.DisneyPlus','05','Films & series'],['HBO Max','5b8c3eb16b.BeamCTVDev','06','Films & series']];
var tools=[['Samsung Home','com.samsung.tv.csfs'],['Samsung Apps','com.samsung.tv.coba.apps'],['TV Settings','com.samsung.tv.coba.setting']];
var buttons=[],selected=0,lastApp=0;
function status(s){document.getElementById('status').textContent=s;}
function focus(i){selected=i;buttons[i].focus();if(i<6)lastApp=i;}
function launch(item){if(!window.tizen||!tizen.application){status('App launching is available on the TV.');return;}status('Opening '+item[0]+'…');tizen.application.launch(item[1],function(){status('Choose an app · Press OK to open');},function(e){status('Could not open '+item[0]+': '+(e.message||e.name)+'. Samsung Home is available below.');});}
function add(item,parent,index){var b=document.createElement('button');b.className=index<6?'tile':'tool';b.type='button';if(index<6){var mark=document.createElement('span');mark.className='mark';mark.textContent=item[2];b.appendChild(mark);b.appendChild(document.createTextNode(item[0]));var sub=document.createElement('small');sub.textContent=item[3];b.appendChild(sub);}else b.textContent=item[0];b.addEventListener('focus',function(){selected=index;if(index<6)lastApp=index;});b.addEventListener('click',function(){launch(item);});parent.appendChild(b);buttons.push(b);}
for(var i=0;i<apps.length;i++)add(apps[i],document.getElementById('apps'),i);
for(var j=0;j<tools.length;j++)add(tools[j],document.getElementById('tools'),j+6);
document.addEventListener('keydown',function(e){var k=e.keyCode,n=selected;if(k===37)n=selected<6?(selected%3?selected-1:selected):Math.max(6,selected-1);else if(k===39)n=selected<6?(selected%3<2?selected+1:selected):Math.min(8,selected+1);else if(k===38)n=selected>=6?lastApp:selected>=3?selected-3:selected;else if(k===40)n=selected<3?selected+3:selected<6?6+(selected%3):selected;else if(k===13){e.preventDefault();launch(selected<6?apps[selected]:tools[selected-6]);return;}else if(k===10009||k===27){e.preventDefault();focus(6);status('Press OK for Samsung Home, or choose an app above.');return;}else return;e.preventDefault();focus(n);});
function clock(){var d=new Date(),h=d.getHours(),m=d.getMinutes();document.getElementById('clock').textContent=(h%12||12)+':'+(m<10?'0':'')+m;}
clock();setInterval(clock,30000);document.addEventListener('visibilitychange',function(){if(!document.hidden){clock();focus(selected);status('Choose an app · Press OK to open');}});focus(0);
window.QuietHome={focus:focus,launch:launch,apps:apps,tools:tools};
}());
