document.addEventListener('DOMContentLoaded',function(){const appointmentsList=document.getElementById('appointmentsList');const loadingSpinner=document.getElementById('loadingSpinner');const noAppointments=document.getElementById('noAppointments');const logoutBtn=document.getElementById('logoutBtn');const novoRegistroBtn=document.getElementById('novoRegistroBtn');const DIARY_STORAGE_BASE='diaryEntries';let currentUser=null;if(novoRegistroBtn){novoRegistroBtn.addEventListener('click',(e)=>{e.preventDefault();const modalHtml=`<div class="modal fade" id="registroDiarioModal" tabindex="-1" aria-labelledby="registroDiarioModalLabel" aria-hidden="true"><div class="modal-dialog modal-lg modal-dialog-centered"><div class="modal-content"><form id="registroForm" novalidate><div class="modal-header"><h5 class="modal-title" id="registroDiarioModalLabel"><i class="bi bi-journal-plus me-2"></i>Novo Registro Diário</h5><button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button></div><div class="modal-body"><div class="row g-3"><div class="col-12"><label class="form-label">Situação</label><textarea class="form-control" name="situacao" rows="2" required></textarea><div class="invalid-feedback">Descreva a situação.</div></div><div class="col-12"><label class="form-label">Pensamento</label><textarea class="form-control" name="pensamento" rows="2" required></textarea><div class="invalid-feedback">Descreva o pensamento.</div></div><div class="col-12"><label class="form-label">Emoções e Intensidades</label><div id="emocoesContainer"></div><button type="button" class="btn btn-sm btn-outline-primary mt-2" id="addEmocaoBtn"><i class="bi bi-plus-circle"></i> Adicionar emoção</button><div class="form-text">Adicione uma ou mais emoções com intensidade (0-10).</div></div><div class="col-12"><label class="form-label">Comportamento</label><textarea class="form-control" name="comportamento" rows="2" required></textarea><div class="invalid-feedback">Descreva o comportamento.</div></div><div class="col-12"><label class="form-label">Consequência</label><textarea class="form-control" name="consequencia" rows="2" placeholder="O que aconteceu depois?" required></textarea><div class="invalid-feedback">Informe a consequência.</div></div></div></div><div class="modal-footer"><button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button><button type="submit" class="btn btn-primary">Salvar</button></div></form></div></div></div>`;if(!document.getElementById('registroDiarioModal')){document.body.insertAdjacentHTML('beforeend',modalHtml);}const modalEl=document.getElementById('registroDiarioModal');const registroModal=new bootstrap.Modal(modalEl);const formEl=modalEl.querySelector('#registroForm');if(formEl&&!formEl.dataset.bound){formEl.dataset.bound='true';const emocoesContainer=formEl.querySelector('#emocoesContainer');const addEmocaoBtn=formEl.querySelector('#addEmocaoBtn');const createEmocaoRow=(defaults={emocao:'',intensidade:5})=>{const row=document.createElement('div');row.className='emocao-row row gx-2 align-items-center mb-2';row.innerHTML='<div class="col-md-4"><select class="form-select emocao-select"><option value="">Selecione...</option><option value="Alegria">Alegria</option><option value="Tristeza">Tristeza</option><option value="Raiva">Raiva</option><option value="Medo">Medo</option><option value="Ansiedade">Ansiedade</option><option value="Nojo">Nojo</option><option value="Surpresa">Surpresa</option><option value="Calma">Calma</option><option value="OUTRAS">Outras</option></select></div><div class="col-md-3 d-none emocao-custom-wrapper"><input type="text" class="form-control emocao-custom" placeholder="Descreva a emoção"></div><div class="col-md-4"><div class="d-flex align-items-center gap-2"><input type="range" class="form-range intensidade-range" min="0" max="10" step="1" value="'+defaults.intensidade+'"><span class="badge text-bg-secondary intensidade-value">'+defaults.intensidade+'</span></div></div><div class="col-md-1 text-end"><button type="button" class="btn btn-outline-danger btn-sm remove-emocao" title="Remover"><i class="bi bi-trash"></i></button></div>';const selectEl=row.querySelector('.emocao-select');const customWrapper=row.querySelector('.emocao-custom-wrapper');const customInput=row.querySelector('.emocao-custom');const rangeEl=row.querySelector('.intensidade-range');const valueEl=row.querySelector('.intensidade-value');const removeBtn=row.querySelector('.remove-emocao');if(defaults.emocao){selectEl.value=defaults.emocao;}const toggleCustom=()=>{if(selectEl.value==='OUTRAS'){customWrapper.classList.remove('d-none');}else{customWrapper.classList.add('d-none');customInput.value='';}};selectEl.addEventListener('change',toggleCustom);toggleCustom();rangeEl.addEventListener('input',()=>{valueEl.textContent=rangeEl.value;});removeBtn.addEventListener('click',()=>{row.remove();});return row;};if(emocoesContainer){emocoesContainer.appendChild(createEmocaoRow());}if(addEmocaoBtn){addEmocaoBtn.addEventListener('click',()=>{emocoesContainer.appendChild(createEmocaoRow());});}formEl.addEventListener('submit',(ev)=>{ev.preventDefault();ev.stopPropagation();const rows=Array.from(formEl.querySelectorAll('.emocao-row'));if(rows.length===0){alert('Adicione pelo menos uma emoção.');return;}const invalidRow=rows.find(r=>{const s=r.querySelector('.emocao-select');const c=r.querySelector('.emocao-custom');return !s.value || (s.value==='OUTRAS' && !c.value.trim());});if(invalidRow){alert('Preencha todas as emoções e intensidades.');return;}if(!formEl.checkValidity()){formEl.classList.add('was-validated');return;}const nowISO=new Date().toISOString();const pares=rows.map(r=>{const s=r.querySelector('.emocao-select');const c=r.querySelector('.emocao-custom');const range=r.querySelector('.intensidade-range');const emocao=s.value==='OUTRAS'?c.value.trim():s.value;return {emocao,intensidade:Number(range.value)};}).filter(p=>p.emocao);const primeira=pares[0]||{emocao:'',intensidade:0};const payload={situacao:formEl.querySelector('[name="situacao"]').value,pensamento:formEl.querySelector('[name="pensamento"]').value,emocao:primeira.emocao||'',intensidade:primeira.intensidade||0,emocao_intensidades:pares,comportamento:formEl.querySelector('[name="comportamento"]').value,consequencia:formEl.querySelector('[name="consequencia"]').value||'',data_registro:nowISO};const storeKey=`${DIARY_STORAGE_BASE}:${currentUser?.id||currentUser?.email||'anon'}`;const fallbackSave=()=>{const entries=JSON.parse(localStorage.getItem(storeKey)||'[]');entries.unshift({id:Date.now(),createdAt:nowISO,dataHora:nowISO,...payload});localStorage.setItem(storeKey,JSON.stringify(entries));};fetch('/api/patients/me/diary-entries',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).then(async(res)=>{if(!res.ok){const err=await res.json().catch(()=>({message:'Erro desconhecido'}));throw new Error(err.message||`Falha ao salvar registro (${res.status})`);}return res.json();}).then((resp)=>{registroModal.hide();alert('Registro salvo com sucesso!');formEl.reset();formEl.classList.remove('was-validated');const entries=JSON.parse(localStorage.getItem(storeKey)||'[]');const saved=unwrapApiData(resp);if(saved&&saved.id){entries.unshift(saved);localStorage.setItem(storeKey,JSON.stringify(entries));}if(typeof loadDiaryEntries==='function'){loadDiaryEntries();}}).catch((error)=>{console.error('Erro ao salvar registro diário:',error);fallbackSave();registroModal.hide();alert('Não foi possível salvar no servidor. Registro salvo localmente.');formEl.reset();formEl.classList.remove('was-validated');});});}registroModal.show();});}function unwrapApiData(payload){if(!payload)return[];if(Array.isArray(payload))return payload;if(typeof payload==='object'&&'data'in payload)return payload.data;return payload;}checkUserAuthentication();loadPatientAppointments();if(typeof loadDiaryEntries==='function'){loadDiaryEntries();}if(logoutBtn){logoutBtn.addEventListener('click',function(e){e.preventDefault();logout();});}function checkUserAuthentication(){fetch('/api/me').then(response=>{if(!response.ok){window.location.href='/entrar.html';throw new Error('Usuário não autenticado');}return response.json();}).then(userData=>{currentUser=userData;if(userData.role!=='patient'){window.location.href='/';throw new Error('Acesso não autorizado');}if(userData.first_login){window.location.href='/paciente-primeiro-login.html';throw new Error('Primeiro login - necessário alterar senha');}}).catch(error=>{console.error('Erro ao verificar usuário:',error);});}function loadPatientAppointments(){
  const nextAppointmentContent=document.getElementById('nextAppointmentContent');
  const dashboardLoadingSpinnerAppointments=document.getElementById('dashboardLoadingSpinnerAppointments');
  const latestDiaryContent=document.getElementById('latestDiaryContent');
  const dashboardLoadingSpinnerDiary=document.getElementById('dashboardLoadingSpinnerDiary');
  loadingSpinner.classList.remove('d-none');
  loadingSpinner.classList.add('d-flex');
  appointmentsList.innerHTML='';
  noAppointments.style.display='none';
  fetch('/api/patients/me/appointments').then(response=>{if(!response.ok){throw new Error('Falha ao buscar agendamentos');}return response.json();}).then(appointmentsPayload=>{
    const appointments=Array.isArray(appointmentsPayload)?appointmentsPayload:(appointmentsPayload&&typeof appointmentsPayload==='object'&&'data' in appointmentsPayload?appointmentsPayload.data:[]);
    loadingSpinner.classList.remove('d-flex');
    loadingSpinner.classList.add('d-none');
    if(dashboardLoadingSpinnerAppointments){dashboardLoadingSpinnerAppointments.classList.remove('d-flex');dashboardLoadingSpinnerAppointments.classList.add('d-none');}
    if(!appointments||appointments.length===0){
      noAppointments.style.display='block';
      if(nextAppointmentContent){nextAppointmentContent.textContent='Nenhum próximo agendamento encontrado.';}
      return;
    }
    appointments.sort((a,b)=>new Date(b.data_primeira_sessao)-new Date(a.data_primeira_sessao));
    // Atualiza resumo do próximo agendamento
    try { updateDashboardNextAppointment(nextAppointmentContent, appointments); } catch(e){ console.error('Erro ao atualizar resumo de agendamentos:', e); }
    appointments.forEach(appointment=>{renderAppointment(appointment);});
  }).catch(error=>{
    loadingSpinner.classList.remove('d-flex');
    loadingSpinner.classList.add('d-none');
    if(dashboardLoadingSpinnerAppointments){dashboardLoadingSpinnerAppointments.classList.remove('d-flex');dashboardLoadingSpinnerAppointments.classList.add('d-none');}
    if(nextAppointmentContent){nextAppointmentContent.textContent=`Erro ao carregar próximo agendamento: ${error.message||'Erro desconhecido'}`;}
    appointmentsList.innerHTML=`<div class="alert alert-danger" role="alert">Erro ao carregar agendamentos: ${error.message||'Erro desconhecido'}</div>`;
    console.error('Erro ao carregar agendamentos:',error);
  });
}
function renderAppointment(appointment){const rawDate=appointment.data_primeira_sessao;const appointmentDate=rawDate?new Date(rawDate):null;const formattedDate=appointmentDate?appointmentDate.toLocaleDateString('pt-BR',{weekday:'long',year:'numeric',month:'long',day:'numeric'}):'Data não informada';const formattedTime=appointmentDate?appointmentDate.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}):'';let statusText='Agendado';const hasSessions=Array.isArray(appointment.sessions)&&appointment.sessions.length>0;const allCompleted=hasSessions&&appointment.sessions.every(s=>normalizeSessionStatus(s.status)==='completed');const anyCancelled=hasSessions&&appointment.sessions.some(s=>normalizeSessionStatus(s.status)==='cancelled');if(anyCancelled){statusText='Cancelado';}else if(allCompleted){statusText='Concluído';}const appointmentElement=document.createElement('div');appointmentElement.className='card shadow-sm mb-3';const valor=appointment.valor_por_sessao?Number(appointment.valor_por_sessao):0;const valorFormatado=valor.toLocaleString('pt-BR',{style:'currency',currency:'BRL'});const collapseId=`sessions-${appointment.id||Math.floor(Math.random()*1e6)}`;const baseBadgeClass='badge rounded-pill';const statusBadgeClass=`${baseBadgeClass} ${anyCancelled?'text-bg-danger':(allCompleted?'text-bg-success':'text-bg-secondary')}`;appointmentElement.innerHTML=`<div class="card-body py-3"><div class="d-flex justify-content-between align-items-center"><div><div class="fw-normal">${formattedDate}</div><div class="text-muted"><i class="bi bi-clock"></i> ${formattedTime}</div></div><span class="${statusBadgeClass}">${statusText}</span></div><div class="row gy-2 mt-2"><div class="col-md-4"><div class="small text-muted">Valor por sessão</div><div class="fw-normal">${valorFormatado}</div></div><div class="col-md-4"><div class="small text-muted">Especialidade</div><div class="fw-normal">${appointment.especialidade_nome||'N/A'}</div></div><div class="col-md-4 text-md-end"><button class="btn btn-sm btn-outline-secondary" type="button" data-bs-toggle="collapse" data-bs-target="#${collapseId}" aria-expanded="false" aria-controls="${collapseId}">Ver sessões (${appointment.sessions?appointment.sessions.length:0})</button></div><div class="col-12"><div class="small text-muted">Observações</div><div class="fw-normal">${appointment.observacoes||'Nenhuma observação'}</div></div></div>${renderSessions(appointment,collapseId)}</div>`;appointmentsList.appendChild(appointmentElement);}function normalizeSessionStatus(status){if(!status)return'scheduled';const s=String(status).toLowerCase();if(s==='completed'||s==='realizada')return'completed';if(s==='cancelled'||s==='cancelada')return'cancelled';return'scheduled';}function renderSessions(appointment,collapseId){const sessions=appointment&&Array.isArray(appointment.sessions)?appointment.sessions:[];if(!sessions||sessions.length===0){return'';}const sortedSessions=[...sessions].sort((a,b)=>new Date(a.data_sessao)-new Date(b.data_sessao));let sessionsHtml=`<div class="collapse mt-3" id="${collapseId}"><ul class="list-group list-group-flush">`;sortedSessions.forEach(session=>{const sessionDate=new Date(session.data_sessao);const formattedSessionDate=sessionDate.toLocaleDateString('pt-BR');const formattedSessionTime=sessionDate.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});let statusText='Agendada';let statusBadge='text-bg-secondary';const normalized=normalizeSessionStatus(session.status);if(normalized==='completed'){statusText='Concluída';statusBadge='text-bg-success';}else if(normalized==='cancelled'){statusText='Cancelada';statusBadge='text-bg-danger';}else if(sessionDate<new Date()){statusText='Pendente';statusBadge='text-bg-warning';}sessionsHtml+=`<li class="list-group-item d-flex justify-content-between align-items-center"><span><i class="bi bi-calendar-event"></i> ${formattedSessionDate} às ${formattedSessionTime}</span><span class="badge rounded-pill ${statusBadge}">${statusText}</span></li>`;});sessionsHtml+='</ul></div>';return sessionsHtml;}function logout(){fetch('/api/logout',{method:'POST',headers:{'Content-Type':'application/json'}}).then(r=>r.json()).then(()=>{window.location.href='/inicial.html';}).catch((error)=>{console.error('Erro ao fazer logout:',error);window.location.href='/inicial.html';});}
function loadDiaryEntries(){
  // Desativado na página de agendamentos: não carregar registros diários
  return;
  const diaryListEl=document.getElementById('diaryList');
  const diaryLoadingSpinnerEl=document.getElementById('diaryLoadingSpinner');
  const noDiaryEntriesEl=document.getElementById('noDiaryEntries');
  const latestDiaryContent=document.getElementById('latestDiaryContent');
  const dashboardLoadingSpinnerDiary=document.getElementById('dashboardLoadingSpinnerDiary');
  if(dashboardLoadingSpinnerDiary){dashboardLoadingSpinnerDiary.classList.remove('d-none');dashboardLoadingSpinnerDiary.classList.add('d-flex');}
  if(latestDiaryContent){latestDiaryContent.textContent='Carregando último registro diário...';}
  if(!diaryListEl||!diaryLoadingSpinnerEl||!noDiaryEntriesEl) return;
  diaryLoadingSpinnerEl.classList.remove('d-none');
  diaryLoadingSpinnerEl.classList.add('d-flex');
  diaryListEl.innerHTML='';
  noDiaryEntriesEl.style.display='none';
  fetch('/api/patients/me/diary-entries')
    .then((response)=>{
      if(!response.ok){
        throw new Error('Falha ao buscar registros diários');
      }
      return response.json();
    })
    .then((payload)=>{
      const entries=(Array.isArray(payload)?payload:(payload&&typeof payload==='object'&&'data' in payload?payload.data:[]));
      diaryLoadingSpinnerEl.classList.remove('d-flex');
      diaryLoadingSpinnerEl.classList.add('d-none');
      if(dashboardLoadingSpinnerDiary){dashboardLoadingSpinnerDiary.classList.remove('d-flex');dashboardLoadingSpinnerDiary.classList.add('d-none');}
      if(!entries||!Array.isArray(entries)||entries.length===0){
        noDiaryEntriesEl.style.display='block';
        if(latestDiaryContent){latestDiaryContent.textContent='Nenhum registro diário encontrado.';}
        return;
      }
      entries.sort((a,b)=>new Date(b.data_registro||b.created_at)-new Date(a.data_registro||a.created_at));
      // Atualiza resumo do último registro diário
      try { updateDashboardLatestDiary(entries[0]); } catch(e){ console.error('Erro ao atualizar resumo do diário:', e); }
      entries.forEach((entry)=>renderDiaryEntry(entry));
    })
    .catch((error)=>{
      diaryLoadingSpinnerEl.classList.remove('d-flex');
      diaryLoadingSpinnerEl.classList.add('d-none');
      if(dashboardLoadingSpinnerDiary){dashboardLoadingSpinnerDiary.classList.remove('d-flex');dashboardLoadingSpinnerDiary.classList.add('d-none');}
      diaryListEl.innerHTML=`<div class="alert alert-danger" role="alert">Erro ao carregar registros diários: ${error.message||'Erro desconhecido'}</div>`;
      if(latestDiaryContent){latestDiaryContent.textContent=`Erro ao carregar último registro diário: ${error.message||'Erro desconhecido'}`;}
      console.error('Erro ao carregar registros diários:',error);
    });
}

// Oculta botões/links do Diário na navbar quando desativado
document.addEventListener('DOMContentLoaded', function(){
  try{
    // Ocultar permanentemente os botões do Diário na navbar
    const novoBtn = document.getElementById('novoRegistroBtn');
    if(novoBtn){ novoBtn.style.display = 'none'; }
    const diaryNavLinkAlways = document.querySelector('a.nav-link[href="paciente-diarios.html"]');
    if(diaryNavLinkAlways){ diaryNavLinkAlways.style.display = 'none'; }

    fetch('/api/patients/me')
      .then(r=>r.ok?r.json():null)
      .then((payload)=>{
        if(!payload) return;
        const patient = (payload && typeof payload==='object' && 'data' in payload) ? payload.data : payload;
        const enabled = !!(patient && patient.diario_tcc_ativo);
        if(!enabled){
          // Já ocultados acima; manter lógica caso precise outras seções
        }
      }).catch(()=>{});
  }catch(_){ /* noop */ }
});
function renderDiaryEntry(entry){const diaryListEl=document.getElementById('diaryList');if(!diaryListEl)return;const createdISO=entry.data_registro||entry.created_at||entry.createdAt||entry.dataHora;const d=createdISO?new Date(createdISO):null;const formattedDate=d?d.toLocaleDateString('pt-BR',{weekday:'long',year:'numeric',month:'long',day:'numeric'}):'Data não informada';const formattedTime=d?d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'}):'';let pares=[];if(Array.isArray(entry.emocao_intensidades)){pares=entry.emocao_intensidades;}else if(typeof entry.emocao==='string'&&entry.emocao){const inten=(typeof entry.intensidade==='number'?entry.intensidade:Number(entry.intensidade||0))||0;pares=[{emocao:entry.emocao,intensidade:inten}];}const maxIntensidade=pares.length?Math.max(...pares.map(p=>Number(p.intensidade||0))):((typeof entry.intensidade==='number'?entry.intensidade:Number(entry.intensidade||0))||0);const badgeClass=maxIntensidade>=7?'text-bg-danger':(maxIntensidade>=4?'text-bg-warning':'text-bg-success');const emotionsHtml=pares.length?pares.map(p=>{const inten=Number(p.intensidade||0);const cls=inten>=7?'text-bg-danger':(inten>=4?'text-bg-warning':'text-bg-info');return `<span class="badge ${cls} me-1">${escapeHtml(p.emocao)} (${inten})</span>`;}).join(''):`<span class="badge text-bg-info">${escapeHtml(entry.emocao||'—')}</span>`;const card=document.createElement('div');card.className='card shadow-sm mb-3';card.innerHTML=`<div class="card-body py-3"><div class="d-flex justify-content-between align-items-center"><div><div class="fw-normal">${formattedDate}</div><div class="text-muted"><i class="bi bi-clock"></i> ${formattedTime}</div></div><span class="badge rounded-pill ${badgeClass}">Intensidade máx: ${maxIntensidade}</span></div><div class="row gy-2 mt-2"><div class="col-12"><div class="small text-muted">Situação</div><div class="fw-normal">${escapeHtml(entry.situacao)||'—'}</div></div><div class="col-12"><div class="small text-muted">Pensamento</div><div class="fw-normal">${escapeHtml(entry.pensamento)||'—'}</div></div><div class="col-12"><div class="small text-muted">Emoções</div><div class="fw-normal">${emotionsHtml}</div></div><div class="col-12"><div class="small text-muted">Comportamento</div><div class="fw-normal">${escapeHtml(entry.comportamento)||'—'}</div></div>${entry.consequencia?`<div class="col-12"><div class="small text-muted">Consequência</div><div class="fw-normal">${escapeHtml(entry.consequencia)}</div></div>`:''}</div></div>`;diaryListEl.appendChild(card);}function escapeHtml(text){if(text==null)return'';return String(text).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;').replace(/'/g,'&#039;');}
});
function updateDashboardNextAppointment(targetEl, appointments){
  if(!targetEl) return;
  const now=new Date();
  let candidate=null; // {date, especialidade, profissional}
  appointments.forEach(appt=>{
    const sessions=Array.isArray(appt.sessions)?appt.sessions:[];
    const futureSessionDates=sessions.map(s=>new Date(s.data_sessao)).filter(d=>!isNaN(d)&&d>now);
    const nextSession=futureSessionDates.sort((a,b)=>a-b)[0];
    const apptBaseDate=appt.data_primeira_sessao?new Date(appt.data_primeira_sessao):null;
    const apptFutureDate=apptBaseDate && apptBaseDate>now ? apptBaseDate : null;
    const chosen= nextSession || apptFutureDate || null;
    if(chosen){
      if(!candidate || chosen < candidate.date){
        candidate={date:chosen, especialidade: appt.especialidade_nome||'N/A', profissional: appt.funcionario_nome||'N/A'};
      }
    }
  });
  if(!candidate){
    targetEl.textContent='Nenhum próximo agendamento encontrado.';
    return;
  }
  const dateStr=candidate.date.toLocaleDateString('pt-BR',{weekday:'long',year:'numeric',month:'long',day:'numeric'});
  const timeStr=candidate.date.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
  targetEl.innerHTML=`<i class=\"bi bi-calendar-event\"></i> ${dateStr} às ${timeStr} <span class=\"ms-2 fw-bold\">${escapeHtml(candidate.especialidade)} ${escapeHtml(candidate.profissional)}</span>`;
}
function updateDashboardLatestDiary(entry){
  if(!latestDiaryContent||!entry) return;
  const createdISO=entry.data_registro||entry.created_at||entry.createdAt||entry.dataHora;
  const d=createdISO?new Date(createdISO):null;
  if(!d){ latestDiaryContent.textContent='Nenhum registro diário encontrado.'; return; }
  const dateStr=d.toLocaleDateString('pt-BR',{weekday:'long',year:'numeric',month:'long',day:'numeric'});
  const timeStr=d.toLocaleTimeString('pt-BR',{hour:'2-digit',minute:'2-digit'});
  let pares=[];
  if(Array.isArray(entry.emocao_intensidades)){
    pares=entry.emocao_intensidades;
  } else if(typeof entry.emocao==='string'&&entry.emocao){
    const inten=(typeof entry.intensidade==='number'?entry.intensidade:Number(entry.intensidade||0))||0;
    pares=[{emocao:entry.emocao,intensidade:inten}];
  }
  const maxIntensidade=pares.length?Math.max(...pares.map(p=>Number(p.intensidade||0))):((typeof entry.intensidade==='number'?entry.intensidade:Number(entry.intensidade||0))||0);
  const badges=pares.length?pares.map(p=>{
    const inten=Number(p.intensidade||0);
    const cls=inten>=7?'text-bg-danger':(inten>=4?'text-bg-warning':'text-bg-info');
    return `<span class="badge ${cls} me-1">${escapeHtml(p.emocao)} (${inten})</span>`;
  }).join(''):`<span class="badge text-bg-info">${escapeHtml(entry.emocao||'—')}</span>`;
  const summaryBadgeClass=maxIntensidade>=7?'text-bg-danger':(maxIntensidade>=4?'text-bg-warning':'text-bg-success');
  latestDiaryContent.innerHTML=`<i class="bi bi-clock"></i> ${dateStr} às ${timeStr} <span class="ms-2 badge rounded-pill ${summaryBadgeClass}">Intensidade máx: ${maxIntensidade}</span><div class="mt-1"><span class="small text-muted">Emoções: </span>${badges}</div>`;
}