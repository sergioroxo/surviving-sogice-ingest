export default {
  name: 'validationBatch',
  title: 'Validation Batch',
  type: 'document',
  fields: [
    {
      name: 'batchId',
      title: 'Batch ID (e.g. val-batch-01)',
      type: 'string',
      validation: (Rule: any) => Rule.required(),
    },
    {
      name: 'composition',
      title: 'Batch Composition',
      type: 'object',
      fields: [
        { name: 'mandatory', title: 'Mandatory Documents', type: 'string', options: { list: ['all'] }, initialValue: 'all' },
        { name: 'recommendedPercentage', title: 'Recommended % (medium-confidence)', type: 'number' },
        { name: 'randomAuditPercentage', title: 'Random Audit % (high-confidence)', type: 'number' },
      ],
    },
    {
      name: 'documentsIncluded',
      title: 'Documents Included',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'sogiceDocument' }] }],
    },
    {
      name: 'manualTriggerDocuments',
      title: 'Manually Triggered Documents',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'sogiceDocument' }] }],
    },
    {
      name: 'status',
      type: 'string',
      options: { list: ['configured', 'exported', 'imported', 'resolved'] },
      initialValue: 'configured',
    },
    { name: 'createdAt', type: 'datetime' },
    { name: 'exportedAt', type: 'datetime' },
    { name: 'importedAt', type: 'datetime' },
    { name: 'resolvedAt', type: 'datetime' },
    { name: 'validationModel', title: 'Validation Model Used', type: 'string' },
    {
      name: 'validationProvider',
      type: 'string',
      options: { list: ['openai', 'anthropic', 'google', 'local', 'manual_paste', 'other'] },
    },
    {
      name: 'promptVersionRef',
      title: 'Validation Prompt Version',
      type: 'reference',
      to: [{ type: 'promptVersion' }],
    },
    { name: 'notes', type: 'text', rows: 3 },
  ],

  preview: {
    select: { title: 'batchId', subtitle: 'status' },
  },
}
