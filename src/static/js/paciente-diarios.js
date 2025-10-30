document.addEventListener('DOMContentLoaded', function () {
  const logoutBtn = document.getElementById('logoutBtn');
  const novoRegistroBtn = document.getElementById('novoRegistroBtn');
  let currentUser = null;

  // Ocultar permanentemente os botões do Diário na navbar
  const diaryNavLinkAlways = document.querySelector('a.nav-link[href="paciente-diarios.html"]');
  if (diaryNavLinkAlways) { diaryNavLinkAlways.style.display = 'none'; }
  if (novoRegistroBtn) { novoRegistroBtn.style.display = 'none'; }

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
    checkDiaryAvailability().then((enabled) => {
      if (enabled) {
        loadDiaryEntries();
      } else {
        if (novoRegistroBtn) { novoRegistroBtn.style.display = 'none'; }
        const diaryNavLink = document.querySelector('a.nav-link[href="paciente-diarios.html"]');
        if (diaryNavLink) { diaryNavLink.style.display = 'none'; }
        const spinnerEl = document.getElementById('diaryLoadingSpinner');
        if (spinnerEl) { spinnerEl.style.display = 'none'; }
        const noDiaryEl = document.getElementById('noDiaryEntries');
        if (noDiaryEl) { noDiaryEl.style.display = 'none'; }
        const diaryListEl = document.getElementById('diaryList');
        if (diaryListEl) { diaryListEl.style.display = 'none'; }
        const headerEl = document.querySelector('main h1');
        if (headerEl) { headerEl.style.display = 'none'; }
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
      return !!(patient && patient.diario_tcc_ativo);
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
                    <button type="button" class="btn btn-sm btn-outline-primary mt-2" id="addEmocaoBtn">
                      <i class="bi bi-plus-circle"></i> Adicionar emoção
                    </button>
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

      const emocoesContainer = formEl.querySelector('#emocoesContainer');
      const addEmocaoBtn = formEl.querySelector('#addEmocaoBtn');

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
          </div>
        `;

        const selectEl = row.querySelector('.emocao-select');
        const customWrapper = row.querySelector('.emocao-custom-wrapper');
        const customInput = row.querySelector('.emocao-custom');
        const rangeEl = row.querySelector('.intensidade-range');
        const valueEl = row.querySelector('.intensidade-value');
        const removeBtn = row.querySelector('.remove-emocao');

        // Inicializar valores
        if (defaults.emocao) {
          selectEl.value = defaults.emocao;
        }
        const toggleCustom = () => {
          if (selectEl.value === 'OUTRAS') {
            customWrapper.classList.remove('d-none');
          } else {
            customWrapper.classList.add('d-none');
            customInput.value = '';
          }
        };
        selectEl.addEventListener('change', toggleCustom);
        toggleCustom();

        rangeEl.addEventListener('input', () => { valueEl.textContent = rangeEl.value; });
        removeBtn.addEventListener('click', () => { row.remove(); });

        return row;
      };

      // Adicionar primeira linha automaticamente
      emocoesContainer.appendChild(createEmocaoRow());
      addEmocaoBtn.addEventListener('click', () => {
        emocoesContainer.appendChild(createEmocaoRow());
      });

      formEl.addEventListener('submit', (ev) => {
        ev.preventDefault();
        ev.stopPropagation();

        // Validação do formulário base
        if (!formEl.checkValidity()) {
          formEl.classList.add('was-validated');
          return;
        }

        // Coletar pares de emoção+intensidade
        const rows = Array.from(formEl.querySelectorAll('.emocao-row'));
        const pairs = [];
        for (const row of rows) {
          const selectEl = row.querySelector('.emocao-select');
          const customInput = row.querySelector('.emocao-custom');
          const rangeEl = row.querySelector('.intensidade-range');
          const emocaoSelecionada = selectEl.value;
          const emocaoCustom = (customInput?.value || '').trim();
          const emocaoFinal = emocaoSelecionada === 'OUTRAS' ? emocaoCustom : emocaoSelecionada;
          if (!emocaoFinal) continue; // permitir linhas vazias serem ignoradas
          pairs.push({ emocao: emocaoFinal, intensidade: Number(rangeEl.value || 0) });
        }

        if (pairs.length === 0) {
          alert('Adicione pelo menos uma emoção com intensidade.');
          return;
        }

        const data = new FormData(formEl);
        const nowISO = new Date().toISOString();
        const payload = {
          situacao: data.get('situacao'),
          pensamento: data.get('pensamento'),
          emocao_intensidades: pairs,
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
            // Resetar container de emoções
            emocoesContainer.innerHTML = '';
            emocoesContainer.appendChild(createEmocaoRow());
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

    const parsePairs = (val) => {
      if (Array.isArray(val)) return val;
      if (!val) return [];
      try { return JSON.parse(val); } catch (_) { return []; }
    };
    const pairs = parsePairs(entry.emocao_intensidades);
    const legacyInt = typeof entry.intensidade === 'number' ? entry.intensidade : Number(entry.intensidade || 0);
    const intensidadeMax = pairs.length ? Math.max(...pairs.map(p => Number(p.intensidade || 0))) : legacyInt;
    const badgeClassFor = (v) => { const i = Number(v || 0); return i >= 7 ? 'text-bg-danger' : (i >= 4 ? 'text-bg-warning' : 'text-bg-success'); };
    const headerBadgeClass = badgeClassFor(intensidadeMax);

    const card = document.createElement('div');
    card.className = 'card shadow-sm mb-3';
    card.innerHTML = `
      <div class="card-body py-3">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <div class="fw-normal">${formattedDate}</div>
            <div class="text-muted"><i class="bi bi-clock"></i> ${formattedTime}</div>
          </div>
          <span class="badge rounded-pill ${headerBadgeClass}">Intensidade máx: ${intensidadeMax}</span>
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
          <div class="col-12">
            <div class="small text-muted">Emoções</div>
            <div class="fw-normal d-flex flex-wrap gap-2">
              ${pairs.length ? pairs.map(p => `<span class="badge rounded-pill ${badgeClassFor(p.intensidade)}">${escapeHtml(p.emocao)}: ${p.intensidade}</span>`).join('') : (escapeHtml(entry.emocao) || '—')}
            </div>
          </div>
          <div class="col-12">
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