from flask import Blueprint, request, jsonify
from src.models.user import db, User, Follow
from src.models.vendor import Vendor
from src.models.video import Video, Like
from src.routes.auth import token_required
from sqlalchemy import desc, func, and_, or_
from datetime import datetime, timedelta
import random

feed_bp = Blueprint('feed', __name__)

@feed_bp.route('/for-you', methods=['GET'])
def get_for_you_feed():
    """
    Main TikTok-style feed with personalized content
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        user_id = request.args.get('user_id', type=int)  # Optional for personalization
        
        # Base query for active videos
        query = Video.query.filter_by(is_active=True)
        
        if user_id:
            # Personalized feed based on user preferences
            user = User.query.get(user_id)
            if user:
                # Get videos from followed users
                followed_users = db.session.query(Follow.followed_id).filter_by(follower_id=user_id).subquery()
                
                # Get user's liked videos to understand preferences
                liked_videos = db.session.query(Like.video_id).filter_by(user_id=user_id).subquery()
                liked_video_objects = Video.query.filter(Video.id.in_(liked_videos)).all()
                
                # Extract preferences from liked videos
                preferred_cuisines = list(set([v.cuisine_type for v in liked_video_objects if v.cuisine_type]))
                preferred_categories = list(set([v.food_category for v in liked_video_objects if v.food_category]))
                
                # Build personalized query
                personalized_conditions = []
                
                # Videos from followed users (high priority)
                personalized_conditions.append(Video.user_id.in_(followed_users))
                
                # Videos matching cuisine preferences
                if preferred_cuisines:
                    personalized_conditions.append(Video.cuisine_type.in_(preferred_cuisines))
                
                # Videos matching category preferences
                if preferred_categories:
                    personalized_conditions.append(Video.food_category.in_(preferred_categories))
                
                # Trending videos (high engagement)
                trending_threshold = datetime.utcnow() - timedelta(days=7)
                personalized_conditions.append(
                    and_(
                        Video.created_at >= trending_threshold,
                        (Video.like_count + Video.comment_count + Video.view_count) > 10
                    )
                )
                
                if personalized_conditions:
                    query = query.filter(or_(*personalized_conditions))
        
        # Order by a mix of recency and engagement
        # This creates a balanced feed of new and popular content
        query = query.order_by(
            desc(
                func.log(Video.view_count + 1) * 0.3 +
                func.log(Video.like_count + 1) * 0.4 +
                func.log(Video.comment_count + 1) * 0.3 +
                func.extract('epoch', Video.created_at) / 100000  # Recency factor
            )
        )
        
        # Pagination
        videos = query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # Shuffle results slightly to add variety
        video_list = list(videos.items)
        if len(video_list) > 5:
            # Keep first few videos in order, shuffle the rest slightly
            stable_count = min(3, len(video_list))
            stable_videos = video_list[:stable_count]
            shuffled_videos = video_list[stable_count:]
            random.shuffle(shuffled_videos)
            video_list = stable_videos + shuffled_videos
        
        return jsonify({
            'videos': [video.to_dict() for video in video_list],
            'total': videos.total,
            'pages': videos.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feed_bp.route('/following', methods=['GET'])
@token_required
def get_following_feed(current_user):
    """
    Feed showing videos from users that the current user follows
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Get followed users
        followed_users = db.session.query(Follow.followed_id).filter_by(
            follower_id=current_user.id
        ).subquery()
        
        # Get videos from followed users
        videos = Video.query.filter(
            and_(
                Video.user_id.in_(followed_users),
                Video.is_active == True
            )
        ).order_by(desc(Video.created_at)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'videos': [video.to_dict() for video in videos.items],
            'total': videos.total,
            'pages': videos.pages,
            'current_page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feed_bp.route('/local', methods=['GET'])
def get_local_feed():
    """
    Feed showing videos from vendors in a specific location
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        lat = request.args.get('lat', type=float)
        lng = request.args.get('lng', type=float)
        radius = request.args.get('radius', 10, type=float)  # km
        
        if not lat or not lng:
            return jsonify({'error': 'Latitude and longitude are required'}), 400
        
        # Simple distance calculation for local videos
        lat_range = radius / 111.0  # Rough conversion
        lng_range = radius / (111.0 * abs(lat))
        
        # Get vendors in the area
        local_vendors = Vendor.query.filter(
            and_(
                Vendor.latitude.between(lat - lat_range, lat + lat_range),
                Vendor.longitude.between(lng - lng_range, lng + lng_range),
                Vendor.is_active == True
            )
        ).all()
        
        vendor_ids = [vendor.id for vendor in local_vendors]
        
        # Get videos from local vendors or videos with location in the area
        videos = Video.query.filter(
            and_(
                Video.is_active == True,
                or_(
                    Video.vendor_id.in_(vendor_ids),
                    and_(
                        Video.latitude.between(lat - lat_range, lat + lat_range),
                        Video.longitude.between(lng - lng_range, lng + lng_range)
                    )
                )
            )
        ).order_by(desc(Video.created_at)).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'videos': [video.to_dict() for video in videos.items],
            'total': videos.total,
            'pages': videos.pages,
            'current_page': page,
            'per_page': per_page,
            'local_vendors_count': len(local_vendors)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feed_bp.route('/cuisine/<cuisine_type>', methods=['GET'])
def get_cuisine_feed(cuisine_type):
    """
    Feed showing videos for a specific cuisine type
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        videos = Video.query.filter(
            and_(
                Video.cuisine_type.ilike(f'%{cuisine_type}%'),
                Video.is_active == True
            )
        ).order_by(
            desc(Video.like_count + Video.comment_count + Video.view_count)
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'videos': [video.to_dict() for video in videos.items],
            'total': videos.total,
            'pages': videos.pages,
            'current_page': page,
            'per_page': per_page,
            'cuisine_type': cuisine_type
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feed_bp.route('/hashtag/<hashtag>', methods=['GET'])
def get_hashtag_feed(hashtag):
    """
    Feed showing videos for a specific hashtag
    """
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Remove # if present
        hashtag = hashtag.lstrip('#')
        
        videos = Video.query.filter(
            and_(
                Video.hashtags.ilike(f'%{hashtag}%'),
                Video.is_active == True
            )
        ).order_by(
            desc(Video.like_count + Video.comment_count + Video.view_count)
        ).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'videos': [video.to_dict() for video in videos.items],
            'total': videos.total,
            'pages': videos.pages,
            'current_page': page,
            'per_page': per_page,
            'hashtag': hashtag
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feed_bp.route('/discover', methods=['GET'])
def get_discover_feed():
    """
    Discovery feed with trending hashtags, cuisines, and featured content
    """
    try:
        # Get trending hashtags (most used in recent videos)
        recent_date = datetime.utcnow() - timedelta(days=7)
        recent_videos = Video.query.filter(
            and_(
                Video.created_at >= recent_date,
                Video.is_active == True,
                Video.hashtags.isnot(None)
            )
        ).all()
        
        hashtag_counts = {}
        for video in recent_videos:
            hashtags = video.get_hashtags_list()
            for hashtag in hashtags:
                hashtag_counts[hashtag] = hashtag_counts.get(hashtag, 0) + 1
        
        trending_hashtags = sorted(hashtag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # Get trending cuisines
        cuisine_counts = db.session.query(
            Video.cuisine_type,
            func.count(Video.id).label('count')
        ).filter(
            and_(
                Video.created_at >= recent_date,
                Video.is_active == True,
                Video.cuisine_type.isnot(None)
            )
        ).group_by(Video.cuisine_type).order_by(desc('count')).limit(10).all()
        
        # Get featured videos
        featured_videos = Video.query.filter(
            and_(
                Video.is_featured == True,
                Video.is_active == True
            )
        ).order_by(desc(Video.created_at)).limit(5).all()
        
        # Get top vendors by engagement
        top_vendors = db.session.query(
            Vendor,
            func.sum(Video.like_count + Video.comment_count + Video.view_count).label('total_engagement')
        ).join(Video, Vendor.id == Video.vendor_id).filter(
            and_(
                Video.created_at >= recent_date,
                Video.is_active == True,
                Vendor.is_active == True
            )
        ).group_by(Vendor.id).order_by(desc('total_engagement')).limit(10).all()
        
        return jsonify({
            'trending_hashtags': [{'hashtag': tag, 'count': count} for tag, count in trending_hashtags],
            'trending_cuisines': [{'cuisine': cuisine, 'count': count} for cuisine, count in cuisine_counts],
            'featured_videos': [video.to_dict() for video in featured_videos],
            'top_vendors': [vendor.to_dict() for vendor, _ in top_vendors]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@feed_bp.route('/search', methods=['GET'])
def search_content():
    """
    Search across videos, vendors, and users
    """
    try:
        query = request.args.get('q', '').strip()
        content_type = request.args.get('type', 'all')  # all, videos, vendors, users
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        results = {}
        
        if content_type in ['all', 'videos']:
            videos = Video.query.filter(
                and_(
                    Video.is_active == True,
                    or_(
                        Video.title.ilike(f'%{query}%'),
                        Video.description.ilike(f'%{query}%'),
                        Video.hashtags.ilike(f'%{query}%'),
                        Video.cuisine_type.ilike(f'%{query}%')
                    )
                )
            ).order_by(desc(Video.created_at)).paginate(
                page=page if content_type == 'videos' else 1,
                per_page=per_page if content_type == 'videos' else 10,
                error_out=False
            )
            results['videos'] = {
                'items': [video.to_dict() for video in videos.items],
                'total': videos.total
            }
        
        if content_type in ['all', 'vendors']:
            vendors = Vendor.query.filter(
                and_(
                    Vendor.is_active == True,
                    or_(
                        Vendor.business_name.ilike(f'%{query}%'),
                        Vendor.description.ilike(f'%{query}%'),
                        Vendor.cuisine_type.ilike(f'%{query}%')
                    )
                )
            ).paginate(
                page=page if content_type == 'vendors' else 1,
                per_page=per_page if content_type == 'vendors' else 10,
                error_out=False
            )
            results['vendors'] = {
                'items': [vendor.to_dict() for vendor in vendors.items],
                'total': vendors.total
            }
        
        if content_type in ['all', 'users']:
            users = User.query.filter(
                or_(
                    User.username.ilike(f'%{query}%'),
                    User.full_name.ilike(f'%{query}%'),
                    User.bio.ilike(f'%{query}%')
                )
            ).paginate(
                page=page if content_type == 'users' else 1,
                per_page=per_page if content_type == 'users' else 10,
                error_out=False
            )
            results['users'] = {
                'items': [user.to_public_dict() for user in users.items],
                'total': users.total
            }
        
        return jsonify({
            'query': query,
            'results': results,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

