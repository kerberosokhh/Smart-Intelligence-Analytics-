import type { ChartSpec } from '~/types/chart'
import { useAppStore } from '~/stores/app'

export function useChartSpec() {
  const store = useAppStore()

  const hasChart = computed(() => store.chartSpec !== null)
  const spec = computed(() => store.chartSpec)
  const queryData = computed(() => store.queryData)

  function applyChartSpec(next: ChartSpec | null) {
    store.setChartSpec(next)
    if (next?.data?.length) {
      store.setQueryData(next.data)
    }
  }

  return {
    hasChart,
    spec,
    queryData,
    applyChartSpec,
  }
}
