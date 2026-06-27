<template>
  <div class="panel">
    <div class="toolbar">
      <div>
        <h2 class="section-title">店铺绑定</h2>
        <span class="page-kicker">用于同步订单、售后、评价和回写处理结果</span>
      </div>
    </div>
    <div class="platform-grid">
      <div v-for="item in platformOptions" :key="item.code" class="platform-card">
        <img :src="item.icon" :alt="item.name" />
        <div>
          <strong>{{ item.name }}</strong>
          <span>{{ item.desc }}</span>
        </div>
        <el-button type="primary" @click="mockAuthorize(item.name)">绑定</el-button>
      </div>
    </div>
    <el-alert
      title="该页优先显示后端真实绑定列表，若未登录或接口不可用，则回退到演示数据。"
      type="info"
      :closable="false"
      show-icon
      style="margin-bottom: 16px"
    />
    <el-descriptions v-loading="loading" border :column="2">
      <el-descriptions-item label="平台">{{ currentBinding.platformName || currentBinding.platformCode }}</el-descriptions-item>
      <el-descriptions-item label="授权状态">
        <el-tag :type="currentBinding.authStatus === 'ACTIVE' ? 'success' : 'warning'">{{ currentBinding.authStatus }}</el-tag>
      </el-descriptions-item>
      <el-descriptions-item label="店铺ID">{{ currentBinding.externalShopId }}</el-descriptions-item>
      <el-descriptions-item label="店铺名称">{{ currentBinding.shopName }}</el-descriptions-item>
      <el-descriptions-item label="同步范围">订单、售后、评价、物流</el-descriptions-item>
      <el-descriptions-item label="最近同步">{{ currentBinding.lastSyncedAt || '-' }}</el-descriptions-item>
    </el-descriptions>
    <div class="split-grid">
      <div class="panel">
        <h2 class="section-title">同步任务</h2>
        <div v-for="item in syncTaskData" :key="item.id" class="status-line">
          <div>
            <strong>{{ item.taskName }}</strong>
            <div class="page-kicker">上次：{{ item.lastRunAt || '-' }} · 下次：{{ item.nextRunAt || '-' }}</div>
          </div>
          <div class="inline-actions">
            <el-tag :type="item.enabled ? 'success' : 'info'">{{ item.enabled ? '已启用' : '已停用' }}</el-tag>
            <el-button link type="primary" :loading="syncingType === item.taskType" @click="runSync(item.taskType)">触发</el-button>
          </div>
        </div>
      </div>
      <div class="panel">
        <h2 class="section-title">开放平台准备项</h2>
        <el-check-tag checked>App Key</el-check-tag>
        <el-check-tag checked>App Secret</el-check-tag>
        <el-check-tag checked>回调地址</el-check-tag>
        <el-check-tag>真实权限审批</el-check-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { loadPlatformBindings, loadSyncTasks, triggerSync } from '../api'
import { loadListWithFallback } from '../api/normalize'
import { platformBindings, syncTasks } from '../data/mock'
import { isDemoMode } from '../utils/auth'
import douyinIcon from '../assets/platforms/douyin.png'
import taobaoIcon from '../assets/platforms/taobao.png'
import pddIcon from '../assets/platforms/pinduoduo.png'
import jdIcon from '../assets/platforms/jd.png'

const bindingData = ref<typeof platformBindings>([])
const syncTaskData = ref<typeof syncTasks>(syncTasks)
const loading = ref(false)
const syncingType = ref('')
const platformOptions = [
  { code: 'DOUYIN', name: '抖音商城', desc: '同步抖店订单与售后', icon: douyinIcon },
  { code: 'TAOBAO', name: '淘宝', desc: '预留淘宝店铺接入', icon: taobaoIcon },
  { code: 'PDD', name: '拼多多', desc: '预留拼多多店铺接入', icon: pddIcon },
  { code: 'JD', name: '京东', desc: '预留京东店铺接入', icon: jdIcon }
]

onMounted(async () => {
  loading.value = true
  bindingData.value = await loadListWithFallback(() => loadPlatformBindings(), platformBindings)
  syncTaskData.value = await loadListWithFallback(() => loadSyncTasks(currentBinding.value.id), syncTasks)
  loading.value = false
})

const currentBinding = computed(() => bindingData.value[0] || platformBindings[0])

async function runSync(syncType: string) {
  syncingType.value = syncType
  try {
    if (isDemoMode()) {
      await new Promise((resolve) => window.setTimeout(resolve, 300))
      ElMessage({ type: 'success', message: '演示模式下已模拟触发同步' })
      return
    }
    await triggerSync(currentBinding.value.id, syncType)
    ElMessage({ type: 'success', message: '同步任务已触发' })
    syncTaskData.value = await loadListWithFallback(() => loadSyncTasks(currentBinding.value.id), syncTasks)
  } catch {
    ElMessage({ type: 'warning', message: '后端暂不可用，当前为演示触发' })
  } finally {
    syncingType.value = ''
  }
}

function mockAuthorize(platformName = '抖音商城') {
  bindingData.value = [{
    ...currentBinding.value,
    platformName,
    authStatus: 'ACTIVE',
    lastSyncedAt: '2026-06-25 19:30:00'
  }]
  ElMessage({ type: 'success', message: `${platformName}店铺已完成模拟绑定` })
}
</script>

<style scoped>
.platform-grid {
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  gap: 14px;
  margin-bottom: 16px;
}

.platform-card {
  display: grid;
  grid-template-columns: 48px 1fr auto;
  align-items: center;
  gap: 12px;
  border: 1px solid #e4e8f0;
  border-radius: 8px;
  padding: 14px;
  background: #fff;
}

.platform-card img {
  width: 48px;
  height: 48px;
  border-radius: 10px;
  object-fit: cover;
}

.platform-card strong,
.platform-card span {
  display: block;
}

.platform-card span {
  margin-top: 4px;
  color: #64748b;
  font-size: 12px;
}

@media (max-width: 1280px) {
  .platform-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
