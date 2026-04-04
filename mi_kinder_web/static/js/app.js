/**
 * Mi Kinder Web - App JavaScript
 * Colegio CAPI - Centro de Atencion Psicopedagogica Infantil
 */

(function() {
  'use strict';

  // ==========================================================
  // Sidebar Toggle (mobile)
  // ==========================================================
  var sidebar = document.getElementById('sidebar');
  var toggleBtn = document.getElementById('sidebarToggle');
  var overlay = document.getElementById('sidebarOverlay');

  function openSidebar() {
    if (sidebar) sidebar.classList.add('open');
    if (overlay) overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeSidebar() {
    if (sidebar) sidebar.classList.remove('open');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
  }

  if (toggleBtn) {
    toggleBtn.addEventListener('click', function() {
      if (sidebar && sidebar.classList.contains('open')) {
        closeSidebar();
      } else {
        openSidebar();
      }
    });
  }

  if (overlay) {
    overlay.addEventListener('click', closeSidebar);
  }

  // Close sidebar on ESC
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      closeSidebar();
    }
  });

  // Close sidebar on nav link click (mobile)
  if (sidebar) {
    var navLinks = sidebar.querySelectorAll('.nav-item');
    navLinks.forEach(function(link) {
      link.addEventListener('click', function() {
        if (window.innerWidth <= 1024) {
          closeSidebar();
        }
      });
    });
  }

  // ==========================================================
  // Auto-dismiss flash messages
  // ==========================================================
  var alerts = document.querySelectorAll('.alert');
  alerts.forEach(function(alert) {
    setTimeout(function() {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      alert.style.transition = 'opacity 0.3s, transform 0.3s';
      setTimeout(function() {
        if (alert.parentElement) {
          alert.remove();
        }
      }, 300);
    }, 6000);
  });

  // ==========================================================
  // Confirm dialogs for dangerous actions
  // ==========================================================
  document.querySelectorAll('[data-confirm]').forEach(function(el) {
    el.addEventListener('click', function(e) {
      if (!confirm(el.getAttribute('data-confirm'))) {
        e.preventDefault();
      }
    });
  });

  // ==========================================================
  // CURP auto-uppercase
  // ==========================================================
  var curpInput = document.getElementById('curp');
  if (curpInput) {
    curpInput.addEventListener('input', function() {
      this.value = this.value.toUpperCase();
    });
  }

  // ==========================================================
  // Smooth transitions for page loads
  // ==========================================================
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.2s ease-out';
  window.addEventListener('load', function() {
    document.body.style.opacity = '1';
  });
  // Fallback in case load already fired
  if (document.readyState === 'complete') {
    document.body.style.opacity = '1';
  }

  // ==========================================================
  // Table row click-to-navigate
  // ==========================================================
  document.querySelectorAll('.table tbody tr').forEach(function(row) {
    var link = row.querySelector('a.link-primary');
    if (link) {
      row.style.cursor = 'pointer';
      row.addEventListener('click', function(e) {
        // Don't navigate if clicking a button or link
        if (e.target.closest('a, button, input, select')) return;
        window.location.href = link.href;
      });
    }
  });

  // ==========================================================
  // Keyboard shortcut: focus search
  // ==========================================================
  document.addEventListener('keydown', function(e) {
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
      e.preventDefault();
      var searchInput = document.getElementById('q');
      if (searchInput) {
        searchInput.focus();
        searchInput.select();
      }
    }
  });

})();
