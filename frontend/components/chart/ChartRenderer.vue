<script setup lang="ts">
import type { ChartSpec } from '~/types/chart'
import VChart from 'vue-echarts'

const props = defineProps<{
  spec: ChartSpec | null
}>()

const option = computed(() => {
  const spec = props.spec
  if (!spec || spec.type === 'table' || !spec.data?.length) return null

  const xField = spec.xField ?? Object.keys(spec.data[0] ?? {})[0]
  const yField = Array.isArray(spec.yField)
    ? spec.yField[0]
    : spec.yField ?? Object.keys(spec.data[0] ?? {})[1]

  if (!xField || !yField) return null

  const categories = spec.data.map((row) => String(row[xField] ?? ''))
  const values = spec.data.map((row) => Number(row[yField] ?? 0))

  if (spec.type === 'pie') {
    return {
      title: spec.title ? { text: spec.title, left: 'center' } : undefined,
      tooltip: { trigger: 'item' },
      series: [
        {
          type: 'pie',
          radius: '60%',
          data: spec.data.map((row) => ({
            name: String(row[xField] ?? ''),
            value: Number(row[yField] ?? 0),
          })),
        },
      ],
    }
  }

  const chartType = spec.type === 'line' ? 'line' : 'bar'

  return {
    title: spec.title
      ? {
          text: spec.title,
          left: 'center',
          textStyle: { color: '#0f172a', fontSize: 14, fontWeight: 600 },
        }
      : undefined,
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(255,255,255,0.95)',
      borderColor: 'rgba(14,165,233,0.2)',
      textStyle: { color: '#334155' },
    },
    grid: { left: 48, right: 24, bottom: 48, top: spec.title ? 48 : 24 },
    xAxis: {
      type: 'category',
      data: categories,
      axisLabel: { rotate: categories.some((c) => c.length > 4) ? 20 : 0, color: '#64748b' },
      axisLine: { lineStyle: { color: 'rgba(14,165,233,0.2)' } },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#64748b' },
      splitLine: { lineStyle: { color: 'rgba(14,165,233,0.08)' } },
    },
    series: [
      {
        type: chartType,
        data: values,
        smooth: chartType === 'line',
        itemStyle: {
          color: {
            type: 'linear',
            x: 0,
            y: 0,
            x2: 0,
            y2: 1,
            colorStops: [
              { offset: 0, color: '#0ea5e9' },
              { offset: 1, color: '#6366f1' },
            ],
          },
          borderRadius: chartType === 'bar' ? [6, 6, 0, 0] : 0,
        },
        areaStyle: chartType === 'line'
          ? {
              color: {
                type: 'linear',
                x: 0,
                y: 0,
                x2: 0,
                y2: 1,
                colorStops: [
                  { offset: 0, color: 'rgba(14,165,233,0.25)' },
                  { offset: 1, color: 'rgba(99,102,241,0.02)' },
                ],
              },
            }
          : undefined,
      },
    ],
  }
})

const tableColumns = computed(() => {
  const spec = props.spec
  if (!spec?.data?.length) return []
  return Object.keys(spec.data[0] ?? {})
})
</script>

<template>
  <div class="chart-renderer">
    <div v-if="!spec" class="empty">
      <div class="empty-chart-icon">▣</div>
      <p class="empty-text">暂无图表</p>
      <span class="empty-hint">发送分析问题后将自动生成可视化</span>
    </div>

    <template v-else-if="spec.type === 'table' || !option">
      <h3 v-if="spec.title" class="chart-title">{{ spec.title }}</h3>
      <el-table :data="spec.data" size="small" stripe style="width: 100%">
        <el-table-column
          v-for="col in tableColumns"
          :key="col"
          :prop="col"
          :label="col"
          min-width="100"
        />
      </el-table>
    </template>

    <VChart v-else class="echart" :option="option" autoresize />
  </div>
</template>

<style scoped>
.chart-renderer {
  height: 100%;
  min-height: 240px;
}

.echart {
  width: 100%;
  height: 280px;
}

.chart-title {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 600;
}

.empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  min-height: 240px;
  text-align: center;
  padding: 24px;
}

.empty-chart-icon {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  color: var(--tech-accent-2);
  background: var(--tech-gradient-soft);
  border: 1px solid var(--tech-border);
  border-radius: 16px;
  margin-bottom: 12px;
}

.empty-text {
  margin: 0 0 4px;
  font-weight: 600;
  color: var(--tech-text-secondary);
}

.empty-hint {
  font-size: 12px;
  color: var(--tech-text-muted);
}
</style>
