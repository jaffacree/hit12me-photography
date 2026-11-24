import type { ImageMetadata } from 'astro';

// Every photo under src/photos is picked up automatically.
const files = import.meta.glob<{ default: ImageMetadata }>(
  '/src/photos/**/*.{jpg,jpeg,png,webp,avif,JPG,JPEG,PNG,WEBP}',
  { eager: true },
);

export interface Photo {
  name: string; // file name without folder
  image: ImageMetadata;
}

const collator = new Intl.Collator('en', { numeric: true, sensitivity: 'base' });
const stem = (n: string) => n.replace(/\.[^.]+$/, '').trim().toLowerCase();

/** Photos directly inside src/photos/<folder>/, sorted by file name. */
export function photosIn(folder: string): Photo[] {
  const prefix = `/src/photos/${folder}/`;
  return Object.entries(files)
    .filter(([path]) => path.startsWith(prefix) && !path.slice(prefix.length).includes('/'))
    .map(([path, mod]) => ({ name: path.slice(prefix.length), image: mod.default }))
    .sort((a, b) => collator.compare(a.name, b.name));
}

/** Find a photo by file name; the extension and letter case don't matter. */
export function findPhoto(list: Photo[], name?: string): Photo | undefined {
  if (!name) return undefined;
  const want = stem(name);
  return list.find((p) => stem(p.name) === want);
}

export function coverFor(list: Photo[], name?: string): Photo | undefined {
  return findPhoto(list, name) ?? list[0];
}
