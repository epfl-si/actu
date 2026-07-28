import neostandard from 'neostandard'

export default [
  {
    ignores: ['src/static', 'ansible/ansible-deps-cache'],
  },
  ...neostandard({}),
  {
    rules: {
      '@stylistic/comma-dangle': ['error', 'always-multiline'],
    },
  },
]
