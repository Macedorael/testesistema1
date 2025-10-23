document.addEventListener('DOMContentLoaded', function () {
  const logoutBtn = document.getElementById('logoutBtn');
  const novoRegistroBtn = document.getElementById('novoRegistroBtn');
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
    novoRegistroBtn.addEventListener('click', (e) => {
      e.preventDefault();
      openDiaryModal();
    });
  }

  checkUserAuthentication().then(() => {
    loadDiaryEntries();
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
            loadDiaryEntries();
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

  function loadDiaryEntries() {
    const diaryListEl = document.getElementById('diaryList');
    const diaryLoadingSpinnerEl = document.getElementById('diaryLoadingSpinner');
    const noDiaryEntriesEl = document.getElementById('noDiaryEntries');

    if (!diaryListEl || !diaryLoadingSpinnerEl || !noDiaryEntriesEl) return;

    diaryLoadingSpinnerEl.classList.remove('d-none');
    diaryLoadingSpinnerEl.classList.add('d-flex');
    diaryListEl.innerHTML = '';
    noDiaryEntriesEl.style.display = 'none';

    fetch('/api/patients/me/diary-entries')
      .then((response) => {
        if (!response.ok) {
          throw new Error('Falha ao buscar registros diários');
        }
        return response.json();
      })
      .then((payload) => {
        const entries = (Array.isArray(payload) ? payload : (payload && typeof payload === 'object' && 'data' in payload ? payload.data : []));
        diaryLoadingSpinnerEl.classList.remove('d-flex');
        diaryLoadingSpinnerEl.classList.add('d-none');
        if (!entries || !Array.isArray(entries) || entries.length === 0) {
          noDiaryEntriesEl.style.display = 'block';
          return;
        }
        entries.sort((a, b) => new Date(b.data_registro || b.created_at) - new Date(a.data_registro || a.created_at));
        entries.forEach((entry) => renderDiaryEntry(entry));
      })
      .catch((error) => {
        diaryLoadingSpinnerEl.classList.remove('d-flex');
        diaryLoadingSpinnerEl.classList.add('d-none');
        diaryListEl.innerHTML = `<div class="alert alert-danger" role="alert">Erro ao carregar registros diários: ${error.message || 'Erro desconhecido'}</div>`;
        console.error('Erro ao carregar registros diários:', error);
      });
  }

  function renderDiaryEntry(entry) {
    const diaryListEl = document.getElementById('diaryList');
    if (!diaryListEl) return;
    const createdISO = entry.data_registro || entry.created_at || entry.createdAt || entry.dataHora;
    const d = createdISO ? new Date(createdISO) : null;
    const formattedDate = d ? d.toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) : 'Data não informada';
    const formattedTime = d ? d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' }) : '';
    const intensidade = typeof entry.intensidade === 'number' ? entry.intensidade : Number(entry.intensidade || 0);
    const badgeClass = intensidade >= 7 ? 'text-bg-danger' : (intensidade >= 4 ? 'text-bg-warning' : 'text-bg-success');
    const card = document.createElement('div');
    card.className = 'card shadow-sm mb-3';
    card.innerHTML = `
      <div class="card-body py-3">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <div class="fw-normal">${formattedDate}</div>
            <div class="text-muted"><i class="bi bi-clock"></i> ${formattedTime}</div>
          </div>
          <span class="badge rounded-pill ${badgeClass}">Intensidade: ${intensidade}</span>
        </div>
        <div class="row gy-2 mt-2">
          <div class="col-12">
            <div class="small text-muted">Situação</div>
            <div class="fw-normal">${escapeHtml(entry.situacao) || '—'}</div>
          </div>
          <div class="col-12">
            <div class="small text-muted">Pensamento</div>
            <div class="fw-normal">${escapeHtml(entry.pensamento) || '—'}</div>
          </div>
          <div class="col-md-6">
            <div class="small text-muted">Emoção</div>
            <div class="fw-normal">${escapeHtml(entry.emocao) || '—'}</div>
          </div>
          <div class="col-md-6">
            <div class="small text-muted">Comportamento</div>
            <div class="fw-normal">${escapeHtml(entry.comportamento) || '—'}</div>
          </div>
          ${entry.consequencia ? `<div class="col-12"><div class="small text-muted">Consequência</div><div class="fw-normal">${escapeHtml(entry.consequencia)}</div></div>` : ''}
        </div>
      </div>
    `;
    diaryListEl.appendChild(card);
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