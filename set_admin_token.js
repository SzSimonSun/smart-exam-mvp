// 在浏览器控制台中运行这个脚本来设置admin用户的token
// 这样就可以直接测试拆题功能而不需要重新登录

// 设置admin用户的token (ID: 13, email: admin@example.com)
const adminToken = 'token_for_13_e64c7d89'
localStorage.setItem('token', adminToken)

console.log('✅ Admin token已设置:', adminToken)
console.log('🔄 请刷新页面以应用新的认证状态')

// 可选：直接重新加载页面
// window.location.reload()