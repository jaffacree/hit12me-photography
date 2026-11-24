import { getCollection, type CollectionEntry } from 'astro:content';
import { sections, type SectionKey } from '../site.config';
import { photosIn, coverFor } from './photos';

export type Post = CollectionEntry<'blog'> | CollectionEntry<'sports'>;

export async function getPosts(section: SectionKey) {
  const posts = (await getCollection(section)) as Post[];
  return posts
    .filter((p) => import.meta.env.DEV || !p.data.draft)
    .sort((a, b) => b.data.date.valueOf() - a.data.date.valueOf());
}

export async function getAllPosts() {
  const [a, b] = await Promise.all([getPosts('blog'), getPosts('sports')]);
  return [...a, ...b].sort((x, y) => y.data.date.valueOf() - x.data.date.valueOf());
}

export const postUrl = (p: Post) => `${sections[p.collection].path}/${p.id}`;
export const postPhotos = (p: Post) => photosIn(`${p.collection}/${p.id}`);
export const postCover = (p: Post) => coverFor(postPhotos(p), p.data.cover);

export const formatDate = (d: Date) =>
  d.toLocaleDateString('en-US', { year: 'numeric', month: 'long', day: 'numeric', timeZone: 'UTC' });

export const readingMinutes = (p: Post) =>
  Math.max(1, Math.round((p.body ?? '').split(/\s+/).filter(Boolean).length / 230));
