import { use } from 'echarts/core'
import { BarChart, LineChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  LegendComponent,
  TitleComponent,
  TooltipComponent,
} from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import VChart from 'vue-echarts'

/** Phase 1：注册 vue-echarts 组件，Phase 2 在 ChartRenderer 中使用 */
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
])

export default defineNuxtPlugin(() => {
  // 预注册依赖，确保 Phase 2 图表模块可直接 import VChart
  void VChart
})
