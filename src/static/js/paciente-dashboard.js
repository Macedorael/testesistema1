document.addEventListener('DOMContentLoaded', function () {
  const logoutBtn = document.getElementById('logoutBtn');
  const novoRegistroBtn = document.getElementById('novoRegistroBtn');
  const shortcutNovoRegistro = document.getElementById('shortcutNovoRegistro');
  let currentUser = null;

  // Ocultar permanentemente os botões do Diário na navbar
  const diaryNavLinkAlways = document.querySelector('a.nav-link[href="paciente-diarios.html"]');
  if (diaryNavLinkAlways) { diaryNavLinkAlways.style.display = 'none'; }
  if (novoRegistroBtn) { novoRegistroBtn.style.display = 'none'; }
  if (shortcutNovoRegistro) { shortcutNovoRegistro.style.display = 'none'; }

  if (logoutBtn) {
    logoutBtn.addEventListener('click', function (e) {
      e.preventDefault();
      fetch('/api/logout', { method: 'POST', headers: { 'Content-Type': 'application/json' } })
        .then(r => r.json())
        .then(() => { window.location.href = '/inicial.html'; })
        .catch((error) => { console.error('Erro ao fazer logout:', error); window.location.href = '/inicial.html'; });
    });
  }

  if (novoRegistroBtn) {
    novoRegistroBtn.addEventListener('click', (e) => { e.preventDefault(); openDiaryModal(); });
  }
  if (shortcutNovoRegistro) {
    shortcutNovoRegistro.addEventListener('click', (e) => { e.preventDefault(); openDiaryModal(); });
  }

  checkUserAuthentication().then(() => {
    loadAppointmentsSummary();
    checkDiaryAvailability().then((enabled) => {
      if (enabled) {
        loadDiarySummary();
      } else {
        const latestDiaryContent = document.getElementById('latestDiaryContent');
        if (latestDiaryContent) {
          const card = latestDiaryContent.closest('.card');
          if (card) { card.style.display = 'none'; }
        }
      }
    });
  });

  async function checkUserAuthentication() {
    try {
      const response = await fetch('/api/me');
      if (!response.ok) {
        window.location.href = '/entrar.html';
        throw new Error('Usuário não autenticado');
      }
      const userData = await response.json();
      currentUser = userData;
      if (userData.role !== 'patient') {
        window.location.href = '/';
        throw new Error('Acesso não autorizado');
      }
      if (userData.first_login) {
        window.location.href = '/paciente-primeiro-login.html';
        throw new Error('Primeiro login - necessário alterar senha');
      }
    } catch (error) {
      console.error('Erro ao verificar usuário:', error);
    }
  }

  async function checkDiaryAvailability() {
    try {
      const response = await fetch('/api/patients/me');
      if (!response.ok) { return false; }
      const payload = await response.json();
      const patient = (payload && typeof payload === 'object' && 'data' in payload) ? payload.data : payload;
      const enabled = !!(patient && patient.diario_tcc_ativo);
      if (!enabled) {
        if (novoRegistroBtn) { novoRegistroBtn.style.display = 'none'; }
        if (shortcutNovoRegistro) { shortcutNovoRegistro.style.display = 'none'; }
        const diaryNavLink = document.querySelector('a.nav-link[href="paciente-diarios.html"]');
        if (diaryNavLink) { diaryNavLink.style.display = 'none'; }
      }
      return enabled;
    } catch (_) {
      return false;
    }
  }

  function openDiaryModal() {
    const modalHtml = `
      <div class="modal fade" id="registroDiarioModal" tabindex="-1" aria-labelledby="registroDiarioModalLabel" aria-hidden="true">
        <div class="modal-dialog modal-lg modal-dialog-centered">
          <div class="modal-content">
            <form id="registroForm" novalidate>
              <div class="modal-header">
                <h5 class="modal-title" id="registroDiarioModalLabel"><i class="bi bi-journal-plus me-2"></i>Novo Registro Diário</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
              </div>
              <div class="modal-body">
                <div class="row g-3">
                  <div class="col-12">
                    <label class="form-label">Situação</label>
                    <textarea class="form-control" name="situacao" rows="2" required></textarea>
                    <div class="invalid-feedback">Descreva a situação.</div>
                  </div>
                  <div class="col-12">
                    <label class="form-label">Pensamento</label>
                    <textarea class="form-control" name="pensamento" rows="2" required></textarea>
                    <div class="invalid-feedback">Descreva o pensamento.</div>
                  </div>
                  <div class="col-12">
                    <label class="form-label">Emoções e Intensidades</label>
                    <div id="emocoesContainer"></div>
                    <button type="button" class="btn btn-sm btn-outline-primary mt-2" id="addEmocaoBtn"><i class="bi bi-plus-circle"></i> Adicionar emoção</button>
                    <div class="form-text">Adicione uma ou mais emoções com intensidade (0-10).</div>
                  </div>

                  <div class="col-12">
                    <label class="form-label">Comportamento</label>
                    <textarea class="form-control" name="comportamento" rows="2" required></textarea>
                    <div class="invalid-feedback">Descreva o comportamento.</div>
                  </div>
                  <div class="col-12">
                    <label class="form-label">Consequência</label>
                    <textarea class="form-control" name="consequencia" rows="2" placeholder="O que aconteceu depois?" required></textarea>
                    <div class="invalid-feedback">Informe a consequência.</div>
                  </div>
                </div>
              </div>
              <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancelar</button>
                <button type="submit" class="btn btn-primary">Salvar</button>
              </div>
            </form>
          </div>
        </div>
      </div>`;

    if (!document.getElementById('registroDiarioModal')) {
      document.body.insertAdjacentHTML('beforeend', modalHtml);
    }

    const modalEl = document.getElementById('registroDiarioModal');
    const registroModal = new bootstrap.Modal(modalEl);
    const formEl = modalEl.querySelector('#registroForm');

    if (formEl && !formEl.dataset.bound) {
      formEl.dataset.bound = 'true';
      const oldFormEl = formEl;
      const newFormEl = oldFormEl.cloneNode(true);
      oldFormEl.parentNode.replaceChild(newFormEl, oldFormEl);
      const emocoesContainer = newFormEl.querySelector('#emocoesContainer');
      const addEmocaoBtn = newFormEl.querySelector('#addEmocaoBtn');
      const createEmocaoRow = (defaults = { emocao: '', intensidade: 5 }) => {
        const row = document.createElement('div');
        row.className = 'emocao-row row gx-2 align-items-center mb-2';
        row.innerHTML = `
          <div class="col-md-4">
            <select class="form-select emocao-select">
              <option value="">Selecione...</option>
              <option value="Alegria">Alegria</option>
              <option value="Tristeza">Tristeza</option>
              <option value="Raiva">Raiva</option>
              <option value="Medo">Medo</option>
              <option value="Ansiedade">Ansiedade</option>
              <option value="Nojo">Nojo</option>
              <option value="Surpresa">Surpresa</option>
              <option value="Calma">Calma</option>
              <option value="OUTRAS">Outras</option>
            </select>
          </div>
          <div class="col-md-3 d-none emocao-custom-wrapper">
            <input type="text" class="form-control emocao-custom" placeholder="Descreva a emoção">
          </div>
          <div class="col-md-4">
            <div class="d-flex align-items-center gap-2">
              <input type="range" class="form-range intensidade-range" min="0" max="10" step="1" value="${defaults.intensidade}">
              <span class="badge text-bg-secondary intensidade-value">${defaults.intensidade}</span>
            </div>
          </div>
          <div class="col-md-1 text-end">
            <button type="button" class="btn btn-outline-danger btn-sm remove-emocao" title="Remover"><i class="bi bi-trash"></i></button>
          </div>`;
        const selectEl = row.querySelector('.emocao-select');
        const customWrapper = row.querySelector('.emocao-custom-wrapper');
        const customInput = row.querySelector('.emocao-custom');
        const rangeEl = row.querySelector('.intensidade-range');
        const valueEl = row.querySelector('.intensidade-value');
        const removeBtn = row.querySelector('.remove-emocao');
        const toggleCustom = () => {
          if (selectEl.value === 'OUTRAS') { customWrapper.classList.remove('d-none'); }
          else { customWrapper.classList.add('d-none'); customInput.value = ''; }
        };
        selectEl.addEventListener('change', toggleCustom); toggleCustom();
        rangeEl.addEventListener('input', () => { valueEl.textContent = rangeEl.value; });
        removeBtn.addEventListener('click', () => { row.remove(); });
        return row;
      };
      if (emocoesContainer) { emocoesContainer.appendChild(createEmocaoRow()); }
      if (addEmocaoBtn) { addEmocaoBtn.addEventListener('click', () => { emocoesContainer.appendChild(createEmocaoRow()); }); }
      newFormEl.addEventListener('submit', (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        if (!newFormEl.checkValidity()) {
          newFormEl.classList.add('was-validated');
          return;
        }
        const rows = Array.from(newFormEl.querySelectorAll('.emocao-row'));
        if (rows.length === 0) { alert('Adicione pelo menos uma emoção.'); return; }
        const invalidRow = rows.find(r => {
          const s = r.querySelector('.emocao-select');
          const c = r.querySelector('.emocao-custom');
          return !s.value || (s.value === 'OUTRAS' && !c.value.trim());
        });
        if (invalidRow) { alert('Preencha todas as emoções e intensidades.'); return; }
        const nowISO = new Date().toISOString();
        const pares = rows.map(r => {
          const s = r.querySelector('.emocao-select');
          const c = r.querySelector('.emocao-custom');
          const range = r.querySelector('.intensidade-range');
          const emocao = s.value === 'OUTRAS' ? c.value.trim() : s.value;
          return { emocao, intensidade: Number(range.value) };
        }).filter(p => p.emocao);
        const primeira = pares[0] || { emocao: '', intensidade: 0 };
        const payload = {
          situacao: newFormEl.querySelector('[name="situacao"]').value,
          pensamento: newFormEl.querySelector('[name="pensamento"]').value,
          emocao: primeira.emocao || '',
          intensidade: primeira.intensidade || 0,
          emocao_intensidades: pares,
          comportamento: newFormEl.querySelector('[name="comportamento"]').value,
          consequencia: newFormEl.querySelector('[name="consequencia"]').value || '',
          data_registro: nowISO
        };
        fetch('/api/patients/me/diary-entries', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
          .then(async (res) => {
            if (!res.ok) {
              const err = await res.json().catch(() => ({ message: 'Erro desconhecido' }));
              throw new Error(err.message || `Falha ao salvar registro (${res.status})`);
            }
            return res.json();
          })
          .then(() => {
            registroModal.hide();
            alert('Registro salvo com sucesso!');
            newFormEl.reset();
            newFormEl.classList.remove('was-validated');
            if (emocoesContainer) { emocoesContainer.innerHTML = ''; emocoesContainer.appendChild(createEmocaoRow()); }
            loadDiarySummary();
          })
          .catch((error) => {
            console.error('Erro ao salvar registro diário:', error);
            registroModal.hide();
            alert('Não foi possível salvar no servidor. Tente novamente.');
          });
      });
    }

    registroModal.show();
  }

  function loadAppointmentsSummary() {
    const nextAppointmentContent = document.getElementById('nextAppointmentContent');
    const spinner = document.getElementById('dashboardLoadingSpinnerAppointments');
    if (spinner) { spinner.classList.remove('d-none'); spinner.classList.add('d-flex'); }
    if (nextAppointmentContent) { nextAppointmentContent.textContent = 'Carregando próximo agendamento...'; }

    fetch('/api/patients/me/appointments')
      .then((response) => {
        if (!response.ok) { throw new Error('Falha ao buscar agendamentos'); }
        return response.json();
      })
      .then((payload) => {
        const appointments = Array.isArray(payload) ? payload : (payload && typeof payload === 'object' && 'data' in payload ? payload.data : []);
        if (spinner) { spinner.classList.remove('d-flex'); spinner.classList.add('d-none'); }
        if (!appointments || appointments.length === 0) {
          if (nextAppointmentContent) { nextAppointmentContent.textContent = 'Nenhum próximo agendamento encontrado.'; }
          return;
        }
        appointments.sort((a,b)=> new Date(b.data_primeira_sessao) - new Date(a.data_primeira_sessao));
        try { updateDashboardNextAppointmentLocal(nextAppointmentContent, appointments); } catch (e) { console.error('Erro ao atualizar resumo de agendamentos:', e); }
      })
      .catch((error) => {
        if (spinner) { spinner.classList.remove('d-flex'); spinner.classList.add('d-none'); }
        if (nextAppointmentContent) { nextAppointmentContent.textContent = `Erro ao carregar próximo agendamento: ${error.message || 'Erro desconhecido'}`; }
        console.error('Erro ao carregar agendamentos:', error);
      });
  }

  function loadDiarySummary() {
    const latestDiaryContent = document.getElementById('latestDiaryContent');
    const spinner = document.getElementById('dashboardLoadingSpinnerDiary');
    if (spinner) { spinner.classList.remove('d-none'); spinner.classList.add('d-flex'); }
    if (latestDiaryContent) { latestDiaryContent.textContent = 'Carregando último registro diário...'; }

    fetch('/api/patients/me/diary-entries')
      .then((response) => {
        if (!response.ok) { throw new Error('Falha ao buscar registros diários'); }
        return response.json();
      })
      .then((payload) => {
        const entries = Array.isArray(payload) ? payload : (payload && typeof payload === 'object' && 'data' in payload ? payload.data : []);
        if (spinner) { spinner.classList.remove('d-flex'); spinner.classList.add('d-none'); }
        if (!entries || entries.length === 0) {
          if (latestDiaryContent) { latestDiaryContent.textContent = 'Nenhum registro diário encontrado.'; }
          return;
        }
        entries.sort((a,b)=> new Date(b.data_registro || b.created_at) - new Date(a.data_registro || a.created_at));
        try { updateDashboardLatestDiaryLocal(latestDiaryContent, entries[0]); } catch (e) { console.error('Erro ao atualizar resumo do diário:', e); }
      })
      .catch((error) => {
        if (spinner) { spinner.classList.remove('d-flex'); spinner.classList.add('d-none'); }
        if (latestDiaryContent) { latestDiaryContent.textContent = `Erro ao carregar último registro diário: ${error.message || 'Erro desconhecido'}`; }
        console.error('Erro ao carregar registros diários:', error);
      });
  }

  function updateDashboardNextAppointmentLocal(targetEl, appointments) {
    if (!targetEl) return;
    const now = new Date();
    let candidate = null; // {date, especialidade, profissional}
    appointments.forEach(appt => {
      const sessions = Array.isArray(appt.sessions) ? appt.sessions : [];
      const futureSessionDates = sessions.map(s => new Date(s.data_sessao)).filter(d => !isNaN(d) && d > now);
      const nextSession = futureSessionDates.sort((a,b)=> a-b)[0];
      const apptBaseDate = appt.data_primeira_sessao ? new Date(appt.data_primeira_sessao) : null;
      const apptFutureDate = apptBaseDate && apptBaseDate > now ? apptBaseDate : null;
      const chosen = nextSession || apptFutureDate || null;
      if (chosen) {
        if (!candidate || chosen < candidate.date) {
          candidate = { date: chosen, especialidade: appt.especialidade_nome || 'N/A', profissional: appt.funcionario_nome || 'N/A' };
        }
      }
    });
    if (!candidate) { targetEl.textContent = 'Nenhum próximo agendamento encontrado.'; return; }
    const dateStr = candidate.date.toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    const timeStr = candidate.date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    targetEl.innerHTML = `<i class=\"bi bi-calendar-event\"></i> ${dateStr} às ${timeStr} <span class=\"ms-2 fw-bold\">${escapeHtml(candidate.especialidade)} ${escapeHtml(candidate.profissional)}</span>`;
  }

  function updateDashboardLatestDiaryLocal(targetEl, entry) {
    if (!targetEl || !entry) return;
    const createdISO = entry.data_registro || entry.created_at || entry.createdAt || entry.dataHora;
    const d = createdISO ? new Date(createdISO) : null;
    if (!d) { targetEl.textContent = 'Nenhum registro diário encontrado.'; return; }
    const dateStr = d.toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    const timeStr = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    const parsePairs = (val) => {
      if (Array.isArray(val)) return val;
      if (!val) return [];
      try { return JSON.parse(val); } catch (_) { return []; }
    };
    const pairs = parsePairs(entry.emocao_intensidades);
    const legacyInt = typeof entry.intensidade === 'number' ? entry.intensidade : Number(entry.intensidade || 0);
    const maxInt = pairs.length ? Math.max(...pairs.map(p => Number(p.intensidade || 0))) : legacyInt;
    const badges = pairs.length
      ? pairs.map(p => {
          const inten = Number(p.intensidade || 0);
          const cls = inten >= 7 ? 'text-bg-danger' : (inten >= 4 ? 'text-bg-warning' : 'text-bg-info');
          return `<span class="badge ${cls} me-1">${escapeHtml(p.emocao)} (${inten})</span>`;
        }).join('')
      : `<span class="badge text-bg-info">${escapeHtml(entry.emocao || '—')}</span>`;
    const summaryCls = maxInt >= 7 ? 'text-bg-danger' : (maxInt >= 4 ? 'text-bg-warning' : 'text-bg-success');
    targetEl.innerHTML = `<i class="bi bi-clock"></i> ${dateStr} às ${timeStr} <span class="ms-2 badge rounded-pill ${summaryCls}">Intensidade máx: ${maxInt}</span><div class="mt-1"><span class="small text-muted">Emoções: </span>${badges}</div>`;
  }

  function escapeHtml(text) {
    if (text == null) return '';
    return String(text)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }
});