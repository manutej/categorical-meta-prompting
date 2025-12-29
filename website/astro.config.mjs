// @ts-check
import { defineConfig } from 'astro/config';
import starlight from '@astrojs/starlight';

// https://astro.build/config
export default defineConfig({
	site: 'https://hermeticormus.github.io',
	base: '/categorical-meta-prompting-oe',
	integrations: [
		starlight({
			title: 'Categorical Meta-Prompting',
			description: 'Transform AI prompts from guesswork to engineering using category theory.',
			logo: {
				src: './src/assets/logo.svg',
				replacesTitle: false,
			},
			social: [
				{ icon: 'github', label: 'GitHub', href: 'https://github.com/HermeticOrmus/categorical-meta-prompting-oe' },
				{ icon: 'x.com', label: 'X/Twitter', href: 'https://x.com/karpathy/status/1820807166371975636' },
			],
			customCss: ['./src/styles/custom.css'],
			head: [
				{
					tag: 'link',
					attrs: {
						rel: 'preconnect',
						href: 'https://fonts.googleapis.com',
					},
				},
				{
					tag: 'link',
					attrs: {
						rel: 'stylesheet',
						href: 'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap',
					},
				},
			],
			sidebar: [
				{
					label: 'Getting Started',
					items: [
						{ label: 'Introduction', slug: 'getting-started/introduction' },
						{ label: 'Quick Start', slug: 'getting-started/quickstart' },
						{ label: 'Installation', slug: 'getting-started/installation' },
					],
				},
				{
					label: 'Core Concepts',
					items: [
						{ label: 'Overview', slug: 'core-concepts/overview' },
						{ label: 'Functors', slug: 'core-concepts/functors' },
						{ label: 'Monads', slug: 'core-concepts/monads' },
						{ label: 'Comonads', slug: 'core-concepts/comonads' },
						{ label: 'Quality Scores', slug: 'core-concepts/quality-scores' },
						{ label: 'Composition', slug: 'core-concepts/composition' },
					],
				},
				{
					label: 'Commands',
					items: [
						{ label: 'Overview', slug: 'commands/overview' },
						{ label: '/meta', slug: 'commands/meta' },
						{ label: '/rmp', slug: 'commands/rmp' },
						{ label: '/chain', slug: 'commands/chain' },
					],
				},
				{
					label: 'Examples',
					items: [
						{ label: 'Game of 24', slug: 'examples/game-of-24' },
						{ label: 'Code Generation', slug: 'examples/code-generation' },
					],
				},
				{
					label: 'Reference',
					autogenerate: { directory: 'reference' },
				},
			],
		}),
	],
});
