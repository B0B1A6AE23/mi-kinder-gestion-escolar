/**
 * Mi Kinder Web v2.0 — App JavaScript
 * Colegio CAPI — Centro de Atencion Psicopedagogica Infantil
 *
 * Features:
 *  - Sidebar toggle (mobile)
 *  - Auto-dismiss flash messages
 *  - Scroll-triggered animations (IntersectionObserver)
 *  - Stat counter animation
 *  - Smooth page transitions
 *  - Table row click-to-navigate
 *  - Keyboard shortcuts
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
    if (e.key === 'Escape') closeSidebar();
  });

  // Close sidebar on nav link click (mobile)
  if (sidebar) {
    sidebar.querySelectorAll('.nav-item').forEach(function(link) {
      link.addEventListener('click', function() {
        if (window.innerWidth <= 1024) closeSidebar();
      });
    });
  }

  // ==========================================================
  // Auto-dismiss flash messages
  // ==========================================================
  document.querySelectorAll('.alert').forEach(function(alert) {
    setTimeout(function() {
      alert.style.opacity = '0';
      alert.style.transform = 'translateY(-10px)';
      alert.style.transition = 'opacity 0.3s, transform 0.3s';
      setTimeout(function() {
        if (alert.parentElement) alert.remove();
      }, 300);
    }, 6000);
  });

  // ==========================================================
  // Scroll-triggered reveal animations
  // ==========================================================
  if ('IntersectionObserver' in window) {
    // Animate cards, stat-cards, and other elements on scroll
    var revealElements = document.querySelectorAll(
      '.card, .stat-card, .quick-action-btn, .birthday-item, .report-group-item'
    );

    var staggerIndex = 0;

    var revealObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          // Add staggered delay for grouped items
          var delay = (staggerIndex % 6) * 60;
          staggerIndex++;

          el.style.transitionDelay = delay + 'ms';
          el.classList.add('is-revealed');
          revealObserver.unobserve(el);
        }
      });
    }, {
      threshold: 0.05,
      rootMargin: '0px 0px -30px 0px'
    });

    revealElements.forEach(function(el) {
      // Set initial state
      el.style.opacity = '0';
      el.style.transform = 'translateY(16px)';
      el.style.transition = 'opacity 0.5s cubic-bezier(0.16, 1, 0.3, 1), transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)';
      revealObserver.observe(el);
    });

    // CSS class for revealed state
    var style = document.createElement('style');
    style.textContent = '.is-revealed { opacity: 1 !important; transform: translateY(0) !important; }';
    document.head.appendChild(style);
  }

  // ==========================================================
  // Stat counter animation
  // ==========================================================
  function animateCounter(el, target, duration) {
    if (isNaN(target)) return;

    var isPercent = el.textContent.includes('%');
    var isDecimal = target % 1 !== 0;
    var start = 0;
    var startTime = null;

    function step(timestamp) {
      if (!startTime) startTime = timestamp;
      var progress = Math.min((timestamp - startTime) / duration, 1);
      // Ease out cubic
      var eased = 1 - Math.pow(1 - progress, 3);
      var current = start + (target - start) * eased;

      if (isDecimal) {
        el.textContent = current.toFixed(1) + (isPercent ? '%' : '');
      } else {
        el.textContent = Math.floor(current) + (isPercent ? '%' : '');
      }

      if (progress < 1) {
        requestAnimationFrame(step);
      } else {
        el.textContent = target + (isPercent ? '%' : '');
      }
    }

    requestAnimationFrame(step);
  }

  if ('IntersectionObserver' in window) {
    var statValues = document.querySelectorAll('.stat-value');
    var counterObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var el = entry.target;
          var text = el.textContent.trim();
          var numericValue = parseFloat(text.replace('%', ''));
          if (!isNaN(numericValue)) {
            animateCounter(el, numericValue, 800);
          }
          counterObserver.unobserve(el);
        }
      });
    }, { threshold: 0.5 });

    statValues.forEach(function(el) {
      counterObserver.observe(el);
    });
  }

  // ==========================================================
  // Progress bar animation
  // ==========================================================
  if ('IntersectionObserver' in window) {
    var progressBars = document.querySelectorAll('.progress-bar');
    var progressObserver = new IntersectionObserver(function(entries) {
      entries.forEach(function(entry) {
        if (entry.isIntersecting) {
          var bar = entry.target;
          var width = bar.style.width;
          bar.style.width = '0';
          requestAnimationFrame(function() {
            bar.style.transition = 'width 1s cubic-bezier(0.16, 1, 0.3, 1)';
            bar.style.width = width;
          });
          progressObserver.unobserve(bar);
        }
      });
    }, { threshold: 0.3 });

    progressBars.forEach(function(bar) {
      progressObserver.observe(bar);
    });
  }

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
  // Smooth page transitions
  // ==========================================================
  document.body.style.opacity = '0';
  document.body.style.transition = 'opacity 0.25s ease-out';
  window.addEventListener('load', function() {
    document.body.style.opacity = '1';
  });
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
        if (e.target.closest('a, button, input, select')) return;
        window.location.href = link.href;
      });
    }
  });

  // ==========================================================
  // Keyboard shortcut: focus search (Ctrl+K)
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

  // ==========================================================
  // Active nav indicator animation
  // ==========================================================
  var activeNav = document.querySelector('.nav-item.active');
  if (activeNav) {
    activeNav.style.animation = 'slideIn 0.4s cubic-bezier(0.16, 1, 0.3, 1) both';
  }

})();
