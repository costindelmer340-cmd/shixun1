import { orders } from "../../utils/mock"

const chatMap = {
  DY202606250001: [
    { role: "user", speaker: "我", content: "手机屏幕有划痕，可以退货吗？" },
    { role: "ai", speaker: "AI客服", content: "可以先上传商品照片和包装照片，我会根据售后规则帮你判断。" },
    { role: "user", speaker: "我", content: "退款进度在哪里看？" },
    { role: "ai", speaker: "AI客服", content: "你可以在订单详情中查看售后进度，也可以告诉我订单号。" }
  ],
  DY202606250002: [
    { role: "ai", speaker: "AI客服", content: "当前咨询的是 Breeze 声学专营店订单，耳机类售后可查询退换货和物流进度。" }
  ]
}

Page({
  data: {
    inputValue: "",
    mode: "AI",
    orders,
    activeOrderNo: orders[0].no,
    consultingOrder: orders[0],
    chatMap,
    messages: chatMap[orders[0].no]
  },
  onInput(e) {
    this.setData({ inputValue: e.detail.value })
  },
  goOrderDetail() {
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
      messages: this.data.chatMap[no] || [
        { role: "ai", speaker: "AI客服", content: `当前已切换到${order.merchant}订单，请描述需要咨询的问题。` }
      ]
    })
  },
  sendMessage() {
    const value = this.data.inputValue.trim()
    if (!value) return
    const wantsHuman = value.includes("人工") || value.includes("客服")
    const reply = wantsHuman
      ? { role: "staff", speaker: "人工客服", content: "您好，已为您转接人工客服，请描述需要处理的问题。" }
      : { role: "ai", speaker: "AI客服", content: "我已收到你的问题，会结合订单和售后规则为你查询。" }
    const no = this.data.activeOrderNo
    const nextMessages = [...this.data.messages, { role: "user", speaker: "我", content: value }, reply]
    this.setData({
      inputValue: "",
      mode: wantsHuman ? "人工" : this.data.mode,
      messages: nextMessages,
      chatMap: { ...this.data.chatMap, [no]: nextMessages }
    })
  }
})
