const API_BASE_URL = 'http://localhost:8085'

const API = {
  CHAT: `${API_BASE_URL}/ai/chat`,
  INTENT: `${API_BASE_URL}/ai/intent`,
  SENTIMENT: `${API_BASE_URL}/ai/sentiment`,
  TOPIC: `${API_BASE_URL}/ai/topic`,
  RULE_CLASSIFY: `${API_BASE_URL}/ai/rule/classify`,
  RULE_INSPECT: `${API_BASE_URL}/ai/rule/inspect`,
  RULE_ESCALATE: `${API_BASE_URL}/ai/rule/escalate`,
  RULE_REVIEW: `${API_BASE_URL}/ai/rule/review`,
  RULE_EXECUTE: `${API_BASE_URL}/ai/rule/execute`,
  RULE_SETS: `${API_BASE_URL}/ai/rule/sets`,
  HEALTH: `${API_BASE_URL}/health`,
  TICKET_CREATE: `${API_BASE_URL}/ticket/create`,
  TICKET_LIST: `${API_BASE_URL}/ticket/list`,
  TICKET_DETAIL: `${API_BASE_URL}/ticket/detail`,
  TICKET_UPDATE: `${API_BASE_URL}/ticket/update`,
  TICKET_CLOSE: `${API_BASE_URL}/ticket/close`,
  AUTH_LOGIN: `${API_BASE_URL}/auth/login`,
  AUTH_USER: `${API_BASE_URL}/auth/user`,
  CONVERSATION_LIST: `${API_BASE_URL}/conversation/list`,
  CONVERSATION_DETAIL: `${API_BASE_URL}/conversation`,
  CONVERSATION_SEND: `${API_BASE_URL}/conversation/send`,
  CONVERSATION_CLOSE: `${API_BASE_URL}/conversation`,
  AFTER_SALE_CREATE: `${API_BASE_URL}/after-sale/create`,
  AFTER_SALE_LIST: `${API_BASE_URL}/after-sale/list`,
  AFTER_SALE_DETAIL: `${API_BASE_URL}/after-sale/detail`,
  AFTER_SALE_REVIEW: `${API_BASE_URL}/after-sale/review`,
  ORDER_LIST: `${API_BASE_URL}/order/list`,
  ORDER_DETAIL: `${API_BASE_URL}/order`,
  ORDER_STATS: `${API_BASE_URL}/order/stats`,
  REVIEW_LIST: `${API_BASE_URL}/review/list`,
  REVIEW_STATS: `${API_BASE_URL}/review/stats`
}

function request(url, options = {}) {
  const { method = 'GET', data = {} } = options
  const fullUrl = url.startsWith('http') ? url : `${API_BASE_URL}${url}`
  
  return new Promise((resolve, reject) => {
    wx.request({
      url: fullUrl,
      method,
      data: data,
      dataType: 'json',
      header: { 'content-type': 'application/json; charset=utf-8' },
      timeout: 10000,
      success(res) {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(new Error(res.data.message || '请求失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function sendChatRequest(params) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API.CHAT,
      method: 'POST',
      data: {
        merchant_id: params.merchant_id || 1,
        user_id: params.user_id || 1,
        message: params.message,
        conversation_id: params.conversation_id || null,
        order_id: params.order_id || null,
        context: params.context || null
      },
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '请求失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function login(phone, password) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API.AUTH_LOGIN,
      method: 'POST',
      data: { phone, password },
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '登录失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function getUserInfo(userId) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API.AUTH_USER}/${userId}`,
      method: 'GET',
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '获取用户信息失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function buildQuery(params) {
  const parts = []
  for (const key of Object.keys(params)) {
    const value = params[key]
    if (Array.isArray(value)) {
      value.forEach(v => parts.push(`${key}=${encodeURIComponent(v)}`))
    } else {
      parts.push(`${key}=${encodeURIComponent(value)}`)
    }
  }
  return parts.join('&')
}

function getOrderList(userId, params = {}) {
  const query = buildQuery({ user_id: userId, ...params })
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API.ORDER_LIST}?${query}`,
      method: 'GET',
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '获取订单列表失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function getOrderDetail(orderNo) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API.ORDER_DETAIL}/${orderNo}`,
      method: 'GET',
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '获取订单详情失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function getAfterSaleList(userId, params = {}) {
  const query = buildQuery({ user_id: userId, ...params })
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API.AFTER_SALE_LIST}?${query}`,
      method: 'GET',
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '获取售后列表失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function createAfterSale(params) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API.AFTER_SALE_CREATE,
      method: 'POST',
      data: params,
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '创建售后申请失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function getAfterSaleDetail(afterSaleNo) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API.AFTER_SALE_DETAIL}?after_sale_no=${afterSaleNo}`,
      method: 'GET',
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '获取售后详情失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function sendConversationMessage(params) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API.CONVERSATION_SEND,
      method: 'POST',
      data: {
        merchant_id: params.merchant_id || 1,
        user_id: params.user_id || 1,
        conversation_id: params.conversation_id || null,
        message: params.message,
        order_id: params.order_id || null
      },
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '发送消息失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function getConversationList(userId) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API.CONVERSATION_LIST}?user_id=${userId}`,
      method: 'GET',
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '获取会话列表失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function getConversationDetail(conversationNo) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API.CONVERSATION_DETAIL}/${conversationNo}`,
      method: 'GET',
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '获取会话详情失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function getTicketList(userId, params = {}) {
  const query = buildQuery({ user_id: userId, ...params })
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API.TICKET_LIST}?${query}`,
      method: 'GET',
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '获取工单列表失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function createTicket(params) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API.TICKET_CREATE,
      method: 'POST',
      data: params,
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '创建工单失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function closeTicket(ticketId, reason = '') {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API.TICKET_CLOSE,
      method: 'PUT',
      data: { ticket_id: ticketId, close_reason: reason },
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '关闭工单失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function getReviewList(merchantId, params = {}) {
  const query = buildQuery({ merchant_id: merchantId, ...params })
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API.REVIEW_LIST}?${query}`,
      method: 'GET',
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '获取评价列表失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function sendIntentRequest(query) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API.INTENT,
      method: 'POST',
      data: { query },
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '请求失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function sendClassifyRequest(text) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API.RULE_CLASSIFY,
      method: 'POST',
      data: { text },
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '请求失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function sendEscalateRequest(params) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: API.RULE_ESCALATE,
      method: 'POST',
      data: {
        text: params.text,
        intent: params.intent,
        sentiment: params.sentiment,
        sentiment_score: params.sentiment_score,
        risk_level: params.risk_level,
        issue_count: params.issue_count || 0,
        order_amount: params.order_amount || 0
      },
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200 && res.data.code === 200) {
          resolve(res.data.data)
        } else {
          reject(new Error(res.data.message || '请求失败'))
        }
      },
      fail(err) {
        reject(err)
      }
    })
  })
}

function checkHealth() {
  return new Promise((resolve) => {
    wx.request({
      url: API.HEALTH,
      method: 'GET',
      success(res) {
        resolve(res.statusCode === 200)
      },
      fail() {
        resolve(false)
      }
    })
  })
}

function updateUser(userId, data) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: `${API_BASE_URL}/users/${userId}`,
      method: 'PUT',
      data: data,
      header: { 'content-type': 'application/json; charset=utf-8' },
      success(res) {
        if (res.statusCode === 200) {
          resolve(res.data)
        } else {
          reject(res)
        }
      },
      fail: reject
    })
  })
}

module.exports = {
  API,
  API_BASE_URL,
  request,
  login,
  getUserInfo,
  updateUser,
  sendChatRequest,
  sendConversationMessage,
  getConversationList,
  getConversationDetail,
  getOrderList,
  getOrderDetail,
  getAfterSaleList,
  createAfterSale,
  getAfterSaleDetail,
  getTicketList,
  createTicket,
  closeTicket,
  getReviewList,
  sendIntentRequest,
  sendClassifyRequest,
  sendEscalateRequest,
  checkHealth
}