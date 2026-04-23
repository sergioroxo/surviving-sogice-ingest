export default {
  name: 'lawPolicy',
  title: 'Law / Policy',
  type: 'document',
  fields: [
    { name: 'name', type: 'string', validation: (Rule: any) => Rule.required() },
    { name: 'country', title: 'Country (ISO 3166-1)', type: 'string' },
    { name: 'year', type: 'number' },
    {
      name: 'status',
      type: 'string',
      options: { list: ['enacted', 'defeated', 'pending', 'challenged', 'amended'] },
    },
    {
      name: 'appliesTo',
      title: 'Applies To',
      type: 'string',
      options: { list: ['ban', 'protection', 'restriction', 'definition', 'consultation'] },
    },
    { name: 'description', type: 'text', rows: 5 },
    {
      name: 'historicalSignificance',
      type: 'string',
      options: { list: ['high', 'medium', 'low'] },
    },
    {
      name: 'sourceDocuments',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'sogiceDocument' }] }],
    },
    {
      name: 'legalDefinitions',
      title: 'Associated Legal Definitions',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'legalDefinition' }] }],
    },
    {
      name: 'registryStatus',
      type: 'string',
      options: { list: ['seeded', 'confirmed'] },
      initialValue: 'seeded',
    },
  ],

  preview: {
    select: { title: 'name', subtitle: 'country' },
  },
}
