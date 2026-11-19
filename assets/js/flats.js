/* JJ Works flats: instant posting (Sell), live listings (Buy), admin hide/show (Admin + Buy).
   Talks to Supabase over its REST API. Config comes from <script id="flats-config"> on each page. */
(function () {
  var cfgEl = document.getElementById('flats-config');
  if (!cfgEl) return;
  var C = JSON.parse(cfgEl.textContent);
  var S = C.strings;
  var BN = C.lang === 'bn';
  var ready = !!(C.url && C.key);
  var PHOTO_BASE = C.url + '/storage/v1/object/public/listing-photos/';

  /* ---------- helpers ---------- */
  function digits(v) { v = String(v); return BN ? v.replace(/[0-9]/g, function (d) { return '০১২৩৪৫৬৭৮৯'[d]; }) : v; }
  function esc(s) { return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  function taka(n) {
    var s = String(Math.round(n)), head = s.slice(0, -3), tail = s.slice(-3), parts = [];
    if (s.length > 3) { while (head.length > 2) { parts.unshift(head.slice(-2)); head = head.slice(0, -2); } if (head) parts.unshift(head); s = parts.join(',') + ',' + tail; }
    return '৳ ' + digits(s);
  }
  function fmt(tpl, o) { return tpl.replace(/\{(\w+)\}/g, function (_, k) { return o[k]; }); }
  function waLink(text) { return 'https://wa.me/' + C.whatsapp + '?text=' + encodeURIComponent(text); }

  function myPosts() { try { return JSON.parse(localStorage.getItem('jjw_my_posts') || '{}'); } catch (e) { return {}; } }
  function rememberPost(code, key) { try { var m = myPosts(); m[code] = key; localStorage.setItem('jjw_my_posts', JSON.stringify(m)); } catch (e) {} }
  function forgetPost(code) { try { var m = myPosts(); delete m[code]; localStorage.setItem('jjw_my_posts', JSON.stringify(m)); } catch (e) {} }
  function editLink(code, key, lang) {
    var base = lang && lang !== C.lang ? (lang === 'bn' ? C.siteUrl + '/bn/sell/edit/' : C.siteUrl + '/sell/edit/') : C.editUrl;
    return base + '#' + code + '.' + key;
  }
  function rpc(name, args) {
    return api('/rest/v1/rpc/' + name, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(args) });
  }
  function copyText(input, btn) {
    input.select();
    var done = function () { var t = btn.textContent; btn.textContent = S.copied; setTimeout(function () { btn.textContent = t; }, 1800); };
    if (navigator.clipboard) navigator.clipboard.writeText(input.value).then(done, function () { document.execCommand('copy'); done(); });
    else { document.execCommand('copy'); done(); }
  }

  function session() {
    try {
      var s = JSON.parse(localStorage.getItem('jjw_admin') || 'null');
      if (s && s.expires_at * 1000 > Date.now() + 30000) return s;
    } catch (e) {}
    return null;
  }
  function headers(extra, token) {
    var h = { apikey: C.key, Authorization: 'Bearer ' + (token || C.key) };
    for (var k in extra) h[k] = extra[k];
    return h;
  }
  function api(path, opts, token) {
    opts = opts || {};
    opts.headers = headers(opts.headers || {}, token);
    return fetch(C.url + path, opts).then(function (r) {
      if (!r.ok) return r.text().then(function (t) { var e = new Error(t || r.statusText); e.status = r.status; throw e; });
      var ct = r.headers.get('content-type') || '';
      return ct.indexOf('json') >= 0 ? r.json() : r.text();
    });
  }

  /* ---------- photo: shrink to max 1600px JPEG (also strips GPS/EXIF) ---------- */
  function shrinkPhoto(file) {
    return new Promise(function (resolve, reject) {
      var img = new Image(), url = URL.createObjectURL(file);
      img.onload = function () {
        var max = 1600, w = img.naturalWidth, h = img.naturalHeight, sc = Math.min(1, max / Math.max(w, h));
        var cv = document.createElement('canvas');
        cv.width = Math.round(w * sc); cv.height = Math.round(h * sc);
        cv.getContext('2d').drawImage(img, 0, 0, cv.width, cv.height);
        URL.revokeObjectURL(url);
        (function attempt(q) {
          cv.toBlob(function (b) {
            if (!b) return reject(new Error('photo'));
            if (b.size > 4.5 * 1024 * 1024 && q > 0.5) return attempt(q - 0.15);
            resolve(b);
          }, 'image/jpeg', q);
        })(0.82);
      };
      img.onerror = function () { URL.revokeObjectURL(url); reject(new Error('photo')); };
      img.src = url;
    });
  }
  function uuid() {
    if (window.crypto && crypto.randomUUID) return crypto.randomUUID();
    return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) { var r = Math.random() * 16 | 0; return (c === 'x' ? r : (r & 3 | 8)).toString(16); });
  }

  /* ---------- listing card ---------- */
  function card(l, admin) {
    var facs = ['parking', 'lift', 'generator'].filter(function (f) { return l[f]; }).map(function (f) { return S['fac_' + f]; }).join(', ');
    var rows = [
      [S.l_size, digits(Number(l.size_sqft).toLocaleString('en-US')) + ' ' + S.l_sqft],
      [S.l_rooms, fmt(S.l_rooms_v, { b: digits(l.bedrooms), t: digits(l.bathrooms) })],
      [S.l_floor, fmt(S.l_floor_v, { f: digits(l.floor), t: digits(l.total_floors) })]
    ];
    if (facs) rows.push([S.s_fac, facs]);
    var dl = rows.map(function (r) { return '<div><dt>' + esc(r[0]) + '</dt><dd>' + esc(r[1]) + '</dd></div>'; }).join('');
    var price = taka(l.price_bdt) + (l.negotiable ? ' <small>' + esc(S.l_neg) + '</small>' : '');
    var tags = (l.sold ? '<span class="sold-tag">' + esc(S.l_sold) + '</span>' : '') + (l.hidden ? '<span class="sold-tag hidden-tag">' + esc(S.a_hidden) + '</span>' : '');
    var actions = l.sold ? '' :
      '<div class="listing-actions">' +
      '<a class="btn btn-wa btn-sm" href="' + waLink(fmt(S.l_wa, { id: l.code })) + '" target="_blank" rel="noopener">' + C.waIcon + esc(S.l_ask) + '</a>' +
      '<a class="btn btn-ghost btn-sm" href="?listing=' + encodeURIComponent(l.code) + '#flat-enquiry">' + esc(S.l_form) + '</a></div>';
    var mine = myPosts()[l.code];
    var adminBar = (admin ? adminButtons(l) : '') +
      (mine && !admin ? '<div class="admin-bar"><a class="btn btn-ghost btn-sm" href="' + C.editPath + '#' + esc(l.code) + '.' + esc(mine) + '">' + esc(S.l_edit) + '</a></div>' : '');
    return '<li class="listing' + (l.sold ? ' is-sold' : '') + (l.hidden ? ' is-hidden' : '') + '" id="' + esc(l.code) + '" data-id="' + l.id + '">' +
      '<div class="listing-img">' + tags + '<img src="' + PHOTO_BASE + encodeURIComponent(l.photo_path) + '" alt="' + esc(l.location) + '" loading="lazy" decoding="async"></div>' +
      '<div class="listing-body"><p class="listing-id">' + esc(S.l_listing) + ' ' + esc(l.code) + '</p>' +
      '<p class="listing-price">' + price + '</p><h2 class="listing-loc">' + esc(l.location) + '</h2>' +
      '<dl class="listing-facts">' + dl + '</dl>' +
      (l.details ? '<p class="listing-details">' + esc(l.details) + '</p>' : '') + actions + adminBar + '</div></li>';
  }
  function adminButtons(l) {
    return '<div class="admin-bar">' +
      '<button type="button" class="btn btn-sm ' + (l.hidden ? 'btn-primary' : 'btn-danger') + '" data-act="hidden" data-val="' + (!l.hidden) + '">' + esc(l.hidden ? S.a_show : S.a_hide) + '</button>' +
      '<button type="button" class="btn btn-sm btn-ghost" data-act="sold" data-val="' + (!l.sold) + '">' + esc(l.sold ? S.a_unsold : S.a_sold) + '</button>' +
      '<button type="button" class="btn btn-sm btn-ghost btn-delete" data-act="delete" data-code="' + esc(l.code) + '" data-photo="' + esc(l.photo_path) + '">' + esc(S.a_delete) + '</button></div>';
  }
  function bindAdmin(root, reload) {
    root.addEventListener('click', function (e) {
      var b = e.target.closest('[data-act]');
      if (!b) return;
      var s = session();
      if (!s) { location.href = C.adminUrl; return; }
      var li = b.closest('[data-id]'), body = {};
      if (b.getAttribute('data-act') === 'delete') {
        if (!confirm(fmt(S.a_delete_confirm, { code: b.getAttribute('data-code') }))) return;
        b.disabled = true;
        api('/rest/v1/listings?id=eq.' + li.getAttribute('data-id'), { method: 'DELETE', headers: { Prefer: 'return=minimal' } }, s.access_token)
          .then(function () {
            return api('/storage/v1/object/listing-photos/' + encodeURIComponent(b.getAttribute('data-photo')), { method: 'DELETE' }, s.access_token).catch(function () {});
          }).then(reload).catch(function (err) { b.disabled = false; alert(S.a_failed + ' ' + err.message); });
        return;
      }
      body[b.getAttribute('data-act')] = b.getAttribute('data-val') === 'true';
      b.disabled = true;
      api('/rest/v1/listings?id=eq.' + li.getAttribute('data-id'), {
        method: 'PATCH', headers: { 'Content-Type': 'application/json', Prefer: 'return=minimal' }, body: JSON.stringify(body)
      }, s.access_token).then(reload).catch(function (err) { b.disabled = false; alert(S.a_failed + ' ' + err.message); });
    });
  }

  /* ---------- Buy page ---------- */
  var list = document.getElementById('live-listings');
  if (list) {
    var admin = session();
    var load = function () {
      if (!ready) { list.innerHTML = emptyHTML(); return; }
      var q = '/rest/v1/listings?select=*&order=created_at.desc';
      api(q, {}, admin && admin.access_token).then(function (rows) {
        list.innerHTML = rows.length ? '<ul class="listings">' + rows.map(function (l) { return card(l, !!admin); }).join('') + '</ul>' : emptyHTML();
        if (location.hash && location.hash !== '#flat-enquiry') { var t = document.getElementById(location.hash.slice(1)); if (t) t.scrollIntoView(); }
      }).catch(function () { list.innerHTML = '<div class="empty-state"><p>' + esc(S.err_load) + '</p></div>'; });
    };
    if (admin) { var note = document.getElementById('admin-note'); if (note) note.hidden = false; bindAdmin(list, load); }
    load();
  }
  function emptyHTML() { return '<div class="empty-state"><h2>' + esc(S.buy_empty_h) + '</h2><p>' + esc(S.buy_empty_p) + '</p></div>'; }

  /* ---------- Sell page (new post) and Edit page ---------- */
  var form = document.getElementById('sell-form');
  if (form) {
    var mode = form.getAttribute('data-mode');
    var status = document.getElementById('sell-status');
    var btn = form.querySelector('button[type=submit]');
    var f = form.elements;
    var editCode = null, editKey = null, current = null;
    var setStatus = function (text, err) { status.className = 'form-status full' + (err ? ' is-error' : ''); status.textContent = text; status.hidden = false; };
    var collect = function () {
      return {
        location: f.flat_location.value, size_sqft: f.size_sqft.value, price_bdt: f.price_bdt.value,
        negotiable: f.negotiable.checked, bedrooms: f.bedrooms.value, bathrooms: f.bathrooms.value,
        floor: f.floor.value, total_floors: f.total_floors.value,
        parking: f.parking.checked, lift: f.lift.checked, generator: f.generator.checked,
        details: f.details.value, name: f.name.value, phone: f.phone.value, email: f.email.value,
        address: f.contact_address.value, website: f.website.value, lang: C.lang
      };
    };
    var upload = function (file) {
      var name = uuid() + '.jpg';
      return shrinkPhoto(file).then(function (blob) {
        return api('/storage/v1/object/listing-photos/' + name, { method: 'POST', headers: { 'Content-Type': 'image/jpeg', 'x-upsert': 'false' }, body: blob });
      }).then(function () { return name; });
    };
    if (!ready) { setStatus(S.err_setup, true); btn.disabled = true; }

    if (mode === 'edit') {
      var msgEl = document.getElementById('edit-msg');
      var m = /^#(F-\d+)\.([a-f0-9]{32,})$/.exec(location.hash);
      var bad = function () { msgEl.textContent = S.e_bad_link; msgEl.className = 'form-status is-error'; form.hidden = true; };
      if (!m || !ready) bad();
      else {
        editCode = m[1]; editKey = m[2];
        rpc('get_my_listing', { p_code: editCode, p_key: editKey }).then(function (r) {
          current = r; msgEl.hidden = true; form.hidden = false;
          f.flat_location.value = r.location; f.size_sqft.value = r.size_sqft; f.price_bdt.value = r.price_bdt;
          f.negotiable.checked = r.negotiable; f.bedrooms.value = r.bedrooms; f.bathrooms.value = r.bathrooms;
          f.floor.value = r.floor; f.total_floors.value = r.total_floors;
          f.parking.checked = r.parking; f.lift.checked = r.lift; f.generator.checked = r.generator;
          f.details.value = r.details || ''; f.name.value = r.name || ''; f.phone.value = r.phone || '';
          f.email.value = r.email || ''; f.contact_address.value = r.address || '';
          var fig = document.getElementById('current-photo');
          fig.querySelector('img').src = PHOTO_BASE + encodeURIComponent(r.photo_path); fig.hidden = false;
          var view = document.getElementById('edit-view-link'); if (view) view.href = C.buyUrl + '#' + editCode;
          rememberPost(editCode, editKey);
          var soldBtn = document.getElementById('edit-sold');
          var paintSold = function () { soldBtn.textContent = current.sold ? soldBtn.getAttribute('data-unsold') : soldBtn.getAttribute('data-sold'); };
          paintSold();
          soldBtn.addEventListener('click', function () {
            soldBtn.disabled = true;
            rpc('set_my_listing_sold', { p_code: editCode, p_key: editKey, p_sold: !current.sold }).then(function () {
              current.sold = !current.sold; paintSold(); soldBtn.disabled = false; setStatus(S.e_saved);
            }).catch(function () { soldBtn.disabled = false; setStatus(S.err_post, true); });
          });
          document.getElementById('edit-delete').addEventListener('click', function () {
            if (!confirm(S.e_delete_confirm)) return;
            rpc('delete_my_listing', { p_code: editCode, p_key: editKey }).then(function () {
              forgetPost(editCode); form.hidden = true;
              msgEl.className = 'form-status'; msgEl.textContent = S.e_deleted; msgEl.hidden = false;
            }).catch(function () { setStatus(S.err_post, true); });
          });
        }).catch(bad);
      }
    }

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!ready || !form.reportValidity()) return;
      var file = f.photo.files[0], p = collect();
      if (mode !== 'edit' && !file) return;
      btn.disabled = true;
      setStatus(mode === 'edit' ? S.e_saving : S.st_sending);
      (file ? upload(file) : Promise.resolve(null)).then(function (name) {
        if (mode === 'edit') {
          if (name) p.photo_path = name;
          return rpc('update_my_listing', { p_code: editCode, p_key: editKey, p: p }).then(function () {
            btn.disabled = false; f.photo.value = '';
            if (name) document.querySelector('#current-photo img').src = PHOTO_BASE + name;
            setStatus(S.e_saved);
          });
        }
        p.photo_path = name;
        return rpc('submit_listing', { p: p }).then(function (r) {
          rememberPost(r.code, r.key);
          return notify(r.code, r.key, p).then(function () {
            location.href = C.thanksUrl + '?code=' + encodeURIComponent(r.code) + '#k=' + r.key;
          });
        });
      }).catch(function (err) {
        btn.disabled = false;
        setStatus((err && err.message === 'photo') ? S.err_photo : S.err_post, true);
      });
    });
  }
  // Email JJ Works about each new post (never blocks the seller if it fails).
  function notify(code, key, p) {
    var body = {
      _subject: 'New flat posted on jjworks.bd: ' + code, _template: 'table', _captcha: 'false',
      listing: code, location: p.location, size_sqft: p.size_sqft, price_bdt: p.price_bdt,
      rooms: p.bedrooms + ' bed / ' + p.bathrooms + ' bath', floor: p.floor + ' of ' + p.total_floors,
      seller_name: p.name, seller_phone: p.phone, seller_email: p.email, seller_address: p.address,
      details: p.details, photo: PHOTO_BASE + p.photo_path,
      view_post: C.siteUrl + '/buy/#' + code, seller_edit_link: editLink(code, key), admin_page: C.siteUrl + '/admin/'
    };
    if (p.email && /^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(p.email)) body._cc = p.email;
    return fetch('https://formsubmit.co/ajax/' + C.email, {
      method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'application/json' }, body: JSON.stringify(body)
    }).catch(function () {});
  }

  /* ---------- Thanks page: show the listing number ---------- */
  var codeEl = document.getElementById('posted-code');
  if (codeEl) {
    var c = new URLSearchParams(location.search).get('code');
    if (c && /^F-\d+$/.test(c)) {
      codeEl.textContent = c;
      var link = document.getElementById('posted-link');
      if (link) link.href = C.buyUrl + '#' + c;
      var km = /^#k=([a-f0-9]{32,})$/.exec(location.hash);
      if (km) {
        var url = editLink(c, km[1]);
        var box = document.getElementById('edit-link-box'), inp = document.getElementById('edit-link');
        inp.value = url; box.hidden = false;
        document.getElementById('wa-edit-link').href = 'https://wa.me/?text=' + encodeURIComponent(fmt(S.wa_self, { code: c, url: url }));
        var cb = document.getElementById('copy-edit-link');
        cb.addEventListener('click', function () { copyText(inp, cb); });
        history.replaceState(null, '', location.pathname + location.search);
      }
    } else { var w = document.getElementById('posted-wrap'); if (w) w.hidden = true; }
  }

  /* ---------- Admin page ---------- */
  var adminRoot = document.getElementById('admin-app');
  if (adminRoot) {
    var loginForm = document.getElementById('admin-login');
    var panel = document.getElementById('admin-panel');
    var msg = document.getElementById('admin-msg');
    var rowsEl = document.getElementById('admin-rows');
    var show = function () {
      var s = session();
      loginForm.hidden = !!s; panel.hidden = !s;
      if (s) loadAdmin(s);
    };
    var loadAdmin = function (s) {
      rowsEl.innerHTML = '<p>' + esc(S.a_loading) + '</p>';
      Promise.all([
        api('/rest/v1/listings?select=*&order=created_at.desc', {}, s.access_token),
        api('/rest/v1/listing_contacts?select=*', {}, s.access_token)
      ]).then(function (res) {
        var contacts = {};
        res[1].forEach(function (c) { contacts[c.listing_id] = c; });
        if (!res[0].length) { rowsEl.innerHTML = '<p>' + esc(S.buy_empty_h) + '</p>'; return; }
        rowsEl.innerHTML = '<ul class="listings admin-list">' + res[0].map(function (l) {
          var c = contacts[l.id] || {};
          var when = new Date(l.created_at).toLocaleString(BN ? 'bn-BD' : 'en-GB', { dateStyle: 'medium', timeStyle: 'short' });
          var seller = '<div class="seller-box"><strong>' + esc(S.a_seller) + '</strong> ' + esc(c.name) +
            ' · <a href="tel:' + esc(c.phone) + '">' + esc(c.phone) + '</a>' + (c.email ? ' · ' + esc(c.email) : '') +
            '<br>' + esc(c.address) + '<br><small>' + esc(S.a_posted) + ' ' + esc(when) + '</small>' +
            (c.edit_key ? '<br><small>' + esc(S.a_edit_link) + ' <a href="' + esc(editLink(l.code, c.edit_key, l.lang)) + '" target="_blank" rel="noopener">' + esc(editLink(l.code, c.edit_key, l.lang)) + '</a></small>'
                        : '<br><small>' + esc(S.a_no_edit_link) + '</small>') + '</div>';
          return card(l, true).replace('<div class="admin-bar">', seller + '<div class="admin-bar">');
        }).join('') + '</ul>';
      }).catch(function (err) {
        if (err.status === 401) { localStorage.removeItem('jjw_admin'); show(); return; }
        rowsEl.innerHTML = '<p class="form-error">' + esc(S.err_load) + '</p>';
      });
    };
    loginForm.addEventListener('submit', function (e) {
      e.preventDefault();
      msg.hidden = true;
      api('/auth/v1/token?grant_type=password', {
        method: 'POST', headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginForm.elements.email.value, password: loginForm.elements.password.value })
      }).then(function (r) {
        localStorage.setItem('jjw_admin', JSON.stringify({ access_token: r.access_token, expires_at: r.expires_at }));
        loginForm.reset(); show();
      }).catch(function () { msg.textContent = S.a_bad_login; msg.hidden = false; });
    });
    document.getElementById('admin-logout').addEventListener('click', function () { localStorage.removeItem('jjw_admin'); show(); });
    bindAdmin(rowsEl, function () { loadAdmin(session()); });
    if (!ready) { msg.textContent = S.err_setup; msg.hidden = false; }
    show();
  }
})();
