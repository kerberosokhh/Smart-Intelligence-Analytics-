export type ChartType = 'bar' | 'line' | 'pie' | 'scatter' | 'table'

export interface ChartSpec {
  type: ChartType
  title?: string
  xField?: string
  yField?: string | string[]
  seriesField?: string
  data: Record<string, unknown>[]
}
