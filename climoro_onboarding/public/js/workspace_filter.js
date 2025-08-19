(() => {
  const ROLE_TO_LABEL = {
    'Scope 1 Access': 'Scope 1',
    'Scope 2 Access': 'Scope 2',
    'Scope 3 Access': 'Scope 3',
    'Reduction Factor Access': 'Reduction Factor',
    'Scope 3 Upstream Access': 'Upstream',
    'Scope 3 Downstream Access': 'Downstream',
    'Scope 1 Stationary Access': 'Stationary Emissions',
    'Scope 1 Mobile Access': 'Mobile Combustion',
    'Scope 1 Fugitives Access': 'Fugitives',
    'Scope 1 Process Access': 'Process',
    'Reduction Energy Efficiency Access': 'Energy Efficiency',
    'Reduction Solar Access': 'Solar',
    'Reduction Process Optimization Access': 'Process Optimization',
    'Reduction Waste Manage Access': 'Waste Manage',
    'Reduction Transportation Access': 'Transportation-Upstream',
    'Reduction Methane Recovery Access': 'Methane Recovery'
  };

  function getAllowedLabels() {
    const roles = (window.frappe && frappe.user_roles) || [];
    const labels = new Set();
    roles.forEach(r => { const lbl = ROLE_TO_LABEL[r]; if (lbl) labels.add(lbl); });
    // Always allow Home; reduce exposure for non-admins
    labels.add('Climoro Dashboard');
    return labels;
  }

  function hideDisallowedSidebarItems() {
    try {
      const allowed = getAllowedLabels();
      const sidebar = document.querySelector('.sidebar-items') || document.querySelector('.standard-sidebar');
      if (!sidebar) return;
      const items = sidebar.querySelectorAll('[data-label], .sidebar-item, .link-item');
      items.forEach(el => {
        const text = (el.getAttribute('data-label') || el.textContent || '').trim();
        // keep parents visible if any child allowed; basic heuristic
        const isParent = /^(Scope 1|Scope 2|Scope 3|Reduction Factor)$/i.test(text);
        if (allowed.has(text) || isParent) return;
        // Hide if it matches managed labels list
        if (Object.values(ROLE_TO_LABEL).includes(text)) {
          el.style.display = 'none';
        }
      });
    } catch (e) { /* no-op */ }
  }

  function install() {
    hideDisallowedSidebarItems();
    document.addEventListener('app_ready', hideDisallowedSidebarItems);
    document.addEventListener('toolbar_setup', hideDisallowedSidebarItems);
    window.addEventListener('hashchange', () => setTimeout(hideDisallowedSidebarItems, 50));
  }

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', install); else install();
})();


