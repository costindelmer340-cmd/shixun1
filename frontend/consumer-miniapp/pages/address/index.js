Page({
  data: {
    form: {
      name: "林同学",
      phone: "138****2856",
      region: "浙江省杭州市余杭区",
      detail: "售后服务中心 3 号楼"
    }
  },
  onLoad() {
    const address = wx.getStorageSync("consumerAddress")
    if (address) {
      this.setData({ form: address })
    }
  },
  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`form.${field}`]: e.detail.value })
  },
  saveAddress() {
    const fullAddress = `${this.data.form.region}${this.data.form.detail}`
    wx.setStorageSync("consumerAddress", { ...this.data.form, fullAddress })
    wx.showToast({ title: "地址已保存", icon: "success" })
    setTimeout(() => wx.navigateBack(), 500)
  }
})
