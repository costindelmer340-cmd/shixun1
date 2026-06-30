const api = require('../../utils/api.js')

Page({
  data: {
    currentTab: '',
    tickets: [],
    page: 1,
    pageSize: 20
  },

  onLoad() {
    this.loadTickets()
  },

  onShow() {
    if (this.data.currentTab) {
      this.loadTickets()
    }
  },

  switchTab(e) {
    const tab = e.currentTarget.dataset.tab
    this.setData({ currentTab: tab, page: 1 })
    this.loadTickets()
  },

  loadTickets() {
    const userId = wx.getStorageSync('userId') || 1
    const params = {
      user_id: userId,
      limit: this.data.pageSize,
      offset: (this.data.page - 1) * this.data.pageSize
    }

    if (this.data.currentTab) {
      const statusMap = {
        'pending': ['PENDING', 'PENDING_REVIEW'],
        'processing': ['PROCESSING'],
        'completed': ['COMPLETED']
      }
      params.status = statusMap[this.data.currentTab] || this.data.currentTab.toUpperCase()
    }

    console.log('loadTickets params:', params)
    
    wx.showLoading({ title: "加载中..." })
    
    api.getAfterSaleList(userId, params).then(res => {
      wx.hideLoading()
      console.log('loadTickets response:', res)
      
      const data = res.data || res
      const applications = data.applications || []
      
      console.log('applications count:', applications.length)
      
      const tickets = applications.map(app => {
        console.log('processing app:', app)
        return {
          id: app.id,
          ticket_id: app.after_sale_no,
          ticket_type: app.after_sale_type,
          title: this.getAfterSaleTitle(app.after_sale_type, app.reason_type),
          description: app.problem_description || '暂无描述',
          status: app.status,
          created_at: app.created_at,
          formatted_time: this.formatTime(app.created_at),
          updated_at: app.updated_at,
          requested_amount: app.requested_amount,
          external_order_no: app.external_order_no,
          total_amount: app.total_amount,
          platform_code: app.platform_code
        }
      })
      
      console.log('tickets to display:', tickets)
      this.setData({ tickets })
    }).catch(err => {
      wx.hideLoading()
      console.error('加载售后申请失败:', err)
      this.setData({ tickets: [] })
    })
  },

  getAfterSaleTitle(type, reason) {
    const typeMap = {
      'RETURN_REFUND': '退货退款',
      'EXCHANGE': '换货',
      'ONLY_REFUND': '仅退款'
    }
    const reasonMap = {
      'PRODUCT_QUALITY': '商品质量问题',
      'WRONG_ITEM': '发错商品',
      'SIZE_ISSUE': '尺寸不符',
      'LOGISTICS_DAMAGE': '物流损坏',
      'CHANGE_MIND': '个人原因',
      'OTHER': '其他原因'
    }
    return `${typeMap[type] || type} - ${reasonMap[reason] || reason}`
  },

  goToDetail(e) {
    const afterSaleNo = e.currentTarget.dataset['after-sale-no'] || e.currentTarget.dataset.afterSaleNo
    console.log('goToDetail afterSaleNo:', afterSaleNo)
    
    if (afterSaleNo) {
      wx.navigateTo({
        url: `/pages/ticket/detail/index?after_sale_no=${afterSaleNo}`,
        success: () => {
          console.log('navigateTo success')
        },
        fail: (err) => {
          console.error('navigateTo failed:', err)
          wx.showToast({ title: '跳转失败', icon: 'none' })
        }
      })
    } else {
      wx.showToast({ title: '参数错误', icon: 'none' })
    }
  },

  getTypeLabel(type) {
    const typeMap = {
      return_refund: '退货退款',
      exchange: '换货',
      only_refund: '仅退款',
      complaint: '投诉',
      compensation: '赔偿',
      after_sale: '售后咨询',
      other: '其他',
      AFTER_SALE: '售后咨询',
      RETURN_REFUND: '退货退款',
      EXCHANGE: '换货',
      ONLY_REFUND: '仅退款',
      COMPLAINT: '投诉',
      QUALITY_ISSUE: '质量问题',
      LOGISTICS_ISSUE: '物流问题',
      SERVICE_ISSUE: '服务问题'
    }
    return typeMap[type] || '其他'
  },

  getStatusLabel(status) {
    const statusMap = {
      pending: '待审核',
      processing: '处理中',
      pending_review: '待复核',
      completed: '已完成',
      closed: '已关闭',
      rejected: '已驳回',
      reopened: '重新审核',
      PENDING: '待审核',
      PROCESSING: '处理中',
      APPROVED: '已通过',
      REJECTED: '已驳回',
      COMPLETED: '已完成',
      CLOSED: '已关闭',
      PENDING_REVIEW: '待审核'
    }
    return statusMap[status] || status
  },

  formatTime(timeStr) {
    if (!timeStr) return ''
    console.log('formatTime input:', timeStr)
    try {
      const date = new Date(timeStr)
      if (isNaN(date.getTime())) {
        console.error('Invalid date:', timeStr)
        return ''
      }
      const result = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
      console.log('formatTime output:', result)
      return result
    } catch (e) {
      console.error('formatTime error:', e)
      return ''
    }
  },

  cancelTicket(e) {
    const ticketId = e.currentTarget.dataset['ticket-id'] || e.currentTarget.dataset.ticketId
    wx.showModal({
      title: '确认取消',
      content: '确定要取消此售后申请吗？取消后将无法恢复。',
      confirmColor: '#e74c3c',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '取消中...' })
          api.request(`/after-sale/close?after_sale_no=${ticketId}`, {
            method: 'PUT',
            data: { final_result: '用户主动取消' }
          }).then(res => {
            wx.hideLoading()
            if (res.code === 200) {
              wx.showToast({ title: '申请已取消', icon: 'success' })
              this.loadTickets()
            } else {
              wx.showToast({ title: res.message || '取消失败', icon: 'none' })
            }
          }).catch(err => {
            wx.hideLoading()
            console.error('取消申请失败:', err)
            wx.showToast({ title: '取消失败，请稍后重试', icon: 'none' })
          })
        }
      }
    })
  },

  onPullDownRefresh() {
    this.setData({ page: 1 })
    this.loadTickets()
    wx.stopPullDownRefresh()
  },

  onReachBottom() {
    this.setData({ page: this.data.page + 1 })
    this.loadTickets()
  }
})
