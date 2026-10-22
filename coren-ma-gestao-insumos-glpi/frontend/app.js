const API_BASE = window.INSUMOS_API_URL || 'http://localhost:8000/api';
const state = { items: [], search: '', category: '' };
const body = document.querySelector('#inventory-body');
const escapeHTML = (value = '') => String(value).replace(/[&<>"']/g, char => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[char]);

function setConnection(connected) {
  const status = document.querySelector('.api-status');
  status.classList.toggle('connected', connected);
  document.querySelector('#connection-status').textContent = connected ? 'API conectada' : 'API indisponível';
}
function visibleItems() {
  const query = state.search.trim().toLocaleLowerCase('pt-BR');
  return state.items.filter(item => (!state.category || item.categoria === state.category) && (!query || `${item.nome} ${item.categoria} ${item.localizacao}`.toLocaleLowerCase('pt-BR').includes(query)));
}
function render() {
  const items = visibleItems();
  body.innerHTML = items.length ? items.map(item => {
    const low = item.quantidade <= item.estoque_minimo;
    return `<tr><td><div class="item-name"><span class="item-icon">▤</span><span><strong>${escapeHTML(item.nome)}</strong><small>Código #${String(item.id).padStart(4, '0')}</small></span></div></td><td><span class="category-tag">${escapeHTML(item.categoria)}</span></td><td><span class="quantity">${item.quantidade}</span> ${escapeHTML(item.unidade)}</td><td>${escapeHTML(item.localizacao)}</td><td><span class="status ${low ? 'low' : 'ok'}">${low ? 'Estoque baixo' : 'Disponível'}</span></td><td><button class="row-actions" aria-label="Registrar movimentação" title="Registrar movimentação" data-move="${item.id}">↕</button></td></tr>`;
  }).join('') : '<tr><td colspan="6" class="empty-state">Nenhum insumo encontrado. Cadastre um novo item para começar.</td></tr>';
  document.querySelector('#total-items').textContent = state.items.length;
  document.querySelector('#low-items').textContent = state.items.filter(item => item.quantidade <= item.estoque_minimo).length;
  document.querySelector('#category-count').textContent = new Set(state.items.map(item => item.categoria)).size;
  document.querySelector('#location-count').textContent = new Set(state.items.map(item => item.localizacao)).size;
  document.querySelector('#nav-count').textContent = state.items.length;
  document.querySelector('#result-count').textContent = `${items.length} ${items.length === 1 ? 'insumo encontrado' : 'insumos encontrados'}`;
  const filter = document.querySelector('#category-filter');
  const selected = state.category;
  filter.innerHTML = '<option value="">Todas</option>' + [...new Set(state.items.map(item => item.categoria))].sort().map(category => `<option value="${escapeHTML(category)}">${escapeHTML(category)}</option>`).join('');
  filter.value = selected;
}
async function loadItems() {
  try {
    const response = await fetch(`${API_BASE}/insumos`);
    if (!response.ok) throw new Error('Não foi possível carregar os insumos.');
    state.items = await response.json();
    setConnection(true);
  } catch (error) {
    setConnection(false);
    body.innerHTML = '<tr><td colspan="6" class="empty-state">Não foi possível conectar à API. Verifique se o backend está em execução.</td></tr>';
    document.querySelector('#result-count').textContent = 'Sem conexão';
    return;
  }
  render();
}
function toast(message) {
  const element = document.querySelector('#toast');
  element.textContent = message;
  element.classList.add('show');
  window.setTimeout(() => element.classList.remove('show'), 2800);
}
function openModal() { document.querySelector('#modal-backdrop').hidden = false; document.querySelector('[name="nome"]').focus(); }
function closeModal() { document.querySelector('#modal-backdrop').hidden = true; document.querySelector('#form-error').textContent = ''; }
document.querySelector('#today').textContent = new Intl.DateTimeFormat('pt-BR', { day: '2-digit', month: 'short', year: 'numeric' }).format(new Date());
document.querySelector('#open-modal').addEventListener('click', openModal);
document.querySelector('#close-modal').addEventListener('click', closeModal);
document.querySelector('#cancel-modal').addEventListener('click', closeModal);
document.querySelector('#modal-backdrop').addEventListener('click', event => { if (event.target.id === 'modal-backdrop') closeModal(); });
document.querySelector('#search-input').addEventListener('input', event => { state.search = event.target.value; render(); });
document.querySelector('#category-filter').addEventListener('change', event => { state.category = event.target.value; render(); });
document.querySelector('#refresh-button').addEventListener('click', loadItems);
document.querySelector('#menu-toggle').addEventListener('click', () => document.querySelector('#sidebar').classList.toggle('open'));
document.querySelector('#insumo-form').addEventListener('submit', async event => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  const data = Object.fromEntries(form.entries());
  data.quantidade = Number(data.quantidade);
  data.estoque_minimo = Number(data.estoque_minimo);
  data.observacoes = data.observacoes || null;
  try {
    const response = await fetch(`${API_BASE}/insumos`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (!response.ok) {
      const result = await response.json();
      throw new Error(result.detail?.[0]?.msg || result.detail || 'Revise os campos e tente novamente.');
    }
    event.currentTarget.reset();
    closeModal();
    await loadItems();
    toast('Insumo cadastrado com sucesso.');
  } catch (error) {
    document.querySelector('#form-error').textContent = error.message.includes('fetch') ? 'Não foi possível conectar à API. Tente novamente.' : error.message;
  }
});
body.addEventListener('click', async event => {
  const button = event.target.closest('[data-move]');
  if (!button) return;
  const item = state.items.find(candidate => candidate.id === Number(button.dataset.move));
  const kind = window.prompt(`Movimentação de ${item.nome}: digite entrada ou saida`);
  if (!kind) return;
  if (!['entrada', 'saida'].includes(kind.toLocaleLowerCase('pt-BR'))) return toast('Tipo inválido. Use entrada ou saida.');
  const amount = Number(window.prompt('Quantidade da movimentação:'));
  if (!Number.isInteger(amount) || amount <= 0) return toast('Informe uma quantidade inteira maior que zero.');
  try {
    const response = await fetch(`${API_BASE}/insumos/${item.id}/movimentacoes`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ tipo: kind.toLocaleLowerCase('pt-BR'), quantidade: amount }) });
    if (!response.ok) { const result = await response.json(); throw new Error(result.detail || 'Não foi possível registrar.'); }
    await loadItems();
    toast('Movimentação registrada.');
  } catch (error) { toast(error.message); }
});
document.querySelector('#export-button').addEventListener('click', () => {
  const rows = [['ID', 'Nome', 'Categoria', 'Quantidade', 'Unidade', 'Mínimo', 'Localização'], ...state.items.map(item => [item.id, item.nome, item.categoria, item.quantidade, item.unidade, item.estoque_minimo, item.localizacao])];
  const csv = '\ufeff' + rows.map(row => row.map(value => `"${String(value).replaceAll('"', '""')}"`).join(';')).join('\n');
  const link = document.createElement('a');
  link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8;' }));
  link.download = 'insumos-coren-ma.csv';
  link.click();
  URL.revokeObjectURL(link.href);
});
loadItems();
