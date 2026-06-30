import { orders } from "../../utils/mock"
import { getTwentyMallBinding } from "../../utils/auth"
import { enrichOrderDisplay } from "../../utils/order-display"

const API_BASE = "http://localhost:8085"

Page({
  data: {
    product: null,
    afterSaleDetail: null,
    afterSaleDetailVisible: false,
    reviewVisible: false,
    reviewScore: 5,
    reviewText: "",
    reviewStars: [
      { value: 1, active: true },
      { value: 2, active: true },
      { value: 3, active: true },
      { value: 4, active: true },
      { value: 5, active: true }
    ]
  },
  onLoad(options) {
    const orderNo = options.no
    this.loadOrderDetail(orderNo)
  },
  loadOrderDetail(orderNo) {
    wx.showLoading({ title: "加载中..." })
    wx.request({
      url: `${API_BASE}/order/list?user_id=${wx.getStorageSync('userId') || 1}`,
      success: (res) => {
        wx.hideLoading()
        const data = res.data && res.data.data
        const ordersList = (data && data.orders) || []
        const order = ordersList.find((item) => item.external_order_no === orderNo)
        
        if (order) {
          this.setProductDetail(order)
        } else {
          const mockOrder = orders.find((item) => item.no === orderNo)
          if (mockOrder) {
            this.setProductDetailFromMock(mockOrder)
          } else {
            this.setProductDetailFromMock(orders[0])
          }
        }
      },
      fail: () => {
        wx.hideLoading()
        const mockOrder = orders.find((item) => item.no === orderNo) || orders[0]
        this.setProductDetailFromMock(mockOrder)
      }
    })
  },
  setProductDetail(order) {
    const platformCode = order.platform_code
    const title = platformCode === 'DOUYIN' ? 'Aurora X1 智能手机' : 
                  platformCode === 'TWENTY_MALL' ? '20商城商品' : '订单商品'
    const image = platformCode === 'DOUYIN' ? '/assets/products/phone.png' : 
                  platformCode === 'TWENTY_MALL' ? '/assets/products/twenty-keyboard.png' : '/assets/products/phone.png'
    const spec = platformCode === 'DOUYIN' ? '星河银｜12GB+256GB' : '标准规格'
    const platform = platformCode === 'DOUYIN' ? '抖音商城' : 
                     platformCode === 'TWENTY_MALL' ? '20商城' : platformCode
    const merchant = platformCode === 'DOUYIN' ? '星链数码旗舰店' : '20商城演示店铺'
    
    const statusText = this.getStatusText(order.order_status)
    const afterSaleText = this.getAfterSaleStatus(order.after_sale_status)
    
    const product = {
      no: order.external_order_no,
      title,
      status: statusText,
      afterSale: afterSaleText,
      platform,
      merchant,
      price: parseFloat(order.total_amount || 0).toFixed(2),
      image,
      spec,
      orderedAt: order.ordered_at ? this.formatDateTime(order.ordered_at) : '',
      deliveredAt: order.completed_at ? this.formatDateTime(order.completed_at) : '',
      policyTags: order.policy_tags || [],
      service: afterSaleText === "未申请" ? "可申请售后" : "售后处理中"
    }
    
    this.setData({ 
      product, 
      afterSaleDetail: this.buildStoredAfterSaleDetail(product.no, product.afterSale) 
    })
  },
  setProductDetailFromMock(order) {
    const product = enrichOrderDisplay(order)
    this.setData({ 
      product, 
      afterSaleDetail: this.buildStoredAfterSaleDetail(product.no, product.afterSale) 
    })
  },
  getStatusText(status) {
    const statusMap = {
      'PENDING_PAYMENT': '待付款',
      'PAID': '已付款',
      'SHIPPED': '已发货',
      'IN_TRANSIT': '运输中',
      'DELIVERED': '已送达',
      'RECEIVED': '已签收',
      'COMPLETED': '已完成',
      'CANCELLED': '已取消'
    }
    return statusMap[status] || status
  },
  getAfterSaleStatus(status) {
    if (!status || status === 'NONE' || status === 'none') return '未申请'
    if (status === 'AFTER_SALE' || status === 'after_sale') return '处理中'
    if (status === 'APPLIED') return '处理中'
    if (status === 'CLOSED') return '已关闭'
    return status
  },
  formatDateTime(dateTime) {
    if (!dateTime) return ''
    const date = new Date(dateTime)
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:${String(date.getMinutes()).padStart(2, '0')}`
  },
  handleAfterSalePrimary() {
    if (!this.data.product) return
    if (this.hasAppliedAfterSale()) {
      this.setData({ afterSaleDetailVisible: true })
      return
    }
    this.submitAfterSale(false)
  },
  modifyAfterSale() {
    this.submitAfterSale(true)
  },
  closeAfterSaleDetail() {
    this.setData({ afterSaleDetailVisible: false })
  },
  submitAfterSale(isModify) {
    if (!this.data.product) return
    wx.showActionSheet({
      itemList: ["仅退款", "退货退款", "价保"],
      success: (res) => {
        const type = ["仅退款", "退货退款", "价保"][res.tapIndex]
        const typeMap = {
          "仅退款": "REFUND_ONLY",
          "退货退款": "RETURN_REFUND",
          "价保": "PRICE_PROTECTION"
        }
        const reasonMap = {
          "仅退款": "PRODUCT_QUALITY",
          "退货退款": "PRODUCT_QUALITY",
          "价保": "PRICE_PROTECTION"
        }
        wx.showLoading({ title: "提交中" })
        wx.request({
          url: `${API_BASE}/after-sale/create`,
          method: "POST",
          header: { "Content-Type": "application/json" },
          data: {
            order_no: this.data.product.no,
            after_sale_type: typeMap[type],
            reason_type: reasonMap[type],
            description: `消费者选择${type}，由消费者端小程序提交售后申请。`,
            user_id: wx.getStorageSync('userId') || 1
          },
          success: (response) => {
            const payload = response.data || {}
            if (payload.code !== 200 && payload.code !== "200") {
              wx.showToast({ title: payload.message || "提交失败", icon: "none" })
              return
            }
            const product = {
              ...this.data.product,
              afterSale: "处理中",
              service: "售后处理中"
            }
            const afterSaleDetail = {
              orderNo: product.no,
              productName: product.title,
              merchantName: product.merchant,
              status: product.afterSale,
              type,
              appliedAt: this.formatNow()
            }
            wx.setStorageSync(`afterSaleDetail:${product.no}`, afterSaleDetail)
            this.setData({ product, afterSaleDetail })
            wx.showToast({ title: isModify ? "售后已修改" : "售后已提交", icon: "success" })
          },
          fail: () => {
            wx.showToast({ title: "请先启动后端服务", icon: "none" })
          },
          complete: () => {
            wx.hideLoading()
          }
        })
      }
    })
  },
  hasAppliedAfterSale() {
    return this.data.product && this.data.product.afterSale && this.data.product.afterSale !== "未申请"
  },
  buildStoredAfterSaleDetail(orderNo, afterSaleStatus) {
    const stored = wx.getStorageSync(`afterSaleDetail:${orderNo}`)
    if (stored) {
      return stored
    }
    if (!afterSaleStatus || afterSaleStatus === "未申请") {
      return null
    }
    return {
      orderNo,
      productName: "",
      merchantName: "",
      status: afterSaleStatus,
      type: "退货退款",
      appliedAt: "2026.6.29 10:35:23"
    }
  },
  formatNow() {
    const date = new Date()
    const pad = (value) => String(value).padStart(2, "0")
    return `${date.getFullYear()}.${date.getMonth() + 1}.${date.getDate()} ${pad(date.getHours())}:${pad(date.getMinutes())}:${pad(date.getSeconds())}`
  },
  contactMerchant() {
    if (!this.data.product) return
    wx.setStorageSync("pendingChatOrderNo", this.data.product.no)
    wx.switchTab({ url: "/pages/chat/index" })
  },
  cancelAfterSale() {
    wx.showModal({
      title: '确认取消',
      content: '确定要取消此售后申请吗？取消后将无法恢复。',
      confirmColor: '#e74c3c',
      success: (res) => {
        if (res.confirm) {
          wx.showLoading({ title: '取消中...' })
          this.getAfterSaleNoAndCancel()
        }
      }
    })
  },
  getAfterSaleNoAndCancel() {
    wx.request({
      url: `${API_BASE}/after-sale/list?user_id=${wx.getStorageSync('userId') || 1}`,
      success: (response) => {
        const payload = response.data || {}
        const applications = (payload.data && payload.data.applications) || []
        const orderNo = this.data.product.no
        let afterSaleNo = null
        
        for (const app of applications) {
          const appOrderNo = app.order_no || ''
          if (appOrderNo === orderNo) {
            const no = app.after_sale_no || app.ticketNo
            if (no && (no.startsWith('TMAS') || no.startsWith('AS'))) {
              afterSaleNo = no
              break
            }
          }
        }
        
        if (afterSaleNo) {
          this.doCancelAfterSale(afterSaleNo)
        } else {
          wx.hideLoading()
          wx.showToast({ title: '未找到售后申请', icon: 'none' })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '获取售后信息失败', icon: 'none' })
      }
    })
  },
  doCancelAfterSale(afterSaleNo) {
    wx.request({
      url: `${API_BASE}/after-sale/close?after_sale_no=${afterSaleNo}&final_result=用户主动取消`,
      method: 'PUT',
      success: (response) => {
        wx.hideLoading()
        const payload = response.data || {}
        if (payload.code === 200 || payload.code === "200") {
          wx.showToast({ 
            title: '申请已取消', 
            icon: 'success',
            duration: 1500
          })
          setTimeout(() => {
            wx.navigateBack({
              delta: 1,
              success: () => {
                const pages = getCurrentPages()
                const prevPage = pages[pages.length - 1]
                if (prevPage && prevPage.loadOrders) {
                  prevPage.loadOrders()
                }
              }
            })
          }, 1500)
        } else {
          wx.showToast({ title: payload.message || '取消失败', icon: 'none' })
        }
      },
      fail: () => {
        wx.hideLoading()
        wx.showToast({ title: '取消失败，请稍后重试', icon: 'none' })
      }
    })
  },
  openReviewDialog() {
    this.setData({
      reviewVisible: true,
      reviewScore: 5,
      reviewText: "",
      reviewStars: this.buildStars(5)
    })
  },
  closeReviewDialog() {
    this.setData({ reviewVisible: false })
  },
  setReviewScore(event) {
    const score = Number(event.currentTarget.dataset.score)
    this.setData({
      reviewScore: score,
      reviewStars: this.buildStars(score)
    })
  },
  onReviewInput(event) {
    this.setData({ reviewText: event.detail.value })
  },
  submitReview() {
    if (!this.data.reviewText.trim()) {
      wx.showToast({ title: "请输入评价内容", icon: "none" })
      return
    }
    wx.showToast({ title: "评价已提交", icon: "success" })
    this.setData({ reviewVisible: false })
  },
  buildStars(score) {
    return [1, 2, 3, 4, 5].map((value) => ({
      value,
      active: value <= score
    }))
  }
})
