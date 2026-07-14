import { defineCollection, z } from 'astro:content';
import { glob } from 'astro/loaders';

const themas = ['installaties', 'webapps', 'podium'] as const;

const projecten = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/projecten' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      slug: z.string().optional(),
      thema: z.enum(themas),
      tags: z.array(z.string()).default([]),
      cover: image().optional(),
      alt: z.string().optional(),
      client: z.string().optional(),
      date: z.coerce.date(),
      featured: z.boolean().default(false),
      excerpt: z.string().optional(),
      video: z.string().optional(),
      lumLeft: z.number().optional(),
      lumRight: z.number().optional(),
    }),
});

const blog = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/blog' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      slug: z.string().optional(),
      thema: z.enum(themas).optional(),
      tags: z.array(z.string()).default([]),
      cover: image().optional(),
      alt: z.string().optional(),
      date: z.coerce.date(),
      featured: z.boolean().default(false),
      excerpt: z.string().optional(),
      video: z.string().optional(),
      lumLeft: z.number().optional(),
      lumRight: z.number().optional(),
    }),
});

export const collections = { projecten, blog };
