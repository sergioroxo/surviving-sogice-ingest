export default {
  name: 'event',
  title: 'Event',
  type: 'document',
  fields: [
    { name: 'name', type: 'string', validation: (Rule: any) => Rule.required() },
    {
      name: 'type',
      type: 'string',
      options: {
        list: [
          'conference', 'court_case', 'media_event', 'publication', 'legislation',
          'network_formation', 'investigation', 'organizational_founding',
          'academic_publication', 'political_campaign', 'other',
        ],
      },
    },
    { name: 'date', type: 'date' },
    {
      name: 'actorsInvolved',
      title: 'Actors Involved',
      type: 'array',
      of: [
        { type: 'reference', to: [{ type: 'person' }] },
        { type: 'reference', to: [{ type: 'organization' }] },
      ],
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
      of: [{ type: 'reference', to: [{ type: 'document' }] }],
    },
    {
      name: 'registryStatus',
      type: 'string',
      options: { list: ['seeded', 'confirmed'] },
      initialValue: 'seeded',
    },
  ],

  preview: {
    select: { title: 'name', subtitle: 'type' },
  },
}
