Page({
  data: {
    orders: [],
    loading: true
  },

  onLoad() {
    this.loadOrders()
  },

  onShow() {
    this.loadOrders()
  },

  loadOrders() {
    this.setData({ loading: true })
    
    wx.request({
      url: 'http://localhost:8085/order/list?user_id=1',
      success: (res) => {
        console.log('订单数据:', res)
        
        if (res.data && res.data.code === 200 && res.data.data && res.data.data.orders) {
          const orders = res.data.data.orders.map(order => {
            const platform = order.platform_code
            return {
              no: order.external_order_no,
              title: platform === 'DOUYIN' ? 'Aurora X1 智能手机' : '20商城商品',
              image: platform === 'DOUYIN' ? '/assets/products/phone.png' : '/assets/products/twenty-keyboard.png',
              price: order.total_amount.toFixed(2),
              platform: platform === 'DOUYIN' ? '抖音商城' : '20商城',
              status: this.getStatus(order.order_status),
              afterSale: order.after_sale_status === 'NONE' ? '未申请' : '处理中'
            }
          })
          
          this.setData({ orders, loading: false }, () => {
            console.log('数据绑定完成')
            console.log('页面orders数据:', this.data.orders)
            console.log('页面orders长度:', this.data.orders.length)
          })
          console.log('订单数量:', orders.length)
        } else {
          this.setData({ orders: [], loading: false })
        }
      },
      fail: () => {
        this.setData({ orders: [], loading: false })
        wx.showToast({ title: '加载失败', icon: 'none' })
      }
    })
  },

  getStatus(status) {
    const map = {
      'PENDING_PAYMENT': '待付款',
      'PAID': '已付款',
      'SHIPPED': '已发货',
      'IN_TRANSIT': '运输中',
      'DELIVERED': '已送达',
      'COMPLETED': '已完成'
    }
    return map[status] || status
  },

  viewDetail(e) {
    const no = e.currentTarget.dataset.no
    wx.navigateTo({ url: `/pages/product/index?no=${no}` })
  }
})
