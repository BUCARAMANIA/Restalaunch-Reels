// API service for FoodTok backend integration
const API_BASE_URL = 'http://localhost:5000/api'

class ApiService {
  constructor() {
    this.token = localStorage.getItem('authToken')
  }

  // Helper method to make authenticated requests
  async makeRequest(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    }

    // Add auth token if available
    if (this.token) {
      config.headers['Authorization'] = `Bearer ${this.token}`
    }

    try {
      const response = await fetch(url, config)
      const data = await response.json()
      
      if (!response.ok) {
        throw new Error(data.error || 'API request failed')
      }
      
      return data
    } catch (error) {
      console.error('API Error:', error)
      throw error
    }
  }

  // Authentication
  async register(userData) {
    const response = await this.makeRequest('/auth/register', {
      method: 'POST',
      body: JSON.stringify(userData)
    })
    
    if (response.token) {
      this.token = response.token
      localStorage.setItem('authToken', response.token)
    }
    
    return response
  }

  async login(credentials) {
    const response = await this.makeRequest('/auth/login', {
      method: 'POST',
      body: JSON.stringify(credentials)
    })
    
    if (response.token) {
      this.token = response.token
      localStorage.setItem('authToken', response.token)
    }
    
    return response
  }

  logout() {
    this.token = null
    localStorage.removeItem('authToken')
  }

  // Videos
  async getVideos(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/videos/?${queryString}`)
  }

  async getVideo(videoId) {
    return this.makeRequest(`/videos/${videoId}`)
  }

  async createVideo(videoData) {
    return this.makeRequest('/videos/', {
      method: 'POST',
      body: JSON.stringify(videoData)
    })
  }

  async likeVideo(videoId) {
    return this.makeRequest(`/videos/${videoId}/like`, {
      method: 'POST'
    })
  }

  async unlikeVideo(videoId) {
    return this.makeRequest(`/videos/${videoId}/unlike`, {
      method: 'DELETE'
    })
  }

  async getVideoComments(videoId, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/videos/${videoId}/comments?${queryString}`)
  }

  async addComment(videoId, commentData) {
    return this.makeRequest(`/videos/${videoId}/comments`, {
      method: 'POST',
      body: JSON.stringify(commentData)
    })
  }

  // Feed
  async getForYouFeed(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/feed/for-you?${queryString}`)
  }

  async getFollowingFeed(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/feed/following?${queryString}`)
  }

  async getLocalFeed(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/feed/local?${queryString}`)
  }

  async getCuisineFeed(cuisineType, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/feed/cuisine/${cuisineType}?${queryString}`)
  }

  async getHashtagFeed(hashtag, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/feed/hashtag/${hashtag}?${queryString}`)
  }

  async getDiscoverFeed() {
    return this.makeRequest('/feed/discover')
  }

  async searchContent(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/feed/search?${queryString}`)
  }

  // Vendors
  async getVendors(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/vendors/?${queryString}`)
  }

  async getVendor(vendorId) {
    return this.makeRequest(`/vendors/${vendorId}`)
  }

  async getMyVendorProfile() {
    return this.makeRequest('/vendors/profile')
  }

  async updateVendorProfile(profileData) {
    return this.makeRequest('/vendors/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    })
  }

  async addMenuItem(menuItemData) {
    return this.makeRequest('/vendors/menu', {
      method: 'POST',
      body: JSON.stringify(menuItemData)
    })
  }

  async updateMenuItem(itemId, menuItemData) {
    return this.makeRequest(`/vendors/menu/${itemId}`, {
      method: 'PUT',
      body: JSON.stringify(menuItemData)
    })
  }

  async deleteMenuItem(itemId) {
    return this.makeRequest(`/vendors/menu/${itemId}`, {
      method: 'DELETE'
    })
  }

  async getVendorReviews(vendorId, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/vendors/${vendorId}/reviews?${queryString}`)
  }

  async addVendorReview(vendorId, reviewData) {
    return this.makeRequest(`/vendors/${vendorId}/reviews`, {
      method: 'POST',
      body: JSON.stringify(reviewData)
    })
  }

  // Users
  async getUsers(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/users/?${queryString}`)
  }

  async getUser(userId) {
    return this.makeRequest(`/users/${userId}`)
  }

  async getMyProfile() {
    return this.makeRequest('/users/profile')
  }

  async updateProfile(profileData) {
    return this.makeRequest('/users/profile', {
      method: 'PUT',
      body: JSON.stringify(profileData)
    })
  }

  async followUser(userId) {
    return this.makeRequest(`/users/${userId}/follow`, {
      method: 'POST'
    })
  }

  async unfollowUser(userId) {
    return this.makeRequest(`/users/${userId}/unfollow`, {
      method: 'DELETE'
    })
  }

  async getUserFollowers(userId, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/users/${userId}/followers?${queryString}`)
  }

  async getUserFollowing(userId, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/users/${userId}/following?${queryString}`)
  }

  async getUserVideos(userId, params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/users/${userId}/videos?${queryString}`)
  }

  async getLikedVideos(params = {}) {
    const queryString = new URLSearchParams(params).toString()
    return this.makeRequest(`/users/liked-videos?${queryString}`)
  }

  async checkFollowingStatus(userId) {
    return this.makeRequest(`/users/check-following/${userId}`)
  }

  async getUserStats() {
    return this.makeRequest('/users/stats')
  }
}

// Create and export a singleton instance
const apiService = new ApiService()
export default apiService

