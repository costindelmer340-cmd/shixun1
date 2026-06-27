<template>
  <div class="panel">
    <div class="toolbar">
      <el-segmented v-model="status" :options="filterOptions" />
      <el-button type="primary" @click="batchApprove">批量审核</el-button>
    </div>
    <el-table v-loading="loading" :data="filteredAfterSales">
      <el-table-column prop="afterSaleNo" label="售后单号" min-width="170" />
      <el-table-column label="类型" width="140">
        <template #default="{ row }">{{ labelText.afterSaleType[row.afterSaleType] || row.afterSaleType }}</template>
      </el-table-column>
      <el-table-column label="原因" width="160">
        <template #default="{ row }">{{ labelText.reason[row.reasonType] || row.reasonType }}</template>
      </el-table-column>
      <el-table-column prop="requestedAmount" label="申请金额" width="110" />
      <el-table-column label="状态" width="140">
        <template #default="{ row }">{{ labelText.status[row.status] || row.status }}</template>
      </el-table-column>
      <el-table-column label="优先级" width="100">
        <template #default="{ row }">{{ labelText.priority[row.priority] || row.priority }}</template>
      </el-table-column>
      <el-table-column prop="reviewOpinion" label="审核意见" min-width="190" />
      <el-table-column label="回写状态" width="130">
        <template #default="{ row }">{{ labelText.writeBack[row.writeBackStatus] || row.writeBackStatus }}</template>
      </el-table-column>
      <el-table-column prop="createdAt" label="创建时间" min-width="160" />
      <el-table-column label="操作" width="160">
        <template #default="{ row }">
          <el-button link type="primary" @click="openReview(row)">审核</el-button>
          <el-button link @click="writeBackAfterSale(row.id)">回写</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="reviewVisible" title="售后审核" width="520px">
      <el-form label-width="88px">
        <el-form-item label="审核结果">
          <el-radio-group v-model="reviewForm.result">
            <el-radio-button label="APPROVE">同意</el-radio-button>
            <el-radio-button label="REJECT">拒绝</el-radio-button>
          </el-radio-group>
        </el-form-item>
        <el-form-item v-if="reviewForm.result === 'REJECT'" label="拒绝原因">
          <el-input
            v-model="reviewForm.reason"
            type="textarea"
            :rows="4"
            placeholder="请输入拒绝售后申请的具体原因"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="reviewVisible = false">取消</el-button>
        <el-button type="primary" @click="submitReview">确认</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { afterSales } from '../data/mock'
import { loadAfterSales } from '../api'
import { loadListWithFallback } from '../api/normalize'
import { ElMessage } from 'element-plus'

const status = ref('全部')
const afterSalesData = ref<typeof afterSales>([])
const loading = ref(false)
const reviewVisible = ref(false)
const reviewingId = ref<number | null>(null)
const reviewForm = ref({ result: 'APPROVE', reason: '' })
const filterOptions = [
  { label: '全部', value: '全部' },
  { label: '待审核', value: 'PENDING_REVIEW' },
  { label: '处理中', value: 'PROCESSING' }
]
const labelText = {
  afterSaleType: { RETURN_REFUND: '退货退款', REFUND_ONLY: '仅退款' } as Record<string, string>,
  reason: { PRODUCT_QUALITY: '商品质量问题', LOGISTICS_DELAY: '物流延迟' } as Record<string, string>,
  status: { PENDING_REVIEW: '待审核', PROCESSING: '处理中', REJECTED: '已拒绝', COMPLETED: '已完成' } as Record<string, string>,
  priority: { HIGH: '高', NORMAL: '普通', LOW: '低' } as Record<string, string>,
  writeBack: { PENDING: '待回写', WAITING: '等待中', SUCCESS: '已回写', FAILED: '回写失败' } as Record<string, string>
}

onMounted(async () => {
  loading.value = true
  afterSalesData.value = await loadListWithFallback(() => loadAfterSales(), afterSales)
  loading.value = false
})

const filteredAfterSales = computed(() => {
  if (status.value === '全部') {
    return afterSalesData.value
  }
  return afterSalesData.value.filter((item) => item.status === status.value)
})

function batchApprove() {
  let changed = 0
  afterSalesData.value = afterSalesData.value.map((item) => {
    if (item.status !== 'PENDING_REVIEW') {
      return item
    }
    changed += 1
    return {
      ...item,
      status: 'PROCESSING',
      priority: item.priority || 'NORMAL',
      reviewOpinion: '批量审核通过，进入售后处理',
      writeBackStatus: 'PENDING'
    }
  })
  ElMessage({
    type: changed ? 'success' : 'info',
    message: changed ? `已审核 ${changed} 条待处理售后` : '当前没有待审核售后'
  })
}

function openReview(row: (typeof afterSales)[number]) {
  reviewingId.value = row.id
  reviewForm.value = { result: 'APPROVE', reason: '' }
  reviewVisible.value = true
}

function submitReview() {
  if (reviewingId.value === null) {
    return
  }
  if (reviewForm.value.result === 'REJECT' && !reviewForm.value.reason.trim()) {
    ElMessage({ type: 'warning', message: '拒绝售后时需要填写原因' })
    return
  }
  approveAfterSale(reviewingId.value, reviewForm.value.result, reviewForm.value.reason.trim())
  reviewVisible.value = false
}

function approveAfterSale(afterSaleId: number, result = 'APPROVE', reason = '') {
  let changed = false
  afterSalesData.value = afterSalesData.value.map((item) => {
    if (item.id !== afterSaleId) {
      return item
    }
    changed = item.status === 'PENDING_REVIEW'
    if (result === 'REJECT') {
      return {
        ...item,
        status: 'REJECTED',
        reviewOpinion: `审核拒绝：${reason}`,
        writeBackStatus: 'PENDING'
      }
    }
    return {
      ...item,
      status: 'PROCESSING',
      priority: item.reasonType === 'PRODUCT_QUALITY' ? 'HIGH' : item.priority,
      reviewOpinion: changed ? '审核通过，等待平台退款或退货流程' : '已复核，当前售后继续处理',
      writeBackStatus: 'PENDING'
    }
  })
  ElMessage({
    type: 'success',
    message: result === 'REJECT' ? '售后申请已拒绝' : (changed ? '售后审核已通过' : '售后复核结果已更新')
  })
}

function writeBackAfterSale(afterSaleId: number) {
  afterSalesData.value = afterSalesData.value.map((item) => {
    if (item.id !== afterSaleId) {
      return item
    }
    return {
      ...item,
      writeBackStatus: 'SUCCESS',
      reviewOpinion: item.reviewOpinion || '处理结果已同步外部平台'
    }
  })
  ElMessage({ type: 'success', message: '售后处理结果已模拟回写到抖音平台' })
}
</script>
