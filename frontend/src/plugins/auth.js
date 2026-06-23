import { defineStore } from "pinia";
import { ref, computed } from "vue";
import api from './axios';
import { io } from "socket.io-client";

export const useAuthStore = defineStore("auth", () => {
    // --- 1. 初始化状态 ---
    const storedToken = localStorage.getItem("token") || "";
    let storedUser = {};
    try {
        const u = localStorage.getItem("user");
        if (u && u !== "undefined") storedUser = JSON.parse(u);
    } catch (e) {
        localStorage.removeItem("user");
    }

    const token = ref(storedToken);
    const user = ref(storedUser);

    // WebSocket 相关状态
    const socket = ref(null);
    const unreadCount = ref(0);
    const friendReqCount = ref(0);

    // 防止重复初始化 socket
    let _socketInitialized = false;

    // --- 2. 计算属性 ---
    const isLoggedIn = computed(() => {
        return !!token.value && user.value && Object.keys(user.value).length > 0;
    });

    const isAdmin = computed(() => {
        return isLoggedIn.value && user.value.role === 'admin';
    });

    // --- 3. WebSocket 连接逻辑 ---
    const initSocket = () => {
        if (!token.value || socket.value || _socketInitialized) return;
        _socketInitialized = true;

        const wsUrl = api.defaults.baseURL.replace(/\/api\/?$/, '');

        socket.value = io(wsUrl, {
            query: { token: token.value },
            transports: ['websocket']
        });

        socket.value.on('connect', () => {
            console.log('WebSocket 已连接');
        });

        socket.value.on('disconnect', () => {
            _socketInitialized = false;
        });

        socket.value.on('new_message', (msg) => {
            if (msg.sender_id !== user.value.id) {
                unreadCount.value++;
            }
        });

        socket.value.on('friend_request', () => {
            friendReqCount.value++;
        });
    };

    const disconnectSocket = () => {
        if (socket.value) {
            socket.value.disconnect();
            socket.value = null;
            _socketInitialized = false;
        }
    };

    // --- 5. 业务动作 ---

    const login = (userData, userToken) => {
        token.value = userToken;
        user.value = userData;
        localStorage.setItem("token", userToken);
        localStorage.setItem("user", JSON.stringify(userData));
        _socketInitialized = false;
        initSocket();
    };

    const logout = () => {
        disconnectSocket();
        token.value = "";
        user.value = {};
        unreadCount.value = 0;
        friendReqCount.value = 0;
        localStorage.removeItem("token");
        localStorage.removeItem("user");
    };

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
        socket, unreadCount, friendReqCount,
        login, logout, fetchUser, initSocket
    };
});
