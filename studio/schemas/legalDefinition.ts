export default {
  name: 'legalDefinition',
  title: 'Legal Definition',
  type: 'document',
  fields: [
    {
      name: 'jurisdiction',
      title: 'Jurisdiction (ISO 3166-1 + subnational if needed)',
      type: 'string',
      validation: (Rule: any) => Rule.required(),
    },
    {
      name: 'instrumentType',
      type: 'string',
      options: { list: ['law', 'regulation', 'guidance', 'resolution', 'policy', 'memorandum'] },
    },
    { name: 'instrumentName', type: 'string' },
    { name: 'yearEnacted', type: 'number' },
    { name: 'yearInForce', type: 'number' },
    { name: 'termUsed', title: 'Term Used (exact text from the law)', type: 'string' },
    {
      name: 'targetDimensions',
      title: 'Target Dimensions',
      type: 'array',
      of: [{ type: 'string' }],
      options: {
        list: ['sexual_orientation', 'gender_identity', 'gender_expression', 'sex_characteristics'],
      },
    },
    {
      name: 'goalVerbs',
      title: 'Goal Verbs',
      type: 'array',
      of: [{ type: 'string' }],
      options: {
        list: ['change', 'suppress', 'repress', 'discourage', 'deter', 'modify', 'eliminate', 'align_to_assigned_sex'],
      },
    },
    {
      name: 'scopeForm',
      title: 'Scope Form',
      type: 'string',
      options: {
        list: ['any treatment', 'practices and efforts', 'repeated practices/behaviours/statements', 'other'],
      },
    },
    { name: 'harmThreshold', type: 'boolean', initialValue: false },
    { name: 'harmThresholdDescription', type: 'string' },
    { name: 'consentOverride', type: 'boolean', initialValue: false },
    { name: 'ageSpecificProvisions', type: 'text', rows: 3 },
    { name: 'modalityExamplesListed', type: 'boolean', initialValue: false },
    {
      name: 'exclusions',
      title: 'Exclusion Clauses',
      type: 'array',
      of: [{ type: 'reference', to: [{ type: 'exclusionClause' }] }],
    },
    {
      name: 'status',
      type: 'string',
      options: { list: ['enacted', 'defeated', 'pending', 'challenged', 'amended'] },
    },
    { name: 'sourceUrl', type: 'url' },
    {
      name: 'parentLawPolicy',
      title: 'Parent Law/Policy',
      type: 'reference',
      to: [{ type: 'lawPolicy' }],
    },
  ],

  preview: {
    select: { title: 'instrumentName', subtitle: 'jurisdiction' },
  },
}
