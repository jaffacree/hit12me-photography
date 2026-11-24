# Hit12me Photography website

A fast, free-to-host photography site built with [Astro](https://astro.build).
All 17 published posts from the old Squarespace site are in `src/content/`, and the old
web addresses (`/blog/...` and `/sports-photo-blog/...`) still work.

## Where things live

| What | Where |
| --- | --- |
| Site name, email, Instagram, contact-form key | `src/site.config.ts` |
| Colors and fonts | top of `src/styles/global.css` |
| Journal posts | `src/content/blog/*.md` |
| Sports posts | `src/content/sports/*.md` |
| Photos for a post | `src/photos/blog/<post-name>/` or `src/photos/sports/<post-name>/` |
| Home page big photo (optional) | `src/photos/pages/home/` |
| About page portrait | `src/photos/pages/about/` (old site used `IMG_0812.jpeg`) |

## Adding photos to a post

1. Export from Lightroom: **JPEG, sRGB, quality 85–90, long edge 2560–3000 px**.
   Full-resolution originals aren't needed; the site makes sharp copies sized for each screen.
2. Put them in the folder named after the post's file, e.g.
   `src/photos/blog/teddy-roosevelt-national-park/`.
3. Done. Every photo in the folder appears in the post's gallery, sorted by file name.
   The cover is the file named in the post's `cover:` line (e.g. `_A1_7377.jpg`); if that file
   isn't there, the first photo is used.

Each post keeps an `originalImages:` note listing the photos the Squarespace version used,
so you can find them in Lightroom.

## Writing a new post

Make a new file in `src/content/blog/` (or `sports/`), e.g. `glacier-national-park.md`:

```md
---
title: "Glacier National Park"
date: 2025-07-04
summary: "One line that shows on the cards."
cover: "_A1_9001.jpg"
gear:
  - "Sony a1"
  - "Sony 70-200mm f/2.8 GMii"
---

Write the story here. Leave a blank line between paragraphs.
```

Then add a matching photo folder `src/photos/blog/glacier-national-park/`.
Add `draft: true` to hide a post until it's ready.

## Contact form (free)

1. Go to https://web3forms.com, enter the email you want messages sent to, and they email you an Access Key.
2. Paste it into `web3formsKey` in `src/site.config.ts`.

Messages then arrive in your inbox (free tier: 250 a month).

## Hosting for free on Cloudflare Pages

1. Sign in at https://dash.cloudflare.com → **Workers & Pages** → **Create** → **Pages** → **Connect to Git**.
2. Pick this GitHub repository. Framework preset: **Astro** (build command `npm run build`, output folder `dist`).
3. After the first deploy, open **Custom domains** and add `www.hit12mephotography.com`.
   Cloudflare shows the DNS records to set at your domain registrar.

Every change committed to GitHub rebuilds and publishes the site automatically.
Cloudflare Pages is free with unlimited bandwidth.

## Working on a computer (optional)

```sh
npm install
npm run dev      # preview at http://localhost:4321
npm run build    # finished site in dist/
```
