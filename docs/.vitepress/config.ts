import { defineConfig } from 'vitepress';

export default defineConfig({
  title: 'signalrgb-python',
  description: 'Python client library and CLI for SignalRGB Pro',
  base: '/signalrgb-python/',
  lastUpdated: true,

  head: [
    ['meta', { name: 'theme-color', content: '#e135ff' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'signalrgb-python' }],
    [
      'meta',
      {
        property: 'og:description',
        content: 'Python client library and CLI for SignalRGB Pro',
      },
    ],
    ['meta', { property: 'og:site_name', content: 'signalrgb-python' }],
    ['meta', { name: 'twitter:card', content: 'summary' }],
  ],

  themeConfig: {
    nav: [
      { text: 'Guide', link: '/guide/' },
      {
        text: 'Reference',
        items: [
          { text: 'CLI', link: '/reference/cli' },
          { text: 'Python Library', link: '/reference/library' },
          { text: 'Async Client', link: '/reference/async' },
          { text: 'Models', link: '/reference/models' },
        ],
      },
    ],

    sidebar: {
      '/guide/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Introduction', link: '/guide/' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'Quick Start', link: '/guide/quick-start' },
            { text: 'Development', link: '/guide/development' },
            { text: 'Contributing', link: '/guide/contributing' },
          ],
        },
      ],
      '/reference/': [
        {
          text: 'Reference',
          items: [
            { text: 'CLI', link: '/reference/cli' },
            { text: 'Python Library', link: '/reference/library' },
            { text: 'Async Client', link: '/reference/async' },
            { text: 'Models', link: '/reference/models' },
          ],
        },
      ],
    },

    editLink: {
      pattern: 'https://github.com/hyperb1iss/signalrgb-python/edit/main/docs/:path',
      text: 'Edit this page on GitHub',
    },

    socialLinks: [{ icon: 'github', link: 'https://github.com/hyperb1iss/signalrgb-python' }],

    footer: {
      message: 'Released under the Apache 2.0 License.',
      copyright: 'Copyright \u00A9 2025 Stefanie Jane',
    },

    search: {
      provider: 'local',
    },
  },

  markdown: {
    theme: {
      light: 'github-light',
      dark: 'one-dark-pro',
    },
  },
});
