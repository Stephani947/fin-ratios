import { defineConfig } from 'tsup'

export default defineConfig({
  entry: {
    index:                       'src/index.ts',
    'fetchers/yahoo/index':      'src/fetchers/yahoo/index.ts',
    'fetchers/fmp/index':        'src/fetchers/fmp/index.ts',
    'fetchers/edgar/index':      'src/fetchers/edgar/index.ts',
    'fetchers/alphavantage/index': 'src/fetchers/alphavantage/index.ts',
    'fetchers/polygon/index':    'src/fetchers/polygon/index.ts',
    'hooks/index':               'src/hooks/index.ts',
  },
  format: ['esm', 'cjs'],
  dts: true,
  sourcemap: false,
  clean: true,
  splitting: false,
  treeshake: true,
  minify: false,
  target: 'es2020',
  external: ['react'],
})
