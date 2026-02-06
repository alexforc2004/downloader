import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000';

const api = axios.create({
    baseURL: API_BASE_URL,
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

export const authAPI = {
    register: (data) => api.post('/register', data),
    login: (formData) => api.post('/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
    }),
    getMe: () => api.get('/users/me'),
};

export const socialAPI = {
    getPosts: () => api.get('/posts'),
    createPost: (data) => api.post('/posts', data),
    sendFriendRequest: (userId) => api.post(`/friends/request/${userId}`),
    getFriendRequests: () => api.get('/friends/requests'),
    acceptFriendRequest: (userId) => api.post(`/friends/accept/${userId}`),
    reactToPost: (data) => api.post('/reactions', data),
    commentOnPost: (data) => api.post('/comments', data),
};

export const downloaderAPI = {
    fetchInfo: (url) => api.get(`/downloader/info?url=${encodeURIComponent(url)}`),
    download: (url, formatType) => api.post(`/downloader/download?url=${encodeURIComponent(url)}&format_type=${formatType}`, {}, {
        responseType: 'blob'
    }),
};

export default api;
