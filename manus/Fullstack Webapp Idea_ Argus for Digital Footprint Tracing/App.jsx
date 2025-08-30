import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Eye, Shield, AlertTriangle, CheckCircle, Plus, Scan, Twitter, Linkedin, Youtube, Users, Heart } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import './App.css'

// API Configuration
const API_BASE_URL = 'http://localhost:5001/api'

function App() {
  const [platforms, setPlatforms] = useState([])
  const [scans, setScans] = useState([])
  const [alerts, setAlerts] = useState([])
  const [isScanning, setIsScanning] = useState(false)
  const [newPlatform, setNewPlatform] = useState({ platform: '', username: '' })
  const [dashboardData, setDashboardData] = useState(null)
  const [overallRiskScore, setOverallRiskScore] = useState(18)

  // Mock data for demonstration
  const mockRiskData = [
    { date: '2025-01-01', risk: 15 },
    { date: '2025-01-15', risk: 22 },
    { date: '2025-02-01', risk: 18 },
    { date: '2025-02-15', risk: 12 },
    { date: '2025-03-01', risk: 8 }
  ]

  const mockPlatformData = [
    { name: 'LinkedIn', value: 35, color: '#0077B5' },
    { name: 'Twitter', value: 25, color: '#1DA1F2' },
    { name: 'YouTube', value: 20, color: '#FF0000' },
    { name: 'TikTok', value: 20, color: '#000000' }
  ]

  // API Functions
  const testBackendConnection = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      const data = await response.json()
      console.log('Backend connection successful:', data)
      return true
    } catch (error) {
      console.error('Backend connection failed:', error)
      return false
    }
  }

  const performDemoScan = async (platform, username) => {
    try {
      const response = await fetch(`${API_BASE_URL}/scan/demo`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ platform, username })
      })
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const data = await response.json()
      return data
    } catch (error) {
      console.error('Demo scan failed:', error)
      throw error
    }
  }

  const getSupportedPlatforms = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/platforms/supported`)
      const data = await response.json()
      return data.platforms || []
    } catch (error) {
      console.error('Failed to get supported platforms:', error)
      return []
    }
  }

  useEffect(() => {
    // Test backend connection on load
    testBackendConnection()
    
    // Initialize with demo data
    setPlatforms([
      { id: 1, platform: 'linkedin', username: 'john-doe', enabled: true, last_scan: '2025-01-15T10:30:00Z' },
      { id: 2, platform: 'twitter', username: 'johndoe', enabled: true, last_scan: '2025-01-15T09:15:00Z' },
      { id: 3, platform: 'youtube', username: 'johndoechannel', enabled: false, last_scan: null }
    ])
    
    setAlerts([
      { id: 1, severity: 'medium', title: 'Controversial Tweet Detected', description: 'Recent tweet contains potentially controversial political content', acknowledged: false },
      { id: 2, severity: 'low', title: 'Privacy Setting Recommendation', description: 'Consider updating LinkedIn privacy settings', acknowledged: true }
    ])
  }, [])

  const handleAddPlatform = async () => {
    if (newPlatform.platform && newPlatform.username) {
      const newId = platforms.length + 1
      setPlatforms([...platforms, {
        id: newId,
        platform: newPlatform.platform,
        username: newPlatform.username,
        enabled: true,
        last_scan: null
      }])
      setNewPlatform({ platform: '', username: '' })
    }
  }

  const handleStartScan = async (platformId) => {
    setIsScanning(true)
    
    try {
      // Find the platform to scan
      const platform = platforms.find(p => p.id === platformId)
      if (!platform) {
        throw new Error('Platform not found')
      }
      
      // Perform real scan using backend API
      const scanResult = await performDemoScan(platform.platform, platform.username)
      
      if (scanResult.success) {
        // Update platform with scan results
        setPlatforms(platforms.map(p => 
          p.id === platformId 
            ? { 
                ...p, 
                last_scan: new Date().toISOString(),
                risk_score: scanResult.scan.risk_score 
              }
            : p
        ))
        
        // Update overall risk score
        const newRiskScore = scanResult.scan.risk_score
        setOverallRiskScore(newRiskScore)
        
        // Add new alerts if high risk
        if (newRiskScore > 25) {
          const newAlert = {
            id: alerts.length + 1,
            severity: newRiskScore > 50 ? 'high' : 'medium',
            title: `Risk Detected on ${platform.platform}`,
            description: `Scan completed with risk score: ${newRiskScore}/100`,
            acknowledged: false
          }
          setAlerts([newAlert, ...alerts])
        }
        
        console.log('Scan completed successfully:', scanResult)
      } else {
        throw new Error(scanResult.error || 'Scan failed')
      }
      
    } catch (error) {
      console.error('Scan failed:', error)
      // Add error alert
      const errorAlert = {
        id: alerts.length + 1,
        severity: 'high',
        title: 'Scan Failed',
        description: `Failed to scan ${platforms.find(p => p.id === platformId)?.platform}: ${error.message}`,
        acknowledged: false
      }
      setAlerts([errorAlert, ...alerts])
    } finally {
      setIsScanning(false)
    }
  }

  const getPlatformIcon = (platform) => {
    switch (platform) {
      case 'twitter': return <Twitter className="h-4 w-4" />
      case 'linkedin': return <Linkedin className="h-4 w-4" />
      case 'youtube': return <Youtube className="h-4 w-4" />
      case 'tiktok': return <Users className="h-4 w-4" />
      default: return <Eye className="h-4 w-4" />
    }
  }

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'high': return 'destructive'
      case 'medium': return 'default'
      case 'low': return 'secondary'
      default: return 'outline'
    }
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="notion-header">
        <div className="notion-container">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <img 
                src="/argus-logo.png" 
                alt="Argus Logo" 
                className="w-8 h-8 rounded-md object-cover"
              />
              <div>
                <h1 className="notion-title">
                  Argus Digital Sentinel
                </h1>
                <p className="notion-subtitle">Your Digital Footprint Guardian</p>
              </div>
            </div>
            <Badge 
              variant={overallRiskScore > 50 ? 'destructive' : overallRiskScore > 25 ? 'default' : 'secondary'}
              className="px-3 py-1"
            >
              Risk Score: {overallRiskScore}/100
            </Badge>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="notion-container py-8">
        <Tabs defaultValue="dashboard" className="space-y-6">
          <TabsList className="notion-tabs">
            <TabsTrigger value="dashboard" className="notion-tab">Dashboard</TabsTrigger>
            <TabsTrigger value="platforms" className="notion-tab">Platforms</TabsTrigger>
            <TabsTrigger value="alerts" className="notion-tab">Alerts</TabsTrigger>
            <TabsTrigger value="reports" className="notion-tab">Reports</TabsTrigger>
          </TabsList>

          {/* Dashboard Tab */}
          <TabsContent value="dashboard" className="space-y-6">
            {/* Overview Cards */}
            <div className="notion-grid-4">
              <Card className="notion-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Overall Risk Score</CardTitle>
                  <Shield className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className={`text-2xl font-bold ${overallRiskScore > 50 ? 'risk-score-high' : overallRiskScore > 25 ? 'risk-score-medium' : 'risk-score-low'}`}>
                    {overallRiskScore}/100
                  </div>
                  <p className="text-xs text-muted-foreground">
                    {overallRiskScore > 50 ? 'High risk detected' : overallRiskScore > 25 ? 'Medium risk detected' : 'Low risk detected'}
                  </p>
                </CardContent>
              </Card>

              <Card className="notion-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Active Platforms</CardTitle>
                  <Eye className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{platforms.filter(p => p.enabled).length}</div>
                  <p className="text-xs text-muted-foreground">Being monitored</p>
                </CardContent>
              </Card>

              <Card className="notion-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Unread Alerts</CardTitle>
                  <AlertTriangle className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold text-orange-600">
                    {alerts.filter(a => !a.acknowledged).length}
                  </div>
                  <p className="text-xs text-muted-foreground">Require attention</p>
                </CardContent>
              </Card>

              <Card className="notion-card">
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Last Scan</CardTitle>
                  <Scan className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">2h ago</div>
                  <p className="text-xs text-muted-foreground">All platforms</p>
                </CardContent>
              </Card>
            </div>

            {/* Charts */}
            <div className="notion-grid-2">
              <Card className="notion-card">
                <CardHeader>
                  <CardTitle>Risk Trend</CardTitle>
                  <CardDescription>Your digital footprint risk over time</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <LineChart data={mockRiskData}>
                      <CartesianGrid strokeDasharray="3 3" stroke="var(--border)" />
                      <XAxis dataKey="date" stroke="var(--muted-foreground)" />
                      <YAxis stroke="var(--muted-foreground)" />
                      <Tooltip 
                        contentStyle={{ 
                          backgroundColor: 'var(--card)', 
                          border: '1px solid var(--border)',
                          borderRadius: '8px'
                        }} 
                      />
                      <Line type="monotone" dataKey="risk" stroke="var(--primary)" strokeWidth={2} />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card className="notion-card">
                <CardHeader>
                  <CardTitle>Platform Risk Distribution</CardTitle>
                  <CardDescription>Risk breakdown by platform</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={300}>
                    <PieChart>
                      <Pie
                        data={mockPlatformData}
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        fill="#8884d8"
                        dataKey="value"
                        label={({ name, value }) => `${name}: ${value}%`}
                      >
                        {mockPlatformData.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={entry.color} />
                        ))}
                      </Pie>
                      <Tooltip />
                    </PieChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            {/* Recent Alerts */}
            <Card>
              <CardHeader>
                <CardTitle>Recent Alerts</CardTitle>
                <CardDescription>Latest risk notifications</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {alerts.slice(0, 3).map((alert) => (
                  <Alert key={alert.id} className={alert.severity === 'high' ? 'border-red-200' : ''}>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertTitle className="flex items-center justify-between">
                      {alert.title}
                      <Badge variant={getSeverityColor(alert.severity)}>{alert.severity}</Badge>
                    </AlertTitle>
                    <AlertDescription>{alert.description}</AlertDescription>
                  </Alert>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Platforms Tab */}
          <TabsContent value="platforms" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Add New Platform</CardTitle>
                <CardDescription>Configure a new social media platform for monitoring</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div>
                    <Label htmlFor="platform">Platform</Label>
                    <Select value={newPlatform.platform} onValueChange={(value) => setNewPlatform({...newPlatform, platform: value})}>
                      <SelectTrigger>
                        <SelectValue placeholder="Select platform" />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="twitter">Twitter</SelectItem>
                        <SelectItem value="linkedin">LinkedIn</SelectItem>
                        <SelectItem value="youtube">YouTube</SelectItem>
                        <SelectItem value="tiktok">TikTok</SelectItem>
                        <SelectItem value="reddit">Reddit</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                  <div>
                    <Label htmlFor="username">Username</Label>
                    <Input
                      id="username"
                      placeholder="Enter username"
                      value={newPlatform.username}
                      onChange={(e) => setNewPlatform({...newPlatform, username: e.target.value})}
                    />
                  </div>
                  <div className="flex items-end">
                    <Button onClick={handleAddPlatform} className="w-full">
                      <Plus className="h-4 w-4 mr-2" />
                      Add Platform
                    </Button>
                  </div>
                </div>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {platforms.map((platform) => (
                <Card key={platform.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        {getPlatformIcon(platform.platform)}
                        <span className="capitalize">{platform.platform}</span>
                      </div>
                      <Badge variant={platform.enabled ? 'default' : 'secondary'}>
                        {platform.enabled ? 'Active' : 'Disabled'}
                      </Badge>
                    </CardTitle>
                    <CardDescription>@{platform.username}</CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="text-sm text-muted-foreground">
                      Last scan: {platform.last_scan ? new Date(platform.last_scan).toLocaleDateString() : 'Never'}
                    </div>
                    <Button 
                      onClick={() => handleStartScan(platform.id)} 
                      disabled={isScanning}
                      className="w-full"
                    >
                      <Scan className="h-4 w-4 mr-2" />
                      {isScanning ? 'Scanning...' : 'Start Scan'}
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Alerts Tab */}
          <TabsContent value="alerts" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Risk Alerts</CardTitle>
                <CardDescription>Monitor and manage potential reputation risks</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {alerts.map((alert) => (
                  <Alert key={alert.id} className={`${alert.severity === 'high' ? 'border-red-200' : ''} ${alert.acknowledged ? 'opacity-60' : ''}`}>
                    <AlertTriangle className="h-4 w-4" />
                    <AlertTitle className="flex items-center justify-between">
                      {alert.title}
                      <div className="flex items-center space-x-2">
                        <Badge variant={getSeverityColor(alert.severity)}>{alert.severity}</Badge>
                        {alert.acknowledged && <CheckCircle className="h-4 w-4 text-green-600" />}
                      </div>
                    </AlertTitle>
                    <AlertDescription>{alert.description}</AlertDescription>
                  </Alert>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Reports Tab */}
          <TabsContent value="reports" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Digital Footprint Report</CardTitle>
                <CardDescription>Comprehensive analysis of your online presence</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="text-center p-8 border-2 border-dashed border-gray-300 rounded-lg">
                  <Shield className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Report Generation</h3>
                  <p className="text-muted-foreground mb-4">
                    Generate a comprehensive report of your digital footprint analysis
                  </p>
                  <Button>Generate Report</Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </main>

      {/* Footer */}
      <footer className="footer-section">
        <div className="notion-container">
          <div className="text-center">
            <p className="footer-text mb-4">
              <strong>Argus Digital Sentinel</strong> - Have you been pwnd? Preventing self-sabotage and career suicide from the get-go with MANUS AI
            </p>
            <p className="footer-text mb-4">
              "In the digital age, your online presence is your reputation. Let Argus be your guardian."
            </p>
            <p className="footer-text">
              Made with <Heart className="inline w-4 h-4 text-red-500" /> by{' '}
              <a 
                href="https://gabrielongzm.com" 
                target="_blank" 
                rel="noopener noreferrer"
                className="footer-link"
              >
                Gabriel Ong
              </a>
              . Source code{' '}
              <a 
                href="https://github.com/gongahkia/argus" 
                target="_blank" 
                rel="noopener noreferrer"
                className="footer-link"
              >
                here
              </a>
              .
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
