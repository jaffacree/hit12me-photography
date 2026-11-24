import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://www.hit12mephotography.com',
  integrations: [sitemap()],
  image: {
    // Allow large originals; Astro makes web-sized copies at build time.
    service: { entrypoint: 'astro/assets/services/sharp', config: { limitInputPixels: false } },
  },
});
