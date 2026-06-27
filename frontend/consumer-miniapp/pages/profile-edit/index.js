Page({
  data: {
    form: {
      nickname: "consumer_demo",
      avatar: "/assets/avatars/user.png"
    },
    phone: "13338907581"
  },
  onLoad() {
    const profile = wx.getStorageSync("consumerProfile")
    if (profile) {
      this.setData({
        form: {
          nickname: profile.nickname || this.data.form.nickname,
          avatar: profile.avatar || this.data.form.avatar
        }
      })
    }
  },
  onInput(e) {
    const field = e.currentTarget.dataset.field
    this.setData({ [`form.${field}`]: e.detail.value })
  },
  chooseAvatar() {
    wx.chooseMedia({
      count: 1,
      mediaType: ["image"],
      success: (res) => {
        const file = res.tempFiles && res.tempFiles[0]
        if (file && file.tempFilePath) {
          this.setData({ "form.avatar": file.tempFilePath })
        }
      },
      fail: () => {
        wx.showToast({ title: "暂未选择头像", icon: "none" })
      }
    })
  },
  saveProfile() {
    wx.setStorageSync("consumerProfile", this.data.form)
    wx.showToast({ title: "资料已保存", icon: "success" })
    setTimeout(() => wx.navigateBack(), 500)
  }
})
