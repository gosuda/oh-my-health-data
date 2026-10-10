import adapter from '@sveltejs/adapter-static';
import { vitePreprocess } from '@sveltejs/vite-plugin-svelte';

/** @type {import('@sveltejs/kit').Config} */
const config = {
  preprocess: vitePreprocess(),
  kit: {
    // Error documents can be served at nested unknown URLs by a static host.
    // Root-absolute assets keep the standalone 404 page styled there too.
    paths: { relative: false },
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      strict: true
    })
  }
};

export default config;
