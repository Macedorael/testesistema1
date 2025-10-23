document.addEventListener('DOMContentLoaded', function () {
  const logoutBtn = document.getElementById('logoutBtn');
  const novoRegistroBtn = document.getElementById('novoRegistroBtn');
  const shortcutNovoRegistro = document.getElementById('shortcutNovoRegistro');
  let currentUser = null;

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
    loadDiarySummary();
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
                  <div class="col-md-6">
                    <label class="form-label">Emoção</label>
                    <input type="text" class="form-control" name="emocao" placeholder="Ex.: Tristeza, Raiva, Medo" required>
                    <div class="invalid-feedback">Informe a emoção principal.</div>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label">Intensidade Emocional (0-10)</label>
                    <div class="d-flex align-items-center gap-2">
                      <input type="range" class="form-range" name="intensidade" id="intensidadeRange" min="0" max="10" step="1" value="5">
                      <span class="badge text-bg-secondary" id="intensidadeValue">5</span>
                    </div>
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
      const rangeEl = formEl.querySelector('#intensidadeRange');
      const valueEl = formEl.querySelector('#intensidadeValue');
      if (rangeEl && valueEl) {
        rangeEl.addEventListener('input', () => { valueEl.textContent = rangeEl.value; });
      }

      formEl.addEventListener('submit', (ev) => {
        ev.preventDefault();
        ev.stopPropagation();
        if (!formEl.checkValidity()) {
          formEl.classList.add('was-validated');
          return;
        }

        const data = new FormData(formEl);
        const nowISO = new Date().toISOString();
        const payload = {
          situacao: data.get('situacao'),
          pensamento: data.get('pensamento'),
          emocao: data.get('emocao'),
          intensidade: Number(data.get('intensidade') || 0),
          comportamento: data.get('comportamento'),
          consequencia: data.get('consequencia') || '',
          data_registro: nowISO
        };

        fetch('/api/patients/me/diary-entries', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        })
          .then(async (res) => {
            if (!res.ok) {
              const err = await res.json().catch(() => ({ message: 'Erro desconhecido' }));
              throw new Error(err.message || `Falha ao salvar registro (${res.status})`);
            }
            return res.json();
          })
          .then((resp) => {
            registroModal.hide();
            alert('Registro salvo com sucesso!');
            formEl.reset();
            formEl.classList.remove('was-validated');
            if (valueEl && rangeEl) { valueEl.textContent = rangeEl.value; }
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
    let candidate = null; // {date, profissional}
    appointments.forEach(appt => {
      const sessions = Array.isArray(appt.sessions) ? appt.sessions : [];
      const futureSessionDates = sessions.map(s => new Date(s.data_sessao)).filter(d => !isNaN(d) && d > now);
      const nextSession = futureSessionDates.sort((a,b)=> a-b)[0];
      const apptBaseDate = appt.data_primeira_sessao ? new Date(appt.data_primeira_sessao) : null;
      const apptFutureDate = apptBaseDate && apptBaseDate > now ? apptBaseDate : null;
      const chosen = nextSession || apptFutureDate || null;
      if (chosen) { if (!candidate || chosen < candidate.date) { candidate = { date: chosen, profissional: appt.funcionario_nome || 'N/A' }; } }
    });
    if (!candidate) { targetEl.textContent = 'Nenhum próximo agendamento encontrado.'; return; }
    const dateStr = candidate.date.toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    const timeStr = candidate.date.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    targetEl.innerHTML = `<i class="bi bi-calendar-event"></i> ${dateStr} às ${timeStr} <span class="ms-2 badge rounded-pill text-bg-secondary">Profissional: ${escapeHtml(candidate.profissional)}</span>`;
  }

  function updateDashboardLatestDiaryLocal(targetEl, entry) {
    if (!targetEl || !entry) return;
    const createdISO = entry.data_registro || entry.created_at || entry.createdAt || entry.dataHora;
    const d = createdISO ? new Date(createdISO) : null;
    if (!d) { targetEl.textContent = 'Nenhum registro diário encontrado.'; return; }
    const dateStr = d.toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
    const timeStr = d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
    const intensidade = typeof entry.intensidade === 'number' ? entry.intensidade : Number(entry.intensidade || 0);
    const emocao = escapeHtml(entry.emocao || '—');
    targetEl.innerHTML = `<i class="bi bi-clock"></i> ${dateStr} às ${timeStr} <span class="ms-2 badge rounded-pill ${intensidade>=7?'text-bg-danger':(intensidade>=4?'text-bg-warning':'text-bg-success')}">Intensidade: ${intensidade}</span><div class="mt-1"><span class="small text-muted">Emoção: </span><span class="fw-normal">${emocao}</span></div>`;
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