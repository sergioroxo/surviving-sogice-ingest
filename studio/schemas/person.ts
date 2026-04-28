export default {
  name: 'person',
  title: 'Person',
  type: 'document',
  fields: [
    { name: 'name', type: 'string', validation: (Rule: any) => Rule.required() },
    { name: 'formerNames', title: 'Former Names', type: 'array', of: [{ type: 'string' }] },
    {
      name: 'role',
      type: 'string',
      options: {
        list: ['founder', 'leader', 'influencer', 'therapist', 'pastor', 'survivor', 'researcher', 'politician', 'other'],
      },
    },
    {
      name: 'affiliatedOrganizations',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'organization' }] }],
    },
    { name: 'countryOfOperation', title: 'Country of Operation (ISO 3166-1)', type: 'string' },
    { name: 'languages', type: 'array', of: [{ type: 'string' }] },
    { name: 'publicProfile', type: 'boolean', initialValue: true },
    {
      name: 'contestedFigure',
      title: 'Contested Figure',
      type: 'boolean',
      initialValue: false,
      description: 'True for researchers cited by both pro- and anti-SOGICE actors.',
    },
    { name: 'contestedFigureNote', type: 'text', rows: 3 },
    { name: 'description', type: 'text', rows: 4 },
    {
      name: 'sourceDocuments',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'sogiceDocument' }] }],
    },
    {
      name: 'registryStatus',
      type: 'string',
      options: { list: ['seeded', 'confirmed', 'under_investigation'] },
      initialValue: 'seeded',
    },
  ],

  preview: {
    select: { title: 'name', subtitle: 'role' },
  },
}
