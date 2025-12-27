import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, 
  Zap,
  Fingerprint,
  Calendar,
  Layers,
  FileText,
  AlertCircle,
  Loader2,
  Eye,
  EyeOff,
  Trash2,
  RefreshCw,
  Clock,
  TrendingDown
} from 'lucide-react';
import { API_ENDPOINTS } from '../config/api';

const ProfileInsights = () => {
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [expandedClusters, setExpandedClusters] = useState(new Set());

  // Fetch profile data from API
  useEffect(() => {
    fetchProfile();
  }, []);

  const fetchProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Replace with actual user ID (from auth context)
      const userId = 'user_665390';
      const response = await fetch(API_ENDPOINTS.getUserProfile(userId));
      
      if (!response.ok) {
        throw new Error('Failed to fetch profile');
      }
      
      const data = await response.json();
      setProfile(data);
    } catch (err) {
      console.error('Error fetching profile:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const toggleCluster = (clusterId) => {
    setExpandedClusters(prev => {
      const newSet = new Set(prev);
      if (newSet.has(clusterId)) {
        newSet.delete(clusterId);
      } else {
        newSet.add(clusterId);
      }
      return newSet;
    });
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp * 1000).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric'
    });
  };

  const formatTimeAgo = (timestamp) => {
    const seconds = Math.floor(Date.now() / 1000 - timestamp);
    if (seconds < 60) return 'just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  };

  const getTierColor = (tier) => {
    switch (tier) {
      case 'PRIMARY':
        return {
          bg: 'bg-indigo-50',
          text: 'text-indigo-700',
          border: 'border-indigo-200',
          badge: 'bg-indigo-600'
        };
      case 'SECONDARY':
        return {
          bg: 'bg-blue-50',
          text: 'text-blue-700',
          border: 'border-blue-200',
          badge: 'bg-blue-500'
        };
      case 'NOISE':
        return {
          bg: 'bg-slate-50',
          text: 'text-slate-600',
          border: 'border-slate-200',
          badge: 'bg-slate-400'
        };
      default:
        return {
          bg: 'bg-slate-50',
          text: 'text-slate-600',
          border: 'border-slate-200',
          badge: 'bg-slate-400'
        };
    }
  };

  // Loading state
  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center space-y-4">
          <Loader2 className="w-12 h-12 text-indigo-600 animate-spin mx-auto" />
          <p className="text-slate-500 font-medium">Loading your behavior profile...</p>
        </div>
      </div>
    );
  }

  // Error state
  if (error) {
    return (
      <div className="bg-red-50 border-2 border-red-200 rounded-3xl p-8">
        <div className="flex items-start gap-4">
          <AlertCircle className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
          <div>
            <h3 className="text-lg font-bold text-red-900 mb-2">Failed to Load Profile</h3>
            <p className="text-red-700 mb-4">{error}</p>
            <button
              onClick={fetchProfile}
              className="flex items-center gap-2 px-4 py-2 bg-red-600 text-white rounded-xl font-bold hover:bg-red-700 transition-colors"
            >
              <RefreshCw size={16} />
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  // No profile found
  if (!profile) {
    return (
      <div className="bg-slate-50 border-2 border-slate-200 rounded-3xl p-12 text-center">
        <Fingerprint className="w-16 h-16 text-slate-300 mx-auto mb-4" />
        <h3 className="text-xl font-bold text-slate-700 mb-2">No Profile Found</h3>
        <p className="text-slate-500">Start interacting to build your behavioral profile.</p>
      </div>
    );
  }

  // Group clusters by tier
  const primaryClusters = profile.behavior_clusters?.filter(c => c.tier === 'PRIMARY') || [];
  const secondaryClusters = profile.behavior_clusters?.filter(c => c.tier === 'SECONDARY') || [];
  const noiseClusters = profile.behavior_clusters?.filter(c => c.tier === 'NOISE') || [];

  const ClusterCard = ({ cluster }) => {
    const colors = getTierColor(cluster.tier);
    const isExpanded = expandedClusters.has(cluster.cluster_id);
    
    return (
      <div 
        className={`${colors.bg} border-2 ${colors.border} rounded-2xl p-6 hover:shadow-lg transition-all cursor-pointer`}
        onClick={() => toggleCluster(cluster.cluster_id)}
      >
        <div className="flex items-start justify-between gap-4 mb-4">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className={`${colors.badge} text-white text-xs font-bold px-2.5 py-1 rounded-full uppercase tracking-wider`}>
                {cluster.tier}
              </span>
              <span className="text-xs font-mono text-slate-400">
                {cluster.cluster_size} observations
              </span>
            </div>
            <h4 className={`text-lg font-bold ${colors.text} leading-snug`}>
              {cluster.canonical_label}
            </h4>
            {cluster.cluster_name && (
              <p className="text-sm text-slate-500 mt-1 italic">
                {cluster.cluster_name}
              </p>
            )}
          </div>
          <div className="text-right flex-shrink-0">
            <div className="text-2xl font-black text-slate-900">
              {Math.round(cluster.cluster_strength * 100)}
            </div>
            <div className="text-xs font-bold text-slate-400 uppercase">strength</div>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4 mb-4">
          <div className="bg-white/50 rounded-xl p-3">
            <div className="flex items-center justify-between">
              <span className="text-xs font-bold text-slate-500">Confidence</span>
              <span className="text-sm font-black text-slate-700">
                {Math.round(cluster.confidence * 100)}%
              </span>
            </div>
            <div className="mt-2 bg-slate-200 h-1.5 rounded-full overflow-hidden">
              <div 
                className="bg-emerald-500 h-full rounded-full transition-all" 
                style={{ width: `${cluster.confidence * 100}%` }}
              />
            </div>
          </div>

          <div className="bg-white/50 rounded-xl p-3">
            <div className="flex items-center gap-2 text-xs">
              <Clock size={12} className="text-slate-400" />
              <span className="font-bold text-slate-500">Active</span>
            </div>
            <div className="text-sm font-bold text-slate-700 mt-1">
              {cluster.days_active ? `${Math.round(cluster.days_active)} days` : '< 1 day'}
            </div>
          </div>
        </div>

        <div className="flex items-center justify-between text-xs text-slate-500 mb-3">
          <div className="flex items-center gap-1">
            <Calendar size={12} />
            <span>First: {formatDate(cluster.first_seen)}</span>
          </div>
          <div className="flex items-center gap-1">
            <span>Last: {formatTimeAgo(cluster.last_seen)}</span>
          </div>
        </div>

        {isExpanded && cluster.wording_variations && cluster.wording_variations.length > 0 && (
          <div className="border-t-2 border-white/50 pt-4 mt-4 space-y-2">
            <p className="text-xs font-bold text-slate-600 uppercase tracking-wider mb-3">
              Wording Variations ({cluster.wording_variations.length})
            </p>
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {cluster.wording_variations.map((variation, idx) => (
                <div key={idx} className="bg-white/60 rounded-lg px-3 py-2 text-sm text-slate-700">
                  "{variation}"
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="mt-3 text-xs text-slate-400 text-center">
          Click to {isExpanded ? 'collapse' : 'expand'} variations
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-black text-slate-900 tracking-tight">Profile Insights</h1>
        <p className="text-slate-500 font-medium mt-1">
          Live analysis of your behavioral identity
        </p>
      </div>
          
      {/* Section 1: Hero Summary */}
      <div className="bg-white rounded-3xl border border-slate-200 p-8 shadow-sm relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-full bg-gradient-to-l from-indigo-50 to-transparent opacity-50"></div>
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-6 relative z-10">
          <div>
            <div className="flex items-center gap-3 mb-3">
              <span className="flex items-center gap-1 text-slate-400 text-xs font-mono">
                <Fingerprint size={14} /> {profile.user_id}
              </span>
              <button 
                onClick={fetchProfile}
                className="p-1 hover:bg-slate-100 rounded-lg transition-colors"
                title="Refresh profile"
              >
                <RefreshCw size={14} className="text-slate-400" />
              </button>
            </div>
            <h2 className="text-3xl font-bold text-slate-900 mb-2">
              {profile.archetype || 'Behavioral Profile'}
            </h2>
            <p className="text-slate-500 max-w-lg mb-4">
              Analyzing your interaction patterns across {profile.statistics?.total_behaviors_analyzed || 0} observed behaviors
              and {profile.statistics?.total_prompts_analyzed || 0} prompts.
            </p>
            <div className="inline-flex items-center gap-2 bg-indigo-600 text-white text-sm font-bold px-4 py-2 rounded-full shadow-md shadow-indigo-200">
              {profile.behavior_clusters?.length || 0} Behavior Clusters Detected
            </div>
          </div>
          <div className="w-full md:w-72 bg-slate-50 p-4 rounded-2xl border border-slate-100">
            <div className="flex justify-between mb-3">
              <span className="text-xs font-bold text-slate-600 uppercase tracking-wide">Analysis Time Span</span>
              <span className="text-xs font-bold text-indigo-600">
                {Math.round(profile.statistics?.analysis_time_span_days || 0)} days
              </span>
            </div>
            <div className="grid grid-cols-2 gap-3 text-center">
              <div className="bg-white rounded-xl p-3">
                <div className="text-2xl font-black text-indigo-600">
                  {profile.statistics?.clusters_formed || 0}
                </div>
                <div className="text-xs text-slate-500 font-bold">Clusters</div>
              </div>
              <div className="bg-white rounded-xl p-3">
                <div className="text-2xl font-black text-blue-600">
                  {profile.statistics?.total_behaviors_analyzed || 0}
                </div>
                <div className="text-xs text-slate-500 font-bold">Behaviors</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Section 2: Primary Behavior Clusters */}
      {primaryClusters.length > 0 && (
        <div className="bg-white rounded-3xl border-2 border-indigo-200 shadow-md">
          <div className="p-6 border-b border-slate-200 bg-indigo-50">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Zap size={20} className="text-indigo-600 fill-indigo-600" /> 
              Primary Behaviors
              <span className="ml-auto text-sm font-bold text-indigo-600">
                {primaryClusters.length} clusters
              </span>
            </h2>
          </div>
          
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            {primaryClusters.map((cluster) => (
              <ClusterCard key={cluster.cluster_id} cluster={cluster} />
            ))}
          </div>
        </div>
      )}

      {/* Section 3: Secondary Behavior Clusters */}
      {secondaryClusters.length > 0 && (
        <div className="bg-white rounded-3xl border-2 border-blue-200 shadow-md">
          <div className="p-6 border-b border-slate-200 bg-blue-50">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <Layers size={20} className="text-blue-600" /> 
              Secondary Behaviors
              <span className="ml-auto text-sm font-bold text-blue-600">
                {secondaryClusters.length} clusters
              </span>
            </h2>
          </div>
          
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            {secondaryClusters.map((cluster) => (
              <ClusterCard key={cluster.cluster_id} cluster={cluster} />
            ))}
          </div>
        </div>
      )}

      {/* Section 4: Evolution Timeline */}
      {profile.behavior_clusters && profile.behavior_clusters.length > 0 && (
        <div className="bg-white p-8 rounded-3xl border border-slate-200 shadow-sm">
          <h3 className="text-lg font-bold mb-8 flex items-center gap-2">
            <TrendingUp size={20} className="text-indigo-500" /> Behavior Evolution Timeline
          </h3>
          <div className="relative border-l-2 border-slate-100 ml-3 space-y-8">
            {profile.behavior_clusters
              .filter(c => c.tier !== 'NOISE')
              .sort((a, b) => b.last_seen - a.last_seen)
              .slice(0, 5)
              .map((cluster, idx) => (
                <div key={cluster.cluster_id} className="relative pl-8">
                  <div className={`absolute -left-[9px] top-1 w-4 h-4 rounded-full bg-white border-4 ${
                    idx === 0 ? 'border-indigo-600' : 'border-slate-300'
                  } shadow-sm`}></div>
                  <p className="text-sm font-bold text-slate-900">
                    {formatTimeAgo(cluster.last_seen)}
                  </p>
                  <p className="text-sm text-slate-500 mt-1">
                    Updated: "{cluster.canonical_label}" 
                    <span className="ml-2 text-xs font-bold text-slate-400">
                      ({cluster.cluster_size} observations)
                    </span>
                  </p>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Section 5: Noise/Outliers (Collapsible) */}
      {noiseClusters.length > 0 && (
        <details className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden">
          <summary className="p-6 cursor-pointer hover:bg-slate-50 transition-colors">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold text-slate-700 flex items-center gap-2">
                <TrendingDown size={20} className="text-slate-400" /> 
                Noise & Outliers
                <span className="text-sm font-normal text-slate-400">
                  ({noiseClusters.length} low-confidence clusters)
                </span>
              </h3>
            </div>
          </summary>
          <div className="p-6 pt-0 grid grid-cols-1 md:grid-cols-2 gap-4">
            {noiseClusters.map((cluster) => (
              <ClusterCard key={cluster.cluster_id} cluster={cluster} />
            ))}
          </div>
        </details>
      )}

      {/* Empty state */}
      {(!profile.behavior_clusters || profile.behavior_clusters.length === 0) && (
        <div className="bg-slate-50 border-2 border-slate-200 rounded-3xl p-12 text-center">
          <Fingerprint className="w-16 h-16 text-slate-300 mx-auto mb-4" />
          <h3 className="text-xl font-bold text-slate-700 mb-2">No Behaviors Detected</h3>
          <p className="text-slate-500">
            Continue interacting to build your behavioral profile.
          </p>
        </div>
      )}
    </div>
  );
};

export default ProfileInsights;