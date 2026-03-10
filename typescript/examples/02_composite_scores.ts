/**
 * TypeScript Example: Composite Scoring Systems
 * ================================================
 * Run: npx ts-node examples/02_composite_scores.ts
 * Or compile: tsc && node dist/examples/02_composite_scores.js
 */

import {
  piotroskiFScore,
  altmanZScore,
  beneishMScore,
  magicFormula,
  ohlsonOScore,
} from '../src/index.js'

// ── Piotroski F-Score ─────────────────────────────────────────────────────────
console.log('\n=== PIOTROSKI F-SCORE ===')
console.log('Reference: Piotroski (2000) Journal of Accounting Research\n')

const strongCompany = piotroskiFScore({
  current: {
    netIncome: 8_500_000,
    totalAssets: 100_000_000,
    operatingCashFlow: 12_000_000,     // CF > NI = quality earnings
    longTermDebt: 20_000_000,          // Reduced from prior year
    currentAssets: 35_000_000,
    currentLiabilities: 15_000_000,
    sharesOutstanding: 10_000_000,
    grossProfit: 45_000_000,
    revenue: 90_000_000,
  },
  prior: {
    netIncome: 5_000_000,
    totalAssets: 95_000_000,
    longTermDebt: 25_000_000,
    currentAssets: 28_000_000,
    currentLiabilities: 14_000_000,
    sharesOutstanding: 10_500_000,
    grossProfit: 38_000_000,
    revenue: 80_000_000,
  },
})

console.log(`Strong Company F-Score: ${strongCompany.score}/9`)
console.log(`Interpretation: ${strongCompany.interpretation}`)
console.log('Signals:')
Object.entries(strongCompany.signals).forEach(([k, v]) => {
  console.log(`  ${v ? '✓' : '✗'} ${k}`)
})

const weakCompany = piotroskiFScore({
  current: {
    netIncome: -2_000_000,             // Negative ROA
    totalAssets: 100_000_000,
    operatingCashFlow: -500_000,       // Negative OCF
    longTermDebt: 45_000_000,          // More debt
    currentAssets: 18_000_000,
    currentLiabilities: 15_000_000,
    sharesOutstanding: 12_000_000,     // Dilution
    grossProfit: 20_000_000,
    revenue: 80_000_000,
  },
  prior: {
    netIncome: 3_000_000,
    totalAssets: 95_000_000,
    longTermDebt: 30_000_000,
    currentAssets: 25_000_000,
    currentLiabilities: 12_000_000,
    sharesOutstanding: 10_000_000,
    grossProfit: 28_000_000,
    revenue: 90_000_000,
  },
})

console.log(`\nWeak Company F-Score: ${weakCompany.score}/9`)
console.log(`Interpretation: ${weakCompany.interpretation}`)


// ── Altman Z-Score ────────────────────────────────────────────────────────────
console.log('\n=== ALTMAN Z-SCORE ===')
console.log('Reference: Altman (1968) Journal of Finance\n')
console.log('Safe > 2.99 | Grey 1.81-2.99 | Distress < 1.81\n')

const scenarios = [
  { name: 'Healthy Tech', wc: 500e6, re: 200e6, ebit: 90e6, mc: 3000e6, tl: 210e6, ta: 411e6, rev: 212e6 },
  { name: 'Grey Zone',    wc: 30e6,  re: 15e6,  ebit: 8e6,  mc: 120e6,  tl: 80e6,  ta: 180e6, rev: 160e6 },
  { name: 'Distress',     wc: -20e6, re: -50e6, ebit: -5e6, mc: 80e6,   tl: 200e6, ta: 250e6, rev: 150e6 },
]

for (const s of scenarios) {
  const z = altmanZScore({
    workingCapital: s.wc,
    retainedEarnings: s.re,
    ebit: s.ebit,
    marketCap: s.mc,
    totalLiabilities: s.tl,
    totalAssets: s.ta,
    revenue: s.rev,
  })
  if (z) {
    const icon = z.zone === 'safe' ? '✅' : z.zone === 'grey' ? '⚠️' : '🚨'
    console.log(`${icon} ${s.name}: Z=${z.z.toFixed(2)} (${z.zone})  — ${z.interpretation}`)
  }
}


// ── Beneish M-Score ───────────────────────────────────────────────────────────
console.log('\n=== BENEISH M-SCORE ===')
console.log('Reference: Beneish (1999) Financial Analysts Journal')
console.log('Threshold: M > -2.22 = possible earnings manipulation\n')

// Clean company
const clean = beneishMScore({
  current: {
    revenue: 100e6, accountsReceivable: 12e6, grossProfit: 40e6,
    totalAssets: 150e6, depreciation: 8e6, ppGross: 50e6,
    sgaExpense: 15e6, totalDebt: 30e6, netIncome: 8e6, cashFlowFromOps: 11e6,
  },
  prior: {
    revenue: 90e6, accountsReceivable: 10e6, grossProfit: 35e6,
    totalAssets: 140e6, depreciation: 7e6, ppGross: 45e6,
    sgaExpense: 14e6, totalDebt: 30e6,
  },
})

if (clean) {
  console.log(`Clean Company:  M=${clean.mScore.toFixed(2)} → ${clean.manipulationLikely ? '⚠️ FLAGGED' : '✅ Clean'}`)
  console.log(`  ${clean.interpretation}`)
}

// Suspicious company
const suspicious = beneishMScore({
  current: {
    revenue: 110e6, accountsReceivable: 25e6,  // AR grew much faster
    grossProfit: 38e6, totalAssets: 155e6,
    depreciation: 6e6,                          // Slowing depreciation
    ppGross: 55e6, sgaExpense: 20e6,
    totalDebt: 45e6, netIncome: 12e6,
    cashFlowFromOps: 3e6,                        // Low OCF vs NI = high accruals
  },
  prior: {
    revenue: 90e6, accountsReceivable: 10e6, grossProfit: 38e6,
    totalAssets: 140e6, depreciation: 8e6, ppGross: 45e6,
    sgaExpense: 14e6, totalDebt: 30e6,
  },
})

if (suspicious) {
  console.log(`\nSuspicious Co:  M=${suspicious.mScore.toFixed(2)} → ${suspicious.manipulationLikely ? '⚠️ FLAGGED — Possible manipulation' : '✅ Clean'}`)
  console.log(`  DSRI=${suspicious.variables.dsri.toFixed(2)} GMI=${suspicious.variables.gmi.toFixed(2)} TATA=${suspicious.variables.tata.toFixed(3)}`)
}


// ── Magic Formula ─────────────────────────────────────────────────────────────
console.log('\n=== GREENBLATT MAGIC FORMULA ===')
console.log('Reference: Greenblatt (2005) The Little Book That Beats the Market\n')
console.log('Strategy: Rank all stocks by ROIC + Earnings Yield. Buy top 20-30.\n')

const stocks = [
  { name: 'AutoZone-like',   ebit: 2.8e9, nwc: 6e9,  nfa: 1.5e9, ev: 15e9   },
  { name: 'Capital-light',   ebit: 3e9,   nwc: 0.5e9, nfa: 0.3e9, ev: 40e9  },
  { name: 'Heavy industry',  ebit: 0.5e9, nwc: 2e9,   nfa: 8e9,   ev: 8e9   },
  { name: 'High-growth tech',ebit: 50e9,  nwc: 20e9,  nfa: 5e9,   ev: 1200e9},
]

for (const s of stocks) {
  const r = magicFormula({
    ebit: s.ebit,
    netWorkingCapital: s.nwc,
    netFixedAssets: s.nfa,
    enterpriseValue: s.ev,
  })
  const roicStr = r.roic != null ? `${(r.roic * 100).toFixed(1)}%` : 'N/A'
  const eyStr = r.evEbit != null ? `${(1 / r.evEbit * 100).toFixed(1)}%` : 'N/A'
  console.log(`  ${s.name.padEnd(20)} ROIC=${roicStr.padStart(8)}  Earnings Yield=${eyStr.padStart(8)}`)
}
