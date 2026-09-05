/* ---------- helpers ---------- */
const $ = (sel, el=document) => el.querySelector(sel);
const $$ = (sel, el=document) => Array.from(el.querySelectorAll(sel));
const fmt = (n, d=1) => Number(n).toFixed(d);

const CHART_GRID = 'rgba(255,255,255,0.06)';
const CHART_TEXT = '#8B93A1';
Chart.defaults.color = CHART_TEXT;
Chart.defaults.font.family = "'IBM Plex Mono', monospace";
Chart.defaults.font.size = 11;

/* ---------- risk model ----------
   Weighted, normalized rule-based score using this dataset's own
   feature/outcome correlations (Vibration .463, Torque .451,
   Current .364, Process_Temp .184, Tool_Wear .065). Each reading is
   scored against the dataset's own percentile bands, not the saved
   .pkl model (which can't run client-side). */
const WEIGHTS = { Torque:0.451, Vibration:0.463, Current:0.364, Process_Temp_K:0.184, Tool_Wear:0.065 };
const TOTAL_W = Object.values(WEIGHTS).reduce((a,b)=>a+b,0);

function pctScore(val, p){
  // returns 0-100 based on where val sits among the dataset's own percentile markers
  const marks = [[50,p['50']],[75,p['75']],[90,p['90']],[95,p['95']],[99,p['99']]];
  if(val <= p['50']) return Math.max(0,(val/p['50'])*40);
  for(let i=0;i<marks.length-1;i++){
    const [lo,loV]=marks[i], [hi,hiV]=marks[i+1];
    if(val<=hiV){
      const frac=(val-loV)/((hiV-loV)||1);
      return lo + frac*(hi-lo);
    }
  }
  return 100;
}

function riskScore(reading){
  let sum=0;
  for(const k in WEIGHTS){
    const p = DATA.percentiles[k];
    sum += WEIGHTS[k]*pctScore(reading[k], p);
  }
  return Math.min(100, sum/TOTAL_W);
}

function driverOf(reading){
  let best=null,bestScore=-1;
  for(const k in WEIGHTS){
    const s = pctScore(reading[k], DATA.percentiles[k]) * WEIGHTS[k];
    if(s>bestScore){bestScore=s;best=k;}
  }
  const names = {Torque:'Torque',Vibration:'Vibration',Current:'Current',Process_Temp_K:'Process temperature',Tool_Wear:'Tool wear'};
  return names[best];
}

function riskTier(score){
  if(score>=72) return 'critical';
  if(score>=45) return 'watch';
  return 'normal';
}

/* ---------- KPI row ---------- */
function renderKpis(){
  const o = DATA.overall;
  const bestModel = MODEL_COMPARISON.reduce((a,b)=> b.roc_auc>a.roc_auc?b:a);
  const kpis = [
    {label:'Total readings', value:o.total_records.toLocaleString(), cls:''},
    {label:'Devices monitored', value:o.total_devices, cls:''},
    {label:'Recorded failures', value:o.total_failures.toLocaleString(), cls:'crit'},
    {label:'Overall failure rate', value:fmt(o.failure_rate,1)+'<span class="unit">%</span>', cls:'crit'},
    {label:'Best model ROC-AUC', value:fmt(bestModel.roc_auc,3)+'<span class="unit">'+bestModel.name+'</span>', cls:'ok'},
  ];
  $('#kpiRow').innerHTML = kpis.map(k=>`
    <div class="kpi ${k.cls}">
      <div class="label">${k.label}</div>
      <div class="value">${k.value}</div>
    </div>`).join('');
}

/* ---------- Charts ---------- */
function renderTrendChart(){
  const ctx = $('#trendChart');
  new Chart(ctx,{
    type:'line',
    data:{
      labels: DATA.monthly.map(m=>m.month),
      datasets:[{
        label:'Failure rate %',
        data: DATA.monthly.map(m=>m.rate),
        borderColor:'#E4483F',
        backgroundColor:'rgba(228,72,63,0.08)',
        fill:true, tension:.3, pointRadius:0, borderWidth:2,
      }]
    },
    options:{
      maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{
        x:{grid:{color:CHART_GRID},ticks:{maxTicksLimit:8}},
        y:{grid:{color:CHART_GRID},ticks:{callback:v=>v+'%'}}
      }
    }
  });
}

function renderModelChart(){
  const ctx = $('#modelChart');
  const labels = MODEL_COMPARISON.map(m=>m.name);
  const metricKeys = [['accuracy','Accuracy','#5B8DEF'],['precision','Precision','#E3A73B'],['recall','Recall','#49B87D'],['f1','F1','#B07CE8'],['roc_auc','ROC-AUC','#E4483F']];
  new Chart(ctx,{
    type:'bar',
    data:{
      labels,
      datasets: metricKeys.map(([key,label,color])=>({
        label, data: MODEL_COMPARISON.map(m=>m[key]), backgroundColor:color,
      }))
    },
    options:{
      maintainAspectRatio:false,
      plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:10,font:{size:10}}}},
      scales:{
        x:{grid:{display:false},ticks:{font:{size:9},maxRotation:20,minRotation:20}},
        y:{grid:{color:CHART_GRID},min:0,max:1}
      }
    }
  });
}

function renderTorqueChart(){
  const ctx = $('#torqueChart');
  new Chart(ctx,{
    type:'bar',
    data:{
      labels: DATA.torque_hist.map(b=>b.bin),
      datasets:[
        {label:'No failure', data: DATA.torque_hist.map(b=>b.no_failure), backgroundColor:'#2F3A4D', stack:'s'},
        {label:'Failure', data: DATA.torque_hist.map(b=>b.failure), backgroundColor:'#E4483F', stack:'s'},
      ]
    },
    options:{
      maintainAspectRatio:false,
      plugins:{legend:{position:'bottom',labels:{boxWidth:10,padding:10,font:{size:10}}}},
      scales:{
        x:{grid:{display:false},stacked:true,ticks:{font:{size:9}}},
        y:{grid:{color:CHART_GRID},stacked:true,type:'logarithmic',ticks:{font:{size:9}}}
      }
    }
  });
}

function renderFeatChart(){
  const ctx = $('#featChart');
  const sorted = [...FEATURE_IMPORTANCE].sort((a,b)=>a.value-b.value);
  new Chart(ctx,{
    type:'bar',
    data:{
      labels: sorted.map(f=>f.name),
      datasets:[{
        data: sorted.map(f=>f.value),
        backgroundColor: sorted.map(f=>f.value>=0?'#5B8DEF':'#E3A73B'),
      }]
    },
    options:{
      indexAxis:'y',
      maintainAspectRatio:false,
      plugins:{legend:{display:false}},
      scales:{
        x:{grid:{color:CHART_GRID}},
        y:{grid:{display:false}}
      }
    }
  });
}

/* ---------- Fleet table ---------- */
let sortKey='failure_rate', sortDir=-1, selectedDevice=null;
function renderFleet(){
  const maxFR = Math.max(...DATA.devices.map(d=>d.failure_rate));
  const q = $('#deviceSearch').value.trim().toUpperCase();
  let rows = DATA.devices.filter(d=>d.device.includes(q));
  rows.sort((a,b)=> (a[sortKey]>b[sortKey]?1:-1)*sortDir);
  $('#fleetMeta').textContent = rows.length + ' shown';
  $('#fleetBody').innerHTML = rows.map(d=>`
    <tr data-device="${d.device}" class="${selectedDevice===d.device?'selected':''}">
      <td>${d.device}</td>
      <td><div class="fr-cell">${fmt(d.failure_rate,1)}%<div class="fr-bar-wrap"><div class="fr-bar" style="width:${(d.failure_rate/maxFR*100)}%"></div></div></div></td>
      <td>${d.records}</td>
      <td>${d.failures}</td>
      <td>${fmt(d.avg_torque,1)}</td>
      <td>${fmt(d.avg_vibration,2)}</td>
      <td>${fmt(d.avg_current,1)}</td>
      <td>${fmt(d.avg_process_temp,1)}</td>
    </tr>`).join('');
  $$('#fleetBody tr').forEach(tr=>{
    tr.addEventListener('click', ()=>{
      selectedDevice = selectedDevice===tr.dataset.device ? null : tr.dataset.device;
      renderFleet();
    });
  });
}

$$('th[data-key]').forEach(th=>{
  th.addEventListener('click', ()=>{
    const key = th.dataset.key;
    if(sortKey===key) sortDir*=-1; else {sortKey=key; sortDir=-1;}
    $$('th').forEach(t=>t.classList.remove('sorted'));
    th.classList.add('sorted');
    renderFleet();
  });
});
$('#deviceSearch').addEventListener('input', renderFleet);

/* ---------- Live feed simulation ---------- */
let feedTimer=null, playing=true, activeAlert=null;
const alerts = [];

function jitter(val, pct=0.06){
  return val * (1 + (Math.random()*2-1)*pct);
}

function pickReading(forceDevice=null, forceFailure=false){
  const pool = DATA.last_readings;
  const base = forceDevice ? pool.find(r=>r.device===forceDevice) : pool[Math.floor(Math.random()*pool.length)];
  const reading = {
    device: base.device,
    Torque: jitter(base.Torque),
    Vibration: jitter(base.Vibration),
    Current: jitter(base.Current),
    Process_Temp_K: jitter(base.Process_Temp_K, 0.01),
    Tool_Wear: jitter(base.Tool_Wear, 0.15),
  };
  if(forceFailure){
    const p = DATA.percentiles;
    reading.Torque = p.Torque['99']*1.02;
    reading.Vibration = p.Vibration['99']*1.05;
    reading.Current = p.Current['99']*1.02;
    reading.Process_Temp_K = p.Process_Temp_K['95'];
  }
  return reading;
}

function addLiveRow(reading, score){
  const feed = $('#liveFeed');
  const tier = riskTier(score);
  const ts = new Date().toLocaleTimeString('en-GB',{hour12:false});
  const row = document.createElement('div');
  row.className='live-row';
  row.innerHTML = `
    <span class="ts">${ts}</span>
    <span class="dev">${reading.device}</span>
    <span class="readings">T ${fmt(reading.Torque,0)}Nm · V ${fmt(reading.Vibration,2)}mm/s · I ${fmt(reading.Current,1)}A</span>
    <span class="risk-tag ${tier}">${tier==='critical'?'critical':tier==='watch'?'watch':'nominal'} · ${fmt(score,0)}</span>
  `;
  feed.prepend(row);
  while(feed.children.length>40) feed.removeChild(feed.lastChild);
}

function triggerEmergency(reading, score){
  activeAlert = {reading, score, time: new Date()};
  $('#mDevice').textContent = reading.device;
  $('#mTorque').textContent = fmt(reading.Torque,1)+' Nm';
  $('#mVibration').textContent = fmt(reading.Vibration,2)+' mm/s';
  $('#mCurrent').textContent = fmt(reading.Current,1)+' A';
  $('#mTemp').textContent = fmt(reading.Process_Temp_K,1)+' K';
  $('#mDriver').textContent = driverOf(reading);
  $('#gaugeFill').style.width = Math.round(score)+'%';
  $('#gaugeVal').textContent = 'risk score '+Math.round(score);
  $('#modalSub').textContent = reading.device+' · '+activeAlert.time.toLocaleTimeString('en-GB',{hour12:false});
  $('#modalOverlay').classList.add('show');
  setPlaying(false);
  logAlert(reading, score, false);
}

function logAlert(reading, score, acked){
  const item = {device:reading.device, score, time:new Date(), acked};
  alerts.unshift(item);
  renderAlertLog();
}

function renderAlertLog(){
  const el = $('#alertLog');
  const activeCount = alerts.filter(a=>!a.acked).length;
  $('#alertCount').textContent = activeCount + ' active';
  if(alerts.length===0){
    el.innerHTML = '<div class="empty-note">No alerts yet. The feed will flag a device the moment its risk score crosses the critical threshold.</div>';
    return;
  }
  el.innerHTML = alerts.slice(0,25).map(a=>`
    <div class="alert-item ${a.acked?'ack':''}">
      <span class="dot"></span>
      <div class="body">
        <div class="t1">${a.device} — risk ${Math.round(a.score)}${a.acked?' · acknowledged':''}</div>
        <div class="t2">${a.time.toLocaleTimeString('en-GB',{hour12:false})} · ${a.acked?'resolved':'awaiting action'}</div>
      </div>
    </div>`).join('');
}

function closeModal(acked){
  $('#modalOverlay').classList.remove('show');
  if(activeAlert && acked){
    const match = alerts.find(a=>a.device===activeAlert.reading.device && !a.acked);
    if(match) match.acked = true;
    renderAlertLog();
  }
  activeAlert=null;
  setPlaying(true);
}

$('#ackBtn').addEventListener('click', ()=>closeModal(true));
$('#dispatchBtn').addEventListener('click', ()=>closeModal(true));

function tick(){
  const forceFail = Math.random() < 0.045; // occasional realistic spike
  const reading = pickReading(null, forceFail);
  const score = riskScore(reading);
  addLiveRow(reading, score);
  if(riskTier(score)==='critical' && !$('#modalOverlay').classList.contains('show')){
    triggerEmergency(reading, score);
  }
}

function setPlaying(state){
  playing = state;
  $('#playBtn').textContent = playing ? 'Pause' : 'Resume';
  $('#playBtn').classList.toggle('active', playing);
  clearInterval(feedTimer);
  if(playing) feedTimer = setInterval(tick, 1800);
}

$('#playBtn').addEventListener('click', ()=> setPlaying(!playing));
$('#forceBtn').addEventListener('click', ()=>{
  const reading = pickReading(null, true);
  const score = riskScore(reading);
  addLiveRow(reading, score);
  triggerEmergency(reading, score);
});

/* ---------- init ---------- */
renderKpis();
renderTrendChart();
renderModelChart();
renderTorqueChart();
renderFeatChart();
renderFleet();
for(let i=0;i<6;i++) tick();
setPlaying(true);
