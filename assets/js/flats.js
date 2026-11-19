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
    var adminBar = admin ? adminButtons(l) : '';
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
      '<button type="button" class="btn btn-sm btn-ghost" data-act="sold" data-val="' + (!l.sold) + '">' + esc(l.sold ? S.a_unsold : S.a_sold) + '</button></div>';
  }
  function bindAdmin(root, reload) {
    root.addEventListener('click', function (e) {
      var b = e.target.closest('[data-act]');
      if (!b) return;
      var s = session();
      if (!s) { location.href = C.adminUrl; return; }
      var li = b.closest('[data-id]'), body = {};
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

  /* ---------- Sell page ---------- */
  var form = document.getElementById('sell-form');
  if (form) {
    var status = document.getElementById('sell-status');
    var btn = form.querySelector('button[type=submit]');
    if (!ready) { status.textContent = S.err_setup; status.hidden = false; btn.disabled = true; }
    form.addEventListener('submit', function (e) {
      e.preventDefault();
      if (!ready || !form.reportValidity()) return;
      var f = form.elements, file = f.photo.files[0];
      if (!file) return;
      btn.disabled = true;
      status.className = 'form-status'; status.hidden = false; status.textContent = S.st_sending;
      var name = uuid() + '.jpg', code;
      shrinkPhoto(file).then(function (blob) {
        return api('/storage/v1/object/listing-photos/' + name, { method: 'POST', headers: { 'Content-Type': 'image/jpeg', 'x-upsert': 'false' }, body: blob });
      }).then(function () {
        var p = {
          location: f.flat_location.value, size_sqft: f.size_sqft.value, price_bdt: f.price_bdt.value,
          negotiable: f.negotiable.checked, bedrooms: f.bedrooms.value, bathrooms: f.bathrooms.value,
          floor: f.floor.value, total_floors: f.total_floors.value,
          parking: f.parking.checked, lift: f.lift.checked, generator: f.generator.checked,
          details: f.details.value, photo_path: name, lang: C.lang,
          name: f.name.value, phone: f.phone.value, email: f.email.value, address: f.contact_address.value,
          website: f.website.value
        };
        return api('/rest/v1/rpc/submit_listing', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ p: p }) }).then(function (c) {
          code = typeof c === 'string' ? c.replace(/"/g, '') : c;
          return notify(code, p);
        });
      }).then(function () {
        location.href = C.thanksUrl + '?code=' + encodeURIComponent(code);
      }).catch(function (err) {
        btn.disabled = false;
        status.className = 'form-status is-error';
        status.textContent = (err && err.message === 'photo') ? S.err_photo : S.err_post;
      });
    });
  }
  // Email JJ Works about each new post (never blocks the seller if it fails).
  function notify(code, p) {
    var body = {
      _subject: 'New flat posted on jjworks.bd: ' + code, _template: 'table', _captcha: 'false',
      listing: code, location: p.location, size_sqft: p.size_sqft, price_bdt: p.price_bdt,
      rooms: p.bedrooms + ' bed / ' + p.bathrooms + ' bath', floor: p.floor + ' of ' + p.total_floors,
      seller_name: p.name, seller_phone: p.phone, seller_email: p.email, seller_address: p.address,
      details: p.details, photo: PHOTO_BASE + p.photo_path,
      view_post: C.siteUrl + '/buy/#' + code, hide_posts_here: C.siteUrl + '/admin/'
    };
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
            '<br>' + esc(c.address) + '<br><small>' + esc(S.a_posted) + ' ' + esc(when) + '</small></div>';
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
