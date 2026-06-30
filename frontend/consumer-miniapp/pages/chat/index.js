import { getTwentyMallBindings } from "../../utils/auth"
import { enrichOrderDisplay } from "../../utils/order-display"

const API_BASE = "http://localhost:8085"

function formatMessageTime(value) {
  if (!value) return ""
  const text = String(value).replace("T", " ").replace(/\.\d+$/, "")
  const match = text.match(/^(\d{4})[-/.](\d{1,2})[-/.](\d{1,2})\s+(\d{1,2}):(\d{1,2})(?::(\d{1,2}))?/)
  if (!match) return text
  const [, year, month, day, hour, minute, second = "00"] = match
  return `${year}.${Number(month)}.${Number(day)} ${hour.padStart(2, "0")}:${minute.padStart(2, "0")}:${second.padStart(2, "0")}`
}

function normalizeMessage(item) {
  const senderType = item.sender_type || "ai"
  const isUser = senderType === "user"
  const isStaff = senderType === "staff"
  return {
    id: item.id,
    role: isUser ? "user" : (isStaff ? "staff" : "ai"),
    speaker: isUser ? "我" : (isStaff ? "人工客服" : "AI客服"),
    time: formatMessageTime(item.created_at),
    content: item.content
  }
}

Page({
  data: {
    inputValue: "",
    mode: "AI",
    platformBound: false,
    orders: [],
    activeOrderNo: "",
    consultingOrder: null,
    messages: [],
    conversationId: null
  },
  onLoad() {
    this.applyPlatformBinding()
  },
  onShow() {
    this.applyPlatformBinding()
  },
  onInput(e) {
    this.setData({ inputValue: e.detail.value })
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
  applyPlatformBinding() {
    const bindings = getTwentyMallBindings()
    if (!bindings.length) {
      this.setData({
        platformBound: false,
        orders: [],
        activeOrderNo: "",
        consultingOrder: null,
        messages: [],
        inputValue: "",
        mode: "AI",
        conversationId: null
      })
      return
    }
    wx.request({
      url: `${API_BASE}/order/list?user_id=${wx.getStorageSync('userId') || 1}`,
      success: (res) => {
        console.log('chat order list response:', res)
        const list = (res.data && res.data.data && res.data.data.orders) || []
        const nextOrders = list.map((item) => enrichOrderDisplay({
          no: item.external_order_no || item.order_no,
          title: item.platform_code === 'DOUYIN' ? 'Aurora X1 智能手机' : '20商城商品',
          status: this.getStatusText(item.order_status),
          afterSale: this.getAfterSaleStatus(item.after_sale_status),
          platform: item.platform_code === 'DOUYIN' ? '抖音商城' : '20商城',
          price: parseFloat(item.total_amount || 0).toFixed(2),
          image: item.platform_code === 'DOUYIN' ? '/assets/products/phone.png' : '/assets/products/twenty-keyboard.png',
          spec: item.platform_code === 'DOUYIN' ? '星河银｜12GB+256GB' : '标准规格',
          service: item.after_sale_status === 'NONE' || !item.after_sale_status ? '可申请售后' : '售后处理中',
          orderId: item.id
        }))
        if (!nextOrders.length) {
          this.setData({
            platformBound: true,
            orders: [],
            activeOrderNo: "",
            consultingOrder: null,
            messages: []
          })
          return
        }
        const pendingOrderNo = wx.getStorageSync("pendingChatOrderNo")
        const activeOrder = nextOrders.find((item) => item.no === pendingOrderNo)
          || nextOrders.find((item) => item.no === this.data.activeOrderNo)
          || nextOrders[0]
        if (pendingOrderNo) {
          wx.removeStorageSync("pendingChatOrderNo")
        }
        this.setData({
          platformBound: true,
          orders: nextOrders,
          activeOrderNo: activeOrder.no,
          consultingOrder: activeOrder
        })
        this.loadConversation()
      },
      fail: () => {
        this.setData({
          platformBound: false,
          orders: [],
          activeOrderNo: "",
          consultingOrder: null,
          messages: [],
          inputValue: "",
          mode: "AI",
          conversationId: null
        })
      }
    })
  },
  goOrderDetail() {
    if (!this.data.consultingOrder) return
    wx.navigateTo({ url: `/pages/product/index?no=${this.data.consultingOrder.no}` })
  },
  switchOrder(e) {
    const no = e.currentTarget.dataset.no
    const order = this.data.orders.find((item) => item.no === no)
    if (!order) return
    this.setData({
      activeOrderNo: no,
      consultingOrder: order,
      mode: "AI",
      inputValue: "",
      messages: [],
      conversationId: null
    })
    this.loadConversation()
  },
  goBind() {
    wx.switchTab({ url: "/pages/home/index" })
  },
  sendMessage() {
    if (!this.data.platformBound || !this.data.activeOrderNo) {
      wx.showToast({ title: "请先绑定电商平台", icon: "none" })
      return
    }
    const value = this.data.inputValue.trim()
    if (!value) return
    const wantsHuman = value.includes("人工") || value.includes("客服")
    const order = this.data.consultingOrder
    this.setData({ inputValue: "", mode: wantsHuman ? "人工" : this.data.mode })
    wx.request({
      url: `${API_BASE}/conversation/send`,
      method: "POST",
      header: { "Content-Type": "application/json" },
      data: {
        merchant_id: 1,
        user_id: wx.getStorageSync('userId') || 1,
        message: value,
        conversation_id: this.data.conversationId,
        order_id: order.orderId,
        order_no: order.no
      },
      success: (res) => {
        console.log('send message response:', res)
        if (res.data && res.data.code === 200) {
          const data = res.data.data
          this.setData({
            conversationId: data.conversation_id,
            mode: data.escalate ? "人工" : "AI"
          })
          this.loadMessages(data.conversation_id)
        }
      },
      fail: () => {
        wx.showToast({ title: "消息发送失败，请确认后端已启动", icon: "none" })
      }
    })
  },
  loadConversation() {
    if (!this.data.platformBound || !this.data.activeOrderNo) return
    const userId = wx.getStorageSync('userId') || 1
    const orderNo = this.data.consultingOrder?.no
    let url = `${API_BASE}/conversation/list?user_id=${userId}`
    if (orderNo) {
      url += `&order_no=${orderNo}`
    }
    wx.request({
      url: url,
      success: (res) => {
        console.log('conversation list response:', res)
        const data = res.data && res.data.data
        if (data && data.id) {
          this.setData({
            conversationId: data.id,
            mode: data.status === "AGENT_SERVING" ? "人工" : "AI"
          })
          this.loadMessages(data.id)
        } else if (Array.isArray(data) && data.length > 0) {
          const conversation = data[0]
          this.setData({
            conversationId: conversation.id,
            mode: conversation.status === "AGENT_SERVING" ? "人工" : "AI"
          })
          this.loadMessages(conversation.id)
        } else {
          this.setData({ messages: [], conversationId: null })
        }
      },
      fail: () => {
        this.setData({ messages: [], conversationId: null })
      }
    })
  },
  loadMessages(conversationId) {
    if (!conversationId) return
    wx.request({
      url: `${API_BASE}/conversation/messages?conversation_id=${conversationId}`,
      success: (res) => {
        console.log('conversation messages response:', res)
        const list = (res.data && res.data.data) || []
        this.setData({ messages: list.map(normalizeMessage) })
      },
      fail: () => {
        this.setData({ messages: [] })
      }
    })
  }
})
