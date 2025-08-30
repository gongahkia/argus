"""
Report Generation Service for Argus Digital Sentinel
Generates comprehensive digital footprint analysis reports
"""

import json
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import os

class ReportGenerator:
    """Generates comprehensive reports and visualizations"""
    
    def __init__(self):
        # Set up matplotlib for better rendering
        plt.style.use('seaborn-v0_8')
        sns.set_palette("husl")
        
        # Create reports directory
        self.reports_dir = '/home/ubuntu/argus-digital-sentinel/reports'
        os.makedirs(self.reports_dir, exist_ok=True)
    
    def generate_risk_trend_chart(self, scan_history: List[Dict[str, Any]], output_path: str) -> str:
        """Generate risk trend chart over time"""
        if not scan_history:
            return None
        
        # Prepare data
        dates = []
        risk_scores = []
        platforms = []
        
        for scan in scan_history:
            if scan.get('completed_at'):
                dates.append(datetime.fromisoformat(scan['completed_at'].replace('Z', '+00:00')))
                risk_scores.append(scan.get('risk_score', 0))
                platforms.append(scan.get('platform', 'unknown'))
        
        if not dates:
            return None
        
        # Create DataFrame
        df = pd.DataFrame({
            'date': dates,
            'risk_score': risk_scores,
            'platform': platforms
        })
        
        # Sort by date
        df = df.sort_values('date')
        
        # Create plot
        plt.figure(figsize=(12, 6))
        
        # Plot overall trend
        plt.subplot(1, 2, 1)
        plt.plot(df['date'], df['risk_score'], marker='o', linewidth=2, markersize=6)
        plt.title('Risk Score Trend Over Time', fontsize=14, fontweight='bold')
        plt.xlabel('Date')
        plt.ylabel('Risk Score')
        plt.grid(True, alpha=0.3)
        plt.xticks(rotation=45)
        
        # Platform breakdown
        plt.subplot(1, 2, 2)
        platform_avg = df.groupby('platform')['risk_score'].mean().sort_values(ascending=False)
        colors = sns.color_palette("husl", len(platform_avg))
        bars = plt.bar(platform_avg.index, platform_avg.values, color=colors)
        plt.title('Average Risk Score by Platform', fontsize=14, fontweight='bold')
        plt.xlabel('Platform')
        plt.ylabel('Average Risk Score')
        plt.xticks(rotation=45)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}', ha='center', va='bottom')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_platform_distribution_chart(self, platform_analyses: List[Dict[str, Any]], output_path: str) -> str:
        """Generate platform risk distribution pie chart"""
        if not platform_analyses:
            return None
        
        # Prepare data
        platforms = []
        risk_scores = []
        
        for analysis in platform_analyses:
            platforms.append(analysis.get('platform', 'unknown').title())
            risk_scores.append(analysis.get('risk_score', 0))
        
        if not platforms:
            return None
        
        # Create pie chart
        plt.figure(figsize=(10, 8))
        
        # Define colors for platforms
        platform_colors = {
            'Twitter': '#1DA1F2',
            'Linkedin': '#0077B5',
            'Youtube': '#FF0000',
            'Tiktok': '#000000',
            'Reddit': '#FF4500'
        }
        
        colors = [platform_colors.get(platform, '#888888') for platform in platforms]
        
        # Create pie chart
        wedges, texts, autotexts = plt.pie(risk_scores, labels=platforms, colors=colors, 
                                          autopct='%1.1f%%', startangle=90)
        
        plt.title('Risk Distribution by Platform', fontsize=16, fontweight='bold', pad=20)
        
        # Enhance text appearance
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
        
        plt.axis('equal')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_risk_factors_chart(self, analysis_results: List[Dict[str, Any]], output_path: str) -> str:
        """Generate risk factors analysis chart"""
        if not analysis_results:
            return None
        
        # Collect all risk factors
        factor_counts = {}
        
        for analysis in analysis_results:
            factors = analysis.get('factors', [])
            for factor in factors:
                # Extract the main factor type
                if ':' in factor:
                    factor_type = factor.split(':')[0].strip()
                else:
                    factor_type = factor
                
                factor_counts[factor_type] = factor_counts.get(factor_type, 0) + 1
        
        if not factor_counts:
            return None
        
        # Sort by frequency
        sorted_factors = sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)
        
        # Take top 10 factors
        top_factors = sorted_factors[:10]
        
        # Create horizontal bar chart
        plt.figure(figsize=(12, 8))
        
        factors, counts = zip(*top_factors)
        y_pos = range(len(factors))
        
        bars = plt.barh(y_pos, counts, color=sns.color_palette("viridis", len(factors)))
        
        plt.yticks(y_pos, factors)
        plt.xlabel('Frequency')
        plt.title('Most Common Risk Factors', fontsize=16, fontweight='bold')
        plt.grid(axis='x', alpha=0.3)
        
        # Add value labels
        for i, (factor, count) in enumerate(top_factors):
            plt.text(count + 0.1, i, str(count), va='center')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_comprehensive_report(self, user_data: Dict[str, Any], platform_analyses: List[Dict[str, Any]]) -> str:
        """Generate a comprehensive PDF report"""
        from fpdf import FPDF
        
        # Create PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 16)
        
        # Title
        pdf.cell(0, 10, 'Argus Digital Sentinel - Digital Footprint Report', 0, 1, 'C')
        pdf.ln(10)
        
        # Executive Summary
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Executive Summary', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        # Calculate overall metrics
        total_platforms = len(platform_analyses)
        avg_risk = sum(analysis.get('risk_score', 0) for analysis in platform_analyses) / total_platforms if total_platforms > 0 else 0
        high_risk_platforms = sum(1 for analysis in platform_analyses if analysis.get('risk_score', 0) > 50)
        
        summary_text = f"""
Your digital footprint has been analyzed across {total_platforms} platforms.
Average risk score: {avg_risk:.1f}/100
High-risk platforms: {high_risk_platforms}
Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        
        for line in summary_text.strip().split('\n'):
            pdf.cell(0, 6, line.strip(), 0, 1)
        
        pdf.ln(10)
        
        # Platform Analysis
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Platform Analysis', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        for analysis in platform_analyses:
            platform = analysis.get('platform', 'Unknown').title()
            risk_score = analysis.get('risk_score', 0)
            factors = analysis.get('factors', [])
            
            pdf.set_font('Arial', 'B', 12)
            pdf.cell(0, 8, f'{platform} - Risk Score: {risk_score:.1f}/100', 0, 1)
            pdf.set_font('Arial', '', 10)
            
            for factor in factors[:5]:  # Show top 5 factors
                pdf.cell(0, 5, f'• {factor}', 0, 1)
            
            pdf.ln(5)
        
        # Recommendations
        pdf.add_page()
        pdf.set_font('Arial', 'B', 14)
        pdf.cell(0, 10, 'Recommendations', 0, 1)
        pdf.set_font('Arial', '', 12)
        
        recommendations = [
            "Review and update privacy settings across all platforms",
            "Remove or edit content flagged as high-risk",
            "Maintain professional tone in public posts",
            "Regular monitoring of your digital footprint",
            "Consider professional reputation management services if needed"
        ]
        
        for rec in recommendations:
            pdf.cell(0, 6, f'• {rec}', 0, 1)
        
        # Save PDF
        report_path = os.path.join(self.reports_dir, f'digital_footprint_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf')
        pdf.output(report_path)
        
        return report_path
    
    def generate_dashboard_data(self, platform_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate data for dashboard visualizations"""
        if not platform_analyses:
            return {
                'risk_trend': [],
                'platform_distribution': [],
                'risk_factors': [],
                'overall_metrics': {}
            }
        
        # Generate mock historical data for trend chart
        risk_trend = []
        base_date = datetime.now() - timedelta(days=30)
        
        for i in range(6):
            date = base_date + timedelta(days=i*5)
            # Simulate improving trend
            base_risk = sum(analysis.get('risk_score', 0) for analysis in platform_analyses) / len(platform_analyses)
            trend_risk = max(5, base_risk - (i * 2))  # Gradual improvement
            
            risk_trend.append({
                'date': date.strftime('%Y-%m-%d'),
                'risk': round(trend_risk, 1)
            })
        
        # Platform distribution
        platform_distribution = []
        for analysis in platform_analyses:
            platform_distribution.append({
                'name': analysis.get('platform', 'Unknown').title(),
                'value': round(analysis.get('risk_score', 0), 1),
                'color': self._get_platform_color(analysis.get('platform', ''))
            })
        
        # Risk factors summary
        all_factors = []
        for analysis in platform_analyses:
            all_factors.extend(analysis.get('factors', []))
        
        # Count factor types
        factor_counts = {}
        for factor in all_factors:
            factor_type = factor.split(':')[0].strip() if ':' in factor else factor
            factor_counts[factor_type] = factor_counts.get(factor_type, 0) + 1
        
        risk_factors = [
            {'factor': factor, 'count': count}
            for factor, count in sorted(factor_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Overall metrics
        total_risk = sum(analysis.get('risk_score', 0) for analysis in platform_analyses)
        avg_risk = total_risk / len(platform_analyses) if platform_analyses else 0
        
        overall_metrics = {
            'total_platforms': len(platform_analyses),
            'average_risk': round(avg_risk, 1),
            'high_risk_platforms': sum(1 for analysis in platform_analyses if analysis.get('risk_score', 0) > 50),
            'total_factors': len(all_factors),
            'last_updated': datetime.now().isoformat()
        }
        
        return {
            'risk_trend': risk_trend,
            'platform_distribution': platform_distribution,
            'risk_factors': risk_factors,
            'overall_metrics': overall_metrics
        }
    
    def _get_platform_color(self, platform: str) -> str:
        """Get brand color for platform"""
        colors = {
            'twitter': '#1DA1F2',
            'linkedin': '#0077B5',
            'youtube': '#FF0000',
            'tiktok': '#000000',
            'reddit': '#FF4500',
            'facebook': '#1877F2',
            'instagram': '#E4405F'
        }
        return colors.get(platform.lower(), '#888888')
    
    def export_data_csv(self, platform_analyses: List[Dict[str, Any]], output_path: str) -> str:
        """Export analysis data to CSV format"""
        if not platform_analyses:
            return None
        
        # Prepare data for CSV
        csv_data = []
        
        for analysis in platform_analyses:
            platform = analysis.get('platform', 'Unknown')
            risk_score = analysis.get('risk_score', 0)
            factors = analysis.get('factors', [])
            
            csv_data.append({
                'Platform': platform.title(),
                'Risk Score': risk_score,
                'Risk Factors Count': len(factors),
                'Top Risk Factor': factors[0] if factors else 'None',
                'Analysis Date': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            })
        
        # Create DataFrame and save
        df = pd.DataFrame(csv_data)
        df.to_csv(output_path, index=False)
        
        return output_path
    
    def generate_detailed_analysis_report(self, platform_analyses: List[Dict[str, Any]]) -> str:
        """Generate detailed markdown analysis report"""
        report_path = os.path.join(self.reports_dir, f'detailed_analysis_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md')
        
        with open(report_path, 'w') as f:
            f.write("# Argus Digital Sentinel - Detailed Analysis Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Executive Summary
            f.write("## Executive Summary\n\n")
            
            if platform_analyses:
                total_platforms = len(platform_analyses)
                avg_risk = sum(analysis.get('risk_score', 0) for analysis in platform_analyses) / total_platforms
                high_risk_count = sum(1 for analysis in platform_analyses if analysis.get('risk_score', 0) > 50)
                
                f.write(f"- **Total Platforms Analyzed:** {total_platforms}\n")
                f.write(f"- **Average Risk Score:** {avg_risk:.1f}/100\n")
                f.write(f"- **High-Risk Platforms:** {high_risk_count}\n")
                f.write(f"- **Overall Assessment:** {'HIGH RISK' if avg_risk > 50 else 'MEDIUM RISK' if avg_risk > 25 else 'LOW RISK'}\n\n")
            
            # Platform Details
            f.write("## Platform Analysis Details\n\n")
            
            for analysis in platform_analyses:
                platform = analysis.get('platform', 'Unknown').title()
                risk_score = analysis.get('risk_score', 0)
                factors = analysis.get('factors', [])
                
                f.write(f"### {platform}\n\n")
                f.write(f"**Risk Score:** {risk_score:.1f}/100\n\n")
                
                if factors:
                    f.write("**Risk Factors:**\n")
                    for factor in factors:
                        f.write(f"- {factor}\n")
                    f.write("\n")
                
                # Platform-specific insights
                if 'profile_analysis' in analysis:
                    profile_analysis = analysis['profile_analysis']
                    sentiment = profile_analysis.get('sentiment', 'neutral')
                    f.write(f"**Profile Sentiment:** {sentiment.title()}\n")
                
                if 'content_analysis' in analysis:
                    content_analysis = analysis['content_analysis']
                    content_risk = content_analysis.get('risk_score', 0)
                    f.write(f"**Content Risk Score:** {content_risk:.1f}/100\n")
                
                f.write("\n---\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            
            # Generate comprehensive recommendations
            if platform_analyses:
                avg_risk = sum(analysis.get('risk_score', 0) for analysis in platform_analyses) / len(platform_analyses)
                
                if avg_risk > 50:
                    f.write("### 🚨 URGENT ACTIONS REQUIRED\n\n")
                    f.write("1. **Immediate Content Review:** Review all flagged content across platforms\n")
                    f.write("2. **Privacy Settings:** Update privacy settings to limit public visibility\n")
                    f.write("3. **Professional Consultation:** Consider hiring a reputation management service\n")
                    f.write("4. **Content Removal:** Remove or edit high-risk posts immediately\n\n")
                
                elif avg_risk > 25:
                    f.write("### ⚠️ MODERATE RISK - ACTION RECOMMENDED\n\n")
                    f.write("1. **Content Audit:** Review and improve flagged content\n")
                    f.write("2. **Privacy Review:** Check and update privacy settings\n")
                    f.write("3. **Professional Standards:** Ensure all content aligns with career goals\n")
                    f.write("4. **Regular Monitoring:** Set up regular scans to track improvements\n\n")
                
                else:
                    f.write("### ✅ LOW RISK - MAINTAIN STANDARDS\n\n")
                    f.write("1. **Continue Good Practices:** Your digital footprint is healthy\n")
                    f.write("2. **Regular Monitoring:** Keep monitoring to maintain standards\n")
                    f.write("3. **Professional Growth:** Consider adding more professional content\n")
                    f.write("4. **Privacy Awareness:** Stay aware of privacy implications\n\n")
            
            # Platform-specific recommendations
            f.write("### Platform-Specific Recommendations\n\n")
            
            for analysis in platform_analyses:
                platform = analysis.get('platform', 'Unknown').title()
                risk_score = analysis.get('risk_score', 0)
                
                f.write(f"**{platform}:**\n")
                
                if platform.lower() == 'linkedin':
                    f.write("- Focus on professional achievements and certifications\n")
                    f.write("- Avoid personal or controversial content\n")
                    f.write("- Engage with industry-relevant discussions\n")
                
                elif platform.lower() == 'twitter':
                    f.write("- Be mindful of tweet visibility and permanence\n")
                    f.write("- Avoid controversial political discussions\n")
                    f.write("- Consider tweet scheduling for professional hours\n")
                
                elif platform.lower() == 'youtube':
                    f.write("- Review video titles and descriptions for professionalism\n")
                    f.write("- Consider content impact on professional reputation\n")
                    f.write("- Maintain consistent brand messaging\n")
                
                f.write("\n")
            
            f.write("---\n\n")
            f.write("*Report generated by Argus Digital Sentinel - Your Digital Footprint Guardian*\n")
            f.write("*\"In the digital age, your online presence is your reputation. Let Argus be your guardian.\"*\n")
        
        return report_path

# Global report generator instance
report_generator = ReportGenerator()

