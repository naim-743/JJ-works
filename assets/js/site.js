/* JJ Works: mobile menu, project filter, form pre-fill from a project page. */
(function () {
  // Mobile menu
  var btn = document.querySelector('.menu-btn');
  var nav = document.getElementById('site-nav');
  if (btn && nav) {
    var openLabel = btn.textContent;
    var closeLabel = document.documentElement.lang === 'bn' ? 'বন্ধ' : 'Close';
    function setOpen(open) {
      nav.classList.toggle('open', open);
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
      btn.textContent = open ? closeLabel : openLabel;
    }
    btn.addEventListener('click', function () { setOpen(!nav.classList.contains('open')); });
    nav.addEventListener('click', function (e) { if (e.target.closest('a')) setOpen(false); });
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && nav.classList.contains('open')) { setOpen(false); btn.focus(); } });
  }

  // Project type filter
  var chips = document.querySelectorAll('.chip[data-filter]');
  var cards = document.querySelectorAll('#project-list .card');
  chips.forEach(function (chip) {
    chip.addEventListener('click', function () {
      var f = chip.getAttribute('data-filter');
      chips.forEach(function (c) { c.setAttribute('aria-pressed', c === chip ? 'true' : 'false'); });
      cards.forEach(function (card) { card.hidden = f !== 'all' && card.getAttribute('data-type') !== f; });
    });
  });

  // Coming from a project page: note which project in the enquiry
  var project = new URLSearchParams(location.search).get('project');
  if (project) {
    var hidden = document.getElementById('f-project');
    var msg = document.getElementById('f-message');
    if (hidden) hidden.value = project;
    if (msg && !msg.value) {
      msg.value = document.documentElement.lang === 'bn'
        ? project + '-এর মতো একটি প্রকল্প নিয়ে জানতে চাই।\n'
        : 'I would like to discuss a project similar to ' + project + '.\n';
    }
  }
})();

/* Sell form: stop oversized photos before upload. Buy page: pre-fill listing number. */
(function () {
  document.querySelectorAll('input[type=file][data-max-mb]').forEach(function (input) {
    var max = parseFloat(input.getAttribute('data-max-mb')) * 1024 * 1024;
    var msg = document.createElement('p');
    msg.className = 'form-error';
    msg.setAttribute('role', 'alert');
    msg.hidden = true;
    input.insertAdjacentElement('afterend', msg);
    input.addEventListener('change', function () {
      var f = input.files && input.files[0];
      var tooBig = f && f.size > max;
      input.setCustomValidity(tooBig ? input.getAttribute('data-too-big') : '');
      msg.textContent = tooBig ? input.getAttribute('data-too-big') : '';
      msg.hidden = !tooBig;
    });
  });
  var listing = new URLSearchParams(location.search).get('listing');
  var field = document.getElementById('f-listing');
  if (listing && field) field.value = listing;
})();
