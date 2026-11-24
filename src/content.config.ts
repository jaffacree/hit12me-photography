import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const schema = z.object({
  title: z.string(),
  date: z.coerce.date(),
  summary: z.string().optional(),
  // File name of the cover photo inside this post's photo folder (extension optional).
  cover: z.string().optional(),
  gear: z.array(z.string()).default([]),
  // Notes from the Squarespace export about which photos the old post used. Not shown on the site.
  originalImages: z.string().optional(),
  draft: z.boolean().default(false),
});

export const collections = {
  blog: defineCollection({ loader: glob({ pattern: '**/*.md', base: './src/content/blog' }), schema }),
  sports: defineCollection({ loader: glob({ pattern: '**/*.md', base: './src/content/sports' }), schema }),
};
