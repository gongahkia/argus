"""
AI Analysis Service for Argus Digital Sentinel
Provides content analysis and risk assessment using local AI models
"""

import re
import json
from datetime import datetime
from typing import Dict, List, Any, Optional

class AIAnalyzer:
    """AI-powered content analyzer for digital footprint risk assessment"""
    
    def __init__(self):
        self.risk_keywords = {
            'high_risk': [
                'hate', 'racist', 'sexist', 'discriminatory', 'offensive',
                'illegal', 'drugs', 'violence', 'threat', 'harassment',
                'confidential', 'leaked', 'insider', 'proprietary',
                'lawsuit', 'fired', 'terminated', 'scandal', 'controversy'
            ],
            'medium_risk': [
                'controversial', 'political', 'religion', 'personal attack',
                'complaint', 'negative', 'criticism', 'unprofessional',
                'drunk', 'party', 'inappropriate', 'gossip', 'rumor'
            ],
            'low_risk': [
                'opinion', 'debate', 'discussion', 'personal', 'casual',
                'informal', 'joke', 'humor', 'sarcasm', 'meme'
            ]
        }
        
        self.professional_keywords = {
            'positive': [
                'achievement', 'award', 'promotion', 'success', 'leadership',
                'innovation', 'collaboration', 'professional', 'expertise',
                'certification', 'education', 'volunteer', 'community',
                'mentor', 'team', 'project', 'accomplished', 'recognized'
            ],
            'negative': [
                'fired', 'terminated', 'lawsuit', 'scandal', 'controversy',
                'misconduct', 'violation', 'breach', 'failure', 'incompetent',
                'lazy', 'unreliable', 'dishonest', 'unethical'
            ]
        }
        
        self.privacy_risk_indicators = [
            'phone number', 'address', 'location', 'home', 'family',
            'children', 'personal email', 'ssn', 'social security',
            'bank', 'credit card', 'password', 'private'
        ]
    
    def analyze_text_content(self, text: str, platform: str) -> Dict[str, Any]:
        """Analyze text content for potential risks"""
        if not text:
            return {'risk_score': 0.0, 'factors': [], 'sentiment': 'neutral'}
        
        text_lower = text.lower()
        risk_factors = []
        risk_score = 0.0
        
        # Check for high-risk keywords
        high_risk_found = [word for word in self.risk_keywords['high_risk'] if word in text_lower]
        if high_risk_found:
            risk_score += len(high_risk_found) * 25
            risk_factors.append(f"High-risk keywords detected: {', '.join(high_risk_found)}")
        
        # Check for medium-risk keywords
        medium_risk_found = [word for word in self.risk_keywords['medium_risk'] if word in text_lower]
        if medium_risk_found:
            risk_score += len(medium_risk_found) * 15
            risk_factors.append(f"Medium-risk keywords detected: {', '.join(medium_risk_found)}")
        
        # Check for low-risk keywords
        low_risk_found = [word for word in self.risk_keywords['low_risk'] if word in text_lower]
        if low_risk_found:
            risk_score += len(low_risk_found) * 3
            risk_factors.append(f"Casual content detected: {', '.join(low_risk_found)}")
        
        # Privacy risk analysis
        privacy_risks = [indicator for indicator in self.privacy_risk_indicators if indicator in text_lower]
        if privacy_risks:
            risk_score += len(privacy_risks) * 20
            risk_factors.append(f"Privacy risks detected: {', '.join(privacy_risks)}")
        
        # Professional content analysis
        positive_prof = [word for word in self.professional_keywords['positive'] if word in text_lower]
        negative_prof = [word for word in self.professional_keywords['negative'] if word in text_lower]
        
        if negative_prof:
            risk_score += len(negative_prof) * 30
            risk_factors.append(f"Negative professional keywords: {', '.join(negative_prof)}")
        
        if positive_prof:
            risk_score = max(0, risk_score - len(positive_prof) * 3)  # Reduce risk for positive content
            risk_factors.append(f"Positive professional content: {', '.join(positive_prof)}")
        
        # Platform-specific adjustments
        if platform == 'linkedin':
            # LinkedIn is professional, so personal content is riskier
            personal_indicators = ['personal', 'private', 'family', 'relationship', 'dating']
            personal_found = [word for word in personal_indicators if word in text_lower]
            if personal_found:
                risk_score += len(personal_found) * 8
                risk_factors.append("Personal content on professional platform")
        
        elif platform == 'twitter':
            # Twitter allows more casual content
            risk_score *= 0.8  # Reduce overall risk for Twitter
        
        # Content length analysis
        if len(text) > 1000:
            risk_factors.append("Long-form content - higher visibility")
            risk_score += 5
        
        # All caps detection (shouting)
        if text.isupper() and len(text) > 20:
            risk_score += 10
            risk_factors.append("All caps content detected (aggressive tone)")
        
        # Excessive punctuation
        if text.count('!') > 3 or text.count('?') > 3:
            risk_score += 5
            risk_factors.append("Excessive punctuation detected")
        
        # Cap risk score at 100
        risk_score = min(100.0, risk_score)
        
        # Determine sentiment
        sentiment = 'neutral'
        if risk_score > 60:
            sentiment = 'negative'
        elif risk_score > 30:
            sentiment = 'mixed'
        elif positive_prof and risk_score < 15:
            sentiment = 'positive'
        
        return {
            'risk_score': risk_score,
            'factors': risk_factors,
            'sentiment': sentiment,
            'positive_indicators': positive_prof,
            'negative_indicators': negative_prof + high_risk_found + medium_risk_found,
            'privacy_risks': privacy_risks
        }
    
    def analyze_twitter_data(self, twitter_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Twitter profile and tweets"""
        analysis_results = {
            'platform': 'twitter',
            'risk_score': 0.0,
            'factors': [],
            'profile_analysis': {},
            'content_analysis': {},
            'engagement_analysis': {}
        }
        
        # Analyze profile
        if 'profile' in twitter_data:
            profile = twitter_data['profile']
            profile_text = ""
            
            if 'result' in profile and 'data' in profile['result']:
                user_data = profile['result']['data']['user']['result']
                legacy = user_data.get('legacy', {})
                profile_text = legacy.get('description', '')
                
                # Analyze follower ratio
                followers = legacy.get('followers_count', 0)
                following = legacy.get('friends_count', 0)
                
                if following > 0:
                    ratio = followers / following
                    if ratio < 0.1:  # Following way more than followers
                        analysis_results['factors'].append("Low follower-to-following ratio")
                        analysis_results['risk_score'] += 5
            
            if profile_text:
                profile_analysis = self.analyze_text_content(profile_text, 'twitter')
                analysis_results['profile_analysis'] = profile_analysis
                analysis_results['risk_score'] += profile_analysis['risk_score'] * 0.3
                analysis_results['factors'].extend([f"Profile: {factor}" for factor in profile_analysis['factors']])
        
        # Analyze tweets
        if 'tweets' in twitter_data:
            tweets = twitter_data['tweets']
            tweet_texts = []
            tweet_count = 0
            
            # Extract tweet texts
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
                                            tweet_texts.append(tweet_text)
                                            tweet_count += 1
            
            # Analyze all tweet content
            if tweet_texts:
                combined_text = ' '.join(tweet_texts)
                content_analysis = self.analyze_text_content(combined_text, 'twitter')
                analysis_results['content_analysis'] = content_analysis
                analysis_results['risk_score'] += content_analysis['risk_score'] * 0.7
                analysis_results['factors'].extend([f"Tweets: {factor}" for factor in content_analysis['factors']])
                analysis_results['factors'].append(f"Analyzed {tweet_count} recent tweets")
        
        return analysis_results
    
    def analyze_linkedin_data(self, linkedin_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze LinkedIn profile data"""
        analysis_results = {
            'platform': 'linkedin',
            'risk_score': 0.0,
            'factors': [],
            'profile_analysis': {},
            'professional_score': 0.0
        }
        
        if 'profile' in linkedin_data:
            profile = linkedin_data['profile']
            
            # Extract profile text
            profile_texts = []
            if 'summary' in profile and profile['summary']:
                profile_texts.append(profile['summary'])
            if 'headline' in profile and profile['headline']:
                profile_texts.append(profile['headline'])
            
            # Analyze positions for professional content
            positions = profile.get('position', [])
            for position in positions:
                if 'description' in position and position['description']:
                    profile_texts.append(position['description'])
            
            if profile_texts:
                combined_text = ' '.join(profile_texts)
                profile_analysis = self.analyze_text_content(combined_text, 'linkedin')
                analysis_results['profile_analysis'] = profile_analysis
                analysis_results['risk_score'] = profile_analysis['risk_score']
                analysis_results['factors'] = profile_analysis['factors']
                
                # Calculate professional score
                positive_count = len(profile_analysis.get('positive_indicators', []))
                negative_count = len(profile_analysis.get('negative_indicators', []))
                analysis_results['professional_score'] = max(0, positive_count * 10 - negative_count * 15)
        
        return analysis_results
    
    def analyze_youtube_data(self, youtube_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze YouTube channel data"""
        analysis_results = {
            'platform': 'youtube',
            'risk_score': 0.0,
            'factors': [],
            'channel_analysis': {},
            'content_analysis': {}
        }
        
        # Analyze channel description
        if 'channel' in youtube_data:
            channel = youtube_data['channel']
            description = channel.get('description', '')
            
            if description:
                channel_analysis = self.analyze_text_content(description, 'youtube')
                analysis_results['channel_analysis'] = channel_analysis
                analysis_results['risk_score'] += channel_analysis['risk_score'] * 0.4
                analysis_results['factors'].extend([f"Channel: {factor}" for factor in channel_analysis['factors']])
        
        # Analyze video titles
        if 'videos' in youtube_data:
            videos = youtube_data['videos']
            video_titles = []
            
            contents = videos.get('contents', [])
            for content in contents:
                if content.get('type') == 'video':
                    video = content.get('video', {})
                    title = video.get('title', '')
                    if title:
                        video_titles.append(title)
            
            if video_titles:
                combined_titles = ' '.join(video_titles)
                content_analysis = self.analyze_text_content(combined_titles, 'youtube')
                analysis_results['content_analysis'] = content_analysis
                analysis_results['risk_score'] += content_analysis['risk_score'] * 0.6
                analysis_results['factors'].extend([f"Videos: {factor}" for factor in content_analysis['factors']])
                analysis_results['factors'].append(f"Analyzed {len(video_titles)} video titles")
        
        return analysis_results
    
    def analyze_tiktok_data(self, tiktok_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze TikTok user data"""
        analysis_results = {
            'platform': 'tiktok',
            'risk_score': 0.0,
            'factors': [],
            'profile_analysis': {}
        }
        
        if 'user' in tiktok_data:
            user = tiktok_data['user']
            user_info = user.get('userInfo', {})
            user_data = user_info.get('user', {})
            
            signature = user_data.get('signature', '')
            nickname = user_data.get('nickname', '')
            
            # Combine text for analysis
            combined_text = f"{signature} {nickname}"
            
            if combined_text.strip():
                profile_analysis = self.analyze_text_content(combined_text, 'tiktok')
                analysis_results['profile_analysis'] = profile_analysis
                analysis_results['risk_score'] = profile_analysis['risk_score']
                analysis_results['factors'] = profile_analysis['factors']
        
        return analysis_results
    
    def analyze_reddit_data(self, reddit_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze Reddit posts data"""
        analysis_results = {
            'platform': 'reddit',
            'risk_score': 0.0,
            'factors': [],
            'content_analysis': {}
        }
        
        if 'posts' in reddit_data:
            posts = reddit_data['posts']
            post_texts = []
            
            posts_list = posts.get('posts', [])
            for post_wrapper in posts_list:
                post = post_wrapper.get('data', {})
                title = post.get('title', '')
                selftext = post.get('selftext', '')
                
                if title:
                    post_texts.append(title)
                if selftext:
                    post_texts.append(selftext)
            
            if post_texts:
                combined_text = ' '.join(post_texts)
                content_analysis = self.analyze_text_content(combined_text, 'reddit')
                analysis_results['content_analysis'] = content_analysis
                analysis_results['risk_score'] = content_analysis['risk_score']
                analysis_results['factors'] = content_analysis['factors']
                analysis_results['factors'].append(f"Analyzed {len(post_texts)} posts/comments")
        
        return analysis_results
    
    def generate_recommendations(self, analysis_result: Dict[str, Any]) -> List[str]:
        """Generate actionable recommendations based on analysis"""
        recommendations = []
        risk_score = analysis_result.get('risk_score', 0.0)
        platform = analysis_result.get('platform', '')
        factors = analysis_result.get('factors', [])
        
        if risk_score > 70:
            recommendations.append("🚨 URGENT: Review and consider removing high-risk content immediately")
            recommendations.append("Consider consulting with a professional reputation management service")
        elif risk_score > 40:
            recommendations.append("⚠️ Review flagged content and consider editing or removing problematic posts")
            recommendations.append("Update privacy settings to limit public visibility")
        elif risk_score > 20:
            recommendations.append("💡 Minor concerns detected - review content for potential improvements")
        else:
            recommendations.append("✅ Your digital footprint looks good! Keep up the professional standards")
        
        # Platform-specific recommendations
        if platform == 'linkedin':
            if risk_score > 15:
                recommendations.append("LinkedIn is a professional platform - ensure all content aligns with career goals")
            recommendations.append("Consider adding more professional achievements and certifications")
        
        elif platform == 'twitter':
            if risk_score > 25:
                recommendations.append("Twitter content is highly visible - consider the professional impact of tweets")
            recommendations.append("Review tweet history and consider deleting controversial posts")
        
        elif platform == 'youtube':
            if risk_score > 20:
                recommendations.append("Video content has lasting impact - review video titles and descriptions")
        
        # Privacy-specific recommendations
        if any('privacy' in factor.lower() for factor in factors):
            recommendations.append("🔒 Review privacy settings across all platforms")
            recommendations.append("Avoid sharing personal information in public posts")
        
        return recommendations
    
    def calculate_overall_risk(self, platform_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate overall risk score across all platforms"""
        if not platform_analyses:
            return {'overall_risk': 0.0, 'platform_breakdown': {}, 'recommendations': []}
        
        total_risk = 0.0
        platform_breakdown = {}
        all_factors = []
        
        # Weight platforms by professional importance
        platform_weights = {
            'linkedin': 1.5,  # Most important for career
            'twitter': 1.2,   # High visibility
            'youtube': 1.0,   # Moderate impact
            'tiktok': 0.8,    # Less professional impact
            'reddit': 0.9     # Community-based
        }
        
        total_weight = 0.0
        
        for analysis in platform_analyses:
            platform = analysis.get('platform', '')
            risk_score = analysis.get('risk_score', 0.0)
            weight = platform_weights.get(platform, 1.0)
            
            weighted_risk = risk_score * weight
            total_risk += weighted_risk
            total_weight += weight
            
            platform_breakdown[platform] = {
                'risk_score': risk_score,
                'weight': weight,
                'weighted_risk': weighted_risk
            }
            
            all_factors.extend(analysis.get('factors', []))
        
        overall_risk = total_risk / total_weight if total_weight > 0 else 0.0
        
        # Generate overall recommendations
        overall_recommendations = []
        if overall_risk > 50:
            overall_recommendations.append("🚨 HIGH RISK: Immediate action required across multiple platforms")
        elif overall_risk > 25:
            overall_recommendations.append("⚠️ MEDIUM RISK: Review and improve content across platforms")
        else:
            overall_recommendations.append("✅ LOW RISK: Your digital footprint is generally healthy")
        
        return {
            'overall_risk': round(overall_risk, 1),
            'platform_breakdown': platform_breakdown,
            'all_factors': all_factors,
            'recommendations': overall_recommendations
        }
    
    def analyze_platform_data(self, platform: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Main entry point for platform-specific analysis"""
        if platform == 'twitter':
            return self.analyze_twitter_data(data)
        elif platform == 'linkedin':
            return self.analyze_linkedin_data(data)
        elif platform == 'youtube':
            return self.analyze_youtube_data(data)
        elif platform == 'tiktok':
            return self.analyze_tiktok_data(data)
        elif platform == 'reddit':
            return self.analyze_reddit_data(data)
        else:
            # Generic analysis for unsupported platforms
            return {
                'platform': platform,
                'risk_score': 0.0,
                'factors': [f'Analysis for {platform} not yet implemented'],
                'analysis_date': datetime.utcnow().isoformat()
            }

# Global analyzer instance
analyzer = AIAnalyzer()

