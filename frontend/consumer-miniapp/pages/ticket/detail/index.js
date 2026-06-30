const api = require('../../../utils/api.js')

Page({
  data: {
    ticket: {},
    afterSale: {},
    orderNo: ''
  },

  onLoad(options) {
    const ticketId = options.ticket_id
    const afterSaleNo = options.after_sale_no
    const orderNo = options.orderNo
    
    if (orderNo) {
      this.setData({ orderNo })
    }
    
    if (afterSaleNo) {
      this.loadAfterSaleDetail(afterSaleNo)
    } else if (ticketId) {
      this.loadTicketDetail(ticketId)
    }
  },

  loadAfterSaleDetail(afterSaleNo) {
    wx.showLoading({ title: "加载中..." })
    console.log('loadAfterSaleDetail afterSaleNo:', afterSaleNo)
    
    api.getAfterSaleDetail(afterSaleNo).then(res => {
      wx.hideLoading()
      console.log('loadAfterSaleDetail response:', res)
      
      if (res) {
        const afterSale = res
        const ticket = {
          id: afterSale.id,
          ticket_id: afterSale.after_sale_no,
          ticket_type: afterSale.after_sale_type,
          title: this.getAfterSaleTitle(afterSale.after_sale_type, afterSale.reason_type),
          description: afterSale.problem_description || '暂无描述',
          status: afterSale.status,
          order_id: afterSale.external_order_id,
          created_at: afterSale.created_at,
          formatted_time: this.formatTime(afterSale.created_at),
          updated_at: afterSale.updated_at,
          requested_amount: afterSale.requested_amount,
          reviewer_id: afterSale.reviewer_id,
          review_opinion: afterSale.review_opinion,
          reviewed_at: afterSale.reviewed_at,
          close_reason: afterSale.final_result,
          resolved_at: afterSale.reviewed_at
        }
        console.log('ticket to display:', ticket)
        this.setData({ 
          ticket, 
          afterSale: res 
        })
      } else {
        console.error('售后详情数据为空')
      }
    }).catch(err => {
      wx.hideLoading()
      console.error('加载售后详情失败:', err)
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

  loadTicketDetail(ticketId) {
    wx.showLoading({ title: "加载中..." })
    
    api.request(`/ticket/detail/${ticketId}`, {
      method: 'GET'
    }).then(res => {
      wx.hideLoading()
      if (res.code === 200) {
        this.setData({ ticket: res.data.ticket || {} })
      }
    }).catch(err => {
      wx.hideLoading()
      console.error('加载申请详情失败:', err)
    })
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
      CLOSED: '已关闭'
    }
    return statusMap[status] || status
  },

  getActionLabel(action) {
    const actionMap = {
      created: '提交申请',
      assigned: '分配处理',
      status_change: '状态变更',
      completed: '处理完成',
      closed: '申请关闭',
      rejected: '申请驳回',
      reopened: '重新申请',
      note_added: '添加备注'
    }
    return actionMap[action] || action
  },

  formatTime(timeStr) {
    if (!timeStr) return '-'
    console.log('formatTime input:', timeStr)
    try {
      let date
      if (timeStr.includes('T')) {
        const parts = timeStr.split('T')
        const datePart = parts[0]
        const timePart = parts[1] || '00:00:00'
        date = new Date(`${datePart} ${timePart}`)
      } else {
        date = new Date(timeStr)
      }
      if (isNaN(date.getTime())) {
        console.error('Invalid date:', timeStr)
        return timeStr
      }
      const result = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
      console.log('formatTime output:', result)
      return result
    } catch (e) {
      console.error('formatTime error:', e)
      return timeStr
    }
  },

  getOperatorLabel(operator) {
    if (operator === 'system') {
      return '系统'
    }
    return operator || '系统'
  },

  getLogDetail(detail) {
    return detail.replace('工单创建成功', '申请已提交').replace('分配给客服', '已分配')
  },

  cancelTicket() {
    wx.showModal({
      title: '确认取消',
      content: '确定要取消此售后申请吗？取消后将无法恢复。',
      confirmColor: '#e74c3c',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '取消中...' })
          const afterSaleNo = this.data.ticket.ticket_id
          api.request(`/after-sale/close?after_sale_no=${afterSaleNo}&final_result=用户主动取消`, {
            method: 'PUT'
          }).then(res => {
            wx.hideLoading()
            if (res.code === 200) {
              wx.showToast({ title: '申请已取消', icon: 'success' })
              setTimeout(() => {
                wx.navigateBack()
              }, 1500)
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

  submitAfterSale() {
    wx.showModal({
      title: '提示',
      content: '请从订单详情页面申请售后，以便获取完整的订单信息。',
      showCancel: false,
      confirmText: '知道了'
    })
  },
  
  goBack() {
    wx.navigateBack()
  }
})