export default {
  name: 'promptVersion',
  title: 'Prompt Version',
  type: 'document',
  fields: [
    {
      name: 'versionId',
      title: 'Version ID (e.g. ingestion-v3.1)',
      type: 'string',
      validation: (Rule: any) => Rule.required(),
    },
    {
      name: 'type',
      title: 'Prompt Type',
      type: 'string',
      options: { list: ['ingestion', 'validation', 'lexicon_validation'] },
    },
    { name: 'targetModel', title: 'Target Model (or "model-agnostic")', type: 'string' },
    { name: 'createdAt', type: 'datetime' },
    {
      name: 'active',
      title: 'Active (used for new documents)',
      type: 'boolean',
      initialValue: false,
    },
    { name: 'ontologyVersion', title: 'Ontology Version (at time of prompt creation)', type: 'string' },
    { name: 'systemPrompt', title: 'System Prompt (full text)', type: 'text', rows: 30 },
    { name: 'changesSummary', title: 'Changes from Previous Version', type: 'text', rows: 4 },
    { name: 'notes', type: 'text', rows: 3 },
  ],

  preview: {
    select: { title: 'versionId', subtitle: 'type' },
  },
}
