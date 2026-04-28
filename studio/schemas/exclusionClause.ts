export default {
  name: 'exclusionClause',
  title: 'Exclusion Clause',
  type: 'document',
  fields: [
    {
      name: 'parentLegalDefinition',
      title: 'Parent Legal Definition',
      type: 'reference',
      to: [{ type: 'legalDefinition' }],
      validation: (Rule: any) => Rule.required(),
    },
    {
      name: 'excludes',
      title: 'What Is Excluded',
      type: 'array',
      of: [{ type: 'string' }],
      options: {
        list: ['exploration', 'affirmation', 'transition_care', 'mental_disorder_treatment', 'reflective_practice'],
      },
    },
    { name: 'textExcerpt', title: 'Text Excerpt (verbatim from law)', type: 'text', rows: 4 },
    {
      name: 'interpretationRisks',
      title: 'Interpretation Risks',
      type: 'text',
      rows: 3,
      description: 'How this exclusion has been or could be exploited by pro-SOGICE actors.',
    },
    { name: 'usedInPolicyArguments', type: 'boolean', initialValue: false },
    { name: 'policyArgumentDescription', title: 'Policy Argument Description', type: 'text', rows: 3 },
  ],

  preview: {
    select: {
      title: 'textExcerpt',
      subtitle: 'parentLegalDefinition.instrumentName',
    },
  },
}
