Page({
  data: {
    profile: {
      nickname: "consumer_demo",
      phone: "13338907581",
      avatar: "/assets/avatars/user.png",
      address: "浙江省杭州市余杭区售后服务中心",
      bindPlatform: "抖音商城",
      lastConsult: "2026-06-25 09:35:00"
    }
  },
  onShow() {
    const profile = wx.getStorageSync("consumerProfile")
    const address = wx.getStorageSync("consumerAddress")
    const nextProfile = profile ? { ...this.data.profile, ...profile } : this.data.profile
    nextProfile.phone = "13338907581"
    if (address) {
      nextProfile.address = address.fullAddress
    }
    this.setData({ profile: nextProfile })
  },
  editProfile() {
    wx.navigateTo({ url: "/pages/profile-edit/index" })
  },
  manageAddress() {
    wx.navigateTo({ url: "/pages/address/index" })
  }
})
