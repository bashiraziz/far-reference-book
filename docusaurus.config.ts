import {themes as prismThemes} from 'prism-react-renderer';
import type {Config} from '@docusaurus/types';
import type * as Preset from '@docusaurus/preset-classic';

const config: Config = {
  title: 'FAR Reference Book',
  tagline: 'Federal Acquisition Regulations - Parts 1-3',
  favicon: 'img/favicon.ico',

  future: {
    v4: true,
  },

  // Set the production url of your site here
  url: 'https://your-username.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  baseUrl: '/',

  // GitHub pages deployment config
  organizationName: 'Bashir Aziz',
  projectName: 'far-reference-book',

  onBrokenLinks: 'warn', // Changed to warn to avoid build failures on broken links

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
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
      ],
      copyright: `FAR Reference Book © ${new Date().getFullYear()}. Built with Docusaurus by Bashir Aziz.`,
    },
    prism: {
      theme: prismThemes.github,
      darkTheme: prismThemes.dracula,
    },
  } satisfies Preset.ThemeConfig,
};

export default config;
