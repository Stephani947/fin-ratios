import { describe, it, expect } from 'vitest'
import { normalizeForScoring, type EdgarFilingData } from '../fetchers/edgar/index.js'

function makeFilings(overrides: Partial<EdgarFilingData>[] = []): EdgarFilingData[] {
  const base = (): EdgarFilingData => ({
    fiscalYear: '2023',
    income: {
      revenue: 400e9, grossProfit: 170e9, cogs: 230e9,
      ebit: 110e9, ebitda: 125e9, netIncome: 97e9,
      interestExpense: 3e9, incomeTaxExpense: 29e9, ebt: 126e9,
      depreciationAndAmortization: 15e9, sharesOutstanding: 15.4e9, eps: 6.3,
    },
    balance: {
      totalAssets: 352e9, currentAssets: 135e9, cash: 62e9,
      accountsReceivable: 29e9, inventory: 7e9, netPPE: 0, goodwill: 0,
      retainedEarnings: 0, totalLiabilities: 278e9, currentLiabilities: 145e9,
      accountsPayable: 62e9, longTermDebt: 106e9, totalDebt: 111e9,
      totalEquity: 74e9, sharesOutstanding: 15.4e9,
    },
    cashFlow: {
      operatingCashFlow: 114e9, capex: 11e9,
      investingCashFlow: 0, financingCashFlow: 0,
      dividendsPaid: 15e9,
    },
  })

  if (overrides.length === 0) return [base()]
  return overrides.map(o => ({ ...base(), ...o }))
}

describe('normalizeForScoring', () => {
  it('reverses filings to oldest-first order', () => {
    const filings = [
      { ...makeFilings()[0]!, fiscalYear: '2023' },
      { ...makeFilings()[0]!, fiscalYear: '2022' },
      { ...makeFilings()[0]!, fiscalYear: '2021' },
    ]
    const records = normalizeForScoring(filings)
    expect(records[0]!.year).toBe('2021')
    expect(records[1]!.year).toBe('2022')
    expect(records[2]!.year).toBe('2023')
  })

  it('maps revenue correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.revenue).toBe(400e9)
  })

  it('maps grossProfit correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.grossProfit).toBe(170e9)
  })

  it('maps ebit correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.ebit).toBe(110e9)
  })

  it('maps netIncome correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.netIncome).toBe(97e9)
  })

  it('maps operatingCashFlow correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.operatingCashFlow).toBe(114e9)
  })

  it('maps capex correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.capex).toBe(11e9)
  })

  it('maps depreciation correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.depreciation).toBe(15e9)
  })

  it('maps dividendsPaid correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.dividendsPaid).toBe(15e9)
  })

  it('maps sharesOutstanding correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.sharesOutstanding).toBe(15.4e9)
  })

  it('maps totalDebt correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.totalDebt).toBe(111e9)
  })

  it('maps currentAssets and currentLiabilities', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.currentAssets).toBe(135e9)
    expect(records[0]!.currentLiabilities).toBe(145e9)
  })

  it('maps accountsReceivable correctly', () => {
    const records = normalizeForScoring(makeFilings())
    expect(records[0]!.accountsReceivable).toBe(29e9)
  })

  it('handles zero depreciation gracefully', () => {
    const f = makeFilings()[0]!
    f.income.depreciationAndAmortization = 0
    const records = normalizeForScoring([f])
    expect(records[0]!.depreciation).toBe(0)
  })

  it('handles zero dividends gracefully', () => {
    const f = makeFilings()[0]!
    f.cashFlow.dividendsPaid = 0
    const records = normalizeForScoring([f])
    expect(records[0]!.dividendsPaid).toBe(0)
  })

  it('flattenEdgarData is aliased to normalizeForScoring', async () => {
    const { flattenEdgarData } = await import('../fetchers/edgar/index.js')
    const records = flattenEdgarData(makeFilings())
    expect(records[0]!.revenue).toBe(400e9)
  })
})
