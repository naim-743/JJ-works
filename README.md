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

## Flats for sale (Sell a flat / Buy a flat)

- Sellers fill in the form at `/sell/`. FormSubmit emails the details and the building photo to jjworks.info@gmail.com. Nothing appears on the site automatically.
- Buyers browse `/buy/` and contact JJ Works by WhatsApp or the enquiry form, quoting the listing number. Sellers' names and phone numbers are never published.

To publish an approved flat:

1. Save the seller's photo as `images/listings/F-001.jpg` (next number each time).
2. Add an entry to `LISTINGS` in `src/listings.py` (copy the example at the top of that file).
3. Run `python3 src/build.py`, then commit and push.

To mark a flat as sold, set `"sold": True` (it stays listed with a "Sold" label), or delete its entry.
