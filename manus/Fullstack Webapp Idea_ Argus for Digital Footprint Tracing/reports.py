"""
Reports Routes for Argus Digital Sentinel
Handles report generation and data export endpoints
"""

from flask import Blueprint, request, jsonify, send_file
from datetime import datetime
import json
import os
import traceback

from ..services.report_generator import report_generator
from ..services.ai_analyzer import analyzer
from ..services.data_collector import collector

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/api/reports/generate', methods=['POST'])
def generate_report():
    """Generate a comprehensive digital footprint report"""
    try:
        data = request.get_json()
        platforms_data = data.get('platforms', [])
        report_type = data.get('type', 'comprehensive')  # comprehensive, summary, csv
        
        if not platforms_data:
            return jsonify({'error': 'Platforms data is required'}), 400
        
        # Collect and analyze data for all platforms
        platform_analyses = []
        
        for platform_info in platforms_data:
            platform = platform_info.get('platform')
            username = platform_info.get('username')
            
            if platform and username:
                # Collect data
                platform_data = collector.collect_platform_data(platform, username)
                
                # Analyze data
                analysis_result = analyzer.analyze_platform_data(platform, platform_data)
                platform_analyses.append(analysis_result)
        
        if not platform_analyses:
            return jsonify({'error': 'No valid platform data to analyze'}), 400
        
        # Generate report based on type
        if report_type == 'comprehensive':
            report_path = report_generator.generate_detailed_analysis_report(platform_analyses)
            
            return jsonify({
                'success': True,
                'report_path': report_path,
                'report_type': 'markdown',
                'download_url': f'/api/reports/download/{os.path.basename(report_path)}'
            })
        
        elif report_type == 'csv':
            csv_path = os.path.join(report_generator.reports_dir, 
                                  f'analysis_data_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv')
            report_generator.export_data_csv(platform_analyses, csv_path)
            
            return jsonify({
                'success': True,
                'report_path': csv_path,
                'report_type': 'csv',
                'download_url': f'/api/reports/download/{os.path.basename(csv_path)}'
            })
        
        elif report_type == 'dashboard':
            dashboard_data = report_generator.generate_dashboard_data(platform_analyses)
            
            return jsonify({
                'success': True,
                'dashboard_data': dashboard_data
            })
        
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
    except Exception as e:
        print(f"Error generating report: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': f'Report generation failed: {str(e)}',
            'success': False
        }), 500

@reports_bp.route('/api/reports/download/<filename>', methods=['GET'])
def download_report(filename):
    """Download a generated report file"""
    try:
        file_path = os.path.join(report_generator.reports_dir, filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'Report file not found'}), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/api/reports/charts/risk-trend', methods=['POST'])
def generate_risk_trend_chart():
    """Generate risk trend chart"""
    try:
        data = request.get_json()
        scan_history = data.get('scan_history', [])
        
        chart_path = os.path.join(report_generator.reports_dir, 
                                f'risk_trend_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        generated_path = report_generator.generate_risk_trend_chart(scan_history, chart_path)
        
        if generated_path:
            return jsonify({
                'success': True,
                'chart_path': generated_path,
                'download_url': f'/api/reports/download/{os.path.basename(generated_path)}'
            })
        else:
            return jsonify({'error': 'Failed to generate chart'}), 500
        
    except Exception as e:
        print(f"Error generating risk trend chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/api/reports/charts/platform-distribution', methods=['POST'])
def generate_platform_distribution_chart():
    """Generate platform risk distribution chart"""
    try:
        data = request.get_json()
        platform_analyses = data.get('platform_analyses', [])
        
        chart_path = os.path.join(report_generator.reports_dir, 
                                f'platform_distribution_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png')
        
        generated_path = report_generator.generate_platform_distribution_chart(platform_analyses, chart_path)
        
        if generated_path:
            return jsonify({
                'success': True,
                'chart_path': generated_path,
                'download_url': f'/api/reports/download/{os.path.basename(generated_path)}'
            })
        else:
            return jsonify({'error': 'Failed to generate chart'}), 500
        
    except Exception as e:
        print(f"Error generating platform distribution chart: {str(e)}")
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/api/reports/summary', methods=['POST'])
def get_analysis_summary():
    """Get a quick analysis summary for dashboard"""
    try:
        data = request.get_json()
        platforms_data = data.get('platforms', [])
        
        if not platforms_data:
            return jsonify({'error': 'Platforms data is required'}), 400
        
        # Quick analysis for dashboard
        platform_analyses = []
        
        for platform_info in platforms_data:
            platform = platform_info.get('platform')
            username = platform_info.get('username')
            
            if platform and username:
                # Use mock data for quick response
                if platform == 'twitter':
                    mock_data = collector._get_mock_twitter_data(username)
                elif platform == 'linkedin':
                    mock_data = collector._get_mock_linkedin_data(username)
                elif platform == 'youtube':
                    mock_data = collector._get_mock_youtube_data(username)
                elif platform == 'tiktok':
                    mock_data = collector._get_mock_tiktok_data(username)
                elif platform == 'reddit':
                    mock_data = collector._get_mock_reddit_data(username)
                else:
                    continue
                
                analysis_result = analyzer.analyze_platform_data(platform, mock_data)
                platform_analyses.append(analysis_result)
        
        # Calculate overall metrics
        overall_analysis = analyzer.calculate_overall_risk(platform_analyses)
        
        # Generate dashboard data
        dashboard_data = report_generator.generate_dashboard_data(platform_analyses)
        
        return jsonify({
            'success': True,
            'platform_analyses': platform_analyses,
            'overall_analysis': overall_analysis,
            'dashboard_data': dashboard_data
        })
        
    except Exception as e:
        print(f"Error generating analysis summary: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'error': f'Analysis summary failed: {str(e)}',
            'success': False
        }), 500

@reports_bp.route('/api/reports/list', methods=['GET'])
def list_reports():
    """List all generated reports"""
    try:
        reports = []
        
        if os.path.exists(report_generator.reports_dir):
            for filename in os.listdir(report_generator.reports_dir):
                file_path = os.path.join(report_generator.reports_dir, filename)
                if os.path.isfile(file_path):
                    stat = os.stat(file_path)
                    reports.append({
                        'filename': filename,
                        'size': stat.st_size,
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'download_url': f'/api/reports/download/{filename}'
                    })
        
        # Sort by creation date (newest first)
        reports.sort(key=lambda x: x['created'], reverse=True)
        
        return jsonify({
            'success': True,
            'reports': reports
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

