<template>
  <div class="panel">
    <div class="toolbar">
      <el-input v-model="keyword" placeholder="搜索订单号、买家" style="max-width: 320px" />
      <el-button type="primary" :loading="syncing" @click="syncOrders">同步订单</el-button>
    </div>
    <el-table v-loading="loading" :data="filteredOrders">
      <el-table-column prop="externalOrderNo" label="订单号" min-width="170" />
      <el-table-column prop="buyerMaskedName" label="买家" width="90" />
      <el-table-column label="订单状态" width="130">
        <template #default="{ row }">{{ statusText.order[row.orderStatus] || row.orderStatus }}</template>
      </el-table-column>
      <el-table-column label="支付状态" width="110">
        <template #default="{ row }">{{ statusText.pay[row.payStatus] || row.payStatus }}</template>
      </el-table-column>
      <el-table-column label="物流状态" width="130">
        <template #default="{ row }">{{ statusText.logistics[row.logisticsStatus] || row.logisticsStatus }}</template>
      </el-table-column>
      <el-table-column label="售后状态" width="130">
        <template #default="{ row }">{{ statusText.afterSale[row.afterSaleStatus] || row.afterSaleStatus }}</template>
      </el-table-column>
      <el-table-column prop="totalAmount" label="金额" width="100" />
      <el-table-column prop="orderedAt" label="下单时间" min-width="160" />
      <el-table-column label="操作" width="110">
        <template #default="{ row }">
          <el-button link type="primary" @click="openDetail(row)">详情</el-button>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="detailVisible" title="订单详情" width="560px">
      <el-descriptions v-if="currentOrder" border :column="2">
        <el-descriptions-item label="订单号">{{ currentOrder.externalOrderNo }}</el-descriptions-item>
        <el-descriptions-item label="买家">{{ currentOrder.buyerMaskedName }}</el-descriptions-item>
        <el-descriptions-item label="订单状态">{{ statusText.order[currentOrder.orderStatus] || currentOrder.orderStatus }}</el-descriptions-item>
        <el-descriptions-item label="支付状态">{{ statusText.pay[currentOrder.payStatus] || currentOrder.payStatus }}</el-descriptions-item>
        <el-descriptions-item label="物流状态">{{ statusText.logistics[currentOrder.logisticsStatus] || currentOrder.logisticsStatus }}</el-descriptions-item>
        <el-descriptions-item label="售后状态">{{ statusText.afterSale[currentOrder.afterSaleStatus] || currentOrder.afterSaleStatus }}</el-descriptions-item>
        <el-descriptions-item label="订单金额">{{ currentOrder.totalAmount }}</el-descriptions-item>
        <el-descriptions-item label="下单时间">{{ currentOrder.orderedAt }}</el-descriptions-item>
      </el-descriptions>
      <template #footer>
        <el-button @click="detailVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { orders } from '../data/mock'
import { loadOrders } from '../api'
import { loadListWithFallback } from '../api/normalize'
import { ElMessage } from 'element-plus'

const keyword = ref('')
const orderData = ref<typeof orders>([])
const loading = ref(false)
const syncing = ref(false)
const detailVisible = ref(false)
const currentOrder = ref<(typeof orders)[number] | null>(null)
const statusText = {
  order: { COMPLETED: '已完成', SHIPPED: '已发货', PENDING: '待处理', CANCELED: '已取消' } as Record<string, string>,
  pay: { PAID: '已支付', UNPAID: '未支付', REFUNDED: '已退款' } as Record<string, string>,
  logistics: { RECEIVED: '已签收', IN_TRANSIT: '运输中', WAITING: '待发货' } as Record<string, string>,
  afterSale: { AFTER_SALE: '售后中', NONE: '未申请', COMPLETED: '已完成' } as Record<string, string>
}

onMounted(async () => {
  loading.value = true
  orderData.value = await loadListWithFallback(() => loadOrders(), orders)
  loading.value = false
})

const filteredOrders = computed(() => {
  const source = orderData.value.length ? orderData.value : orders
  return source.filter((item) => item.externalOrderNo.includes(keyword.value) || item.buyerMaskedName.includes(keyword.value))
})

async function syncOrders() {
  syncing.value = true
  await new Promise((resolve) => window.setTimeout(resolve, 500))
  orderData.value = [...orders]
  syncing.value = false
  ElMessage({ type: 'success', message: '订单已同步到最新演示数据' })
}

function openDetail(row: (typeof orders)[number]) {
  currentOrder.value = row
  detailVisible.value = true
}
</script>
