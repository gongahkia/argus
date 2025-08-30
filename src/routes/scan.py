from flask import Blueprint, request, jsonify
from datetime import datetime
import sys
import os

# Add the API client path for Manus APIs
sys.path.append('/opt/.manus/.sandbox-runtime')

from ..models.user import db, User
from ..models.scan import DigitalFootprintScan, PlatformConfig, RiskAlert

scan_bp = Blueprint('scan', __name__)

@scan_bp.route('/platforms', methods=['GET'])
def get_platforms():
    """Get all configured platforms for a user"""
    user_id = request.args.get('user_id', 1)  # Default to user 1 for demo
    
    platforms = PlatformConfig.query.filter_by(user_id=user_id).all()
    return jsonify({
        'platforms': [platform.to_dict() for platform in platforms]
    })

@scan_bp.route('/platforms', methods=['POST'])
def add_platform():
    """Add a new platform configuration"""
    data = request.get_json()
    
    platform_config = PlatformConfig(
        user_id=data.get('user_id', 1),
        platform=data.get('platform'),
        username=data.get('username'),
        enabled=data.get('enabled', True),
        scan_frequency=data.get('scan_frequency', 24)
    )
    
    db.session.add(platform_config)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'platform': platform_config.to_dict()
    })

@scan_bp.route('/platforms/<int:platform_id>', methods=['PUT'])
def update_platform(platform_id):
    """Update platform configuration"""
    data = request.get_json()
    platform = PlatformConfig.query.get_or_404(platform_id)
    
    platform.username = data.get('username', platform.username)
    platform.enabled = data.get('enabled', platform.enabled)
    platform.scan_frequency = data.get('scan_frequency', platform.scan_frequency)
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'platform': platform.to_dict()
    })

@scan_bp.route('/platforms/<int:platform_id>', methods=['DELETE'])
def delete_platform(platform_id):
    """Delete platform configuration"""
    platform = PlatformConfig.query.get_or_404(platform_id)
    db.session.delete(platform)
    db.session.commit()
    
    return jsonify({'success': True})

@scan_bp.route('/scan', methods=['POST'])
def start_scan():
    """Start a digital footprint scan for a platform"""
    data = request.get_json()
    platform = data.get('platform')
    username = data.get('username')
    user_id = data.get('user_id', 1)
    
    # Create scan record
    scan = DigitalFootprintScan(
        user_id=user_id,
        platform=platform,
        username=username,
        status='pending'
    )
    
    db.session.add(scan)
    db.session.commit()
    
    # Perform the actual scan based on platform
    try:
        scan_result = perform_platform_scan(platform, username)
        
        # Update scan with results
        scan.set_raw_data(scan_result)
        scan.status = 'completed'
        
        # Perform AI analysis
        analysis_result = analyze_content(scan_result, platform)
        scan.set_analysis_results(analysis_result)
        scan.risk_score = analysis_result.get('risk_score', 0.0)
        
        # Create risk alerts if needed
        create_risk_alerts(scan, analysis_result)
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'scan': scan.to_dict()
        })
        
    except Exception as e:
        scan.status = 'failed'
        db.session.commit()
        
        return jsonify({
            'success': False,
            'error': str(e),
            'scan': scan.to_dict()
        }), 500

@scan_bp.route('/scans', methods=['GET'])
def get_scans():
    """Get all scans for a user"""
    user_id = request.args.get('user_id', 1)
    limit = request.args.get('limit', 50, type=int)
    
    scans = DigitalFootprintScan.query.filter_by(user_id=user_id)\
                                     .order_by(DigitalFootprintScan.scan_date.desc())\
                                     .limit(limit).all()
    
    return jsonify({
        'scans': [scan.to_dict() for scan in scans]
    })

@scan_bp.route('/scans/<int:scan_id>', methods=['GET'])
def get_scan_details(scan_id):
    """Get detailed scan results"""
    scan = DigitalFootprintScan.query.get_or_404(scan_id)
    
    # Get associated alerts
    alerts = RiskAlert.query.filter_by(scan_id=scan_id).all()
    
    return jsonify({
        'scan': scan.to_dict(),
        'alerts': [alert.to_dict() for alert in alerts]
    })

@scan_bp.route('/alerts', methods=['GET'])
def get_alerts():
    """Get all risk alerts for a user"""
    user_id = request.args.get('user_id', 1)
    acknowledged = request.args.get('acknowledged', type=bool)
    
    # Join with scans to filter by user
    query = db.session.query(RiskAlert).join(DigitalFootprintScan)\
                     .filter(DigitalFootprintScan.user_id == user_id)
    
    if acknowledged is not None:
        query = query.filter(RiskAlert.acknowledged == acknowledged)
    
    alerts = query.order_by(RiskAlert.created_date.desc()).all()
    
    return jsonify({
        'alerts': [alert.to_dict() for alert in alerts]
    })

@scan_bp.route('/alerts/<int:alert_id>/acknowledge', methods=['POST'])
def acknowledge_alert(alert_id):
    """Acknowledge a risk alert"""
    alert = RiskAlert.query.get_or_404(alert_id)
    alert.acknowledged = True
    db.session.commit()
    
    return jsonify({
        'success': True,
        'alert': alert.to_dict()
    })

def perform_platform_scan(platform, username):
    """Perform scan for specific platform"""
    try:
        from data_api import ApiClient
        client = ApiClient()
        
        if platform == 'twitter':
            # Get Twitter profile
            profile_result = client.call_api('Twitter/get_user_profile_by_username', 
                                           query={'username': username})
            
            # Get user tweets if profile exists
            if profile_result and 'result' in profile_result:
                user_data = profile_result['result']['data']['user']['result']
                user_id = user_data.get('rest_id')
                
                if user_id:
                    tweets_result = client.call_api('Twitter/get_user_tweets',
                                                  query={'user': user_id, 'count': '20'})
                    return {
                        'profile': profile_result,
                        'tweets': tweets_result
                    }
            
            return {'profile': profile_result}
            
        elif platform == 'linkedin':
            # Get LinkedIn profile
            profile_result = client.call_api('LinkedIn/get_user_profile_by_username',
                                           query={'username': username})
            return {'profile': profile_result}
            
        elif platform == 'youtube':
            # Get YouTube channel details
            channel_result = client.call_api('Youtube/get_channel_details',
                                           query={'id': username, 'hl': 'en'})
            return {'channel': channel_result}
            
        elif platform == 'tiktok':
            # Get TikTok user info
            user_result = client.call_api('Tiktok/get_user_info',
                                        query={'uniqueId': username})
            return {'user': user_result}
            
        elif platform == 'reddit':
            # Get Reddit posts (assuming username is subreddit)
            posts_result = client.call_api('Reddit/AccessAPI',
                                         query={'subreddit': username, 'limit': '25'})
            return {'posts': posts_result}
            
        else:
            raise ValueError(f"Unsupported platform: {platform}")
            
    except Exception as e:
        raise Exception(f"Failed to scan {platform}: {str(e)}")

def analyze_content(scan_data, platform):
    """Analyze scanned content for risks using local AI"""
    from src.services.ai_analyzer import analyzer
    
    try:
        analysis_result = analyzer.analyze_platform_data(platform, scan_data)
        analysis_result['analysis_date'] = datetime.utcnow().isoformat()
        return analysis_result
    except Exception as e:
        return {
            'risk_score': 0.0,
            'factors': [f"Analysis failed: {str(e)}"],
            'analysis_date': datetime.utcnow().isoformat(),
            'platform': platform
        }

def create_risk_alerts(scan, analysis_result):
    """Create risk alerts based on analysis results"""
    risk_score = analysis_result.get('risk_score', 0.0)
    risk_factors = analysis_result.get('risk_factors', [])
    
    if risk_score > 50:
        severity = 'high'
    elif risk_score > 25:
        severity = 'medium'
    else:
        severity = 'low'
    
    if risk_score > 20:  # Only create alerts for meaningful risks
        alert = RiskAlert(
            scan_id=scan.id,
            alert_type='content_risk',
            severity=severity,
            title=f'Potential risk detected on {scan.platform}',
            description=f'Risk score: {risk_score}/100. Factors: {", ".join(risk_factors)}',
            recommendation='Review flagged content and consider privacy settings adjustments'
        )
        
        db.session.add(alert)


@scan_bp.route('/scan/demo', methods=['POST'])
def demo_scan():
    """Demo scan endpoint for testing the interface"""
    try:
        data = request.get_json()
        platform = data.get('platform', 'twitter')
        username = data.get('username', 'demo_user')
        
        # Simulate scan process with mock data
        from ..services.data_collector import collector
        from ..services.ai_analyzer import analyzer
        
        platform_data = collector.collect_platform_data(platform, username)
        analysis_result = analyzer.analyze_platform_data(platform, platform_data)
        
        # Create demo scan result
        scan_result = {
            'scan_id': f"demo_{platform}_{username}_{int(datetime.utcnow().timestamp())}",
            'platform': platform,
            'username': username,
            'status': 'completed',
            'risk_score': analysis_result.get('risk_score', 0.0),
            'analysis_result': analysis_result,
            'started_at': datetime.utcnow().isoformat(),
            'completed_at': datetime.utcnow().isoformat()
        }
        
        return jsonify({
            'success': True,
            'scan': scan_result
        })
        
    except Exception as e:
        print(f"Error in demo_scan: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return jsonify({
            'error': f'Demo scan failed: {str(e)}',
            'success': False
        }), 500

@scan_bp.route('/platforms/supported', methods=['GET'])
def get_supported_platforms():
    """Get list of supported platforms"""
    platforms = [
        {
            'id': 'twitter',
            'name': 'Twitter',
            'description': 'Monitor tweets and profile information',
            'icon': 'twitter',
            'risk_weight': 1.2
        },
        {
            'id': 'linkedin',
            'name': 'LinkedIn',
            'description': 'Professional network monitoring',
            'icon': 'linkedin',
            'risk_weight': 1.5
        },
        {
            'id': 'youtube',
            'name': 'YouTube',
            'description': 'Video content and channel analysis',
            'icon': 'youtube',
            'risk_weight': 1.0
        },
        {
            'id': 'tiktok',
            'name': 'TikTok',
            'description': 'Short-form video content monitoring',
            'icon': 'tiktok',
            'risk_weight': 0.8
        },
        {
            'id': 'reddit',
            'name': 'Reddit',
            'description': 'Community posts and comments',
            'icon': 'reddit',
            'risk_weight': 0.9
        }
    ]
    
    return jsonify({
        'success': True,
        'platforms': platforms
    })

