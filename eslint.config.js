import neostandard from 'neostandard'

export default [
  ...neostandard({}),
  {
    languageOptions: {
      globals: {
        $: 'readonly',
        jQuery: 'readonly',
      },
    },
    rules: {
      '@stylistic/comma-dangle': ['error', 'always-multiline'],
    },
  },
]
