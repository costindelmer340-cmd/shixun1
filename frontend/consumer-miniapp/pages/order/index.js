import { orders } from "../../utils/mock"

Page({
  data: { orders },
  goDetail(e) {
    const no = e.currentTarget.dataset.no
    wx.navigateTo({ url: `/pages/product/index?no=${no}` })
  }
})
