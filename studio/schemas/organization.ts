export default {
  name: 'organization',
  title: 'Organization',
  type: 'document',
  fields: [
    { name: 'name', type: 'string', validation: (Rule: any) => Rule.required() },
    {
      name: 'formerNames',
      title: 'Former Names',
      type: 'array',
      of: [{
        type: 'object',
        fields: [
          { name: 'name', type: 'string' },
          { name: 'fromYear', type: 'number' },
          { name: 'toYear', type: 'number' },
        ],
      }],
    },
    {
      name: 'type',
      type: 'string',
      options: {
        list: [
          'ministry', 'therapy_practice', 'advocacy', 'academic', 'media',
          'government', 'network_node', 'pseudo-professional-body',
          'political_party', 'church', 'legal', 'monitoring', 'other',
        ],
      },
    },
    { name: 'country', title: 'Country (ISO 3166-1)', type: 'string' },
    { name: 'foundedYear', type: 'number' },
    { name: 'dissolvedYear', type: 'number' },
    { name: 'parentOrganization', type: 'reference', to: [{ type: 'organization' }] },
    { name: 'fundingSources', type: 'array', of: [{ type: 'string' }] },
    {
      name: 'affiliatedOrganizations',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'organization' }] }],
    },
    { name: 'description', type: 'text', rows: 5 },
    {
      name: 'visibility',
      type: 'string',
      options: { list: ['public', 'research_contextualized', 'internal_only'] },
      initialValue: 'public',
    },
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
    select: { title: 'name', subtitle: 'type' },
  },
}
