import { orders } from "../../utils/mock"

Page({
  data: {
    product: null
  },
  onLoad(options) {
    const product = orders.find((item) => item.no === options.no) || orders[0]
    this.setData({ product })
  },
  applyAfterSale() {
    wx.showModal({
      title: "发起售后",
      content: "当前将从订单页面进入售后申请流程，真实提交接口后续接入。",
      confirmText: "确认",
      showCancel: false
    })
  }
})
