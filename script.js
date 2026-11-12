// ===== STATE =====
let state={tasks:[],xp:0,level:1,pomoCount:0,pomoTotalMin:0,pomoSessions:[],achievements:[],streak:0,lastActiveDate:null,dailyFocus:'',dailyFocusTask:'',rewards:[]};
let booksData=[],abData=[],waterData={},sleepData=[],moodData=[],journalData=[],customT=[];
let jState={days:{},nasihat:[],streak:0,lastWrite:''};
let settings={pinOn:false,pin:'1234',notifOn:true,vibOn:true,soundOn:false,reminderMin:10,fontSize:'medium',animOn:true,confettiOn:true,xpTask:10,xpPomo:15,xpBook:20,xpAch:25,pomoWork:25,pomoBreak:5,pomoLong:15,pomoCycleN:4,bookTime:25,bookBreak:true,waterGoal:8,sleepGoal:8};
const todayKey=new Date().toISOString().split('T')[0];
const CATS={study:{icon:'📚',name:"O'qish",color:'#4ade80'},work:{icon:'💼',name:'Ish',color:'#a855f7'},sport:{icon:'🏋️',name:'Sport',color:'#3b82f6'},meal:{icon:'🍽️',name:'Ovqatlanish',color:'#92400e'},rest:{icon:'🧘',name:'Dam olish',color:'#06b6d4'},worship:{icon:'🤲',name:'Ibadat',color:'#ffffff'},family:{icon:'👨‍👩‍👧',name:'Oila',color:'#ec4899'},home:{icon:'🧹',name:'Uy ishlari',color:'#eab308'},detox:{icon:'📵',name:'Detoks',color:'#00ffff'},goals:{icon:'🎯',name:'Maqsadlar',color:'#ef4444'}};
const QUOTES=["Bilim - eng katta boylik","Har bir kitob - yangi dunyo","O'qish - ruhning ozuqasi","Bugungi mehnat - ertangi muvaffaqiyat","Intizom - erkinlik kaliti","Kichik qadamlar katta natijalarga olib boradi","Sabr - muvaffaqiyat kaliti","Har kun yangi imkoniyat","O'zingga ishonsang - hamma narsa mumkin","Bugun qiyin, ertaga oson"];
const LEVEL_TITLES={1:'Boshlovchi',3:'Faol',5:'Tajribali',8:'Usta',12:'Ekspert',15:'Chempion',20:'Afsona',30:'Intizom Ustasi'};
const MOTIVATION=["🔥 Ajoyib ish! Davom eting!","💪 Siz kuchlisiz! Yana bir vazifa!","⭐ Har bir qadam muhim!","🚀 To'xtamang, maqsad yaqin!","🌟 Siz buni uddalaysiz!"];
document.addEventListener('DOMContentLoaded',()=>{loadAll();renderAll();checkStreak();if('Notification'in window&&Notification.permission==='default')Notification.requestPermission();setInterval(checkReminders,60000)});
function saveAll(){
localStorage.setItem('mi3_state',JSON.stringify(state));
localStorage.setItem('mi3_books',JSON.stringify(booksData));
localStorage.setItem('mi3_ab',JSON.stringify(abData));
localStorage.setItem('mi3_water',JSON.stringify(waterData));
localStorage.setItem('mi3_sleep',JSON.stringify(sleepData));
localStorage.setItem('mi3_mood',JSON.stringify(moodData));
localStorage.setItem('mi3_journal',JSON.stringify(journalData));
localStorage.setItem('mi3_ct',JSON.stringify(customT));
localStorage.setItem('mi3_settings',JSON.stringify(settings));
localStorage.setItem('mi3_jstate',JSON.stringify(jState));
}
function loadAll(){try{
const s=localStorage.getItem('mi3_state');if(s)state={...state,...JSON.parse(s)};
const b=localStorage.getItem('mi3_books');if(b)booksData=JSON.parse(b);
const a=localStorage.getItem('mi3_ab');if(a)abData=JSON.parse(a);
const w=localStorage.getItem('mi3_water');if(w)waterData=JSON.parse(w);
const sl=localStorage.getItem('mi3_sleep');if(sl)sleepData=JSON.parse(sl);
const m=localStorage.getItem('mi3_mood');if(m)moodData=JSON.parse(m);
const j=localStorage.getItem('mi3_journal');if(j)journalData=JSON.parse(j);
const c=localStorage.getItem('mi3_ct');if(c)customT=JSON.parse(c);
const st=localStorage.getItem('mi3_settings');if(st)settings={...settings,...JSON.parse(st)};
const js=localStorage.getItem('mi3_jstate');if(js)jState={...jState,...JSON.parse(js)};
}catch(e){console.log('Load error:',e)}}
function showToast(msg,type='info'){const c=document.getElementById('toastContainer');const t=document.createElement('div');t.className='toast '+type;t.innerHTML='<span>'+msg+'</span>';c.appendChild(t);setTimeout(()=>t.remove(),3500)}
function vibrate(p){if(settings.vibOn&&navigator.vibrate)navigator.vibrate(p)}
function playBeep(){if(settings.soundOn){try{new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA=').play()}catch(e){}}}
function checkStreak(){const today=new Date().toDateString();const yest=new Date(Date.now()-864e5).toDateString();if(state.lastActiveDate===today)return;if(state.lastActiveDate===yest)state.streak++;else state.streak=1;state.lastActiveDate=today;saveAll()}
function getLevelTitle(l){let t='Boshlovchi';for(let k of Object.keys(LEVEL_TITLES).sort((a,b)=>a-b)){if(l>=k)t=LEVEL_TITLES[k]}return t}
function addXP(n){state.xp+=n;const need=state.level*100;if(state.xp>=need){state.xp-=need;state.level++;showToast('🎉 Daraja '+state.level+' — '+getLevelTitle(state.level)+'!','success');if(settings.confettiOn)launchConfetti();vibrate([200,100,200]);checkRewards()}updateXPDisplay();saveAll()}
function updateXPDisplay(){const need=state.level*100;const pct=Math.min((state.xp/need)*100,100);document.getElementById('levelNum').textContent=state.level;document.getElementById('levelTitle').textContent=getLevelTitle(state.level);document.getElementById('xpNum').textContent=state.xp;document.getElementById('xpMax').textContent=need;document.getElementById('xpFill').style.width=pct+'%'}
function editDailyFocus(){document.getElementById('focusGoalInput').value=state.dailyFocus||'';document.getElementById('focusTaskInput').value=state.dailyFocusTask||'';document.getElementById('focusModal').classList.add('active')}
function saveDailyFocus(){state.dailyFocus=document.getElementById('focusGoalInput').value.trim();state.dailyFocusTask=document.getElementById('focusTaskInput').value.trim();saveAll();renderDailyFocus();closeModal('focusModal');showToast('🎯 Fokus saqlandi!','success')}
function renderDailyFocus(){document.getElementById('dfGoal').textContent=state.dailyFocus||'Maqsad belgilash uchun bosing';document.getElementById('dfTask').textContent=state.dailyFocusTask?'→ '+state.dailyFocusTask:''}
let currentFilter='all',currentCat=null,viewingDate=null;
function renderCategories(){const g=document.getElementById('catGrid');g.innerHTML=Object.entries(CATS).map(([k,c])=>{const cnt=state.tasks.filter(t=>t.category===k&&!t.completed&&t.date===todayKey).length;return '<div class="cat-item'+(currentCat===k?' active':'')+'" style="--cat-color:'+c.color+'" onclick="filterCat(\''+k+'\')">'+(cnt>0?'<div class="cat-count">'+cnt+'</div>':'')+'<div class="cat-icon">'+c.icon+'</div><div class="cat-name">'+c.name+'</div></div>'}).join('')}
function getOverdueTasks(){return state.tasks.filter(t=>t.date<todayKey&&!t.completed)}
function renderOverdueAlert(){const o=getOverdueTasks();const el=document.getElementById('overdueAlert');if(o.length>0){el.style.display='flex';document.getElementById('overdueCount').textContent=o.length}else el.style.display='none'}
function showOverdue(){const o=getOverdueTasks();let html='<h3>⚠️ Kechikkan vazifalar ('+o.length+' ta)</h3>';o.forEach(t=>{const c=CATS[t.category];html+='<div class="task-item overdue" style="--task-color:'+c.color+';cursor:default;margin-top:8px"><div class="task-body"><div class="task-title">'+c.icon+' '+t.title+'</div><div class="task-meta"><span>📅 '+t.date+'</span>'+(t.startTime?'<span>⏰ '+t.startTime+'</span>':'')+'</div></div></div>'});html+='<button class="btn btn-ghost" onclick="closeModal(\'overdueModal\')" style="width:100%;margin-top:12px;justify-content:center">Yopish</button>';document.getElementById('overdueModalContent').innerHTML=html;document.getElementById('overdueModal').classList.add('active')}
function openTaskForm(){document.getElementById('taskFormContainer').style.display='block';document.getElementById('taskTitle').focus()}
function closeTaskForm(){document.getElementById('taskFormContainer').style.display='none'}
function toggleExtraFields(){const el=document.getElementById('extraFields');const b=document.getElementById('extraFieldsBtn');if(el.style.display==='none'){el.style.display='block';b.textContent='▲ Yashirish'}else{el.style.display='none';b.textContent="▼ Qo'shimcha maydonlar"}}
function setFilter(f,el){currentFilter=f;viewingDate=null;document.querySelectorAll('#view-home .filter-tab').forEach(t=>t.classList.remove('active'));el.classList.add('active');renderTasks()}
function filterCat(c){currentCat=currentCat===c?null:c;renderCategories();renderTasks()}
function openDatePicker(){const dp=document.getElementById('datePicker');dp.style.display='block';if(dp.showPicker)dp.showPicker();else dp.click()}
function filterByDate(d){viewingDate=d;renderTasks();showToast('📅 '+d+' vazifalari','info')}
function toggleSearch(){const b=document.getElementById('searchBar');b.style.display=b.style.display==='none'?'flex':'none';if(b.style.display==='flex')document.getElementById('searchInput').focus()}
function addTask(){const title=document.getElementById('taskTitle').value.trim();if(!title){showToast('⚠️ Vazifa nomini kiriting!','warning');return}const img=document.getElementById('taskImage');if(img&&img.files.length){const r=new FileReader();r.onload=e=>finishAddTask(title,e.target.result);r.readAsDataURL(img.files[0])}else finishAddTask(title,null)}
function finishAddTask(title,image){
const task={id:Date.now(),title,category:document.getElementById('taskCat').value,priority:document.getElementById('taskPriority').value,startTime:document.getElementById('taskStart').value,endTime:document.getElementById('taskEnd').value,duration:parseInt(document.getElementById('taskDuration').value)||0,recurring:document.getElementById('taskRecurring').value,tags:document.getElementById('taskTags').value.split(',').map(t=>t.trim()).filter(t=>t),notes:document.getElementById('taskNotes').value,image,link:(document.getElementById('taskLink')?document.getElementById('taskLink').value:'')||null,isFocus:document.getElementById('focusToggle').classList.contains('active'),completed:false,completedAt:null,completionNote:'',completionImage:null,date:new Date().toISOString().split('T')[0]};
state.tasks.push(task);saveAll();renderTasks();renderCategories();updateStats();renderOverdueAlert();addXP(5);showToast("✅ Vazifa qo'shildi! +5 XP",'success');vibrate(100);
['taskTitle','taskStart','taskEnd','taskDuration','taskTags','taskNotes','taskImage','taskLink'].forEach(id=>{const e=document.getElementById(id);if(e)e.value=''});
document.getElementById('focusToggle').classList.remove('active');closeTaskForm();checkAch();
}
let completingTaskId=null;
function requestComplete(id){const task=state.tasks.find(t=>t.id===id);if(!task||task.completed)return;const now=new Date();const cur=String(now.getHours()).padStart(2,'0')+':'+String(now.getMinutes()).padStart(2,'0');if(task.endTime&&cur<task.endTime){showToast('⏰ Vazifa '+task.endTime+' da tugaydi. Hali vaqt bor!','warning');vibrate([100,50,100]);return}completingTaskId=id;document.getElementById('tcmTaskName').textContent=task.title;document.getElementById('tcmTime').textContent=cur;document.getElementById('tcmImage').value='';document.getElementById('tcmNote').value='';document.getElementById('taskCompleteModal').classList.add('active')}
function confirmTaskComplete(){const task=state.tasks.find(t=>t.id===completingTaskId);if(!task)return;const img=document.getElementById('tcmImage');const note=document.getElementById('tcmNote').value.trim();if(img.files.length){const r=new FileReader();r.onload=e=>{task.completed=true;task.completedAt=new Date().toISOString();task.completionImage=e.target.result;task.completionNote=note;finishComplete(task)};r.readAsDataURL(img.files[0])}else{if(!note&&!confirm('Rasm va izoh yo\'q. Rostdan bajardingizmi?'))return;task.completed=true;task.completedAt=new Date().toISOString();task.completionNote=note;finishComplete(task)}}
function finishComplete(task){saveAll();renderTasks();updateStats();renderCategories();renderOverdueAlert();addXP(settings.xpTask);showToast('🎉 Vazifa bajarildi! +'+settings.xpTask+' XP','success');vibrate([200,100,200]);playBeep();closeTcm();checkAch();const done=state.tasks.filter(t=>t.date===todayKey&&t.completed).length;if(done%5===0){const m=document.getElementById('motivationMsg');m.style.display='block';m.textContent=MOTIVATION[Math.floor(Math.random()*MOTIVATION.length)];setTimeout(()=>m.style.display='none',4000)}}
function closeTcm(){document.getElementById('taskCompleteModal').classList.remove('active');completingTaskId=null}
let deletingTaskId=null;
function deleteTask(id){const task=state.tasks.find(t=>t.id===id);if(!task)return;deletingTaskId=id;document.getElementById('tdmTaskName').textContent=task.title;document.getElementById('tdmInput').value='';document.getElementById('tdmTime').value='';document.getElementById('taskDeleteModal').classList.add('active')}
function confirmDelete(){const task=state.tasks.find(t=>t.id===deletingTaskId);if(!task)return;const input=document.getElementById('tdmInput').value.trim();const time=document.getElementById('tdmTime').value;if(input!==task.title){showToast("❌ Nom to'g'ri yozilmadi!",'warning');return}if(!time){showToast('⚠️ Vaqtni belgilang!','warning');return}state.tasks=state.tasks.filter(t=>t.id!==deletingTaskId);saveAll();renderTasks();updateStats();renderCategories();renderOverdueAlert();closeModal('taskDeleteModal');showToast("🗑️ Vazifa o'chirildi",'info');deletingTaskId=null}
function renderTasks(){
const list=document.getElementById('taskList');const empty=document.getElementById('emptyState');
const search=(document.getElementById('searchInput')?document.getElementById('searchInput').value:'').toLowerCase();
let tasks;if(viewingDate)tasks=state.tasks.filter(t=>t.date===viewingDate);else tasks=state.tasks.filter(t=>t.date===todayKey);
if(currentCat)tasks=tasks.filter(t=>t.category===currentCat);
if(currentFilter==='pending')tasks=tasks.filter(t=>!t.completed);
if(currentFilter==='completed')tasks=tasks.filter(t=>t.completed);
if(currentFilter==='high')tasks=tasks.filter(t=>t.priority==='high');
if(currentFilter==='overdue')tasks=state.tasks.filter(t=>t.date<todayKey&&!t.completed);
if(search)tasks=tasks.filter(t=>t.title.toLowerCase().includes(search));
document.getElementById('taskCountLabel').textContent='('+tasks.length+' ta)';
if(!tasks.length){list.innerHTML='';empty.style.display='block';return}
empty.style.display='none';
list.innerHTML=tasks.map(t=>{const c=CATS[t.category];const od=t.date<todayKey&&!t.completed;let cls='task-item';if(t.completed)cls+=' completed';if(od)cls+=' overdue';if(t.isFocus&&!t.completed)cls+=' focus-task';
let html='<div class="'+cls+'" style="--task-color:'+c.color+'" onclick="openTaskDetail('+t.id+')">';
html+=!t.completed?'<div class="task-check" onclick="event.stopPropagation();requestComplete('+t.id+')"></div>':'<div class="task-check checked"></div>';
html+='<div class="task-body"><div class="task-title">'+c.icon+' '+t.title+'</div><div class="task-meta">';
if(t.startTime)html+='<span>⏰ '+t.startTime+(t.endTime?'-'+t.endTime:'')+'</span>';
if(t.duration)html+='<span>⏱️'+t.duration+'daq</span>';
if(od)html+='<span style="color:var(--accent1)">⚠️ Kechikkan</span>';
if(t.isFocus&&!t.completed)html+='<span style="color:var(--gold)">🎯 Fokus</span>';
t.tags.forEach(tag=>{html+='<span class="task-tag">'+tag+'</span>'});
html+='</div>';
if(t.notes)html+='<div style="font-size:.7em;color:var(--text3);margin-top:3px">📝 '+t.notes.substring(0,50)+(t.notes.length>50?'...':'')+'</div>';
if(t.image)html+='<div class="task-attachment"><img class="task-img-thumb" src="'+t.image+'"></div>';
if(t.link)html+='<div class="task-attachment"><a class="task-link" href="'+t.link+'" target="_blank" onclick="event.stopPropagation()">🔗 Havola</a></div>';
html+='</div><div class="task-actions"><button class="task-action-btn delete" onclick="event.stopPropagation();deleteTask('+t.id+')">🗑️</button></div></div>';
return html}).join('');
}
function openTaskDetail(id){const t=state.tasks.find(x=>x.id===id);if(!t)return;const c=CATS[t.category];
let html='<h3>'+c.icon+' '+t.title+'</h3><div style="font-size:.8em;color:var(--text2);margin:8px 0">📅 '+t.date+(t.startTime?' | ⏰ '+t.startTime:'')+(t.endTime?'-'+t.endTime:'')+(t.duration?' | ⏱️ '+t.duration+' daqiqa':'')+'</div>';
html+='<div style="font-size:.75em;color:var(--text3);margin-bottom:8px">Kategoriya: '+c.icon+' '+c.name+' | Muhimlik: '+(t.priority==='high'?'🔴 Juda muhim':t.priority==='medium'?'🟡 Muhim':'🟢 Oddiy')+'</div>';
if(t.notes)html+='<div style="font-size:.85em;margin:10px 0;padding:10px;background:var(--bg3);border-radius:8px">📝 '+t.notes+'</div>';
if(t.tags.length)html+='<div style="margin:8px 0">'+t.tags.map(tag=>'<span class="task-tag">'+tag+'</span>').join(' ')+'</div>';
if(t.image)html+='<img src="'+t.image+'" style="width:100%;border-radius:10px;margin:8px 0">';
if(t.link)html+='<a href="'+t.link+'" target="_blank" style="color:var(--neon-cyan);font-size:.85em">🔗 '+t.link+'</a><br>';
if(t.completed){html+='<div style="color:var(--green);font-size:.85em;margin-top:10px">✅ Bajarilgan: '+(t.completedAt?new Date(t.completedAt).toLocaleString():'')+'</div>';if(t.completionNote)html+='<div style="font-size:.8em;color:var(--text2);margin-top:5px;padding:8px;background:var(--bg3);border-radius:6px">📝 '+t.completionNote+'</div>';if(t.completionImage)html+='<img src="'+t.completionImage+'" style="width:100%;border-radius:8px;margin-top:8px">'}
html+='<div style="display:flex;gap:8px;margin-top:15px;flex-wrap:wrap">';
if(!t.completed)html+='<button class="btn btn-sm btn-success" onclick="closeModal(\'taskDetailModal\');requestComplete('+t.id+')">✅ Bajardim</button>';
html+='<button class="btn btn-sm btn-danger" onclick="closeModal(\'taskDetailModal\');deleteTask('+t.id+')">🗑️ O\'chirish</button><button class="btn btn-sm btn-ghost" onclick="closeModal(\'taskDetailModal\')">Yopish</button></div>';
document.getElementById('taskDetailModalContent').innerHTML=html;document.getElementById('taskDetailModal').classList.add('active');
}
function closeModal(id){const el=document.getElementById(id);if(el)el.classList.remove('active')}
function showModal(id,html){const m=document.getElementById(id);if(m){const c=m.querySelector('.modal-content');if(c)c.innerHTML=html;m.classList.add('active')}}

// ===== KALENDAR =====
let weekStart=getMonday(new Date()),curMonth=new Date().getMonth(),curYear=new Date().getFullYear();
function getMonday(d){const dt=new Date(d);const day=dt.getDay();dt.setDate(dt.getDate()-day+(day===0?-6:1));return dt}
function switchCal(v,el){
document.querySelectorAll('#view-calendar .filter-tab').forEach(t=>t.classList.remove('active'));
el.classList.add('active');
if(v==='week'){document.getElementById('calWeek').style.display='block';document.getElementById('calMonth').style.display='none';renderWeek()}
else{document.getElementById('calWeek').style.display='none';document.getElementById('calMonth').style.display='block';renderMonth()}
}
function changeWeek(d){weekStart.setDate(weekStart.getDate()+d*7);renderWeek()}
function changeMonth(d){curMonth+=d;if(curMonth>11){curMonth=0;curYear++}if(curMonth<0){curMonth=11;curYear--}renderMonth()}
function renderWeek(){
const days=['Du','Se','Ch','Pa','Ju','Sh','Ya'];
const end=new Date(weekStart);end.setDate(end.getDate()+6);
document.getElementById('weekTitle').textContent=weekStart.getDate()+'/'+(weekStart.getMonth()+1)+' - '+end.getDate()+'/'+(end.getMonth()+1);
const g=document.getElementById('weekGrid');g.innerHTML='';
for(let i=0;i<7;i++){
const dt=new Date(weekStart);dt.setDate(dt.getDate()+i);
const ds=dt.toISOString().split('T')[0];
const dtasks=state.tasks.filter(t=>t.date===ds);
const isToday=ds===todayKey;
let dots=dtasks.slice(0,4).map(t=>'<div class="week-task-dot" style="background:'+CATS[t.category].color+'"></div>').join('');
g.innerHTML+='<div class="week-day'+(isToday?' today':'')+'" onclick="showDayReport(\''+ds+'\')"><div class="week-day-name">'+days[i]+'</div><div class="week-day-num">'+dt.getDate()+'</div><div class="week-day-tasks">'+dots+'</div></div>';
}
}
function renderMonth(){
const names=['Yanvar','Fevral','Mart','Aprel','May','Iyun','Iyul','Avgust','Sentabr','Oktabr','Noyabr','Dekabr'];
document.getElementById('monthTitle').textContent=names[curMonth]+' '+curYear;
const g=document.getElementById('monthGrid');
const first=new Date(curYear,curMonth,1).getDay();
const dim=new Date(curYear,curMonth+1,0).getDate();
const start=first===0?6:first-1;
let html='';
for(let i=0;i<start;i++)html+='<div></div>';
for(let d=1;d<=dim;d++){
const ds=curYear+'-'+String(curMonth+1).padStart(2,'0')+'-'+String(d).padStart(2,'0');
const dayTasks=state.tasks.filter(t=>t.date===ds);
const has=dayTasks.length>0;
const isT=ds===todayKey;
let rateClass='';
if(has){
const done=dayTasks.filter(t=>t.completed).length;
const rate=Math.round((done/dayTasks.length)*100);
if(rate>=80)rateClass=' high-rate';else if(rate<50)rateClass=' low-rate';else rateClass=' mid-rate';
}
html+='<div class="month-day'+(isT?' today':'')+(has?' has-tasks':'')+rateClass+'" onclick="showDayReport(\''+ds+'\')">'+d+'</div>';
}
g.innerHTML=html;
}
function showDayReport(dateStr){
const dayTasks=state.tasks.filter(t=>t.date===dateStr);
const done=dayTasks.filter(t=>t.completed).length;
const total=dayTasks.length;
const rate=total>0?Math.round((done/total)*100):0;
const d=new Date(dateStr+'T00:00:00');
const dayNames=['Yakshanba','Dushanba','Seshanba','Chorshanba','Payshanba','Juma','Shanba'];
const monthNames=['Yanvar','Fevral','Mart','Aprel','May','Iyun','Iyul','Avgust','Sentabr','Oktabr','Noyabr','Dekabr'];
const dayPomo=state.pomoSessions.filter(s=>s.date===dateStr);
const dayWater=waterData[dateStr]||0;
const daySleep=sleepData.find(s=>s.date===dateStr);
const dayMood=moodData.find(m=>m.date===dateStr);
let html='<h3 style="margin-bottom:12px">📅 '+d.getDate()+' '+monthNames[d.getMonth()]+' — '+dayNames[d.getDay()]+'</h3>';
html+='<div class="report-stats">';
html+='<div class="report-stat"><div class="rs-val" style="color:var(--neon-cyan)">'+total+'</div><div class="rs-lbl">Jami</div></div>';
html+='<div class="report-stat"><div class="rs-val" style="color:var(--green)">'+done+'</div><div class="rs-lbl">Bajarilgan</div></div>';
html+='<div class="report-stat"><div class="rs-val" style="color:var(--accent3)">'+(total-done)+'</div><div class="rs-lbl">Qolgan</div></div>';
html+='</div>';
html+='<div style="text-align:center;margin:10px 0;font-size:.9em">📊 Bajarish: <strong>'+rate+'%</strong></div>';
html+='<div class="report-bar-row"><span class="report-bar-label">'+rate+'%</span><div class="report-bar"><div class="report-bar-fill done" style="width:'+rate+'%"></div></div></div>';
if(dayPomo.length>0)html+='<div style="font-size:.8em;color:var(--text2);margin:8px 0">🍅 Pomodoro: '+dayPomo.length+' seans</div>';
if(dayWater>0)html+='<div style="font-size:.8em;color:var(--text2);margin:4px 0">💧 Suv: '+dayWater+'/'+(settings.waterGoal||8)+' stakan</div>';
if(daySleep)html+='<div style="font-size:.8em;color:var(--text2);margin:4px 0">😴 Uyqu: '+daySleep.duration+' soat</div>';
if(dayMood)html+='<div style="font-size:.8em;color:var(--text2);margin:4px 0">🌡️ Kayfiyat: '+(dayMood.emoji||dayMood.scale+'/10')+'</div>';
if(dayTasks.length){
html+='<div style="margin-top:12px;font-size:.8em;font-weight:600">Vazifalar:</div>';
dayTasks.forEach(t=>{const c=CATS[t.category];
html+='<div style="display:flex;align-items:center;gap:6px;padding:6px 8px;background:var(--bg3);border-radius:6px;margin-top:4px;font-size:.75em"><span>'+(t.completed?'✅':'⬜')+'</span><span>'+c.icon+'</span><span style="flex:1;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">'+t.title+'</span></div>';
});
}
html+='<button class="btn btn-ghost" onclick="closeModal(\'calDayModal\')" style="width:100%;margin-top:12px;justify-content:center">Yopish</button>';
document.getElementById('calDayModalContent').innerHTML=html;
document.getElementById('calDayModal').classList.add('active');
}

// ===== POMODORO =====
let pomoTime=25*60,pomoInterval=null,pomoRunning=false,pomoModeTime=25,pomoType='classic';
let restMusicFiles=[],restMusicAudio=null,workMusicFiles=[],workMusicAudio=null;
function setPomoType(type,el){
pomoType=type;
document.querySelectorAll('#view-pomodoro .filter-tab').forEach(t=>t.classList.remove('active'));
el.classList.add('active');
document.getElementById('pomoClassic').style.display=type==='classic'?'block':'none';
document.getElementById('pomoSmart').style.display=type==='smart'?'block':'none';
document.getElementById('pomoFree').style.display=type==='free'?'block':'none';
document.getElementById('pomoRest').style.display=type==='rest'?'block':'none';
}
function setPomoTime(m,el){pomoModeTime=m;pomoTime=m*60;pausePomo();updatePomoDisp();document.querySelectorAll('.pomo-mode-btn').forEach(b=>b.classList.remove('active'));el.classList.add('active')}
function setCustomPomoTime(){const v=parseInt(document.getElementById('customPomoTime').value);if(v&&v>0){pomoModeTime=v;pomoTime=v*60;pausePomo();updatePomoDisp();showToast('⏱️ '+v+' daqiqa o\'rnatildi','info')}else showToast('⚠️ To\'g\'ri raqam kiriting!','warning')}
function calcSmartPlan(){
const hours=parseInt(document.getElementById('smartHours').value)||4;
const parts=document.getElementById('smartCycleType').value.split('/');
const workMin=parseInt(parts[0]),breakMin=parseInt(parts[1]);
const cycles=Math.floor(hours*60/(workMin+breakMin));
const totalWork=cycles*workMin,totalBreak=cycles*breakMin;
const longBreaks=Math.floor(cycles/settings.pomoCycleN);
const el=document.getElementById('smartPlanResult');
el.style.display='block';
el.innerHTML='📊 <strong>'+hours+' soat</strong> = '+cycles+' sikl ('+workMin+'/'+breakMin+')<br>🕐 Jami ish: '+Math.round(totalWork/60*10)/10+' soat<br>☕ Dam: '+Math.round(totalBreak/60*10)/10+' soat<br>🛋️ Uzun tanaffus: '+longBreaks+' marta';
pomoModeTime=workMin;pomoTime=workMin*60;updatePomoDisp();
}
function setRestType(type,el){
document.querySelectorAll('#pomoRest .filter-tab').forEach(t=>t.classList.remove('active'));
el.classList.add('active');
document.getElementById('restMusicSelect').style.display=type==='music'?'block':'none';
document.getElementById('restPhoneInfo').style.display=type==='phone'?'block':'none';
document.getElementById('restQuietInfo').style.display=type==='quiet'?'block':'none';
}
function handleRestMusic(e){for(let f of e.target.files){restMusicFiles.push({name:f.name.replace(/\.[^/.]+$/,''),url:URL.createObjectURL(f)})}document.getElementById('restMusicList').innerHTML=restMusicFiles.map((f,i)=>'<div class="audio-track-item" onclick="playRestMusic('+i+')"><span class="track-icon">🎵</span><span class="audio-track-name">'+f.name+'</span></div>').join('');e.target.value='';showToast('🎵 '+e.target.files.length+' ta musiqa yuklandi','success')}
function playRestMusic(i){if(restMusicAudio)restMusicAudio.pause();restMusicAudio=new Audio(restMusicFiles[i].url);restMusicAudio.loop=true;restMusicAudio.play();showToast('🎵 Musiqa chalinyapti','info')}
function handleWorkMusic(e){for(let f of e.target.files){workMusicFiles.push({name:f.name.replace(/\.[^/.]+$/,''),url:URL.createObjectURL(f)})}document.getElementById('workMusicList').innerHTML=workMusicFiles.map((f,i)=>'<div class="audio-track-item" onclick="playWorkMusic('+i+')"><span class="track-icon">🎵</span><span class="audio-track-name">'+f.name+'</span></div>').join('');e.target.value=''}
function playWorkMusic(i){if(workMusicAudio)workMusicAudio.pause();workMusicAudio=new Audio(workMusicFiles[i].url);workMusicAudio.loop=true;workMusicAudio.play();showToast('🎵 Ish musiqasi','info')}
function startPomo(){
if(pomoRunning)return;
pomoRunning=true;
if(pomoType==='free'){pomoModeTime=parseInt(document.getElementById('freeWork').value)||25;pomoTime=pomoModeTime*60;updatePomoDisp()}
if(pomoType==='rest'){pomoModeTime=parseInt(document.getElementById('restDuration').value)||30;pomoTime=pomoModeTime*60;updatePomoDisp()}
const wm=document.getElementById('workMusicToggle');
if(wm&&wm.classList.contains('active')&&workMusicFiles.length>0){if(workMusicAudio)workMusicAudio.pause();workMusicAudio=new Audio(workMusicFiles[0].url);workMusicAudio.loop=true;workMusicAudio.play()}
pomoInterval=setInterval(()=>{pomoTime--;updatePomoDisp();if(pomoTime<=0){clearInterval(pomoInterval);pomoRunning=false;pomoDone()}},1000);
}
function pausePomo(){clearInterval(pomoInterval);pomoRunning=false}
function resetPomo(){pausePomo();pomoTime=pomoModeTime*60;updatePomoDisp()}
function updatePomoDisp(){const m=Math.floor(pomoTime/60),s=pomoTime%60;document.getElementById('pomoTimer').textContent=String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')}
function pomoDone(){
state.pomoCount++;state.pomoTotalMin+=pomoModeTime;
state.pomoSessions.push({time:new Date().toLocaleTimeString().slice(0,5),type:pomoType,duration:pomoModeTime,date:todayKey});
if(state.pomoSessions.length>100)state.pomoSessions=state.pomoSessions.slice(-100);
updatePomoStats();renderPomoHistory();addXP(settings.xpPomo);
showToast('🍅 Seans yakunlandi! +'+settings.xpPomo+' XP','success');vibrate([200,100,200]);playBeep();
if('Notification'in window&&Notification.permission==='granted')new Notification('🍅 Pomodoro',{body:'Seans tugadi!'});
if(workMusicAudio){workMusicAudio.pause();workMusicAudio=null}
if(pomoType==='rest'&&restMusicAudio){restMusicAudio.pause();restMusicAudio=null}
saveAll();checkAch();
}
function updatePomoStats(){
document.getElementById('pomoCount').textContent=state.pomoCount;
document.getElementById('pomoTotalMin').textContent=state.pomoTotalMin;
const t=state.pomoSessions.filter(s=>s.date===todayKey);
document.getElementById('pomoTodayMin').textContent=t.reduce((a,s)=>a+s.duration,0);
}
function renderPomoHistory(){
const el=document.getElementById('pomoHistory');
const today=state.pomoSessions.filter(s=>s.date===todayKey);
if(!today.length){el.innerHTML='<div style="color:var(--text3);font-size:.8em;text-align:center;padding:10px">Hozircha seanslar yo\'q</div>';return}
el.innerHTML=today.map(s=>{
const isRest=s.type==='rest';
const lbl=isRest?'☕ Dam olish':s.type==='smart'?'🧠 Aqlli ish':s.type==='free'?'⏱️ Erkin ish':'🍅 Klassik ish';
return '<div class="pomo-history-item"><div class="phi-type" style="background:'+(isRest?'var(--accent3)':'var(--green)')+'"></div><span>'+s.time+'</span><span style="flex:1">'+lbl+'</span><span>'+s.duration+' daq</span></div>';
}).join('');
}

// ===== KITOBLAR =====
function openBookForm(){document.getElementById('bookFormContainer').style.display='block'}
function closeBookForm(){document.getElementById('bookFormContainer').style.display='none'}
function saveBook(){
const name=document.getElementById('bookName').value.trim();
if(!name){showToast('⚠️ Kitob nomini kiriting!','warning');return}
const book={id:Date.now(),name:name,author:document.getElementById('bookAuthor').value.trim(),pages:parseInt(document.getElementById('bookPages').value)||0,genre:document.getElementById('bookGenre').value,status:document.getElementById('bookStatus').value,currentPage:0,startDate:null,finishedDate:null,totalReadMin:0,sessions:[]};
if(book.status==='reading')book.startDate=todayKey;
booksData.push(book);saveAll();renderBooks();closeBookForm();
document.getElementById('bookName').value='';document.getElementById('bookAuthor').value='';document.getElementById('bookPages').value='';
showToast('📖 Kitob qo\'shildi!','success');addXP(3);checkAch();
}
function renderBooks(){
const reading=booksData.filter(b=>b.status==='reading'),later=booksData.filter(b=>b.status==='later'),done=booksData.filter(b=>b.status==='done');
document.getElementById('bookTotalCount').textContent=booksData.length;
document.getElementById('bookDoneCount').textContent=done.length;
document.getElementById('bookReadingCount').textContent=reading.length;
document.getElementById('bookPagesRead').textContent=booksData.reduce((a,b)=>a+b.currentPage,0);
document.getElementById('booksReading').innerHTML=reading.length?'<div class="section-title" style="font-size:.9em">📖 Hozir o\'qiyapman ('+reading.length+')</div>'+reading.map(bookCard).join(''):'';
document.getElementById('booksLater').innerHTML=later.length?'<div class="section-title" style="font-size:.9em">📚 Keyinroq ('+later.length+')</div>'+later.map(bookCard).join(''):'';
document.getElementById('booksDone').innerHTML=done.length?'<div class="section-title" style="font-size:.9em">✅ Tugatilgan ('+done.length+')</div>'+done.map(bookCard).join(''):'';
}
function bookCard(b){
const pct=b.pages>0?Math.round((b.currentPage/b.pages)*100):0;
let html='<div class="book-card"><div class="book-card-header"><div style="flex:1"><div class="book-card-title">📖 '+b.name+'</div><div class="book-card-author">'+(b.author||'Noma\'lum muallif')+'</div></div><span class="book-status-badge '+b.status+'">'+(b.status==='reading'?"O'qiyapman":b.status==='later'?'Keyinroq':'Tugagan')+'</span></div>';
html+='<div class="book-card-meta"><span>📑 '+(b.pages||'?')+' bet</span><span>🏷️ '+b.genre+'</span>';
if(b.currentPage>0)html+='<span>📄 '+b.currentPage+'/'+b.pages+'</span>';
if(b.totalReadMin>0)html+='<span>⏱️ '+b.totalReadMin+' daq</span>';
if(b.startDate&&b.status==='reading')html+='<span>📅 '+b.startDate+'</span>';
if(b.finishedDate)html+='<span>🏁 '+b.finishedDate+'</span>';
html+='</div>';
if(b.pages>0)html+='<div class="book-progress"><div class="book-progress-fill" style="width:'+pct+'%"></div></div><div style="font-size:.65em;color:var(--text3)">'+pct+'%</div>';
html+='<div class="book-card-actions">';
if(b.status==='reading')html+='<button class="btn btn-sm btn-success" onclick="startBookSession('+b.id+')">▶ O\'qish</button>';
if(b.status==='later')html+='<button class="btn btn-sm btn-ghost" onclick="startBookNow('+b.id+')">📖 Boshlash</button>';
html+='<button class="btn btn-sm btn-ghost" onclick="editBook('+b.id+')">✏️</button><button class="btn btn-sm btn-danger" onclick="deleteBook('+b.id+')">🗑️</button></div></div>';
return html;
}
function startBookNow(id){const b=booksData.find(x=>x.id===id);if(b){b.status='reading';b.startDate=todayKey;saveAll();renderBooks();showToast('📖 Kitob boshlandi!','success')}}
function editBook(id){
const b=booksData.find(x=>x.id===id);if(!b)return;
const name=prompt('📕 Kitob nomi:',b.name);if(name&&name.trim())b.name=name.trim();
const author=prompt('✍️ Muallif:',b.author);if(author!==null)b.author=author.trim();
const pages=prompt('📑 Betlar soni:',b.pages);if(pages)b.pages=parseInt(pages)||b.pages;
saveAll();renderBooks();showToast('✏️ Kitob tahrirlandi','info');
}
function deleteBook(id){if(!confirm('📖 Kitobni o\'chirasizmi?'))return;booksData=booksData.filter(b=>b.id!==id);saveAll();renderBooks();showToast('🗑️ Kitob o\'chirildi','info')}
let currentBookId=null,readInterval=null,readRemaining=0,readPaused=false,readSessionMin=0;
function startBookSession(id){
const b=booksData.find(x=>x.id===id);if(!b)return;
currentBookId=id;
const def=settings.bookTime||25;
const time=prompt('⏱️ Necha daqiqa o\'qiysiz?',String(def));if(!time)return;
readSessionMin=parseInt(time)||def;readRemaining=readSessionMin*60;readPaused=false;
document.getElementById('rmBookTitle').textContent=b.name;
document.getElementById('rmQuote').textContent='"'+QUOTES[Math.floor(Math.random()*QUOTES.length)]+'"';
document.getElementById('rmPageInfo').textContent=b.pages>0?'📑 Bet: '+b.currentPage+'/'+b.pages+' ('+Math.round((b.currentPage/b.pages)*100)+'%)':'📑 Bet kuzatuvi yo\'q';
document.getElementById('readingMode').classList.add('active');
createStars('readingStars');updateReadDisp();
readInterval=setInterval(()=>{if(!readPaused){readRemaining--;updateReadDisp();if(readRemaining<=0)readingTimeUp()}},1000);
if(document.documentElement.requestFullscreen)document.documentElement.requestFullscreen().catch(()=>{});
}
function createStars(id){const c=document.getElementById(id);c.innerHTML='';for(let i=0;i<50;i++){const s=document.createElement('div');s.className='star';s.style.left=Math.random()*100+'%';s.style.top=Math.random()*100+'%';s.style.animationDelay=Math.random()*2+'s';c.appendChild(s)}}
function updateReadDisp(){const m=Math.floor(readRemaining/60),s=readRemaining%60;document.getElementById('rmTimer').textContent=String(m).padStart(2,'0')+':'+String(s).padStart(2,'0')}
function pauseReading(btn){readPaused=!readPaused;btn.textContent=readPaused?'▶ Davom':'⏸ Pauza'}
function readingTimeUp(){
clearInterval(readInterval);
const b=booksData.find(x=>x.id===currentBookId);
if(b){b.totalReadMin+=readSessionMin;b.sessions.push({date:todayKey,min:readSessionMin})}
document.getElementById('readingMode').classList.remove('active');
if(b&&b.pages>0){
document.getElementById('bcmBookName').textContent=b.name;
document.getElementById('bcmPage').value='';
document.getElementById('bcmPageInfo').textContent='Hozirgi: '+b.currentPage+' | Jami: '+b.pages+' | Faqat oldinga! ('+(b.currentPage+1)+'-'+b.pages+')';
document.getElementById('bcmNote').value='';
document.getElementById('bookCompleteModal').classList.add('active');
}else{saveAll();renderBooks();addXP(settings.xpBook);showToast('📖 O\'qish yakunlandi! +'+settings.xpBook+' XP','success')}
if(settings.bookBreak)setTimeout(()=>showToast('☕ Qisqa tanaffus qiling — koʼzlaringizga dam bering','info'),1200);
vibrate([200,100,200]);playBeep();
if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});
}
function finishReading(){clearInterval(readInterval);readingTimeUp()}
function confirmBookPage(){
const b=booksData.find(x=>x.id===currentBookId);if(!b)return;
const page=parseInt(document.getElementById('bcmPage').value);
if(!page){showToast('⚠️ Bet raqamini kiriting!','warning');return}
if(page<=b.currentPage){showToast('⚠️ Orqaga qaytib bo\'lmaydi! Hozirgi: '+b.currentPage,'warning');return}
if(page>b.pages){showToast('⚠️ Kitob betlaridan oshdi! Jami: '+b.pages,'warning');return}
b.currentPage=page;
if(b.currentPage>=b.pages){b.status='done';b.finishedDate=todayKey;showToast('🎉 Kitob tugadi!','success');if(settings.confettiOn)launchConfetti()}
saveAll();renderBooks();closeModal('bookCompleteModal');addXP(settings.xpBook);
showToast('📖 Bet '+page+' ga yetdingiz! +'+settings.xpBook+' XP','success');checkAch();
}
function confirmBookDone(){
const b=booksData.find(x=>x.id===currentBookId);if(!b)return;
if(b.pages>0&&b.currentPage<b.pages&&!confirm('Kitob hali tugamagan ('+b.currentPage+'/'+b.pages+'). Rostdan tugatdingizmi?'))return;
b.status='done';b.finishedDate=todayKey;if(b.pages>0)b.currentPage=b.pages;
saveAll();renderBooks();closeModal('bookCompleteModal');addXP(settings.xpBook+10);
showToast('🎉 "'+b.name+'" tugadi! +'+(settings.xpBook+10)+' XP','success');
if(settings.confettiOn)launchConfetti();vibrate([300,100,300,100,300]);checkAch();
}
// ===== AUDIO =====
function openAudiobookForm(){document.getElementById('audiobookFormContainer').style.display='block'}
function closeAudiobookForm(){document.getElementById('audiobookFormContainer').style.display='none'}
function saveAudiobook(){
const name=document.getElementById('abName').value.trim();
if(!name){showToast('⚠️ Nom kiriting!','warning');return}
const ab={id:Date.now(),name:name,author:document.getElementById('abAuthor').value.trim(),genre:document.getElementById('abGenre').value,count:parseInt(document.getElementById('abCount').value)||1,note:document.getElementById('abNote').value.trim(),tracks:[],currentTrack:0,currentPos:0,totalListenedMin:0,status:'new'};
abData.push(ab);saveAll();renderAudiobooks();closeAudiobookForm();
document.getElementById('abName').value='';document.getElementById('abAuthor').value='';document.getElementById('abNote').value='';document.getElementById('abCount').value='1';
showToast('🎧 Audiokitob qo\'shildi! Endi audio yuklang.','success');
}
function renderAudiobooks(){
const el=document.getElementById('audiobookList');
document.getElementById('abTotalCount').textContent=abData.length;
document.getElementById('abDoneCount').textContent=abData.filter(a=>a.status==='done').length;
document.getElementById('abTotalMin').textContent=Math.round(abData.reduce((s,a)=>s+a.totalListenedMin,0));
document.getElementById('abTrackCount').textContent=abData.reduce((s,a)=>s+a.tracks.length,0);
if(!abData.length){el.innerHTML='<div class="empty-state"><div class="icon">🎧</div><div class="text">Audiokitoblar yo\'q</div></div>';return}
el.innerHTML=abData.map(ab=>{
let html='<div class="audiobook-card"><div class="audiobook-card-title">🎧 '+ab.name+'</div><div class="audiobook-card-meta">'+(ab.author?'<span>✍️ '+ab.author+'</span>':'')+'<span>🎭 '+ab.genre+'</span><span>🔊 '+ab.tracks.length+'/'+(ab.count||'?')+'</span>'+(ab.status==='done'?'<span style="color:var(--green)">✅</span>':'')+'</div>';
if(ab.note)html+='<div style="font-size:.7em;color:var(--text3);margin-bottom:8px">📝 '+ab.note+'</div>';
html+='<button class="btn btn-sm btn-ghost" onclick="addABTracks('+ab.id+')" style="margin-bottom:8px;width:100%;justify-content:center">📁 Audio qo\'shish</button>';
html+='<input type="file" id="abInput'+ab.id+'" accept="audio/*" multiple style="display:none" onchange="handleABFiles('+ab.id+',event)">';
ab.tracks.forEach((t,i)=>{html+='<div class="audio-track-item'+(ab.currentTrack===i&&ab.status==='listening'?' playing':'')+'" onclick="playABTrack('+ab.id+','+i+')"><span class="track-icon">'+(ab.currentTrack===i&&ab.status==='listening'?'🔊':'')+'</span><span class="audio-track-name">'+(i+1)+'. '+t.name+'</span>'+(t.duration?'<span class="audio-track-dur">'+fmtTime(t.duration)+'</span>':'')+'</div>'});
html+='<div style="display:flex;gap:6px;margin-top:8px"><button class="btn btn-sm btn-ghost" onclick="editAB('+ab.id+')" style="flex:1;justify-content:center">✏️</button><button class="btn btn-sm btn-danger" onclick="deleteAB('+ab.id+')" style="flex:1;justify-content:center">🗑️</button></div></div>';
return html;
}).join('');
}
function addABTracks(id){document.getElementById('abInput'+id).click()}
function handleABFiles(id,e){
const ab=abData.find(x=>x.id===id);if(!ab)return;
const files=e.target.files;
const room=(ab.count||0)>0?ab.count-ab.tracks.length:Infinity;
if(files.length>room){showToast('⚠️ Faqat '+Math.max(room,0)+' ta joy qoldi. Sonni ✏️ oshiring.','warning');e.target.value='';editAB(id);return}
for(let f of files){
const url=URL.createObjectURL(f);
const track={name:f.name.replace(/\.[^/.]+$/,''),url:url,duration:0};
const tmp=new Audio(url);
tmp.addEventListener('loadedmetadata',()=>{track.duration=tmp.duration;saveAll();renderAudiobooks()});
ab.tracks.push(track);
}
saveAll();renderAudiobooks();showToast('🎵 '+files.length+' ta audio qo\'shildi','success');
e.target.value='';
}
function editAB(id){
const ab=abData.find(x=>x.id===id);if(!ab)return;
let html='<h3>✏️ Audiokitobni tahrirlash</h3>'
+'<div class="form-group"><label>📕 Nomi</label><input class="form-input" id="eabName" value="'+(ab.name||'')+'"></div>'
+'<div class="form-group"><label>✍️ Muallif</label><input class="form-input" id="eabAuthor" value="'+(ab.author||'')+'"></div>'
+'<div class="form-group"><label>🎭 Janr</label><input class="form-input" id="eabGenre" value="'+(ab.genre||'')+'"></div>'
+'<div class="form-group"><label>🔊 Audio soni</label><input type="number" class="form-input" id="eabCount" value="'+(ab.count||ab.tracks.length)+'"></div>'
+'<button class="btn btn-primary" onclick="saveABEdit('+id+')">💾 Saqlash</button>'
+'<button class="btn btn-ghost" style="width:100%;margin-top:8px;justify-content:center" onclick="closeModal(\'taskDetailModal\')">Bekor</button>';
showModal('taskDetailModal',html);
}
function saveABEdit(id){
const ab=abData.find(x=>x.id===id);if(!ab)return;
ab.name=document.getElementById('eabName').value.trim()||ab.name;
ab.author=document.getElementById('eabAuthor').value.trim();
ab.genre=document.getElementById('eabGenre').value.trim()||ab.genre;
ab.count=parseInt(document.getElementById('eabCount').value)||ab.count;
saveAll();renderAudiobooks();closeModal('taskDetailModal');showToast('✏️ Saqlandi','success');
}
function deleteAB(id){if(!confirm('🎧 Audiokitobni o\'chirasizmi?'))return;abData=abData.filter(x=>x.id!==id);saveAll();renderAudiobooks();showToast('🗑️ O\'chirildi','info')}
let abAudio=null,abCurrent=null;
function playABTrack(abId,trackIdx){
const ab=abData.find(x=>x.id===abId);if(!ab)return;
const track=ab.tracks[trackIdx];if(!track)return;
if(abAudio){abAudio.pause();abAudio=null}
ab.currentTrack=trackIdx;ab.status='listening';
if(ab.currentPos>5&&track.duration>0&&!confirm('Oldingi joydan davom etasizmi?\nOK = Davomidan\nBekor = Boshidan'))ab.currentPos=0;
abAudio=new Audio(track.url);abAudio.currentTime=ab.currentPos||0;
abAudio.addEventListener('timeupdate',()=>{ab.currentPos=abAudio.currentTime;updateABProgress()});
abAudio.addEventListener('ended',()=>{
ab.totalListenedMin+=(track.duration||0)/60;ab.currentPos=0;
if(trackIdx<ab.tracks.length-1){playABTrack(abId,trackIdx+1)}
else{ab.status='done';saveAll();renderAudiobooks();showToast('🎉 Audiokitob tugadi!','success');addXP(25);if(settings.confettiOn)launchConfetti();document.getElementById('listeningMode').classList.remove('active');if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});checkAch()}
saveAll();
});
abAudio.play();abCurrent=ab;
document.getElementById('lmTitle').textContent=ab.name;
document.getElementById('lmInfo').textContent=(ab.author?ab.author+' | ':'')+(trackIdx+1)+'/'+ab.tracks.length+' | '+ab.genre;
document.getElementById('listeningMode').classList.add('active');
createStars('listeningStars');createVis();
if(document.documentElement.requestFullscreen)document.documentElement.requestFullscreen().catch(()=>{});
saveAll();renderAudiobooks();
}
function createVis(){const c=document.getElementById('visContainer');c.innerHTML='';for(let i=0;i<20;i++){const b=document.createElement('div');b.className='vis-bar';b.style.animationDelay=(Math.random()*0.5)+'s';b.style.animationDuration=(0.5+Math.random()*0.5)+'s';c.appendChild(b)}}
function updateABProgress(){if(!abAudio)return;const cur=abAudio.currentTime,tot=abAudio.duration||0;const pct=tot>0?(cur/tot)*100:0;document.getElementById('lmProgressFill').style.width=pct+'%';document.getElementById('lmCurTime').textContent=fmtTime(cur);document.getElementById('lmTotTime').textContent=fmtTime(tot)}
function toggleLmPlay(){if(!abAudio)return;if(abAudio.paused){abAudio.play();document.getElementById('lmPlayBtn').textContent='⏸'}else{abAudio.pause();document.getElementById('lmPlayBtn').textContent='▶'}}
function toggleLmPause(btn){toggleLmPlay();btn.textContent=abAudio.paused?'▶ Davom':'⏸ Pauza'}
function skipAudio(s){if(abAudio)abAudio.currentTime=Math.max(0,abAudio.currentTime+s)}
function setLmSpeed(s,el){if(abAudio)abAudio.playbackRate=s;document.querySelectorAll('.speed-btn').forEach(b=>b.classList.remove('active'));el.classList.add('active')}
function seekAudio(e){if(!abAudio)return;const r=document.getElementById('lmProgressBar').getBoundingClientRect();const pct=(e.clientX-r.left)/r.width;abAudio.currentTime=pct*(abAudio.duration||0)}
function finishListening(){
if(abAudio){if(abCurrent)abCurrent.totalListenedMin+=abAudio.currentTime/60;abAudio.pause();abAudio=null}
if(abCurrent){abCurrent.currentPos=0;saveAll()}
document.getElementById('listeningMode').classList.remove('active');
if(document.fullscreenElement)document.exitFullscreen().catch(()=>{});
addXP(15);showToast('🎧 Tinglash yakunlandi! +15 XP','success');renderAudiobooks();checkAch();
}
function fmtTime(s){if(!s||isNaN(s))return'0:00';const m=Math.floor(s/60),sec=Math.floor(s%60);return m+':'+String(sec).padStart(2,'0')}
// ===== TREKERLAR =====
function switchTracker(t,el){
document.querySelectorAll('.tracker-tab').forEach(x=>x.classList.remove('active'));
document.querySelectorAll('.tracker-content').forEach(x=>x.classList.remove('active'));
el.classList.add('active');
document.getElementById('tracker-'+t).classList.add('active');
}
function initWater(){if(!waterData[todayKey])waterData[todayKey]=0;renderWater();renderWaterWeekly();renderWaterStreak()}
function renderWater(){
const count=waterData[todayKey]||0,goal=settings.waterGoal||8;
document.getElementById('waterCount').textContent=count;
const gl=document.getElementById('waterGoalLbl');if(gl)gl.textContent=goal;
document.getElementById('waterMl').textContent=count*250;
const grid=document.getElementById('waterGrid');grid.innerHTML='';
for(let i=0;i<goal;i++){
const filled=i<count;
grid.innerHTML+='<div class="water-cup'+(filled?' filled':'')+(filled?' locked':'')+'" onclick="setWater('+(i+1)+')"><span class="cup-num">'+(i+1)+'</span></div>';
}
}
function addWater(){
const goal=settings.waterGoal||8;
if(!waterData[todayKey])waterData[todayKey]=0;
if(waterData[todayKey]<goal){
waterData[todayKey]++;saveAll();renderWater();renderWaterWeekly();renderWaterStreak();
showToast('💧 +1 stakan! ('+waterData[todayKey]+'/'+goal+')','success');addXP(2);vibrate(50);
if(waterData[todayKey]===goal){showToast('🎉 Bugungi suv maqsadi to\'ldi!','success');if(settings.confettiOn)launchConfetti()}
}else showToast('🎉 Bugun '+goal+' stakan to\'ldi!','success');
}
function setWater(n){
const goal=settings.waterGoal||8;
if(n<(waterData[todayKey]||0)){showToast('⚠️ Suvni qaytarib bo\'lmaydi!','warning');return}
if(n>goal){showToast('⚠️ Maqsad '+goal+' stakan!','warning');return}
waterData[todayKey]=n;saveAll();renderWater();renderWaterWeekly();renderWaterStreak();
if(n>0)addXP(1);
}
function renderWaterWeekly(){
const el=document.getElementById('waterWeekly');
const days=['Ya','Du','Se','Ch','Pa','Ju','Sh'],goal=settings.waterGoal||8;
let html='';
for(let i=6;i>=0;i--){
const d=new Date();d.setDate(d.getDate()-i);
const key=d.toISOString().split('T')[0],val=waterData[key]||0;
const pct=Math.min((val/goal)*100,100);
html+='<div class="sleep-bar-container"><span class="sleep-bar-label">'+days[d.getDay()]+'</span><div class="sleep-bar"><div class="sleep-bar-fill" style="width:'+pct+'%;background:linear-gradient(90deg,#06b6d4,#22d3ee)">'+val+'/'+goal+'</div></div></div>';
}
el.innerHTML=html;
}
function renderWaterStreak(){
let streak=0;const goal=settings.waterGoal||8;
for(let i=0;i<30;i++){const d=new Date();d.setDate(d.getDate()-i);if((waterData[d.toISOString().split('T')[0]]||0)>=goal)streak++;else break}
document.getElementById('waterStreak').textContent=streak>0?'🔥 '+streak+' kun ketma-ket '+goal+' stakan!':'';
}
function saveSleep(){
const start=document.getElementById('sleepStart').value,end=document.getElementById('sleepEnd').value;
if(!start||!end){showToast('⚠️ Vaqtlarni kiriting!','warning');return}
let sM=parseInt(start.split(':')[0])*60+parseInt(start.split(':')[1]);
let eM=parseInt(end.split(':')[0])*60+parseInt(end.split(':')[1]);
if(eM<sM)eM+=1440;
const dur=(eM-sM)/60;
const note=document.getElementById('sleepNote')?document.getElementById('sleepNote').value.trim():'';
sleepData=sleepData.filter(s=>s.date!==todayKey);
sleepData.push({date:todayKey,start:start,end:end,duration:parseFloat(dur.toFixed(1)),quality:'',note:note});
if(sleepData.length>30)sleepData=sleepData.slice(-30);
saveAll();
document.getElementById('sleepResult').style.display='block';
document.getElementById('sleepDuration').textContent=dur.toFixed(1)+' soat';
renderSleepHistory();renderSleepAvg();addXP(3);showToast('😴 Uyqu saqlandi! +3 XP','success');
}
function setSleepQ(q,el){const e=sleepData.find(s=>s.date===todayKey);if(e){e.quality=q;saveAll()}document.querySelectorAll('.sleep-quality-btn').forEach(b=>b.classList.remove('active'));el.classList.add('active')}
function renderSleepHistory(){
const el=document.getElementById('sleepHistory');
const last7=sleepData.slice(-7);
if(!last7.length){el.innerHTML='<div style="color:var(--text3);font-size:.8em;text-align:center;padding:8px">Hozircha ma\'lumot yo\'q</div>';return}
let html='';
last7.forEach(s=>{
const pct=Math.min((s.duration/10)*100,100);
const q={bad:'😞',ok:'😐',good:'😊',great:'🤩'}[s.quality]||'';
html+='<div class="sleep-bar-container"><span class="sleep-bar-label">'+s.date.slice(8)+'</span><div class="sleep-bar"><div class="sleep-bar-fill" style="width:'+pct+'%">'+s.duration+' soat '+q+'</div></div></div>';
});
el.innerHTML=html;
}
function renderSleepAvg(){
const last7=sleepData.slice(-7);
if(!last7.length){document.getElementById('sleepAvg').textContent='';return}
const avg=last7.reduce((a,s)=>a+s.duration,0)/last7.length;
const goal=settings.sleepGoal||8;
document.getElementById('sleepAvg').textContent='📊 O\'rtacha: '+avg.toFixed(1)+' soat | Maqsad: '+goal+' soat'+(avg>=goal?' ✅':' ⚠️');
}
let moodType='emoji',selMood='',selScale=0;
function setMoodType(type,el){
moodType=type;
document.querySelectorAll('.mood-type-btn').forEach(b=>b.classList.remove('active'));
el.classList.add('active');
document.getElementById('moodEmojiSection').style.display=(type==='emoji'||type==='all')?'block':'none';
document.getElementById('moodScaleSection').style.display=(type==='scale'||type==='all')?'block':'none';
document.getElementById('moodNoteSection').style.display=(type==='note'||type==='all')?'block':'none';
if(type==='scale'||type==='all')renderMoodScale();
}
function selectMoodEmoji(e,el){selMood=e;document.querySelectorAll('.mood-emoji').forEach(x=>x.classList.remove('selected'));el.classList.add('selected')}
function renderMoodScale(){const el=document.getElementById('moodScale');el.innerHTML='';for(let i=1;i<=10;i++){el.innerHTML+='<button class="mood-scale-btn'+(selScale===i?' selected':'')+'" onclick="selScaleFn('+i+',this)">'+i+'</button>'}}
function selScaleFn(n,el){selScale=n;document.querySelectorAll('.mood-scale-btn').forEach(b=>b.classList.remove('selected'));el.classList.add('selected')}
function saveMood(){
const entry={date:todayKey,type:moodType,emoji:selMood,scale:selScale,note:''};
if(moodType==='note'||moodType==='all')entry.note=document.getElementById('moodNote').value.trim();
if(moodType==='emoji'&&!selMood){showToast('⚠️ Emoji tanlang!','warning');return}
if(moodType==='scale'&&!selScale){showToast('⚠️ Ball tanlang!','warning');return}
if(moodType==='note'&&!entry.note){showToast('⚠️ Izoh yozing!','warning');return}
if(moodType==='all'&&!selMood&&!selScale&&!entry.note){showToast('⚠️ Kamida bittasini to\'ldiring!','warning');return}
moodData=moodData.filter(m=>m.date!==todayKey);
moodData.push(entry);
if(moodData.length>30)moodData=moodData.slice(-30);
saveAll();addXP(3);showToast('🌡️ Kayfiyat saqlandi! +3 XP','success');
renderMoodHistory();resetMood();
}
function skipMood(){showToast('⏭️ Yaxshi, bugun yozmadingiz','info')}
function resetMood(){selMood='';selScale=0;document.querySelectorAll('.mood-emoji').forEach(e=>e.classList.remove('selected'));document.querySelectorAll('.mood-scale-btn').forEach(b=>b.classList.remove('selected'));document.getElementById('moodNote').value=''}
function renderMoodHistory(){
const el=document.getElementById('moodHistory');
const last7=moodData.slice(-7);
if(!last7.length){el.innerHTML='<div style="color:var(--text3);font-size:.8em">Hozircha ma\'lumot yo\'q</div>';return}
el.innerHTML=last7.map(m=>{
let html='<div class="mood-history-item" onclick="showMoodDetail(\''+m.date+'\')">';
html+='<div class="emoji">'+(m.emoji||'📊')+'</div><div class="date">'+m.date.slice(8)+'</div>';
if(m.scale)html+='<div class="scale-val">'+m.scale+'/10</div>';
if(m.note)html+='<div class="note-indicator">📝</div>';
html+='</div>';
return html;
}).join('');
}
function showMoodDetail(date){
const m=moodData.find(x=>x.date===date);if(!m)return;
let html='<h3 style="margin-bottom:12px">🌡️ Kayfiyat — '+date+'</h3>';
if(m.emoji)html+='<div style="font-size:3em;text-align:center;margin:15px 0">'+m.emoji+'</div>';
if(m.scale)html+='<div style="text-align:center;margin:10px 0;font-size:1.2em">📊 Ball: <strong style="color:var(--accent3)">'+m.scale+'/10</strong></div>';
if(m.note)html+='<div style="padding:12px;background:var(--bg3);border-radius:8px;font-size:.85em;margin:10px 0;line-height:1.5">📝 '+m.note+'</div>';
if(!m.emoji&&!m.scale&&!m.note)html+='<div style="color:var(--text3);text-align:center">Ma\'lumot yo\'q</div>';
html+='<button class="btn btn-ghost" onclick="closeModal(\'moodDetailModal\')" style="width:100%;margin-top:12px;justify-content:center">Yopish</button>';
document.getElementById('moodDetailModalContent').innerHTML=html;
document.getElementById('moodDetailModal').classList.add('active');
}

// ===== AI MASLAHATCHI =====
function generateAI(){
const el=document.getElementById('aiMessages');
const adv=[];
const tt=state.tasks.filter(t=>t.date===todayKey);
const done=tt.filter(t=>t.completed).length;
const rate=tt.length>0?Math.round((done/tt.length)*100):0;
if(tt.length===0)adv.push({t:'warning',i:'📝',x:"Bugun hali vazifa qo'shmadingiz. Kamida 3 ta vazifa rejalashtiring!"});
else if(tt.length>10)adv.push({t:'danger',i:'⚠️',x:'Bugun '+tt.length+' ta vazifa bor — juda ko\'p! 5-7 taga kamaytiring.'});
else if(tt.length>=3&&tt.length<=7)adv.push({t:'success',i:'✅',x:'Bugun '+tt.length+' ta vazifa — optimal miqdor! Davom eting.'});
if(rate===100&&tt.length>0)adv.push({t:'success',i:'🎉',x:'Barcha vazifalar bajarildi! Ajoyib ish!'});
else if(rate<30&&tt.length>3)adv.push({t:'danger',i:'📉',x:'Bajarish foizi atigi '+rate+'%. Eng oson vazifadan boshlang!'});
else if(rate>=50&&rate<80)adv.push({t:'warning',i:'💪',x:'Yarim yo\'ldasiz! '+rate+'% bajarildi. Kuchliroq davom eting!'});
const catCounts={};
tt.forEach(t=>{catCounts[t.category]=(catCounts[t.category]||0)+1});
const maxCat=Object.entries(catCounts).sort((a,b)=>b[1]-a[1])[0];
if(maxCat&&maxCat[1]>tt.length*0.6&&tt.length>3)adv.push({t:'warning',i:'⚖️',x:'Vazifalarning '+maxCat[1]+' tasi "'+CATS[maxCat[0]].name+'" ga tegishli. Boshqa sohalarga ham vaqt ajrating.'});
const water=waterData[todayKey]||0,waterGoal=settings.waterGoal||8;
if(water<waterGoal/2)adv.push({t:'warning',i:'💧',x:'Bugun atigi '+water+'/'+waterGoal+' stakan suv ichdingiz. Ko\'proq iching!'});
if(state.streak>=3)adv.push({t:'success',i:'🔥',x:state.streak+' kun ketma-ket faolsiz! Ajoyib intizom!'});
const overdue=getOverdueTasks();
if(overdue.length>0)adv.push({t:'warning',i:'⚠️',x:overdue.length+' ta kechikkan vazifa bor! Ko\'rib chiqing.'});
const reading=booksData.filter(b=>b.status==='reading');
if(reading.length>0)adv.push({t:'info',i:'📖',x:'"'+reading[0].name+'" kitobini davom eting. Bet: '+reading[0].currentPage+'/'+reading[0].pages});
const hour=new Date().getHours();
if(hour>=22)adv.push({t:'info',i:'🌙',x:'Kech bo\'ldi. Ertangi kunni rejalashtiring va uxlang!'});
else if(hour>=6&&hour<9)adv.push({t:'success',i:'🌅',x:'Xayrli tong! Bugungi eng muhim vazifani birinchi bajaring!'});
if(state.pomoCount===0&&tt.filter(t=>!t.completed).length>0)adv.push({t:'info',i:'🍅',x:'Pomodoro usulini sinang: 25 daqiqa ish + 5 daqiqa dam. Fokusni oshiradi!'});
const lastSleep=sleepData[sleepData.length-1];
if(lastSleep&&lastSleep.duration<6)adv.push({t:'danger',i:'😴',x:'Oxirgi uyqungiz '+lastSleep.duration+' soat. Kamida '+(settings.sleepGoal||8)+' soat uxlang!'});
if(!state.dailyFocus)adv.push({t:'info',i:'🎯',x:'Bugungi fokus maqsadingizni belgilang!'});
el.innerHTML=adv.slice(0,6).map(a=>'<div class="ai-msg '+a.t+'"><span class="ai-icon">'+a.i+'</span>'+a.x+'</div>').join('');
if(!adv.length)el.innerHTML='<div class="ai-msg success"><span class="ai-icon">✨</span>Hammasi joyida! Davom eting!</div>';
renderWeeklyReport();renderDailyReport();renderGoalsProgress();
}
function renderWeeklyReport(){
const monday=getMonday(new Date());
const days=['Du','Se','Ch','Pa','Ju','Sh','Ya'];
let wTotal=0,wDone=0;
let html='<div class="report-card"><div class="report-stats">';
for(let i=0;i<7;i++){const d=new Date(monday);d.setDate(d.getDate()+i);const ds=d.toISOString().split('T')[0];const dt=state.tasks.filter(t=>t.date===ds);wTotal+=dt.length;wDone+=dt.filter(t=>t.completed).length}
html+='<div class="report-stat"><div class="rs-val" style="color:var(--neon-cyan)">'+wTotal+'</div><div class="rs-lbl">Jami</div></div>';
html+='<div class="report-stat"><div class="rs-val" style="color:var(--green)">'+wDone+'</div><div class="rs-lbl">Bajarilgan</div></div>';
html+='<div class="report-stat"><div class="rs-val" style="color:var(--accent3)">'+(wTotal-wDone)+'</div><div class="rs-lbl">Qolgan</div></div></div>';
for(let i=0;i<7;i++){const d=new Date(monday);d.setDate(d.getDate()+i);const ds=d.toISOString().split('T')[0];const dt=state.tasks.filter(t=>t.date===ds);const dd=dt.filter(t=>t.completed).length;const pct=dt.length>0?Math.round((dd/dt.length)*100):0;
html+='<div class="report-bar-row"><span class="report-bar-label">'+days[i]+'</span><div class="report-bar"><div class="report-bar-fill done" style="width:'+pct+'%">'+dd+'/'+dt.length+'</div></div></div>'}
html+='</div>';
document.getElementById('weeklyReport').innerHTML=html;
}
function renderDailyReport(){
const tt=state.tasks.filter(t=>t.date===todayKey);
const done=tt.filter(t=>t.completed).length;
const water=waterData[todayKey]||0,goal=settings.waterGoal||8;
const sleep=sleepData.find(s=>s.date===todayKey);
const mood=moodData.find(m=>m.date===todayKey);
const todayPomo=state.pomoSessions.filter(s=>s.date===todayKey);
let html='<div class="report-card"><div class="report-stats">';
html+='<div class="report-stat"><div class="rs-val" style="color:var(--neon-cyan)">'+done+'/'+tt.length+'</div><div class="rs-lbl">Vazifalar</div></div>';
html+='<div class="report-stat"><div class="rs-val" style="color:var(--gold)">'+todayPomo.length+'</div><div class="rs-lbl">Pomodoro</div></div>';
html+='<div class="report-stat"><div class="rs-val" style="color:#06b6d4">'+water+'/'+goal+'</div><div class="rs-lbl">Suv</div></div></div>';
if(sleep)html+='<div style="font-size:.8em;color:var(--text2);margin-top:6px">😴 Uyqu: '+sleep.duration+' soat '+(sleep.quality?({bad:'😞',ok:'😐',good:'😊',great:'🤩'}[sleep.quality]||''):'')+'</div>';
if(mood)html+='<div style="font-size:.8em;color:var(--text2);margin-top:4px">🌡️ Kayfiyat: '+(mood.emoji||mood.scale+'/10')+(mood.note?' 📝':'')+'</div>';
const reading=booksData.filter(b=>b.status==='reading');
if(reading.length>0)html+='<div style="font-size:.8em;color:var(--text2);margin-top:4px">📖 Kitob: "'+reading[0].name+'" — '+reading[0].currentPage+'/'+reading[0].pages+' bet</div>';
html+='</div>';
document.getElementById('dailyReport').innerHTML=html;
}
function renderGoalsProgress(){
const el=document.getElementById('goalsProgress');let html='';
html+='<div class="goal-item"><div class="goal-item-title">🎯 Bugungi fokus</div>';
html+='<div style="font-size:.8em;color:var(--text2)">'+(state.dailyFocus||'Belgilanmagan')+(state.dailyFocusTask?' → '+state.dailyFocusTask:'')+'</div>';
const focusDone=state.tasks.some(t=>t.isFocus&&t.completed&&t.date===todayKey);
html+='<div style="margin-top:6px;font-size:.9em;font-weight:700;color:'+(focusDone?'var(--green)':'var(--accent3)')+'">'+(state.dailyFocus?(focusDone?'✅ Bajarildi':'⬜ Hali bajarilmadi'):'—')+'</div></div>';
const tt=state.tasks.filter(t=>t.date===todayKey);const done=tt.filter(t=>t.completed).length;const pct=tt.length?Math.round((done/tt.length)*100):0;
html+='<div class="goal-item"><div class="goal-item-title">📊 Bugun umumiy</div><div class="goal-progress-bar"><div class="goal-progress-fill" style="width:'+pct+'%"></div></div><div class="goal-progress-text">'+done+'/'+tt.length+' ('+pct+'%)</div></div>';
el.innerHTML=html;
}
// ===== SHABLONLAR =====
const TEMPLATES=[
{id:'work',icon:'💼',name:'Ish kuni',desc:'Professional kun',goal:'Ish samaradorligi',tags:['ish','kunlik'],tasks:[{title:'Rejalashtirish',category:'work',time:'09:00',dur:15},{title:'Asosiy loyiha',category:'work',time:'09:30',dur:120},{title:'Tushlik',category:'meal',time:'13:00',dur:30},{title:'Email va xabarlar',category:'work',time:'14:00',dur:30},{title:'Dam olish',category:'rest',time:'18:00',dur:30}]},
{id:'rest',icon:'🧘',name:'Dam olish',desc:'Relax kuni',goal:'Ruhiy tiklanish',tags:['dam','salomatlik'],tasks:[{title:'Ertalabki mashq',category:'sport',time:'08:00',dur:20},{title:'Kitob o\'qish',category:'study',time:'10:00',dur:30},{title:'Oila bilan vaqt',category:'family',time:'15:00',dur:60},{title:'Xobbi',category:'rest',time:'17:00',dur:45},{title:'Detoks',category:'detox',time:'20:00',dur:60}]},
{id:'sport',icon:'🏋️',name:'Sport kuni',desc:'Faol kun',goal:'Jismoniy salomatlik',tags:['sport'],tasks:[{title:'Yugurish',category:'sport',time:'07:00',dur:30},{title:'Kuch mashqlari',category:'sport',time:'08:00',dur:45},{title:'Stretching',category:'sport',time:'09:00',dur:15},{title:'Suv 8 stakan',category:'meal',time:'',dur:0}]},
{id:'study',icon:'📚',name:"O'qish kuni",desc:'Bilim kuni',goal:'Bilim oshirish',tags:['o\'qish'],tasks:[{title:'Yangi mavzu',category:'study',time:'09:00',dur:60},{title:'Amaliyot',category:'study',time:'10:30',dur:45},{title:'Takrorlash',category:'study',time:'14:00',dur:30},{title:'Ibadat',category:'worship',time:'18:00',dur:20}]},
{id:'family',icon:'👨‍👩‍👧',name:'Oila kuni',desc:'Oila bilan vaqt',goal:'Oila mustahkamligi',tags:['oila'],tasks:[{title:'Birga nonushta',category:'meal',time:'08:00',dur:30},{title:'Oila bilan sayr',category:'family',time:'10:00',dur:60},{title:'Birga o\'yin',category:'family',time:'16:00',dur:45},{title:'Kechki ovqat',category:'meal',time:'19:00',dur:45}]},
{id:'detox',icon:'📵',name:'Detoks kuni',desc:'Raqamli detoks',goal:'Ruhiy tozalanish',tags:['detoks'],tasks:[{title:'Telefonsiz ertalab',category:'detox',time:'07:00',dur:120},{title:'Tabiatda sayr',category:'rest',time:'10:00',dur:60},{title:'Kitob o\'qish',category:'study',time:'14:00',dur:45},{title:'Meditatsiya',category:'rest',time:'20:00',dur:20}]}
];
let ctTasks=[];
function renderTemplates(){
document.getElementById('templatesGrid').innerHTML=TEMPLATES.map(t=>{
let html='<div class="template-card"><div class="t-icon">'+t.icon+'</div><div class="t-name">'+t.name+'</div><div class="t-desc">'+t.desc+'</div>';
if(t.goal)html+='<div class="t-goal">🎯 '+t.goal+'</div>';
html+='<div class="t-count">'+t.tasks.length+' vazifa</div>';
if(t.tags.length)html+='<div class="t-tags">'+t.tags.map(tag=>'<span class="t-tag">'+tag+'</span>').join('')+'</div>';
html+='<button class="template-apply-btn" onclick="applyT(\''+t.id+'\')">📥 Qo\'llash</button></div>';
return html;
}).join('');
renderMyT();renderTemplateStats();
}
function applyT(id){
const t=TEMPLATES.find(x=>x.id===id);if(!t)return;
t.tasks.forEach(task=>{state.tasks.push({id:Date.now()+Math.random(),title:task.title,category:task.category,priority:'medium',startTime:task.time||'',endTime:'',duration:task.dur||0,recurring:'none',tags:t.tags||[],notes:'',image:null,link:null,isFocus:false,completed:false,completedAt:null,completionNote:'',completionImage:null,date:todayKey})});
saveAll();renderTasks();renderCategories();updateStats();addXP(3);
showToast('📋 "'+t.name+'" qo\'llandi! +3 XP','success');
if(settings.confettiOn)launchConfetti();
}
function addCTTask(){
const name=document.getElementById('ctTaskName').value.trim();
if(!name){showToast('⚠️ Vazifa nomini kiriting!','warning');return}
ctTasks.push({title:name,category:document.getElementById('ctTaskCat').value,time:document.getElementById('ctTaskTime').value,dur:parseInt(document.getElementById('ctTaskDur').value)||0});
document.getElementById('ctTaskName').value='';document.getElementById('ctTaskTime').value='';document.getElementById('ctTaskDur').value='';
renderCTList();
}
function renderCTList(){
document.getElementById('ctTaskList').innerHTML=ctTasks.map((t,i)=>'<div class="template-task-item"><span>'+CATS[t.category].icon+' '+t.title+(t.time?' ⏰'+t.time:'')+(t.dur?' ⏱️'+t.dur+'daq':'')+'</span><span class="remove-tt" onclick="ctTasks.splice('+i+',1);renderCTList()">✕</span></div>').join('');
}
function saveCT(){
const name=document.getElementById('ctName').value.trim();
if(!name||!ctTasks.length){showToast('⚠️ Nom va kamida 1 vazifa kerak!','warning');return}
const tags=document.getElementById('ctTags').value.split(',').map(t=>t.trim()).filter(t=>t);
customT.push({id:Date.now(),name:name,goal:document.getElementById('ctGoal').value.trim(),tags:tags,tasks:[...ctTasks],usedCount:0});
saveAll();
document.getElementById('ctName').value='';document.getElementById('ctGoal').value='';document.getElementById('ctTags').value='';
ctTasks=[];renderCTList();renderMyT();
showToast('💾 Shablon saqlandi!','success');
}
function renderMyT(){
const el=document.getElementById('myTemplates');
if(!customT.length){el.innerHTML='<div style="color:var(--text3);font-size:.8em;text-align:center;padding:10px">Hozircha shablonlar yo\'q</div>';return}
el.innerHTML=customT.map(t=>{
let html='<div class="template-card" style="margin-bottom:8px;text-align:left;display:flex;align-items:center;gap:10px;flex-wrap:wrap">';
html+='<div class="t-icon">📋</div><div style="flex:1;min-width:120px"><div class="t-name">'+t.name+'</div><div class="t-count">'+t.tasks.length+' vazifa';
if(t.goal)html+=' | 🎯 '+t.goal;
html+='</div>';
if(t.tags&&t.tags.length)html+='<div class="t-tags" style="justify-content:flex-start;margin-top:3px">'+t.tags.map(tag=>'<span class="t-tag">'+tag+'</span>').join('')+'</div>';
html+='</div>';
html+='<button class="template-apply-btn" style="width:auto;padding:7px 12px" onclick="applyCT('+t.id+')">📥</button>';
html+='<button class="task-action-btn delete" onclick="delCT('+t.id+')">🗑️</button></div>';
return html;
}).join('');
}
function applyCT(id){
const t=customT.find(x=>x.id===id);if(!t)return;
t.tasks.forEach(task=>{state.tasks.push({id:Date.now()+Math.random(),title:task.title,category:task.category,priority:'medium',startTime:task.time||'',endTime:'',duration:task.dur||0,recurring:'none',tags:t.tags||[],notes:'',image:null,link:null,isFocus:false,completed:false,completedAt:null,completionNote:'',completionImage:null,date:todayKey})});
t.usedCount=(t.usedCount||0)+1;
saveAll();renderTasks();renderCategories();updateStats();renderTemplateStats();addXP(3);
showToast('📋 "'+t.name+'" qo\'llandi! +3 XP','success');
}
function delCT(id){
if(!confirm('Shablonni o\'chirasizmi?'))return;
customT=customT.filter(t=>t.id!==id);
saveAll();renderMyT();renderTemplateStats();
showToast('🗑️ Shablon o\'chirildi','info');
}
function renderTemplateStats(){
const el=document.getElementById('templateStats');
const allUsed=[...TEMPLATES.map(t=>({name:t.name,icon:t.icon,count:0})),...customT.map(t=>({name:t.name,icon:'📋',count:t.usedCount||0}))];
const used=allUsed.filter(t=>t.count>0);
if(!used.length){el.innerHTML='<div style="color:var(--text3);font-size:.8em;text-align:center;padding:8px">Hali shablonlar ishlatilmagan</div>';return}
el.innerHTML=used.map(t=>'<div class="detailed-stat-row"><span class="ds-label">'+t.icon+' '+t.name+'</span><span class="ds-value">'+t.count+' marta</span></div>').join('');
}
// ===== SOZLAMALAR =====
function renderSettings(){
document.getElementById('pinToggle').classList.toggle('active',settings.pinOn);
document.getElementById('fontSizeSetting').value=settings.fontSize;
document.getElementById('xpTask').value=settings.xpTask;
document.getElementById('xpPomo').value=settings.xpPomo;
document.getElementById('xpBook').value=settings.xpBook;
document.getElementById('xpAch').value=settings.xpAch;
document.getElementById('setPomoWork').value=settings.pomoWork;
document.getElementById('setPomoBreak').value=settings.pomoBreak;
document.getElementById('setPomoLong').value=settings.pomoLong;
document.getElementById('setPomoCycle').value=settings.pomoCycleN;
document.getElementById('setBookTime').value=settings.bookTime;
document.getElementById('setWaterGoal').value=settings.waterGoal;
document.getElementById('setSleepGoal').value=settings.sleepGoal;
document.getElementById('reminderTime').value=settings.reminderMin;
document.getElementById('notifToggle').classList.toggle('active',settings.notifOn);
document.getElementById('soundToggle').classList.toggle('active',settings.soundOn);
document.getElementById('animToggle').classList.toggle('active',settings.animOn);
document.getElementById('bookBreakToggle').classList.toggle('active',settings.bookBreak);
document.documentElement.classList.toggle('no-anim',!settings.animOn);
let totalSize=0;
for(let key in localStorage){if(localStorage.hasOwnProperty(key))totalSize+=localStorage[key].length*2}
document.getElementById('dataSize').textContent=(totalSize/1024).toFixed(1)+' KB';
}
function togglePinSetting(){
settings.pinOn=!settings.pinOn;
document.getElementById('pinToggle').classList.toggle('active',settings.pinOn);
saveAll();
showToast(settings.pinOn?'🔐 PIN himoya yoqildi':'🔓 PIN himoya o\'chirildi','info');
}
function toggleNotifSetting(){
settings.notifOn=!settings.notifOn;
document.getElementById('notifToggle').classList.toggle('active',settings.notifOn);
saveAll();
if(settings.notifOn&&'Notification'in window)Notification.requestPermission();
showToast(settings.notifOn?'🔔 Bildirishnoma yoqildi':'🔕 Bildirishnoma o\'chirildi','info');
}
function toggleSoundSetting(){
settings.soundOn=!settings.soundOn;
document.getElementById('soundToggle').classList.toggle('active',settings.soundOn);
saveAll();
if(settings.soundOn)playBeep();
}
function toggleAnimSetting(){
settings.animOn=!settings.animOn;
document.getElementById('animToggle').classList.toggle('active',settings.animOn);
document.documentElement.classList.toggle('no-anim',!settings.animOn);
saveAll();
}
function toggleBookBreakSetting(){
settings.bookBreak=!settings.bookBreak;
document.getElementById('bookBreakToggle').classList.toggle('active',settings.bookBreak);
saveAll();
}
function changePin(){
const p=prompt('Yangi 4 xonali PIN kiriting:');
if(p&&p.length===4&&!isNaN(p)){settings.pin=p;saveAll();showToast('✅ PIN o\'zgartirildi!','success')}
else if(p!==null)showToast('❌ 4 xonali raqam kiriting!','warning');
}
function saveSettings(){
settings.xpTask=parseInt(document.getElementById('xpTask').value)||10;
settings.xpPomo=parseInt(document.getElementById('xpPomo').value)||15;
settings.xpBook=parseInt(document.getElementById('xpBook').value)||20;
settings.xpAch=parseInt(document.getElementById('xpAch').value)||25;
settings.pomoWork=parseInt(document.getElementById('setPomoWork').value)||25;
settings.pomoBreak=parseInt(document.getElementById('setPomoBreak').value)||5;
settings.pomoLong=parseInt(document.getElementById('setPomoLong').value)||15;
settings.pomoCycleN=parseInt(document.getElementById('setPomoCycle').value)||4;
settings.bookTime=parseInt(document.getElementById('setBookTime').value)||25;
settings.waterGoal=parseInt(document.getElementById('setWaterGoal').value)||8;
settings.sleepGoal=parseInt(document.getElementById('setSleepGoal').value)||8;
settings.reminderMin=parseInt(document.getElementById('reminderTime').value)||10;
saveAll();
showToast('⚙️ Sozlamalar saqlandi','info');
}
function applyFontSize(size){
settings.fontSize=size;
document.body.className='';
document.body.classList.add('font-'+size);
saveAll();
}
function clearTasksOnly(){
if(!confirm('⚠️ Barcha vazifalar o\'chiriladi!'))return;
state.tasks=[];saveAll();renderAll();
showToast('🗑️ Vazifalar tozalandi','info');
}
function clearAllData(){
if(!confirm('⚠️ BARCHA ma\'lumotlar o\'chiriladi! Ishonchingiz komilmi?'))return;
if(!confirm('❌ Bu qaytarib BO\'LMAYDI! Rostdan ham?'))return;
localStorage.clear();location.reload();
}
function resetSettings(){
if(!confirm('Barcha sozlamalar standartga qaytarilsinmi?'))return;
settings={pinOn:false,pin:'1234',notifOn:true,vibOn:true,soundOn:false,reminderMin:10,fontSize:'medium',animOn:true,confettiOn:true,xpTask:10,xpPomo:15,xpBook:20,xpAch:25,pomoWork:25,pomoBreak:5,pomoLong:15,pomoCycleN:4,bookTime:25,bookBreak:true,waterGoal:8,sleepGoal:8};
saveAll();renderSettings();applyFontSize('medium');
showToast('🔄 Sozlamalar tiklandi','info');
}
// ===== STATISTIKA =====
function updateStats(){
const tt=state.tasks.filter(t=>t.date===todayKey);
const done=tt.filter(t=>t.completed).length;
const total=tt.length;
const rate=total>0?Math.round((done/total)*100):0;
document.getElementById('statTotal').textContent=total;
document.getElementById('statDone').textContent=done;
document.getElementById('statPending').textContent=total-done;
document.getElementById('statRate').textContent=rate+'%';
const circ=283,off=circ-(rate/100)*circ;
document.getElementById('ringFill').style.strokeDashoffset=off;
document.getElementById('ringText').textContent=rate+'%';
renderStatsPage();
}
function renderStatsPage(){
const totalTasks=state.tasks.length;
const doneTasks=state.tasks.filter(t=>t.completed).length;
const doneBooks=booksData.filter(b=>b.status==='done').length;
const pagesRead=booksData.reduce((a,b)=>a+b.currentPage,0);
const doneAB=abData.filter(a=>a.status==='done').length;
document.getElementById('statsGrid').innerHTML=
'<div class="stat-card"><div class="value" style="color:var(--neon-cyan)">'+totalTasks+'</div><div class="label">Jami vazifalar</div></div>'+
'<div class="stat-card"><div class="value" style="color:var(--green)">'+doneTasks+'</div><div class="label">Bajarilgan</div></div>'+
'<div class="stat-card"><div class="value" style="color:var(--accent3)">'+state.streak+'</div><div class="label">Kunlik streak</div></div>'+
'<div class="stat-card"><div class="value" style="color:var(--neon-magenta)">'+state.pomoCount+'</div><div class="label">Pomodoro</div></div>'+
'<div class="stat-card"><div class="value" style="color:var(--gold)">'+doneBooks+'/'+booksData.length+'</div><div class="label">Kitoblar</div></div>'+
'<div class="stat-card"><div class="value" style="color:var(--blue)">'+state.level+'</div><div class="label">Daraja</div></div>';
let dhtml='';
dhtml+='<div class="detailed-stat-row"><span class="ds-label">📖 O\'qilgan betlar</span><span class="ds-value">'+pagesRead+'</span></div>';
dhtml+='<div class="detailed-stat-row"><span class="ds-label">🎧 Audiokitoblar</span><span class="ds-value">'+doneAB+'/'+abData.length+'</span></div>';
dhtml+='<div class="detailed-stat-row"><span class="ds-label">⏱️ Jami pomodoro daqiqa</span><span class="ds-value">'+state.pomoTotalMin+'</span></div>';
dhtml+='<div class="detailed-stat-row"><span class="ds-label">💧 Bugungi suv</span><span class="ds-value">'+(waterData[todayKey]||0)+'/'+(settings.waterGoal||8)+'</span></div>';
dhtml+='<div class="detailed-stat-row"><span class="ds-label">🏆 Daraja</span><span class="ds-value">'+state.level+' — '+getLevelTitle(state.level)+'</span></div>';
dhtml+='<div class="detailed-stat-row"><span class="ds-label">⭐ Jami XP</span><span class="ds-value">'+((state.level-1)*100+state.xp)+'</span></div>';
document.getElementById('detailedStats').innerHTML=dhtml;
renderWeekComparison();
}
function renderWeekComparison(){
const el=document.getElementById('weekComparison');
const thisMonday=getMonday(new Date());
const lastMonday=new Date(thisMonday);lastMonday.setDate(lastMonday.getDate()-7);
let thisWeek=0,lastWeek=0;
for(let i=0;i<7;i++){
const d1=new Date(thisMonday);d1.setDate(d1.getDate()+i);
const d2=new Date(lastMonday);d2.setDate(d2.getDate()+i);
thisWeek+=state.tasks.filter(t=>t.date===d1.toISOString().split('T')[0]&&t.completed).length;
lastWeek+=state.tasks.filter(t=>t.date===d2.toISOString().split('T')[0]&&t.completed).length;
}
const maxVal=Math.max(thisWeek,lastWeek,1);
const diff=thisWeek-lastWeek;
let html='<div class="week-comp-row"><span class="week-comp-label">Bu hafta</span><div class="week-comp-bars"><div class="week-comp-bar this" style="width:'+(thisWeek/maxVal*100)+'%"></div></div><span style="font-size:.7em;color:var(--neon-cyan)">'+thisWeek+'</span></div>';
html+='<div class="week-comp-row"><span class="week-comp-label">O\'tgan hafta</span><div class="week-comp-bars"><div class="week-comp-bar last" style="width:'+(lastWeek/maxVal*100)+'%"></div></div><span style="font-size:.7em;color:var(--text3)">'+lastWeek+'</span></div>';
html+='<div class="week-comp-legend"><span><span class="dot this"></span> Bu hafta</span><span><span class="dot last"></span> O\'tgan hafta</span></div>';
html+='<div style="text-align:center;margin-top:8px;font-size:.8em;color:'+(diff>=0?'var(--green)':'var(--accent1)')+'">'+(diff>=0?'📈 +'+diff:'📉 '+diff)+' vazifa farqi</div>';
el.innerHTML=html;
}
// ===== YUTUQLAR =====
function journalTotalCount(){return journalData.length+Object.keys(jState.days).length}
const ACH=[
{id:'t1',icon:'🌱',title:'Birinchi qadam',desc:'1 vazifa',check:()=>state.tasks.length>=1},
{id:'t5',icon:'🔥',title:'Faol',desc:'5 vazifa',check:()=>state.tasks.length>=5},
{id:'t10',icon:'💪',title:'Ishchan',desc:'10 vazifa',check:()=>state.tasks.length>=10},
{id:'t25',icon:'⚡',title:'Professional',desc:'25 vazifa',check:()=>state.tasks.length>=25},
{id:'t50',icon:'👑',title:'Chempion',desc:'50 vazifa',check:()=>state.tasks.length>=50},
{id:'d1',icon:'⭐',title:'Birinchi g\'alaba',desc:'1 bajarildi',check:()=>state.tasks.some(t=>t.completed)},
{id:'d5',icon:'🌟',title:'Barqaror',desc:'5 bajarildi',check:()=>state.tasks.filter(t=>t.completed).length>=5},
{id:'d10',icon:'💎',title:'O\'nlik',desc:'10 bajarildi',check:()=>state.tasks.filter(t=>t.completed).length>=10},
{id:'d25',icon:'🏅',title:'Yigirmabesh',desc:'25 bajarildi',check:()=>state.tasks.filter(t=>t.completed).length>=25},
{id:'p1',icon:'🍅',title:'Pomodoro boshlovchi',desc:'1 seans',check:()=>state.pomoCount>=1},
{id:'p5',icon:'🍅',title:'Pomodoro faol',desc:'5 seans',check:()=>state.pomoCount>=5},
{id:'p10',icon:'🍅',title:'Pomodoro ustasi',desc:'10 seans',check:()=>state.pomoCount>=10},
{id:'p25',icon:'🍅',title:'Pomodoro eksperti',desc:'25 seans',check:()=>state.pomoCount>=25},
{id:'p50',icon:'🍅',title:'Pomodoro afsonasi',desc:'50 seans',check:()=>state.pomoCount>=50},
{id:'b1',icon:'📖',title:'Kitobxon',desc:'1 kitob boshlandi',check:()=>booksData.some(b=>b.status==='reading'||b.status==='done')},
{id:'bd1',icon:'📚',title:'Birinchi kitob tugadi',desc:'1 kitob tugagan',check:()=>booksData.some(b=>b.status==='done')},
{id:'bd3',icon:'📚',title:'Uch kitob',desc:'3 kitob tugagan',check:()=>booksData.filter(b=>b.status==='done').length>=3},
{id:'bp100',icon:'📄',title:'100 bet',desc:'100 bet o\'qildi',check:()=>booksData.reduce((a,b)=>a+b.currentPage,0)>=100},
{id:'bp500',icon:'📄',title:'500 bet',desc:'500 bet o\'qildi',check:()=>booksData.reduce((a,b)=>a+b.currentPage,0)>=500},
{id:'a1',icon:'🎧',title:'Audio tinglovchi',desc:'1 audiokitob',check:()=>abData.length>=1},
{id:'ad1',icon:'🎧',title:'Audiokitob tugadi',desc:'1 tugagan',check:()=>abData.some(a=>a.status==='done')},
{id:'s3',icon:'🔥',title:'3 kun streak',desc:'3 kun',check:()=>state.streak>=3},
{id:'s7',icon:'🔥',title:'7 kun streak',desc:'7 kun',check:()=>state.streak>=7},
{id:'s14',icon:'🔥',title:'14 kun streak',desc:'14 kun',check:()=>state.streak>=14},
{id:'s30',icon:'🔥',title:'30 kun streak',desc:'30 kun',check:()=>state.streak>=30},
{id:'w1',icon:'💧',title:'Suv boshlandi',desc:'Birinchi stakan',check:()=>(waterData[todayKey]||0)>=1},
{id:'w7',icon:'💧',title:'Suv ustasi',desc:'7 kun to\'liq suv',check:()=>{let c=0;for(let i=0;i<7;i++){const d=new Date();d.setDate(d.getDate()-i);if((waterData[d.toISOString().split('T')[0]]||0)>=(settings.waterGoal||8))c++}return c>=7}},
{id:'l5',icon:'🏆',title:'Tajribali',desc:'Daraja 5',check:()=>state.level>=5},
{id:'l10',icon:'👑',title:'Usta',desc:'Daraja 10',check:()=>state.level>=10},
{id:'l20',icon:'🌟',title:'Afsona',desc:'Daraja 20',check:()=>state.level>=20},
{id:'j1',icon:'📝',title:'Kundalik boshlandi',desc:'1 yozuv',check:()=>journalTotalCount()>=1},
{id:'j7',icon:'📝',title:'Haftalik kundalik',desc:'7 yozuv',check:()=>journalTotalCount()>=7},
{id:'f1',icon:'🎯',title:'Fokus belgilandi',desc:'Kunlik fokus',check:()=>!!state.dailyFocus},
{id:'all',icon:'🎉',title:'Hammasini sinadi',desc:'Barcha bo\'limlar',check:()=>state.pomoCount>0&&booksData.length>0&&(waterData[todayKey]||0)>0&&moodData.length>0}
];
function checkAch(){
let newAch=false;
ACH.forEach(a=>{
if(!state.achievements.includes(a.id)&&a.check()){
state.achievements.push(a.id);
showToast('🏆 Yutuq ochildi: '+a.title+'!','success');
addXP(settings.xpAch);
if(settings.confettiOn)launchConfetti();
vibrate([200,100,200,100,200]);
newAch=true;
}
});
if(newAch){saveAll();renderAch();checkRewards()}
}
function renderAch(){
document.getElementById('achCount').textContent=state.achievements.length;
document.getElementById('achTotal').textContent=ACH.length;
document.getElementById('achieveGrid').innerHTML=ACH.map(a=>{
const u=state.achievements.includes(a.id);
return '<div class="achieve-card '+(u?'unlocked':'locked')+'"><div class="achieve-icon">'+a.icon+'</div><div class="achieve-title">'+a.title+'</div><div class="achieve-desc">'+a.desc+'</div></div>';
}).join('');
}
// ===== SOVG'ALAR =====
const REWARDS=[
{id:'r1',icon:'🎨',name:'Yangi tema rangi',desc:'5 ta yutuq',need:5},
{id:'r2',icon:'✨',name:'Maxsus confetti',desc:'10 ta yutuq',need:10},
{id:'r3',icon:'🔥',name:'Olov animatsiyasi',desc:'15 ta yutuq',need:15},
{id:'r4',icon:'👑',name:'"Intizom Ustasi" unvoni',desc:'20 ta yutuq',need:20},
{id:'r5',icon:'🏅',name:'Maxsus logotip',desc:'Barcha yutuqlar',need:30}
];
function checkRewards(){
REWARDS.forEach(r=>{
if(!state.rewards.includes(r.id)&&state.achievements.length>=r.need){
state.rewards.push(r.id);
showToast('🎁 Sovg\'a: '+r.name+'!','success');
}
});
saveAll();renderRewards();
}
function renderRewards(){
const el=document.getElementById('rewardsList');
el.innerHTML=REWARDS.map(r=>{
const unlocked=state.rewards.includes(r.id);
const progress=Math.min(state.achievements.length,r.need);
return '<div class="reward-item'+(unlocked?'':' locked')+'"><div class="reward-icon">'+r.icon+'</div><div class="reward-info"><div class="reward-name">'+r.name+'</div><div class="reward-desc">'+r.desc+' ('+progress+'/'+r.need+')</div></div><span class="reward-status '+(unlocked?'unlocked':'locked')+'">'+(unlocked?'✅':'🔒')+'</span></div>';
}).join('');
}
// ===== CONFETTI =====
function launchConfetti(){
const c=document.createElement('div');c.className='confetti-container';document.body.appendChild(c);
const colors=['#ff4444','#ffd700','#00ffff','#ff00ff','#00ff00','#ff8800','#3b82f6','#a855f7'];
for(let i=0;i<45;i++){
const p=document.createElement('div');p.className='confetti-piece';
p.style.left=Math.random()*100+'%';
p.style.background=colors[Math.floor(Math.random()*colors.length)];
p.style.animationDelay=Math.random()*0.5+'s';
p.style.animationDuration=(2.5+Math.random()*1.5)+'s';
p.style.width=(5+Math.random()*8)+'px';
p.style.height=(5+Math.random()*8)+'px';
p.style.borderRadius=Math.random()>0.5?'50%':'2px';
c.appendChild(p);
}
setTimeout(()=>c.remove(),4000);
}
// ===== ESLATMALAR =====
function checkReminders(){
if(!settings.notifOn)return;
const now=new Date();
const remindMin=settings.reminderMin||10;
state.tasks.forEach(t=>{
if(t.date===todayKey&&!t.completed&&t.startTime){
const[tH,tM]=t.startTime.split(':').map(Number);
const taskMin=tH*60+tM;
const nowMin=now.getHours()*60+now.getMinutes();
const diff=taskMin-nowMin;
if(diff===remindMin){
showToast('🔔 "'+t.title+'" '+remindMin+' daqiqadan keyin boshlanadi!','warning');
vibrate([100,50,100]);
if('Notification'in window&&Notification.permission==='granted')new Notification('🔔 Eslatma',{body:t.title+' '+remindMin+' daqiqadan keyin!'});
}
}
});
const waterRem=document.getElementById('waterRemToggle');
if(waterRem&&waterRem.classList.contains('active')){
const w=waterData[todayKey]||0,goal=settings.waterGoal||8;
if(w<goal&&now.getMinutes()===0&&now.getHours()%2===0)showToast('💧 Suv ichishni unutmang! ('+w+'/'+goal+')','info');
}
}
// ===== NAVIGATSIYA =====
function navTo(view){
document.querySelectorAll('.view').forEach(x=>x.classList.remove('active'));
document.querySelectorAll('.nav-item').forEach(n=>n.classList.remove('active'));
document.getElementById('view-'+view).classList.add('active');
const viewOrder=['home','calendar','pomodoro','books','audio','trackers','journal','ai','templates','stats','settings'];
const navItems=document.querySelectorAll('.nav-item');
const idx=viewOrder.indexOf(view);
if(idx>=0&&navItems[idx])navItems[idx].classList.add('active');
if(view==='calendar'){renderWeek();renderMonth()}
if(view==='stats'){updateStats();renderAch();renderRewards()}
if(view==='books')renderBooks();
if(view==='audio')renderAudiobooks();
if(view==='trackers'){initWater();renderSleepHistory();renderSleepAvg();renderMoodHistory();renderMoodScale()}
if(view==='journal')jRender();
if(view==='ai')generateAI();
if(view==='templates')renderTemplates();
if(view==='settings')renderSettings();
if(view==='home'){renderTasks();renderCategories();renderOverdueAlert()}
if(view==='pomodoro'){updatePomoStats();renderPomoHistory()}
window.scrollTo(0,0);
}
// ===== LOADING =====
function hideLoading(){
setTimeout(()=>{
document.getElementById('appLoading').classList.add('hidden');
setTimeout(()=>{const el=document.getElementById('appLoading');if(el)el.remove()},500);
},1000);
}
// ===== RENDER ALL =====
function renderAll(){
try{
if(settings.fontSize!=='medium')applyFontSize(settings.fontSize);
renderCategories();renderTasks();updateStats();updateXPDisplay();
renderDailyFocus();renderDailyQuote();renderOverdueAlert();
renderWeek();renderMonth();
updatePomoStats();renderPomoHistory();
renderBooks();renderAudiobooks();
initWater();renderSleepHistory();renderSleepAvg();renderMoodHistory();renderMoodScale();
generateAI();renderTemplates();renderSettings();renderAch();renderRewards();
checkAch();
}catch(e){
console.error('renderAll xato:',e);
if(typeof showToast==='function')showToast('⚠️ Xato: '+e.message,'warning');
}finally{
hideLoading();
}
}
// ===== ORQAGA TUGMA BLOKI =====
history.pushState(null,null,location.href);
window.addEventListener('popstate',function(){
if(document.getElementById('readingMode').classList.contains('active')||document.getElementById('listeningMode').classList.contains('active')){
history.pushState(null,null,location.href);
showToast('⏳ Hali vaqt tugamadi! Davom eting!','warning');
vibrate([100,50,100]);
}
});
window.addEventListener('beforeunload',function(e){
if(document.getElementById('readingMode').classList.contains('active')||document.getElementById('listeningMode').classList.contains('active')){
e.preventDefault();e.returnValue='';
}
});

// ===== HIKMAT + KUNLIK IQTIBOS =====
const HIKMAT=[
{x:"Allohga eng sevimli amal — oz bo'lsa-da muntazam bajarilgani.",s:"Buxoriy & Muslim"},
{x:"Albatta, qiyinchilik bilan birga yengillik bor.",s:"Qur'on, Ash-Sharh 6"},
{x:"Alloh rahmatidan umid uzmang.",s:"Qur'on, Az-Zumar 53"},
{x:"Ikki so'z: Subhanallohi va bihamdihi, Subhanallohil-'Azim — Rahmonga sevimli.",s:"Buxoriy & Muslim"},
{x:"La havla va la quvvata illa billah — jannat xazinalaridan.",s:"Buxoriy & Muslim"},
{x:"Jilmayish — sadaqa.",s:"Tirmiziy"},
{x:"Yaxshi so'z — sadaqa.",s:"Buxoriy & Muslim"}
];
function renderDailyQuote(){
const day=Math.floor((new Date()-new Date(new Date().getFullYear(),0,0))/864e5);
const h=HIKMAT[day%HIKMAT.length];
document.getElementById('dailyQuote').innerHTML='💬 "'+h.x+'" <span style="font-size:.7em;color:var(--text3)">— '+h.s+'</span>';
}
// ===== KUNDALIK (yangi) =====
let jUnlocked=false;
function saveJ(){localStorage.setItem('mi3_jstate',JSON.stringify(jState))}
function dToday(){return new Date().toISOString().split('T')[0]}
function dYesterday(){return new Date(Date.now()-864e5).toISOString().split('T')[0]}
const JMOODS={good:'😄 Yaxshi',mid:'😐 Oddiy',sad:'😔 G\'amgin',angry:'😤 Asabiy'};
const JMOOD_MSG={good:'Ajoyib! Nima bo\'ldi?',mid:'Tushunarli. Bugun nima haqida yozmoqchisiz?',sad:'G\'am ham insonning bir qismi. Yozing, men tinglayapman.',angry:'Bu tabiiy. Kim yoki nima jahlingizni chiqardi?'};
const JEMO=['😄','😅','😌','🤔','😤','😢','🥳','','💪','🤲','📚','🎧'];
const JGRAT=['Sog\'liq','Oila','Ovqat','Suv','Ilm','Tinchlik','Do\'st','Uy','Vaqt','Imon'];
const JWORDS=['Barakali','Charchagan','Barakallilik','Tez','Sekin','Iliq','Sokin','Qiyin','Yengil','Go\'zal'];
const JENERGY=['🔋 Yuqori','🔋 O\'rta','🪫 Past'];
const JMEAN=['🧠 Tushunish','💪 Kuch','🤲 Tinchlik','❤️ Sevgi'];
const JCARDS=[
{q:'Agar shu vaziyat yana takrorlansa, nima qilaman?',c:['Xuddi shunday','Boshqacha','Sukut','Suhbat','Kechaman']},
{q:'Bugun kimga yaxshilik qildim?',c:['Oila','Do\'st','Nepoznat','O\'zim','Hech kimga']},
{q:'Bugun nimadan xursand bo\'ldim?',c:['Odamlardan','Natijadan','Tabiatdan','Ilimdan','Hech narsadan']}];
let jDraft={mood:'',emojis:[],grat:[],word:'',energy:'',meaning:'',text:'',reflections:[],whys:[],card:null,cardAns:''};
let jDelayTimer=null;
function jLockHTML(){
return '<div class="journal-lock"><div style="font-size:2.5em;margin-bottom:10px">🔐</div>'
+'<div style="color:var(--text2);margin-bottom:10px;font-size:.9em">Kundalik — PIN kiriting</div>'
+'<div id="jDelay" style="font-size:.8em;color:var(--accent3);margin-bottom:10px">⏳ 3...</div>'
+'<input type="password" maxlength="4" id="journalPinInput" placeholder="••••" oninput="checkJournalPin(this)" disabled>'
+'<div id="pinError" style="color:var(--accent1);font-size:.75em;margin-top:6px;display:none">❌ Noto\'g\'ri PIN</div></div>';
}
function startJDelay(){
let n=3;const el=document.getElementById('jDelay');const inp=document.getElementById('journalPinInput');
clearInterval(jDelayTimer);
jDelayTimer=setInterval(()=>{n--;if(el)el.textContent='⏳ '+n+'...';if(n<=0){clearInterval(jDelayTimer);if(el)el.style.display='none';if(inp)inp.disabled=false}},1000);
}
function checkJournalPin(inp){
if(inp.value.length===4){
if(inp.value===settings.pin){jUnlocked=true;jRender();showToast('🔓 Kundalik ochildi','success')}
else{inp.value='';const e=document.getElementById('pinError');if(e)e.style.display='block'}
}
}
function jRender(){
const v=document.getElementById('view-journal');
if(!jUnlocked){v.innerHTML=jLockHTML();startJDelay();return}
v.innerHTML='<div class="section-title">📝 Kundalik <span style="font-size:.7em;color:var(--text3)">🔥 '+jState.streak+' kun</span></div>'
+jMemoryBanner()+jSmartNasihatBanner()
+'<div class="filter-tabs"><div class="filter-tab active" onclick="jTab(\'bugun\',this)">📝 Bugun</div><div class="filter-tab" onclick="jTab(\'arxiv\',this)">📅 Arxiv</div><div class="filter-tab" onclick="jTab(\'nasihat\',this)">📜 Nasihat</div><div class="filter-tab" onclick="jTab(\'stat\',this)">📊 Stat</div></div>'
+'<div id="jBody"></div>';
jTab('bugun',v.querySelector('.filter-tab'));
}
function jMemoryBanner(){
const d=new Date();d.setDate(d.getDate()-7);const key=d.toISOString().split('T')[0];
const day=jState.days[key];if(!day)return'';
return '<div class="j-greet">🔮 <strong>1 hafta oldin:</strong> '+(day.word||JMOODS[day.mood]||'')+' — '+(day.opinion||'')+'</div>';
}
function jSmartNasihatBanner(){
if(!jDraft.mood)return'';
const map={angry:'😤',sad:'😔',good:'😊',mid:'🤔'};
const n=jState.nasihat.filter(x=>x.trigger===map[jDraft.mood]).pop();
if(!n)return'';
return '<div class="j-nasihat"><div class="jn-text">📜 O\'zingiz aytgan edingiz: "'+n.text+'"</div><div class="jn-meta">'+n.date+'</div></div>';
}
function jTab(tab,el){
const b=document.getElementById('jBody');if(!b)return;
document.querySelectorAll('#view-journal .filter-tab').forEach(t=>t.classList.remove('active'));if(el)el.classList.add('active');
if(tab==='bugun')b.innerHTML=jTodayHTML();
else if(tab==='arxiv')b.innerHTML=jRenderArxiv();
else if(tab==='nasihat')b.innerHTML=jRenderNasihat();
else b.innerHTML=jRenderStat();
}
function jTodayHTML(){
let html='<div class="j-greet">💬 Assalomu alaykum. Bugun qanday keldingiz?<div class="j-mood-row">';
for(let k in JMOODS){html+='<button class="j-mood-btn'+(jDraft.mood===k?' sel':'')+'" onclick="jSetMood(\''+k+'\')">'+JMOODS[k]+'</button>'}
html+='</div>';
if(jDraft.mood)html+='<div style="font-size:.8em;color:var(--text2)">'+JMOOD_MSG[jDraft.mood]+'</div>';
html+='</div>';
if(jDraft.mood){
html+='<div class="filter-tabs"><div class="filter-tab active" onclick="jMode(\'write\',this)">✍️ Yozish</div><div class="filter-tab" onclick="jMode(\'play\',this)">🎮 O\'yin</div><div class="filter-tab" onclick="jMode(\'think\',this)">🧠 Fikrlash</div><div class="filter-tab" onclick="jMode(\'quick\',this)">⚡ Tezkor</div></div>';
html+='<div id="jModeBody">'+jModeHTML('write')+'</div>';
html+='<div class="j-label">💎 Bu yozuv sizga nima berdi?</div><div class="j-chips">'+JMEAN.map(m=>'<button class="j-chip'+(jDraft.meaning===m?' sel':'')+'" onclick="jDraft.meaning=\''+m+'\';jModeRefresh(currentJMode())">'+m+'</button>').join('')+'</div>';
html+='<button class="btn btn-primary" onclick="jSave()" style="margin-top:12px">💾 Saqlash</button>';
}
return html;
}
function jSetMood(m){jDraft.mood=m;jTab('bugun',document.querySelector('#view-journal .filter-tab'))}
function jMode(m,el){
const parent=el.parentElement;parent.querySelectorAll('.filter-tab').forEach(t=>t.classList.remove('active'));el.classList.add('active');
document.getElementById('jModeBody').innerHTML=jModeHTML(m);
}
function jModeHTML(m){
if(m==='write'){
let h='<textarea class="journal-input" id="jText" placeholder="Yozing... men tinglayapman">'+(jDraft.text||'')+'</textarea>';
h+='<div class="j-label">Refleksiya (ixtiyoriy):</div><div class="j-chips">'+['Bu sizga nima his qildirdi?','Bu vaziyatda yana nima qilgan bo\'lardingiz?','Bu sizni qanday o\'zgartirdi?'].map(q=>'<button class="j-chip" onclick="jAddRefl(\''+q.replace(/'/g,"\\'")+'\')">'+q+'</button>').join('')+'</div>';
h+='<div id="jReflList">'+jDraft.reflections.map(r=>'<div class="j-opinion">❓ '+r.q+'<br>💬 '+r.a+'</div>').join('')+'</div>';
h+='<div class="j-label">🙏 3 shukr:</div><div class="j-chips">'+JGRAT.map(g=>'<button class="j-chip'+(jDraft.grat.includes(g)?' sel':'')+'" onclick="jToggleGrat(\''+g+'\')">'+g+'</button>').join('')+'</div>';
h+='<div class="j-label">🤲 Duo (ixtiyoriy):</div><div class="j-chips"><button class="j-chip" onclick="jShowDua()">Ko\'rsatish</button></div><div id="jDuaBox"></div>';
return h;
}
if(m==='play'){
let h='<div class="j-label">😊 Emoji-hikoya (ketma-ket):</div><div class="j-chips">'+JEMO.map(e=>'<button class="j-chip" onclick="jAddEmo(\''+e+'\')">'+e+'</button>').join('')+'</div><div style="font-size:1.2em;margin:6px 0">'+(jDraft.emojis.join(' → ')||'—')+'</div>';
h+='<div class="j-label">🙏 3 shukr:</div><div class="j-chips">'+JGRAT.map(g=>'<button class="j-chip'+(jDraft.grat.includes(g)?' sel':'')+'" onclick="jToggleGrat(\''+g+'\')">'+g+'</button>').join('')+'</div>';
h+='<div class="j-label">🔤 Bir so\'z:</div><div class="j-chips">'+JWORDS.map(w=>'<button class="j-chip'+(jDraft.word===w?' sel':'')+'" onclick="jDraft.word=\''+w+'\';jModeRefresh(\'play\')">'+w+'</button>').join('')+'</div>';
h+='<div class="j-label">⚡ Energiya:</div><div class="j-chips">'+JENERGY.map(e=>'<button class="j-chip'+(jDraft.energy===e?' sel':'')+'" onclick="jDraft.energy=\''+e+'\';jModeRefresh(\'play\')">'+e+'</button>').join('')+'</div>';
return h;
}
if(m==='think'){
let h='<div class="j-label">❓ 5 "Nega" (chuqurlashish):</div>';
for(let i=0;i<5;i++){h+='<input class="reflection-input" style="margin-bottom:5px" placeholder="'+(i===0?'Nega shu kayfiyat?':'Nega? ('+(i+1)+')')+'" value="'+(jDraft.whys[i]||'')+'" oninput="jDraft.whys['+i+']=this.value">'}
const card=jDraft.card||JCARDS[0];
h+='<div class="j-label">💭 Fikr kartasi:</div><div style="font-size:.85em;margin:6px 0">'+card.q+'</div><div class="j-chips">'+card.c.map(c=>'<button class="j-chip'+(jDraft.cardAns===c?' sel':'')+'" onclick="jDraft.cardAns=\''+c+'\';jModeRefresh(\'think\')">'+c+'</button>').join('')+'</div>';
return h;
}
let h='<div class="j-mood-row">'+JEMO.slice(0,6).map(e=>'<button class="j-chip'+(jDraft.emojis[0]===e?' sel':'')+'" onclick="jDraft.emojis=[\''+e+'\'];jModeRefresh(\'quick\')">'+e+'</button>').join('')+'</div>';
h+='<div class="j-chips">'+JWORDS.map(w=>'<button class="j-chip'+(jDraft.word===w?' sel':'')+'" onclick="jDraft.word=\''+w+'\';jModeRefresh(\'quick\')">'+w+'</button>').join('')+'</div>';
h+='<div class="j-chips">'+JENERGY.map(e=>'<button class="j-chip'+(jDraft.energy===e?' sel':'')+'" onclick="jDraft.energy=\''+e+'\';jModeRefresh(\'quick\')">'+e+'</button>').join('')+'</div>';
return h;
}
function jModeRefresh(m){document.getElementById('jModeBody').innerHTML=jModeHTML(m)}
function currentJMode(){const a=document.querySelector('#jModeBody');return a&&a.dataset.mode||'write'}
function jAddEmo(e){if(jDraft.emojis.length<5)jDraft.emojis.push(e);jModeRefresh('play')}
function jToggleGrat(g){const i=jDraft.grat.indexOf(g);if(i>=0)jDraft.grat.splice(i,1);else if(jDraft.grat.length<3)jDraft.grat.push(g);jModeRefresh(currentJMode())}
function jAddRefl(q){const a=prompt(q);if(a&&a.trim()){jDraft.reflections.push({q:q,a:a.trim()});document.getElementById('jReflList').innerHTML=jDraft.reflections.map(r=>'<div class="j-opinion">❓ '+r.q+'<br>💬 '+r.a+'</div>').join('')}}
function jShowDua(){document.getElementById('jDuaBox').innerHTML='<div class="j-opinion">🤲 "Alhamdulillah" — shukr.<br>🤲 "Astaghfirulloh" — istig\'for.<br><span style="font-size:.7em;color:var(--text3)">Manba: Buxoriy/Muslim</span></div>'}
function jOpinion(day){
let o='';
if(day.mood==='angry')o='Bugun og\'ir edi, lekin siz to\'xtamadingiz — yozdingiz. Bu kuch belgisi.';
else if(day.mood==='sad')o='G\'amgin kunlarda yozish — o\'zini tinglash. Siz buni qila oldingiz.';
else if(day.mood==='good')o='Bugun siz nur taratdingiz. Buni eslab qoling.';
else o='Oddiy kunlar ham qimmat. Siz ularni payqadingiz.';
if(day.grat&&day.grat.length)o+=' Va shukr qila oldingiz.';
return o;
}
function jSave(){
const textEl=document.getElementById('jText');if(textEl)jDraft.text=textEl.value;
const day={date:todayKey,mood:jDraft.mood,emojis:jDraft.emojis,grat:jDraft.grat,word:jDraft.word,energy:jDraft.energy,meaning:jDraft.meaning,text:jDraft.text,reflections:jDraft.reflections,whys:jDraft.whys.filter(w=>w),cardAns:jDraft.cardAns,opinion:''};
day.opinion=jOpinion(day);
jState.days[todayKey]=day;
if(jState.lastWrite!==todayKey){if(jState.lastWrite===dYesterday())jState.streak++;else jState.streak=1;jState.lastWrite=todayKey}
saveJ();saveAll();
showToast('📝 Saqlandi! 💬 Hamroh fikri yozildi','success');addXP(5);
jDraft={mood:jDraft.mood,emojis:[],grat:[],word:'',energy:'',meaning:'',text:'',reflections:[],whys:[],card:null,cardAns:''};
jTab('bugun',document.querySelector('#view-journal .filter-tab.active'));
checkAch();
}
let jArY=new Date().getFullYear(),jArM=new Date().getMonth();
function jRenderArxiv(){
const names=['Yanvar','Fevral','Mart','Aprel','May','Iyun','Iyul','Avgust','Sentabr','Oktabr','Noyabr','Dekabr'];
let html='<div class="cal-header"><button class="cal-nav-btn" onclick="jArNav(-1)">◀</button><span class="cal-title">'+names[jArM]+' '+jArY+'</span><button class="cal-nav-btn" onclick="jArNav(1)">▶</button></div>';
const first=new Date(jArY,jArM,1).getDay();const dim=new Date(jArY,jArM+1,0).getDate();const start=first===0?6:first-1;
html+='<div class="month-grid">';
for(let i=0;i<start;i++)html+='<div></div>';
for(let d=1;d<=dim;d++){
const ds=jArY+'-'+String(jArM+1).padStart(2,'0')+'-'+String(d).padStart(2,'0');
const has=jState.days[ds];
html+='<div class="month-day'+(has?' has-tasks':'')+'" onclick="jShowDay(\''+ds+'\')">'+d+'</div>';
}
html+='</div>';
html+='<div class="j-label">🔍 Hikmat qidiruv:</div><div style="display:flex;gap:6px"><input class="form-input" id="jSearch" placeholder="qachon g\'azablandim / nima yordam berdi"><button class="btn btn-sm btn-ghost" onclick="jHikmat()">Qidirish</button></div><div id="jSearchRes"></div>';
return html;
}
function jArNav(d){jArM+=d;if(jArM>11){jArM=0;jArY++}if(jArM<0){jArM=11;jArY--}jTab('arxiv',document.querySelectorAll('#view-journal .filter-tab')[1])}
function jShowDay(date){
const day=jState.days[date];
const w=waterData[date]||0;const sl=sleepData.find(s=>s.date===date);
const tt=state.tasks.filter(t=>t.date===date);const td=tt.filter(t=>t.completed).length;
let html='<h3>📅 '+date+'</h3>';
if(!day){html+='<div style="color:var(--text3);font-size:.85em;margin:8px 0">Bu kun kundalik yozilmagan.</div>'}
else{
html+='<div class="j-daycard">';
if(day.mood)html+='<div class="jd-line">'+JMOODS[day.mood]+' '+(day.energy||'')+'</div>';
if(day.word)html+='<div class="jd-line">🔤 '+day.word+'</div>';
if(day.emojis&&day.emojis.length)html+='<div class="jd-line">🎬 '+day.emojis.join(' → ')+'</div>';
if(day.grat&&day.grat.length)html+='<div class="jd-line">🙏 '+day.grat.join(', ')+'</div>';
if(day.text)html+='<div class="jd-line">✍️ '+day.text+'</div>';
if(day.reflections)day.reflections.forEach(r=>{html+='<div class="j-opinion">❓ '+r.q+'<br>💬 '+r.a+'</div>'});
if(day.whys&&day.whys.length)html+='<div class="jd-line">🧠 '+day.whys.join(' → ')+'</div>';
if(day.cardAns)html+='<div class="jd-line">💭 '+day.cardAns+'</div>';
if(day.meaning)html+='<div class="jd-line">💎 '+day.meaning+'</div>';
if(day.opinion)html+='<div class="j-opinion">💬 '+day.opinion+'</div>';
html+='</div>';
}
html+='<div class="jd-line" style="font-size:.75em;color:var(--text2)">💧 '+w+'/8 | 😴 '+(sl?sl.duration:'—')+'s | ✅ '+td+'/'+tt.length+'</div>';
html+='<button class="btn btn-ghost" style="width:100%;margin-top:10px;justify-content:center" onclick="closeModal(\'taskDetailModal\')">Yopish</button>';
showModal('taskDetailModal',html);
}
function jHikmat(){
const q=(document.getElementById('jSearch').value||'').toLowerCase();
const res=Object.values(jState.days).filter(d=>{
const blob=((d.text||'')+(d.word||'')+(d.grat||[]).join(' ')+(d.cardAns||'')+(JMOODS[d.mood]||'')).toLowerCase();
return blob.includes(q);
});
const el=document.getElementById('jSearchRes');
if(!res.length){el.innerHTML='<div style="color:var(--text3);font-size:.8em;margin-top:8px">Topilmadi</div>';return}
el.innerHTML=res.map(d=>'<div class="j-daycard"><div class="jd-date">'+d.date+'</div><div class="jd-line">'+(JMOODS[d.mood]||'')+' '+(d.word||'')+'</div>'+(d.cardAns?'<div class="jd-line">💭 '+d.cardAns+'</div>':'')+(d.opinion?'<div class="j-opinion">💬 '+d.opinion+'</div>':'')+'</div>').join('');
}
let jNasTrig='';
function jRenderNasihat(){
const todayCount=jState.nasihat.filter(n=>n.date===todayKey).length;
let html='<div class="j-label">📜 Kelajakdagi o\'zimga nasihat <span class="j-count">(bugun: '+todayCount+'/5)</span></div>';
html+='<div class="j-chips">'+['😤 Jahl','😔 Xafa','😊 Xursand','🤔 Xato','💪 Yengdim'].map(t=>'<button class="j-chip" onclick="jNasTrigSel(this,\''+t.split(' ')[0]+'\')">'+t+'</button>').join('')+'</div>';
html+='<input class="reflection-input" id="jNasState" placeholder="O\'sha payt qanday holatda edingiz?">';
html+='<textarea class="mood-note" id="jNasText" placeholder="Kelajakda nimani takrorlamaysiz / nima qilasiz?"></textarea>';
html+='<button class="btn btn-primary" onclick="jAddNasihat()" style="margin-top:8px">💾 Nasihat qoldirish</button>';
html+='<div class="j-label" style="margin-top:14px">📖 Nasihatlar kitobi:</div>';
html+=jState.nasihat.slice().reverse().map(n=>'<div class="j-nasihat"><div class="jn-text">'+n.trigger+' "'+n.text+'"</div><div class="jn-meta">'+n.date+(n.state?' • '+n.state:'')+'</div></div>').join('')||'<div style="color:var(--text3);font-size:.8em">Hali nasihat yo\'q</div>';
return html;
}
function jNasTrigSel(el,t){jNasTrig=t;el.parentElement.querySelectorAll('.j-chip').forEach(c=>c.classList.remove('sel'));el.classList.add('sel')}
function jAddNasihat(){
if(jState.nasihat.filter(n=>n.date===todayKey).length>=5){showToast('⚠️ Bugun 5 tadan oshdi!','warning');return}
if(!jNasTrig){showToast('⚠️ Holatni tanlang!','warning');return}
const text=document.getElementById('jNasText').value.trim();
if(!text){showToast('⚠️ Nasihatni yozing!','warning');return}
jState.nasihat.push({id:Date.now(),date:todayKey,trigger:jNasTrig,state:document.getElementById('jNasState').value.trim(),text:text});
saveJ();showToast('📜 Nasihat saqlandi!','success');
jTab('nasihat',document.querySelectorAll('#view-journal .filter-tab')[2]);
}
function jRenderStat(){
const days=Object.values(jState.days);
if(!days.length)return '<div style="color:var(--text3);font-size:.8em;text-align:center;padding:20px">Hali yozuv yo\'q</div>';
let moodC={},meanC={},gratC={};
days.forEach(d=>{if(d.mood)moodC[d.mood]=(moodC[d.mood]||0)+1;if(d.meaning)meanC[d.meaning]=(meanC[d.meaning]||0)+1;(d.grat||[]).forEach(g=>gratC[g]=(gratC[g]||0)+1)});
let html='<div class="j-label">📊 Hislar taqsimoti:</div>';
for(let k in moodC){html+='<div class="report-bar-row"><span class="report-bar-label">'+JMOODS[k].split(' ')[0]+'</span><div class="report-bar"><div class="report-bar-fill done" style="width:'+Math.min(100,moodC[k]/days.length*100)+'%">'+moodC[k]+'</div></div></div>'}
html+='<div class="j-label">💎 Ma\'no qidiruvi:</div>';
for(let k in meanC){html+='<div class="jd-line">'+k+': '+meanC[k]+' marta</div>'}
const topGrat=Object.entries(gratC).sort((a,b)=>b[1]-a[1])[0];
if(topGrat)html+='<div class="j-opinion">🙏 Eng ko\'p shukr: '+topGrat[0]+' ('+topGrat[1]+' marta)</div>';
html+='<div class="jd-line" style="margin-top:8px">🔥 Streak: '+jState.streak+' kun | 📝 Jami yozuv: '+days.length+'</div>';
return html;
}
// ===== MAXFIY PIN STATE =====
let dState={unlocked:false,pin:'1234'};
(function loadD(){const s=localStorage.getItem('mi3_diamond');if(s)dState={...dState,...JSON.parse(s)};})();
function saveD(){localStorage.setItem('mi3_diamond',JSON.stringify(dState))}
// ===== KIRISH (logo→asosiy, ⚙️→sozlamalar) =====
let diamondTarget='main';
function openDiamondPin(target){
if(!target)return;
diamondTarget=target;
document.getElementById('diamondPinInput').value='';
document.getElementById('diamondPinError').style.display='none';
document.getElementById('diamondPinModal').classList.add('active');
}
function checkDiamondPin(inp){
if(inp.value.length===4){
if(inp.value===dState.pin){
dState.unlocked=true;saveD();
closeModal('diamondPinModal');
if(diamondTarget==='settings')openHiddenSettings();else openHiddenMain();
}else{inp.value='';document.getElementById('diamondPinError').style.display='block'}
}
}
function lp3(el,cb,ms){if(!el)return;let t=null;
const s=()=>{t=setTimeout(cb,ms)};const en=()=>clearTimeout(t);
el.addEventListener('touchstart',s,{passive:true});el.addEventListener('touchend',en);el.addEventListener('touchcancel',en);
el.addEventListener('mousedown',s);el.addEventListener('mouseup',en);el.addEventListener('mouseleave',en);
el.addEventListener('contextmenu',e=>e.preventDefault());}
lp3(document.querySelector('.logo-svg'),()=>openDiamondPin('main'),3000);
lp3(document.querySelectorAll('.header-btn')[1],()=>openDiamondPin('settings'),3000);
// ===== YASHIRIN ASOSIY =====
let hState={enabled:{},day:{date:'',counts:{}},custom:[],set:null};
(function loadH(){const s=localStorage.getItem('mi3_hidden');if(s)hState={...hState,...JSON.parse(s)};})();
function saveH(){localStorage.setItem('mi3_hidden',JSON.stringify(hState))}
function hToday(){if(hState.day.date!==todayKey)hState.day={date:todayKey,counts:{}};return hState.day.counts}
function hSetGet(){if(!hState.set)hState.set={vib:true,sound:false,target:33,live:true,chips:{}};return hState.set}
function hEnabled(id){return hState.enabled[id]!==false}
const HCARDS=[
{id:'tong',n:'🌅 Tong boshlanishi',r:"Uyg'onish duosi",l:"Alhamdu lillaahil-lazii ahyaanaa ba'da maa amaatanaa wa ilayhin-nushoor",m:"Alloh bizni uyg'otgani uchun hamd",c:1,s:'Buxoriy',w:[4,9]},
{id:'taomOldin',n:'🍽️ Taom — oldin',r:'Ovqat boshlash',l:"Bismillah (unutsa: Bismillaahi awwalahu wa aakhirahu)",m:"Alloh nomi bilan boshlash",c:1,s:'Buxoriy/Abu Dovud',w:[7,21]},
{id:'taomKeyin',n:'🍽️ Taom — keyin',r:'Taom shukri',l:"Alhamdu lillaahil-lazii at'amanaa wa saqaanaa wa ja'alanaa muslimeen",m:"Ovqat uchun Allohga hamd",c:1,s:'Abu Dovud/Tirmiziy',w:[7,21]},
{id:'chiqish',n:'🚪 Chiqish',r:'Uydan chiqish',l:"Bismillaahi tawakkaltu 'alal-laah, wa laa hawla wa laa quwwata illaa billaah",m:"Allohga tavakkul qilib chiqish",c:1,s:'Abu Dovud/Tirmiziy',w:[7,18]},
{id:'kirish',n:'🏠 Kirish',r:'Uyga kirish',l:"Bismillaahi walajnaa, wa bismillaahi kharajnaa, wa 'alal-laahi rabbinaa tawakkalnaa",m:"Alloh nomi bilan kirish",c:1,s:'Abu Dovud',w:[12,23]},
{id:'xursand',n:'😊 Xursand',r:'Minnatdorlik (odamdan)',l:"Jazaakal-laahu khayran",m:"Alloh senga yaxshilik bersin",c:1,s:'Tirmiziy',w:[0,24]},
{id:'jahl',n:'😤 Jahl',r:"G'azabdan himoya",l:"A'oozu billaahi minash-shaytaanir-rajeem",m:"Shaytondan Allohga panoh",c:1,s:'Buxoriy/Muslim',w:[0,24]},
{id:'qiyin',n:'⚠️ Qiyinlik',r:'Siqilish duosi',l:"Laa ilaaha illal-laahu rabbul-'arshil-'azim",m:"Ulug' Arsh Robbisiga tavakkul",c:1,s:'Buxoriy/Muslim',w:[0,24]},
{id:'osish',n:"✅ O'sish",r:'Muvaffaqiyat shukri',l:"Al-hamdu lillaahil-lazii bi-ni'matihi tatimmus-saalihaat",m:"Yaxshi amallar Alloh ne'mati bilan",c:1,s:'Ibn Moja',w:[0,24]},
{id:'uyqu',n:'🌙 Uyqu',r:'Yotish duosi',l:"Bismika Allaahumma amootu wa ahya",m:"Alloh nomi bilan uxlab uyg'onish",c:1,s:'Buxoriy',w:[21,24]},
{id:'bosh',n:"💬 Bo'sh kun",r:'Kundalik kalimalar',l:"SubhanAlloh / Alhamdulillah / Allohu Akbar / La ilaha illalloh / Astag'firulloh",m:"Kundalik zikr",c:33,s:'Buxoriy/Muslim',w:[0,24]}
];
const HQUICK=[
{id:'salavot',n:'Salavot',l:"Allohumma solli 'alaa Muhammad",c:10,s:'Sunnat'},
{id:'hamd',n:'Hamd',l:'Alhamdulillah',c:33,s:'Buxoriy'},
{id:'subhan',n:'Subhan',l:'SubhanAlloh',c:33,s:'Buxoriy'},
{id:'istigfor',n:"Istig'for",l:'Astaghfirulloh',c:100,s:'Sunnat'},
{id:'lahavla',n:'La havla',l:'La havla va la quvvata illa billah',c:10,s:'Buxoriy'}
];
function openHiddenMain(){
buildHiddenMain();
document.getElementById('hiddenMainOverlay').classList.add('active');
hmTab('oqim',document.querySelector('#hiddenMainOverlay .hm-tab'));
}
function closeHiddenMain(){document.getElementById('hiddenMainOverlay').classList.remove('active')}
function buildHiddenMain(){
if(document.getElementById('hiddenMainOverlay'))return;
const o=document.createElement('div');o.className='hidden-overlay';o.id='hiddenMainOverlay';
o.innerHTML='<div class="diamond-header"><span class="diamond-title">🌿 Kunlik oqim odatlari</span><button class="close-form" onclick="closeHiddenMain()">✕</button></div>'
+'<div class="diamond-tabs"><button class="hm-tab diamond-tab active" onclick="hmTab(\'oqim\',this)">🌿 Oqim</button><button class="hm-tab diamond-tab" onclick="hmTab(\'odat\',this)">📊 Odat</button><button class="hm-tab diamond-tab" onclick="hmTab(\'qidiruv\',this)">🔍 Qidiruv</button></div>'
+'<div id="hmBody"></div>';
document.body.appendChild(o);
}
function hmTab(t,el){
document.querySelectorAll('#hiddenMainOverlay .hm-tab').forEach(b=>b.classList.remove('active'));if(el)el.classList.add('active');
const b=document.getElementById('hmBody');
if(t==='oqim')b.innerHTML=hmOqim();
else if(t==='odat')b.innerHTML=hmOdat();
else b.innerHTML=hmQidiruv();
}
function hmLive(){
const h=new Date().getHours();
const all=HCARDS.concat(hState.custom);
const card=all.find(c=>hEnabled(c.id||c.cid)&&c.w&&h>=c.w[0]&&h<c.w[1]);
if(!card)return'';
return '<div class="j-greet">⏰ <strong>Hozirgi holat:</strong> '+(card.n||card.name)+'<br><button class="btn btn-sm btn-success" style="margin-top:8px" onclick="hmOpen(\''+(card.id||card.cid)+'\')">Ochish</button></div>';
}
function hmOqim(){
const S=hSetGet();
let html=S.live?hmLive():'';
const chips=HQUICK.filter(q=>S.chips[q.id]!==false);
html+='<div class="j-label">⚡ Tezkor:</div><div class="j-chips">'+chips.map(q=>'<button class="j-chip" onclick="hmQuick(\''+q.id+'\')">'+q.n+' <span class="j-count">'+(hToday()['q_'+q.id]||0)+'</span></button>').join('')+'</div>';
html+='<div class="j-label">🗂️ Holatlar:</div>';
HCARDS.forEach(c=>{if(hEnabled(c.id)){
const cnt=hToday()[c.id]||0;
html+='<div class="deed-card'+(cnt>=c.c?' done':'')+'"><div class="deed-head"><span class="deed-name">'+c.n+'</span><span class="deed-streak">'+cnt+'/'+c.c+'</span></div><div class="deed-src">📖 '+c.s+'</div><button class="deed-enable on" style="margin-top:6px" onclick="hmOpen(\''+c.id+'\')">Ochish</button></div>';
}});
hState.custom.forEach(c=>{if(hEnabled(c.cid)){
html+='<div class="deed-card"><div class="deed-head"><span class="deed-name">✨ '+c.name+'</span></div><div class="deed-src">📖 '+c.s+' | ➕ '+c.added+'</div><button class="deed-enable on" style="margin-top:6px" onclick="hmOpen(\''+c.cid+'\')">Ochish</button></div>';
}});
return html;
}
function hmFind(id){return HCARDS.find(c=>c.id===id)||hState.custom.find(c=>c.cid===id)}
function hmOpen(id){
const c=hmFind(id);if(!c)return;
let html='<h3>'+c.n+'</h3><div style="font-size:.75em;color:var(--text3);margin:4px 0">'+c.r+'</div>';
html+='<div class="deed-arabic" style="font-size:1em;margin:10px 0">'+c.l+'</div>';
html+='<div class="deed-meaning">💚 '+c.m+'</div>';
html+='<div class="deed-src">📖 Manba: '+c.s+' | 🔁 '+(c.c||1)+' marta</div>';
html+='<button class="btn btn-success" style="width:100%;margin-top:10px;justify-content:center" onclick="hmDone(\''+id+'\')">✅ Aytdim</button>';
html+='<button class="btn btn-ghost" style="width:100%;margin-top:8px;justify-content:center" onclick="hmToCounter(\''+id+'\')">📊 Sanab aytish</button>';
html+='<button class="btn btn-ghost" style="width:100%;margin-top:8px;justify-content:center" onclick="closeModal(\'taskDetailModal\')">Yopish</button>';
showModal('taskDetailModal',html);
}
function hmDone(id){
const c=hmFind(id);if(!c)return;
hToday()[id]=(hToday()[id]||0)+1;saveH();
closeModal('taskDetailModal');
showToast('✅ '+c.n+' — bajarildi','success');
addXP(3);hmTab('oqim',document.querySelector('#hiddenMainOverlay .hm-tab'));
}
function hmQuick(id){hToday()['q_'+id]=(hToday()['q_'+id]||0)+1;saveH();hmTab('oqim',document.querySelector('#hiddenMainOverlay .hm-tab'))}
let hmTarget=33,hmCount=0,hmSel=null;
function hmToCounter(id){hmSel=hmFind(id);hmCount=0;hmTarget=hmSel.c||33;closeModal('taskDetailModal');hmTab('odat',document.querySelectorAll('#hiddenMainOverlay .hm-tab')[1])}
function hmSelCounter(id){hmSel=hmFind(id);hmCount=0;hmTarget=hmSel.c||33;hmTab('odat',document.querySelectorAll('#hiddenMainOverlay .hm-tab')[1])}
function hmOdat(){
const S=hSetGet();
let html='<div class="j-label">📊 Odat hisoblagich</div>';
html+='<div class="j-chips">'+HQUICK.filter(q=>S.chips[q.id]!==false).map(q=>'<button class="j-chip'+(hmSel&&hmSel.id===q.id?' sel':'')+'" onclick="hmSelCounter(\''+q.id+'\')">'+q.n+'</button>').join('')+HCARDS.filter(c=>c.c>1&&hEnabled(c.id)).map(c=>'<button class="j-chip'+(hmSel&&hmSel.id===c.id?' sel':'')+'" onclick="hmSelCounter(\''+c.id+'\')">'+c.n+'</button>').join('')+'</div>';
html+='<div style="text-align:center;margin:15px 0"><div style="font-size:2.5em;font-weight:800;color:var(--neon-cyan)">'+hmCount+' / '+hmTarget+'</div>';
html+='<div class="deed-bar" style="margin:10px 0"><div class="deed-bar-fill" style="width:'+Math.min(100,hmCount/hmTarget*100)+'%"></div></div>';
html+='<button class="tap-btn" onclick="hmTap()">+1</button></div>';
return html;
}
function hmTap(){
const S=hSetGet();
hmCount++;
if(hmCount%33===0){if(S.vib&&navigator.vibrate)navigator.vibrate(100);if(S.sound){try{new Audio('data:audio/wav;base64,UklGRiQAAABXQVZFZm10IBAAAAABAAEAQB8AAIA+AAACABAAZGF0YQAAAAA=').play()}catch(e){}}}
if(hmCount>=(hmSel?hmSel.c||S.target:S.target)){
if(hmSel){hToday()[hmSel.id]=(hToday()[hmSel.id]||0)+1}
showToast('📊 Maqsadga yetdi! +5','success');addXP(5);hmCount=0;
}
saveH();hmTab('odat',document.querySelectorAll('#hiddenMainOverlay .hm-tab')[1]);
}
let hmOnlineResults=[];
function hmQidiruv(){
let html='<div class="j-label">🔍 Offline kutubxona qidiruvi:</div>';
html+='<div style="display:flex;gap:6px"><input class="form-input" id="hmOffQ" placeholder="kalit so\'z (salavot, jahl, shukr...)"><button class="btn btn-sm btn-ghost" onclick="hmOffline()">Qidirish</button></div>';
html+='<div id="hmOffRes"></div>';
html+='<div class="j-label" style="margin-top:14px">🌐 Qur\'on onlayn qidiruvi (arabcha):</div>';
html+='<div style="display:flex;gap:6px"><input class="form-input" id="hmSearchQ" placeholder="arabcha so\'z"><button class="btn btn-sm btn-ghost" onclick="hmOnlineSearch()">🔍 Qidirish</button></div>';
html+='<div style="font-size:.65em;color:var(--text3);margin-top:4px">Faqat tugma bosilganda ishlaydi. O\'zbekcha uchun qo\'lda qo\'shing.</div>';
html+='<div id="hmSearchRes"></div>';
html+='<div class="j-label" style="margin-top:14px">✍️ Qo\'lda qo\'shish (manba majburiy):</div>';
html+='<input class="form-input" id="hmName" placeholder="Nomi" style="margin-bottom:6px">';
html+='<input class="form-input" id="hmLatin" placeholder="Matn (lotin/arab)" style="margin-bottom:6px">';
html+='<input class="form-input" id="hmMean" placeholder="Ma\'nosi" style="margin-bottom:6px">';
html+='<input class="form-input" id="hmSrc" placeholder="📖 Manba (majburiy)" style="margin-bottom:6px">';
html+='<select class="form-input" id="hmSit" style="margin-bottom:6px"><option value="any">Har qanday vaqt</option><option value="tong">Tong</option><option value="taom">Taom</option><option value="chiqish">Chiqish</option><option value="kirish">Kirish</option><option value="uyqu">Uyqu</option></select>';
html+='<button class="btn btn-primary" onclick="hmAddManual()">➕ Qo\'shish</button>';
return html;
}
function hmOffline(){
const q=(document.getElementById('hmOffQ').value||'').toLowerCase();
const all=HCARDS.concat(HQUICK).concat(hState.custom.map(c=>({id:c.cid,n:c.name,r:'',l:c.l,m:c.m||'',s:c.s})));
const res=all.filter(c=>((c.n||'')+(c.r||'')+(c.l||'')+(c.m||'')+(c.s||'')).toLowerCase().includes(q));
const el=document.getElementById('hmOffRes');
if(!res.length){el.innerHTML='<div style="color:var(--text3);font-size:.8em;margin-top:8px">Topilmadi</div>';return}
el.innerHTML=res.map(c=>'<div class="deed-card"><div class="deed-head"><span class="deed-name">'+(c.n||c.name)+'</span></div><div class="deed-src">📖 '+c.s+'</div><button class="deed-enable on" style="margin-top:6px" onclick="hmOpen(\''+(c.id||c.cid)+'\')">Ochish</button></div>').join('');
}
function hmOnlineSearch(){
const q=document.getElementById('hmSearchQ').value.trim();
if(!q){showToast('⚠️ So\'z kiriting','warning');return}
const res=document.getElementById('hmSearchRes');
res.innerHTML='<div style="color:var(--text2);font-size:.8em;margin-top:8px">⏳ Qidirilmoqda...</div>';
fetch('https://api.alquran.cloud/v1/search/'+encodeURIComponent(q)+'/all/quran-uthmani')
.then(r=>r.json())
.then(d=>{
hmOnlineResults=[];
if(d&&d.data&&d.data.matches&&d.data.matches.length){
hmOnlineResults=d.data.matches.slice(0,5);
res.innerHTML=hmOnlineResults.map((m,i)=>{
const ref=m.surah.number+':'+m.numberInSurah;
return '<div class="deed-card"><div class="deed-arabic">'+m.text+'</div><div class="deed-src">📖 Qur\'on '+ref+' ('+m.surah.englishName+')</div><button class="deed-enable on" style="margin-top:6px" onclick="hmAddQuran('+i+')">➕ Qo\'shish</button></div>';
}).join('');
}else res.innerHTML='<div style="color:var(--text3);font-size:.8em;margin-top:8px">Topilmadi. Qo\'lda qo\'shing.</div>';
})
.catch(()=>{res.innerHTML='<div style="color:var(--accent1);font-size:.8em;margin-top:8px">Internet yo\'q yoki xato.</div>'});
}
function hmAddQuran(i){
const m=hmOnlineResults[i];if(!m)return;
const ref=m.surah.number+':'+m.numberInSurah;
hState.custom.push({cid:'q'+Date.now(),name:"Qur'on "+ref,arabic:m.text,l:m.text,m:'',s:"Qur'on "+ref,c:1,added:todayKey,w:[0,24]});
saveH();showToast('➕ Qur\'on oyati qo\'shildi','success');
hmTab('oqim',document.querySelector('#hiddenMainOverlay .hm-tab'));
}
function hmAddManual(){
const name=document.getElementById('hmName').value.trim();
const latin=document.getElementById('hmLatin').value.trim();
const src=document.getElementById('hmSrc').value.trim();
if(!name||!latin){showToast('⚠️ Nom va matn kerak','warning');return}
if(!src){showToast('⚠️ MANBA majburiy! (xato yo\'li yopiq)','warning');return}
const sitMap={any:[0,24],tong:[4,9],taom:[7,21],chiqish:[7,18],kirish:[12,23],uyqu:[21,24]};
const sit=document.getElementById('hmSit').value;
hState.custom.push({cid:'c'+Date.now(),name:name,arabic:latin,l:latin,m:document.getElementById('hmMean').value.trim(),s:src,c:1,added:todayKey,w:sitMap[sit]});
saveH();showToast('➕ Qo\'shildi!','success');
['hmName','hmLatin','hmMean','hmSrc'].forEach(id=>document.getElementById(id).value='');
hmTab('oqim',document.querySelector('#hiddenMainOverlay .hm-tab'));
}
// ===== YASHIRIN SOZLAMALAR =====
function openHiddenSettings(){
buildHiddenSet();
document.getElementById('hiddenSetOverlay').classList.add('active');
hsRender();
}
function closeHiddenSet(){document.getElementById('hiddenSetOverlay').classList.remove('active')}
function buildHiddenSet(){
if(document.getElementById('hiddenSetOverlay'))return;
const o=document.createElement('div');o.className='hidden-overlay';o.id='hiddenSetOverlay';
o.innerHTML='<div class="diamond-header"><span class="diamond-title">⚙️ Yashirin sozlamalar</span><button class="close-form" onclick="closeHiddenSet()">✕</button></div><div id="hsBody"></div>';
document.body.appendChild(o);
}
function hsToggleRow(label,desc,on,fn){
return '<div class="settings-item"><div><div class="si-label">'+label+'</div>'+(desc?'<div class="si-desc">'+desc+'</div>':'')+'</div><div class="toggle-switch'+(on?' active':'')+'" onclick="'+fn+'()"></div></div>';
}
function hsRender(){
const S=hSetGet();
let html='';
html+='<div class="settings-group"><div class="settings-group-title">🔐 Xavfsizlik</div>';
html+='<div class="settings-item"><div><div class="si-label">Maxfiy PIN o\'zgartirish</div></div><button class="btn btn-sm btn-ghost" onclick="hsChangePin()">O\'zgartirish</button></div></div>';
html+='<div class="settings-group"><div class="settings-group-title">🌱 Asta-sekin boshqaruv</div>';
html+='<div class="settings-item"><div><div class="si-label">💡 Keyingi odatni och</div><div class="si-desc">Ilova taklif qiladi, siz ko\'rib yoqasiz</div></div><button class="btn btn-sm btn-success" onclick="hsNext()">Taklif</button></div>';
HCARDS.forEach(c=>{html+='<div class="settings-item"><div><div class="si-label">'+c.n+'</div><div class="si-desc">📖 '+c.s+'</div></div><div class="toggle-switch'+(hEnabled(c.id)?' active':'')+'" onclick="hsToggleCard(\''+c.id+'\')"></div></div>'});
hState.custom.forEach(c=>{html+='<div class="settings-item"><div><div class="si-label">✨ '+c.name+'</div><div class="si-desc">📖 '+c.s+'</div></div><div class="toggle-switch'+(hEnabled(c.cid)?' active':'')+'" onclick="hsToggleCard(\''+c.cid+'\')"></div></div>'});
html+='</div>';
html+='<div class="settings-group"><div class="settings-group-title">📊 Odat hisoblagich</div>';
html+=hsToggleRow('Vibratsiya','Har 33 da',S.vib,'hsVib');
html+=hsToggleRow('Ovoz','Yumshoq signal',S.sound,'hsSound');
html+='<div class="settings-item"><div><div class="si-label">Standart maqsad</div></div><input type="number" class="form-input" style="width:70px;padding:6px" value="'+S.target+'" onchange="hsTarget(this.value)"></div></div>';
html+='<div class="settings-group"><div class="settings-group-title">⚡ Tezkor chiplar</div>';
HQUICK.forEach(q=>{const on=S.chips[q.id]!==false;html+='<div class="settings-item"><div><div class="si-label">'+q.n+'</div></div><div class="toggle-switch'+(on?' active':'')+'" onclick="hsChip(\''+q.id+'\')"></div></div>'});
html+='</div>';
html+='<div class="settings-group"><div class="settings-group-title">🌿 Jonli oqim</div>';
html+=hsToggleRow('Jonli oqim','Soatga qarab avto-taklif',S.live,'hsLive');
html+='</div>';
document.getElementById('hsBody').innerHTML=html;
}
function hsChangePin(){
const p=prompt('Yangi 4 xonali maxfiy PIN:');
if(p&&p.length===4&&!isNaN(p)){dState.pin=p;saveD();showToast('✅ Maxfiy PIN o\'zgartirildi','success')}
else if(p!==null)showToast('❌ 4 xonali raqam!','warning');
}
function hsToggleCard(id){hState.enabled[id]=!hEnabled(id);saveH();hsRender()}
function hsNext(){
const disabled=HCARDS.filter(c=>!hEnabled(c.id));
if(!disabled.length){showToast('🎉 Hamma odatlar yoqilgan!','success');return}
const c=disabled[0];
if(confirm('💡 Taklif: "'+c.n+'" ('+c.r+')\n📖 '+c.s+'\n\nYoqilsinmi?')){hState.enabled[c.id]=true;saveH();showToast('🌱 '+c.n+' qo\'shildi!','success');hsRender()}
}
function hsVib(){const S=hSetGet();S.vib=!S.vib;saveH();hsRender()}
function hsSound(){const S=hSetGet();S.sound=!S.sound;saveH();hsRender()}
function hsLive(){const S=hSetGet();S.live=!S.live;saveH();hsRender()}
function hsTarget(v){const S=hSetGet();S.target=parseInt(v)||33;saveH()}
function hsChip(id){const S=hSetGet();S.chips[id]=S.chips[id]===false?true:false;saveH();hsRender()}
// ===== XAVFSIZ EXPORT/IMPORT (.intizom + merge, maxfiy CHIQMAYDI) =====
function isArr(x){return Array.isArray(x)}
function isObj(x){return x&&typeof x==='object'&&!Array.isArray(x)}
function exportData(){
const payload={app:'MaqsadliyIntizom',version:2,exportedAt:new Date().toISOString(),
data:{state:state,books:booksData,audiobooks:abData,water:waterData,sleep:sleepData,mood:moodData,journal:journalData,jstate:jState,templates:customT,settings:settings}};
const blob=new Blob([JSON.stringify(payload,null,2)],{type:'application/octet-stream'});
const a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='intizom-'+todayKey+'.intizom';a.click();
showToast('📤 Eksport (.intizom) — maxfiy ma\'lumot CHIQMADI','success');
}
function importData(e){
const f=e.target.files[0];if(!f)return;
const r=new FileReader();
r.onload=function(ev){
try{
const p=JSON.parse(ev.target.result);
if(!p||p.app!=='MaqsadliyIntizom'){showToast('❌ Bu Intizom formati emas!','warning');return}
const d=p.data||{};
const full=confirm('To\'liq almashtirishmi?\nOK = To\'liq almashtirish\nBekor = Birlashtirish (xavfsiz)');
if(full)applyFull(d);else applyMerge(d);
saveAll();renderAll();showToast('📥 Import qilindi','success');
}catch(err){showToast('❌ Fayl buzilgan!','warning')}
};
r.readAsText(f);e.target.value='';
}
function applyMerge(d){
if(isObj(d.state)&&isArr(d.state.tasks)){const ids=new Set(state.tasks.map(t=>t.id));d.state.tasks.forEach(t=>{if(t&&t.id&&!ids.has(t.id))state.tasks.push(t)})}
if(isArr(d.books))d.books.forEach(b=>{if(b&&b.id&&!booksData.some(x=>x.id===b.id))booksData.push(b)});
if(isArr(d.audiobooks))d.audiobooks.forEach(a=>{if(a&&a.id&&!abData.some(x=>x.id===a.id))abData.push(a)});
if(isObj(d.water))for(let k in d.water){if(!(k in waterData))waterData[k]=d.water[k]}
if(isArr(d.sleep))d.sleep.forEach(s=>{if(s&&s.date&&!sleepData.some(x=>x.date===s.date))sleepData.push(s)});
if(isArr(d.mood))d.mood.forEach(m=>{if(m&&m.date&&!moodData.some(x=>x.date===m.date))moodData.push(m)});
if(isArr(d.journal))d.journal.forEach(j=>{if(j&&j.id&&!journalData.some(x=>x.id===j.id))journalData.push(j)});
if(isArr(d.templates))d.templates.forEach(t=>{if(t&&t.id&&!customT.some(x=>x.id===t.id))customT.push(t)});
if(isObj(d.jstate)){for(let k in d.jstate.days){if(!(k in jState.days))jState.days[k]=d.jstate.days[k]}d.jstate.nasihat.forEach(n=>{if(n&&n.id&&!jState.nasihat.some(x=>x.id===n.id))jState.nasihat.push(n)})}
}
function applyFull(d){
if(isObj(d.state))state={...state,...d.state};
if(isArr(d.books))booksData=d.books;
if(isArr(d.audiobooks))abData=d.audiobooks;
if(isObj(d.water))waterData=d.water;
if(isArr(d.sleep))sleepData=d.sleep;
if(isArr(d.mood))moodData=d.mood;
if(isArr(d.journal))journalData=d.journal;
if(isArr(d.templates))customT=d.templates;
if(isObj(d.settings))settings={...settings,...d.settings};
if(isObj(d.jstate))jState={...jState,...d.jstate};
}
