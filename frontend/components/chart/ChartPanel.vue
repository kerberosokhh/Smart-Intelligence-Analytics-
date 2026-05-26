<script setup lang="ts">
const { spec, queryData, hasChart } = useChartSpec()

const tableColumns = computed(() => {
  if (!queryData.value?.length) return []
  return Object.keys(queryData.value[0] ?? {})
})
</script>

<template>
  <div class="chart-panel">
    <div class="chart-card">
      <ChartRenderer :spec="spec" />
    </div>

    <div v-if="hasChart && queryData?.length" class="data-preview">
      <div class="preview-header">
        <span class="preview-dot" />
        <h4 class="preview-title">数据预览</h4>
      </div>
      <el-table :data="queryData" size="small" max-height="200" stripe>
        <el-table-column
          v-for="col in tableColumns"
          :key="col"
          :prop="col"
          :label="col"
          min-width="90"
        />
      </el-table>
    </div>
  </div>
</template>

<style scoped>
.chart-panel {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.chart-card {
  padding: 8px;
  border-radius: var(--tech-radius-sm);
  background: rgba(255, 255, 255, 0.5);
  border: 1px solid var(--tech-border);
}

.data-preview {
  border-top: 1px solid var(--tech-border);
  padding-top: 14px;
}

.preview-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
}

.preview-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: var(--tech-accent-3);
  box-shadow: 0 0 6px rgba(6, 182, 212, 0.5);
}

.preview-title {
  margin: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--tech-text-secondary);
  letter-spacing: 0.02em;
}
</style>
