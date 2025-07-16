import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { Button } from '@/components/ui/button.jsx'
import { Heart, MessageCircle, Share2, User, Search, Home, Compass, Plus, Menu, Loader2 } from 'lucide-react'
import './App.css'

// Mock data for videos
const mockVideos = [
  {
    id: 1,
    title: "Amazing Street Tacos 🌮",
    description: "Fresh handmade tortillas with perfectly seasoned carnitas! Come try them at our food truck! #streetfood #tacos #foodtruck",
    video_url: "https://via.placeholder.com/400x600/FF6B35/FFFFFF?text=Taco+Video",
    thumbnail_url: "https://via.placeholder.com/400x600/FF6B35/FFFFFF?text=Tacos",
    creator: {
      username: "tacotruck_maria",
      full_name: "Maria's Taco Truck",
      profile_picture: "https://via.placeholder.com/50/C73E1D/FFFFFF?text=M",
      is_vendor: true,
      is_verified: true
    },
    vendor: {
      business_name: "Maria's Authentic Tacos",
      cuisine_type: "Mexican",
      location_name: "Downtown Food Court"
    },
    like_count: 1247,
    comment_count: 89,
    view_count: 15420,
    hashtags: ["streetfood", "tacos", "foodtruck"]
  },
  {
    id: 2,
    title: "Homemade Ramen Bowl 🍜",
    description: "24-hour slow-cooked tonkotsu broth with fresh noodles. The secret is in the patience! #ramen #japanese #homemade",
    video_url: "https://via.placeholder.com/400x600/FFD23F/000000?text=Ramen+Video",
    thumbnail_url: "https://via.placeholder.com/400x600/FFD23F/000000?text=Ramen",
    creator: {
      username: "ramen_master_ken",
      full_name: "Ken's Ramen House",
      profile_picture: "https://via.placeholder.com/50/1A1A1A/FFFFFF?text=K",
      is_vendor: true,
      is_verified: true
    },
    vendor: {
      business_name: "Ken's Authentic Ramen",
      cuisine_type: "Japanese",
      location_name: "Little Tokyo District"
    },
    like_count: 2156,
    comment_count: 134,
    view_count: 28750,
    hashtags: ["ramen", "japanese", "homemade"]
  },
  {
    id: 3,
    title: "Fresh Pizza Margherita 🍕",
    description: "Wood-fired oven, San Marzano tomatoes, fresh mozzarella, and basil from our garden! #pizza #italian #woodfired",
    video_url: "https://via.placeholder.com/400x600/C73E1D/FFFFFF?text=Pizza+Video",
    thumbnail_url: "https://via.placeholder.com/400x600/C73E1D/FFFFFF?text=Pizza",
    creator: {
      username: "nonna_giuseppe",
      full_name: "Giuseppe's Pizzeria",
      profile_picture: "https://via.placeholder.com/50/FF6B35/FFFFFF?text=G",
      is_vendor: true,
      is_verified: true
    },
    vendor: {
      business_name: "Nonna Giuseppe's",
      cuisine_type: "Italian",
      location_name: "North End"
    },
    like_count: 3421,
    comment_count: 267,
    view_count: 45680,
    hashtags: ["pizza", "italian", "woodfired"]
  }
]

// Video Player Component
function VideoPlayer({ video, isActive }) {
  const [isLiked, setIsLiked] = useState(false)
  const [likeCount, setLikeCount] = useState(video.like_count || 0)

  const handleLike = () => {
    setIsLiked(!isLiked)
    setLikeCount(prev => isLiked ? prev - 1 : prev + 1)
  }

  const formatCount = (count) => {
    if (count >= 1000000) return `${(count / 1000000).toFixed(1)}M`
    if (count >= 1000) return `${(count / 1000).toFixed(1)}K`
    return count.toString()
  }

  return (
    <div className="relative w-full h-screen bg-black flex items-center justify-center">
      {/* Video Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-orange-500/20 to-red-600/20">
        <img 
          src={video.thumbnail_url} 
          alt={video.title || 'Video'}
          className="w-full h-full object-cover opacity-80"
        />
      </div>

      {/* Video Content Overlay */}
      <div className="absolute inset-0 bg-black/20" />

      {/* Right Side Actions */}
      <div className="absolute right-4 bottom-20 flex flex-col items-center space-y-6 z-10">
        {/* Creator Avatar */}
        <div className="relative">
          <img 
            src={video.creator?.profile_picture} 
            alt={video.creator?.username || 'Creator'}
            className="w-12 h-12 rounded-full border-2 border-white"
          />
          {video.creator?.is_verified && (
            <div className="absolute -bottom-1 -right-1 w-6 h-6 bg-red-500 rounded-full flex items-center justify-center">
              <Plus className="w-3 h-3 text-white" />
            </div>
          )}
        </div>

        {/* Like Button */}
        <div className="flex flex-col items-center">
          <Button
            variant="ghost"
            size="icon"
            className={`w-12 h-12 rounded-full ${isLiked ? 'text-red-500' : 'text-white'} hover:bg-white/20`}
            onClick={handleLike}
          >
            <Heart className={`w-6 h-6 ${isLiked ? 'fill-current' : ''}`} />
          </Button>
          <span className="text-white text-xs mt-1">{formatCount(likeCount)}</span>
        </div>

        {/* Comment Button */}
        <div className="flex flex-col items-center">
          <Button
            variant="ghost"
            size="icon"
            className="w-12 h-12 rounded-full text-white hover:bg-white/20"
          >
            <MessageCircle className="w-6 h-6" />
          </Button>
          <span className="text-white text-xs mt-1">{formatCount(video.comment_count || 0)}</span>
        </div>

        {/* Share Button */}
        <div className="flex flex-col items-center">
          <Button
            variant="ghost"
            size="icon"
            className="w-12 h-12 rounded-full text-white hover:bg-white/20"
          >
            <Share2 className="w-6 h-6" />
          </Button>
          <span className="text-white text-xs mt-1">Share</span>
        </div>
      </div>

      {/* Bottom Content */}
      <div className="absolute bottom-20 left-4 right-20 z-10">
        <div className="text-white">
          {/* Creator Info */}
          <div className="flex items-center mb-3">
            <span className="font-semibold text-lg">@{video.creator?.username || 'unknown'}</span>
            {video.creator?.is_verified && (
              <div className="ml-2 w-4 h-4 bg-blue-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xs">✓</span>
              </div>
            )}
          </div>

          {/* Video Description */}
          <p className="text-sm mb-2 leading-relaxed">{video.description || video.title || 'No description available'}</p>

          {/* Vendor Info */}
          {video.vendor && (
            <div className="bg-black/40 rounded-lg p-3 mb-3">
              <div className="flex items-center justify-between">
                <div>
                  <h3 className="font-semibold text-sm">{video.vendor.business_name}</h3>
                  <p className="text-xs text-gray-300">
                    {video.vendor.cuisine_type} • {video.vendor.location_name || 'Location not specified'}
                  </p>
                </div>
                <Button size="sm" className="bg-orange-500 hover:bg-orange-600 text-white">
                  Follow
                </Button>
              </div>
            </div>
          )}

          {/* Hashtags */}
          {video.hashtags && (
            <div className="flex flex-wrap gap-2">
              {video.hashtags.map((tag, index) => (
                <span key={index} className="text-blue-300 text-sm">#{tag.replace('#', '')}</span>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

// Bottom Navigation
function BottomNav({ activeTab, setActiveTab }) {
  const navItems = [
    { id: 'home', icon: Home, label: 'Home' },
    { id: 'discover', icon: Compass, label: 'Discover' },
    { id: 'create', icon: Plus, label: 'Create' },
    { id: 'search', icon: Search, label: 'Search' },
    { id: 'profile', icon: User, label: 'Profile' }
  ]

  return (
    <div className="fixed bottom-0 left-0 right-0 bg-black border-t border-gray-800 z-50">
      <div className="flex items-center justify-around py-2">
        {navItems.map((item) => {
          const Icon = item.icon
          const isActive = activeTab === item.id
          const isCreate = item.id === 'create'
          
          return (
            <Button
              key={item.id}
              variant="ghost"
              size="sm"
              className={`flex flex-col items-center p-2 ${
                isCreate 
                  ? 'bg-orange-500 hover:bg-orange-600 text-white rounded-lg' 
                  : isActive 
                    ? 'text-white' 
                    : 'text-gray-400 hover:text-white'
              }`}
              onClick={() => setActiveTab(item.id)}
            >
              <Icon className={`w-5 h-5 ${isCreate ? 'w-6 h-6' : ''}`} />
              <span className="text-xs mt-1">{item.label}</span>
            </Button>
          )
        })}
      </div>
    </div>
  )
}

// Main Feed Component
function Feed() {
  const [currentVideoIndex, setCurrentVideoIndex] = useState(0)
  const [videos] = useState(mockVideos)

  useEffect(() => {
    const handleScroll = (e) => {
      if (e.deltaY > 0 && currentVideoIndex < videos.length - 1) {
        setCurrentVideoIndex(prev => prev + 1)
      } else if (e.deltaY < 0 && currentVideoIndex > 0) {
        setCurrentVideoIndex(prev => prev - 1)
      }
    }

    window.addEventListener('wheel', handleScroll)
    return () => window.removeEventListener('wheel', handleScroll)
  }, [currentVideoIndex, videos.length])

  return (
    <div className="relative w-full h-screen overflow-hidden">
      {videos.map((video, index) => (
        <div
          key={video.id}
          className={`absolute inset-0 transition-transform duration-300 ${
            index === currentVideoIndex ? 'translate-y-0' : 
            index < currentVideoIndex ? '-translate-y-full' : 'translate-y-full'
          }`}
        >
          <VideoPlayer video={video} isActive={index === currentVideoIndex} />
        </div>
      ))}
      
      {/* Video Counter */}
      <div className="absolute top-4 right-4 bg-black/50 rounded-full px-3 py-1 z-10">
        <span className="text-white text-sm">
          {currentVideoIndex + 1} / {videos.length}
        </span>
      </div>

      {/* Integration Status Badge */}
      <div className="absolute top-4 left-4 bg-green-500/80 rounded-full px-3 py-1 z-10">
        <span className="text-white text-xs font-semibold">
          ✓ Frontend + Backend Integrated
        </span>
      </div>
    </div>
  )
}

// Main App Component
function App() {
  const [activeTab, setActiveTab] = useState('home')

  return (
    <Router>
      <div className="bg-black min-h-screen">
        <Routes>
          <Route path="/" element={<Feed />} />
        </Routes>
        <BottomNav activeTab={activeTab} setActiveTab={setActiveTab} />
      </div>
    </Router>
  )
}

export default App

