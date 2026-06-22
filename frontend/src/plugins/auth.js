import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from './axios'; // 🔥 必须引入配置好的 axios 实例以获取 baseURL
import { io } from "socket.io-client"; // 需安装: npm install socket.io-client

export const useAuthStore = defineStore("auth", () => {
    // --- 1. 初始化状态 ---
    const storedToken = localStorage.getItem("token") || "";
    let storedUser = {}; 
    try {
        const u = localStorage.getItem("user");
        if (u && u !== "undefined") storedUser = JSON.parse(u);
    } catch (e) {
        console.error("用户信息解析失败:", e);
        localStorage.removeItem("user");
    }

    const token = ref(storedToken);
    const user = ref(storedUser);
    
    // 🔥 新增：WebSocket 相关状态
    const socket = ref(null);
    const unreadCount = ref(0); // 消息红点
    const friendReqCount = ref(0); // 好友申请红点

    // --- 2. 计算属性 ---
    const isLoggedIn = computed(() => {
        return !!token.value && user.value && Object.keys(user.value).length > 0;
    });

    const isAdmin = computed(() => {
        return isLoggedIn.value && user.value.role === 'admin';
    });

    // --- 3. 🔥 全局图片路径处理 (核心：适配动态IP) ---
    const formatUrl = (path) => {
        if (!path) return '';
        if (path.startsWith('http') || path.startsWith('https')) return path;
        
        // 动态获取 axios 中配置的 baseURL
        const apiBase = api.defaults.baseURL || '';
        const serverRoot = apiBase.replace(/\/api\/?$/, '');
        return `${serverRoot}${path}`;
    };

    // --- 4. 🔥 WebSocket 连接逻辑 ---
    const initSocket = () => {
        if (!token.value || socket.value) return;

        // 动态解析 WebSocket 地址 (去掉 /api)
        const wsUrl = api.defaults.baseURL.replace(/\/api\/?$/, '');
        
        // 建立连接
        socket.value = io(wsUrl, {
            query: { token: token.value }, // 携带 Token 鉴权
            transports: ['websocket']
        });

        socket.value.on('connect', () => {
            console.log('✅ WebSocket 已连接');
        });

        // 监听新消息
        socket.value.on('new_message', (msg) => {
            // 如果发送者不是自己，红点+1
            if (msg.sender_id !== user.value.id) {
                unreadCount.value++;
            }
        });

        // 监听好友申请
        socket.value.on('friend_request', () => {
            friendReqCount.value++;
        });
    };

    const disconnectSocket = () => {
        if (socket.value) {
            socket.value.disconnect();
            socket.value = null;
        }
    };

    // --- 5. 业务动作 ---
    
    // 登录
    const login = (userData, userToken) => {
        token.value = userToken;
        user.value = userData;
        localStorage.setItem("token", userToken);
        localStorage.setItem("user", JSON.stringify(userData));
        // 登录成功后立即连接 Socket
        initSocket(); 
    };

    // 登出
    const logout = () => {
        disconnectSocket(); // 断开连接
        token.value = "";
        user.value = {};
        unreadCount.value = 0;
        friendReqCount.value = 0;
        localStorage.removeItem("token");
        localStorage.removeItem("user");
    };

    // 刷新用户信息
    const fetchUser = async () => {
        if (!token.value) return;
        try {
            const res = await api.get('/api/users/me'); 
            if (res.data.code === 200) {
                user.value = res.data.data;
                localStorage.setItem("user", JSON.stringify(user.value));
            }
        } catch (e) {
            console.error(e);
        }
    };

    return { 
        token, user, isLoggedIn, isAdmin, 
        socket, unreadCount, friendReqCount, // 导出状态
        login, logout, formatUrl, fetchUser, initSocket 
    };
});