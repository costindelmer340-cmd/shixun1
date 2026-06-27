Page({
  data: {
    platforms: [
      { name: "抖音商城绑定", icon: "/assets/platforms/douyin.png", status: "已绑定" },
      { name: "淘宝绑定", icon: "/assets/platforms/taobao.png", status: "待绑定" },
      { name: "拼多多绑定", icon: "/assets/platforms/pinduoduo.png", status: "待绑定" },
      { name: "京东绑定", icon: "/assets/platforms/jd.png", status: "待绑定" }
    ]
  },
  bindPlatform(e) {
    const name = e.currentTarget.dataset.name
    wx.showToast({ title: `${name}功能接入中`, icon: "none" })
  }
})
