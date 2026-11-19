# JJ Works website (jjworks.bd)

Static site in English (`/`) and Bangla (`/bn/`), hosted on GitHub Pages.

## Editing content

All text, projects, services and contact details live in `src/data.py`, plus interface wording in `src/build.py` (the `UI` table). Each text is a pair: `("English", "বাংলা")`.

After any change, rebuild the pages and commit:

```
python3 src/build.py
```

This regenerates `index.html`, `bn/`, `projects/`, `thanks/`, `404.html`, `sitemap.xml` and `robots.txt`. Don't edit those files by hand; your changes would be overwritten.

## Adding a project

1. Put a photo in `images/projects/<slug>.jpg` (portrait, about 640×780) and a WebP copy as `<slug>.webp`.
2. Add a line to `PROJECTS` in `src/data.py`.
3. Run `python3 src/build.py`.

## Contact form

The form sends to jjworks.info@gmail.com through FormSubmit (formsubmit.co). The first time someone submits it, FormSubmit emails that inbox an activation link; click it once and later enquiries arrive normally.

## Look and feel

Styles: `assets/css/site.css`. Script (mobile menu, project filter, form pre-fill): `assets/js/site.js`.

## Flats for sale (Sell a flat / Buy a flat / Admin)

- Sellers post at `/sell/`; the post appears on `/buy/` straight away. Photos are resized in the browser and stored in Supabase Storage.
- Seller name, phone, email and address are stored separately and are visible only to the admin.
- Each new post also emails jjworks.info@gmail.com (via FormSubmit) with the details and the seller's contact.
- Admin: `/admin/`, sign in as jjworks.info@gmail.com. Hide / show posts and mark them sold. While signed in, the same buttons appear on `/buy/`.

Backend: Supabase project `jjworks` (URL and public anon key in `src/data.py`). Database tables, security rules and the photo bucket are created by `src/supabase-setup.sql` (run once in the Supabase SQL editor). Public sign-ups are disabled; the admin user is added in Supabase under Authentication → Users.
