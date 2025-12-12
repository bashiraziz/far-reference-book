import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'FAR Reference Book',
  tagline: 'Federal Acquisition Regulations - All 53 Parts',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // Set the production url of your site here
  url: 'https://bashiraziz.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/far-reference-book/',

  // GitHub pages deployment config
  organizationName: 'bashiraziz',
  projectName: 'far-reference-book',

  onBrokenLinks: 'warn', // Changed to warn to avoid build failures on broken links

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // Custom fields for environment configuration
  customFields: {
    backendUrl: process.env.BACKEND_URL ||
      (process.env.NODE_ENV === 'production'
        ? 'https://far-reference-book-production.up.railway.app'
        : 'http://localhost:8080'),
  },

  presets: [
    [
      'classic',
      {
        docs: {
          routeBasePath: '/', // Serve docs at the root
          sidebarPath: './sidebars.ts',
        },
        blog: false, // Disable blog
        theme: {
          customCss: './src/css/custom.css',
        },
      } satisfies Preset.Options,
    ],
  ],

  themeConfig: {
    image: 'img/docusaurus-social-card.jpg',
    colorMode: {
      respectPrefersColorScheme: true,
    },
    navbar: {
      title: 'Reference',
      logo: {
        alt: 'FAR Logo',
        src: 'img/logo.jpg',
      },
      items: [
        {
          to: '/',
          label: 'Introduction',
          position: 'left',
        },
        {
          to: '/part-1/1.000',
          label: 'FAR Parts',
          position: 'left',
        },
        {
          href: 'https://github.com/bashiraziz/far-reference-book.git',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Resources',
          items: [
            {
              label: 'Official FAR',
              href: 'https://www.acquisition.gov/browse/index/far',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub Repository',
              href: 'https://github.com/bashiraziz/far-reference-book',
            },
            {
              label: 'bashiraziz@gmail.com',
              href: '#',
            },
          ],
        },
      ],
      copyright: `FAR Reference Book built with Docusaurus by Bashir Aziz and contribution from the community.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
