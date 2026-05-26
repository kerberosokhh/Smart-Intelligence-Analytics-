import type { ChartSpec } from '~/types/chart'
import type { Message } from '~/types/message'
import type { Session } from '~/types/session'
import { createId } from '~/utils/id'

const now = () => new Date().toISOString()

export const MOCK_SESSIONS: Session[] = [
  {
    id: 'session-demo-1',
    title: '各品类销售分析',
    createdAt: '2026-05-24T10:00:00.000Z',
    updatedAt: '2026-05-24T10:05:00.000Z',
  },
  {
    id: 'session-demo-2',
    title: '华东区域订单',
    createdAt: '2026-05-23T14:00:00.000Z',
    updatedAt: '2026-05-23T14:30:00.000Z',
  },
]

export const MOCK_MESSAGES: Record<string, Message[]> = {
  'session-demo-1': [
    {
      id: 'msg-1',
      sessionId: 'session-demo-1',
      role: 'user',
      content: '各品类销售总额是多少？',
      createdAt: '2026-05-24T10:01:00.000Z',
    },
    {
      id: 'msg-2',
      sessionId: 'session-demo-1',
      role: 'assistant',
      content:
        '已为您统计各品类销售总额。电子产品最高，其次是家居与服饰。下方图表展示了品类维度的汇总结果。',
      sql: `SELECT category, SUM(amount) AS total_sales
FROM biz_orders
GROUP BY category
ORDER BY total_sales DESC`,
      createdAt: '2026-05-24T10:02:00.000Z',
    },
  ],
  'session-demo-2': [],
}

export const MOCK_CATEGORY_SALES: Record<string, unknown>[] = [
  { category: '电子产品', total_sales: 128000 },
  { category: '家居', total_sales: 86000 },
  { category: '服饰', total_sales: 72000 },
  { category: '食品', total_sales: 54000 },
]

export const DEMO_CHART_SPEC: ChartSpec = {
  type: 'bar',
  title: '各品类销售总额',
  xField: 'category',
  yField: 'total_sales',
  data: MOCK_CATEGORY_SALES,
}

export function createEmptySession(title = '新会话'): Session {
  const ts = now()
  return {
    id: createId(),
    title,
    createdAt: ts,
    updatedAt: ts,
  }
}
