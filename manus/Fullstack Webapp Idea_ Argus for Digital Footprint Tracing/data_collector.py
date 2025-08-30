"""
Data Collection Service for Argus Digital Sentinel
Handles data collection from various social media platforms using Manus APIs
"""

import sys
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

# Add the API client path for Manus APIs
sys.path.append('/opt/.manus/.sandbox-runtime')

class DataCollector:
    """Handles data collection from various social media platforms"""
    
    def __init__(self):
        try:
            from data_api import ApiClient
            self.client = ApiClient()
            self.api_available = True
        except ImportError:
            print("Warning: Manus API client not available. Using mock data.")
            self.api_available = False
    
    def collect_twitter_data(self, username: str) -> Dict[str, Any]:
        """Collect Twitter profile and tweets data"""
        if not self.api_available:
            return self._get_mock_twitter_data(username)
        
        try:
            # Get Twitter profile
            profile_result = self.client.call_api('Twitter/get_user_profile_by_username', 
                                                query={'username': username})
            
            data = {'profile': profile_result}
            
            # Get user tweets if profile exists
            if profile_result and 'result' in profile_result:
                user_data = profile_result['result']['data']['user']['result']
                user_id = user_data.get('rest_id')
                
                if user_id:
                    tweets_result = self.client.call_api('Twitter/get_user_tweets',
                                                       query={'user': user_id, 'count': '20'})
                    data['tweets'] = tweets_result
            
            return data
            
        except Exception as e:
            print(f"Error collecting Twitter data: {str(e)}")
            return self._get_mock_twitter_data(username)
    
    def collect_linkedin_data(self, username: str) -> Dict[str, Any]:
        """Collect LinkedIn profile data"""
        if not self.api_available:
            return self._get_mock_linkedin_data(username)
        
        try:
            profile_result = self.client.call_api('LinkedIn/get_user_profile_by_username',
                                                query={'username': username})
            return {'profile': profile_result}
            
        except Exception as e:
            print(f"Error collecting LinkedIn data: {str(e)}")
            return self._get_mock_linkedin_data(username)
    
    def collect_youtube_data(self, username: str) -> Dict[str, Any]:
        """Collect YouTube channel data"""
        if not self.api_available:
            return self._get_mock_youtube_data(username)
        
        try:
            # Get channel details
            channel_result = self.client.call_api('Youtube/get_channel_details',
                                                query={'id': username, 'hl': 'en'})
            
            data = {'channel': channel_result}
            
            # Get channel videos if channel exists
            if channel_result and 'channelId' in channel_result:
                videos_result = self.client.call_api('Youtube/get_channel_videos',
                                                   query={'id': channel_result['channelId'], 'filter': 'videos_latest'})
                data['videos'] = videos_result
            
            return data
            
        except Exception as e:
            print(f"Error collecting YouTube data: {str(e)}")
            return self._get_mock_youtube_data(username)
    
    def collect_tiktok_data(self, username: str) -> Dict[str, Any]:
        """Collect TikTok user data"""
        if not self.api_available:
            return self._get_mock_tiktok_data(username)
        
        try:
            user_result = self.client.call_api('Tiktok/get_user_info',
                                             query={'uniqueId': username})
            return {'user': user_result}
            
        except Exception as e:
            print(f"Error collecting TikTok data: {str(e)}")
            return self._get_mock_tiktok_data(username)
    
    def collect_reddit_data(self, username: str) -> Dict[str, Any]:
        """Collect Reddit posts data"""
        if not self.api_available:
            return self._get_mock_reddit_data(username)
        
        try:
            posts_result = self.client.call_api('Reddit/AccessAPI',
                                              query={'subreddit': username, 'limit': '25'})
            return {'posts': posts_result}
            
        except Exception as e:
            print(f"Error collecting Reddit data: {str(e)}")
            return self._get_mock_reddit_data(username)
    
    def collect_platform_data(self, platform: str, username: str) -> Dict[str, Any]:
        """Main entry point for platform data collection"""
        print(f"Collecting data for {platform}: {username}")
        
        if platform == 'twitter':
            return self.collect_twitter_data(username)
        elif platform == 'linkedin':
            return self.collect_linkedin_data(username)
        elif platform == 'youtube':
            return self.collect_youtube_data(username)
        elif platform == 'tiktok':
            return self.collect_tiktok_data(username)
        elif platform == 'reddit':
            return self.collect_reddit_data(username)
        else:
            raise ValueError(f"Unsupported platform: {platform}")
    
    def extract_text_content(self, platform: str, data: Dict[str, Any]) -> List[str]:
        """Extract text content from platform data for analysis"""
        texts = []
        
        if platform == 'twitter':
            # Extract profile description
            if 'profile' in data:
                profile = data['profile']
                if 'result' in profile and 'data' in profile['result']:
                    user_data = profile['result']['data']['user']['result']
                    legacy = user_data.get('legacy', {})
                    description = legacy.get('description', '')
                    if description:
                        texts.append(description)
            
            # Extract tweet texts
            if 'tweets' in data:
                tweets = data['tweets']
                if 'result' in tweets and 'timeline' in tweets['result']:
                    timeline = tweets['result']['timeline']
                    instructions = timeline.get('instructions', [])
                    
                    for instruction in instructions:
                        if instruction.get('type') == 'TimelineAddEntries':
                            entries = instruction.get('entries', [])
                            for entry in entries:
                                if entry.get('entryId', '').startswith('tweet-'):
                                    content = entry.get('content', {})
                                    if 'itemContent' in content:
                                        tweet_results = content['itemContent'].get('tweet_results', {})
                                        if 'result' in tweet_results:
                                            tweet_data = tweet_results['result']
                                            legacy = tweet_data.get('legacy', {})
                                            tweet_text = legacy.get('full_text', '')
                                            if tweet_text:
                                                texts.append(tweet_text)
        
        elif platform == 'linkedin':
            if 'profile' in data:
                profile = data['profile']
                
                # Extract summary and headline
                if 'summary' in profile:
                    texts.append(profile['summary'])
                if 'headline' in profile:
                    texts.append(profile['headline'])
                
                # Extract position descriptions
                positions = profile.get('position', [])
                for position in positions:
                    if 'description' in position:
                        texts.append(position['description'])
        
        elif platform == 'youtube':
            if 'channel' in data:
                channel = data['channel']
                if 'description' in channel:
                    texts.append(channel['description'])
            
            # Extract video titles and descriptions
            if 'videos' in data:
                videos = data['videos']
                contents = videos.get('contents', [])
                for content in contents:
                    if content.get('type') == 'video':
                        video = content.get('video', {})
                        title = video.get('title', '')
                        if title:
                            texts.append(title)
        
        elif platform == 'tiktok':
            if 'user' in data:
                user = data['user']
                user_info = user.get('userInfo', {})
                user_data = user_info.get('user', {})
                
                signature = user_data.get('signature', '')
                if signature:
                    texts.append(signature)
        
        elif platform == 'reddit':
            if 'posts' in data:
                posts = data['posts']
                posts_list = posts.get('posts', [])
                for post_wrapper in posts_list:
                    post = post_wrapper.get('data', {})
                    title = post.get('title', '')
                    selftext = post.get('selftext', '')
                    if title:
                        texts.append(title)
                    if selftext:
                        texts.append(selftext)
        
        return texts
    
    # Mock data methods for testing when APIs are not available
    def _get_mock_twitter_data(self, username: str) -> Dict[str, Any]:
        """Generate mock Twitter data for testing"""
        return {
            'profile': {
                'result': {
                    'data': {
                        'user': {
                            'result': {
                                'legacy': {
                                    'description': f'Mock Twitter profile for {username}. This is a test profile for Argus Digital Sentinel.',
                                    'screen_name': username,
                                    'name': f'{username.title()} Test User',
                                    'followers_count': 1250,
                                    'friends_count': 890
                                },
                                'rest_id': '123456789'
                            }
                        }
                    }
                }
            },
            'tweets': {
                'result': {
                    'timeline': {
                        'instructions': [{
                            'type': 'TimelineAddEntries',
                            'entries': [{
                                'entryId': 'tweet-1',
                                'content': {
                                    'itemContent': {
                                        'tweet_results': {
                                            'result': {
                                                'legacy': {
                                                    'full_text': 'Just finished an amazing project! Really excited about the future of AI and technology.',
                                                    'created_at': 'Mon Jan 15 10:30:00 +0000 2025'
                                                }
                                            }
                                        }
                                    }
                                }
                            }]
                        }]
                    }
                }
            }
        }
    
    def _get_mock_linkedin_data(self, username: str) -> Dict[str, Any]:
        """Generate mock LinkedIn data for testing"""
        return {
            'profile': {
                'firstName': username.title(),
                'lastName': 'TestUser',
                'headline': 'Software Engineer at Tech Company',
                'summary': f'Experienced professional with expertise in technology and innovation. Mock profile for {username}.',
                'position': [{
                    'title': 'Senior Software Engineer',
                    'companyName': 'Tech Innovations Inc.',
                    'description': 'Leading development of cutting-edge software solutions.',
                    'start': {'year': 2022},
                    'end': {'year': 0}  # Current position
                }]
            }
        }
    
    def _get_mock_youtube_data(self, username: str) -> Dict[str, Any]:
        """Generate mock YouTube data for testing"""
        return {
            'channel': {
                'channelId': 'UC123456789',
                'title': f'{username.title()} Channel',
                'description': f'Welcome to {username}\'s channel! Creating content about technology and innovation.',
                'stats': {
                    'subscribers': '10.5K',
                    'videos': '45',
                    'views': '250K'
                }
            },
            'videos': {
                'contents': [{
                    'type': 'video',
                    'video': {
                        'title': 'My Latest Tech Review - Amazing Innovation!',
                        'videoId': 'abc123def456',
                        'publishedTimeText': '2 days ago',
                        'stats': {'views': 5420}
                    }
                }]
            }
        }
    
    def _get_mock_tiktok_data(self, username: str) -> Dict[str, Any]:
        """Generate mock TikTok data for testing"""
        return {
            'user': {
                'userInfo': {
                    'user': {
                        'id': '123456789',
                        'uniqueId': username,
                        'nickname': f'{username.title()} TikTok',
                        'signature': f'Creating fun content! Follow {username} for more amazing videos.',
                        'verified': False,
                        'privateAccount': False
                    },
                    'stats': {
                        'followerCount': 8500,
                        'followingCount': 450,
                        'heartCount': 125000,
                        'videoCount': 67
                    }
                }
            }
        }
    
    def _get_mock_reddit_data(self, username: str) -> Dict[str, Any]:
        """Generate mock Reddit data for testing"""
        return {
            'posts': {
                'posts': [{
                    'data': {
                        'title': 'Great discussion about technology trends',
                        'selftext': 'I wanted to share my thoughts on the latest developments in AI and how they might impact our industry.',
                        'author': username,
                        'score': 45,
                        'created_utc': 1705320600
                    }
                }]
            }
        }

# Global data collector instance
collector = DataCollector()

