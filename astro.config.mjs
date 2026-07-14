import { defineConfig } from 'astro/config';
import mdx from '@astrojs/mdx';
import sitemap from '@astrojs/sitemap';

// https://astro.build/config
export default defineConfig({
  site: 'https://jwotto.github.io',
  base: '/studio-wotto-website',
  integrations: [mdx(), sitemap()],
});
