// ─────────────────────────────────────────────────────────────
//  Site settings — edit these to change names, links and the form.
// ─────────────────────────────────────────────────────────────
export const site = {
  name: 'Hit12me Photography',
  shortName: 'Hit12me',
  owner: 'Dustin Heath',
  tagline: 'Finding beauty in the ordinary',
  description:
    'Landscape, wildlife, astro, portrait and sports photography by Dustin Heath — stories and galleries from National Parks, ballparks and everywhere in between.',
  email: 'dustin.heath@hit12mephotography.com',
  instagram: 'https://www.instagram.com/jaffacree/',
  instagramHandle: '@jaffacree',

  // Free contact-form delivery from https://web3forms.com
  // 1. Enter your email there and they send you an "Access Key".
  // 2. Paste it between the quotes below. Messages then arrive in your inbox.
  web3formsKey: '',
};

export const sections = {
  blog: {
    label: 'Journal',
    title: 'Journal',
    path: '/blog',
    blurb: 'National Parks, road trips, portraits and the stories behind the shots.',
  },
  sports: {
    label: 'Sports',
    title: 'Sports',
    path: '/sports-photo-blog',
    blurb: 'From the photo well and the press box — baseball, basketball, football and more.',
  },
} as const;

export type SectionKey = keyof typeof sections;
