import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Search, BookOpen, Database, Loader2, ExternalLink, AlertCircle, CheckCircle } from 'lucide-react';
import './App.css';

// Types
interface SearchResult {
  content: string;
  score: number;
  source_type: string;
  source_location?: string;
  metadata: Record<string, any>;
}

interface SearchResponse {
  query: string;
  results: SearchResult[];
  total_results: number;
  knowledge_base_id: string;
  timestamp: string;
}

interface Citation {
  content: string;
  source_location?: string;
  metadata: Record<string, any>;
}

interface SummarizeResponse {
  query: string;
  generated_response: string;
  citations: Citation[];
  knowledge_base_id: string;
  model_used: string;
  timestamp: string;
}

interface HealthResponse {
  status: string;
  timestamp: string;
  aws_region: string;
  knowledge_base_id: string;
  bedrock_available: boolean;
}

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState<'search' | 'summarize'>('search');
  const [query, setQuery] = useState('');
  const [maxResults, setMaxResults] = useState(5);
  const [loading, setLoading] = useState(false);
  const [searchResults, setSearchResults] = useState<SearchResponse | null>(null);
  const [summarizeResults, setSummarizeResults] = useState<SummarizeResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [health, setHealth] = useState<HealthResponse | null>(null);

  // Check health on component mount
  useEffect(() => {
    checkHealth();
  }, []);

  const checkHealth = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      setHealth(response.data);
    } catch (err) {
      console.error('Health check failed:', err);
      setError('Unable to connect to backend service');
    }
  };

  const handleSearch = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setSearchResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/search`, {
        query: query.trim(),
        max_results: maxResults
      });
      setSearchResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Search failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSummarize = async () => {
    if (!query.trim()) return;

    setLoading(true);
    setError(null);
    setSummarizeResults(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/summarize`, {
        query: query.trim(),
        max_results: maxResults
      });
      setSummarizeResults(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Summarization failed');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (activeTab === 'search') {
      handleSearch();
    } else {
      handleSummarize();
    }
  };

  const formatScore = (score: number) => {
    return (score * 100).toFixed(1) + '%';
  };

  const truncateContent = (content: string, maxLength: number = 300) => {
    if (content.length <= maxLength) return content;
    return content.substring(0, maxLength) + '...';
  };

  const getSourceDisplayName = (sourceLocation?: string) => {
    if (!sourceLocation) return 'Unknown Source';
    if (sourceLocation.startsWith('s3://')) {
      const parts = sourceLocation.split('/');
      return parts[parts.length - 1] || 'S3 Document';
    }
    return sourceLocation;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white shadow-lg border-b border-blue-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg mr-4 flex items-center justify-center shadow-lg">
                <Database className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">
                  Knowledge Base Explorer
                </h1>
                <p className="text-sm text-gray-600">
                  Search and summarize with Amazon Bedrock AI
                </p>
              </div>
            </div>
            
            {/* Health Status */}
            <div className="flex items-center space-x-4">
              {health && (
                <div className={`flex items-center space-x-2 px-3 py-2 rounded-lg ${
                  health.bedrock_available ? 'bg-green-50' : 'bg-red-50'
                }`}>
                  {health.bedrock_available ? (
                    <CheckCircle className="w-4 h-4 text-green-600" />
                  ) : (
                    <AlertCircle className="w-4 h-4 text-red-600" />
                  )}
                  <span className={`text-sm font-medium ${
                    health.bedrock_available ? 'text-green-700' : 'text-red-700'
                  }`}>
                    {health.bedrock_available ? 'Bedrock Connected' : 'Bedrock Unavailable'}
                  </span>
                </div>
              )}
              <div className="text-sm text-gray-500">
                Region: {health?.aws_region || 'Unknown'}
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="bg-white rounded-lg shadow-lg">
          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              <button
                onClick={() => setActiveTab('search')}
                className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors duration-200 ${
                  activeTab === 'search'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Search className="w-4 h-4" />
                <span>Search</span>
              </button>
              <button
                onClick={() => setActiveTab('summarize')}
                className={`py-4 px-2 border-b-2 font-medium text-sm flex items-center space-x-2 transition-colors duration-200 ${
                  activeTab === 'summarize'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <BookOpen className="w-4 h-4" />
                <span>Summarize</span>
              </button>
            </nav>
          </div>

          {/* Content */}
          <div className="p-6">
            {/* Query Form */}
            <form onSubmit={handleSubmit} className="mb-8">
              <div className="space-y-4">
                <div>
                  <label htmlFor="query" className="block text-sm font-medium text-gray-700 mb-2">
                    {activeTab === 'search' ? 'Search Query' : 'Question for AI Summary'}
                  </label>
                  <textarea
                    id="query"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={
                      activeTab === 'search'
                        ? 'Enter your search terms...'
                        : 'Ask a question about your knowledge base...'
                    }
                    className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    rows={3}
                    required
                  />
                </div>
                
                <div className="flex items-center space-x-4">
                  <div>
                    <label htmlFor="maxResults" className="block text-sm font-medium text-gray-700 mb-1">
                      Max Results
                    </label>
                    <select
                      id="maxResults"
                      value={maxResults}
                      onChange={(e) => setMaxResults(parseInt(e.target.value))}
                      className="px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                    >
                      <option value={3}>3</option>
                      <option value={5}>5</option>
                      <option value={10}>10</option>
                      <option value={15}>15</option>
                      <option value={20}>20</option>
                    </select>
                  </div>
                  
                  <div className="flex-1"></div>
                  
                  <button
                    type="submit"
                    disabled={loading || !query.trim()}
                    className={`px-6 py-2 rounded-lg font-medium text-white transition-all duration-200 transform hover:scale-105 flex items-center space-x-2 ${
                      loading || !query.trim()
                        ? 'bg-gray-400 cursor-not-allowed'
                        : 'bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg'
                    }`}
                  >
                    {loading ? (
                      <>
                        <Loader2 className="w-4 h-4 animate-spin" />
                        <span>Processing...</span>
                      </>
                    ) : (
                      <>
                        {activeTab === 'search' ? (
                          <Search className="w-4 h-4" />
                        ) : (
                          <BookOpen className="w-4 h-4" />
                        )}
                        <span>{activeTab === 'search' ? 'Search' : 'Summarize'}</span>
                      </>
                    )}
                  </button>
                </div>
              </div>
            </form>

            {/* Error Display */}
            {error && (
              <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                <div className="flex items-center">
                  <AlertCircle className="w-5 h-5 text-red-600 mr-2" />
                  <span className="text-red-800">{error}</span>
                </div>
              </div>
            )}

            {/* Search Results */}
            {activeTab === 'search' && searchResults && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-gray-900">Search Results</h2>
                  <span className="text-sm text-gray-500">
                    {searchResults.total_results} results found
                  </span>
                </div>
                
                {searchResults.results.map((result, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-blue-600">
                          Result {index + 1}
                        </span>
                        <span className="text-sm text-gray-500">
                          Relevance: {formatScore(result.score)}
                        </span>
                      </div>
                      {result.source_location && (
                        <div className="flex items-center space-x-1 text-sm text-gray-500">
                          <ExternalLink className="w-3 h-3" />
                          <span>{getSourceDisplayName(result.source_location)}</span>
                        </div>
                      )}
                    </div>
                    
                    <p className="text-gray-800 leading-relaxed mb-3">
                      {truncateContent(result.content)}
                    </p>
                    
                    {Object.keys(result.metadata).length > 0 && (
                      <div className="text-xs text-gray-500">
                        <strong>Metadata:</strong> {JSON.stringify(result.metadata)}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* Summarize Results */}
            {activeTab === 'summarize' && summarizeResults && (
              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <h2 className="text-xl font-bold text-gray-900">AI Summary</h2>
                  <span className="text-sm text-gray-500">
                    Model: {summarizeResults.model_used}
                  </span>
                </div>
                
                {/* Generated Response */}
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <h3 className="text-lg font-semibold text-blue-900 mb-3">Generated Response</h3>
                  <div className="text-gray-800 leading-relaxed whitespace-pre-wrap">
                    {summarizeResults.generated_response}
                  </div>
                </div>
                
                {/* Citations */}
                {summarizeResults.citations.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                      Sources ({summarizeResults.citations.length} citations)
                    </h3>
                    <div className="space-y-4">
                      {summarizeResults.citations.map((citation, index) => (
                        <div key={index} className="border border-gray-200 rounded-lg p-4 bg-gray-50">
                          <div className="flex items-center justify-between mb-2">
                            <span className="text-sm font-medium text-gray-700">
                              Citation {index + 1}
                            </span>
                            {citation.source_location && (
                              <div className="flex items-center space-x-1 text-sm text-gray-500">
                                <ExternalLink className="w-3 h-3" />
                                <span>{getSourceDisplayName(citation.source_location)}</span>
                              </div>
                            )}
                          </div>
                          <p className="text-gray-700 text-sm leading-relaxed">
                            {truncateContent(citation.content, 200)}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Empty State */}
            {!loading && !error && !searchResults && !summarizeResults && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">
                  {activeTab === 'search' ? '🔍' : '📚'}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  {activeTab === 'search' ? 'Search Your Knowledge Base' : 'Get AI-Powered Summaries'}
                </h3>
                <p className="text-gray-600 max-w-md mx-auto">
                  {activeTab === 'search'
                    ? 'Enter a search query to find relevant documents and information from your knowledge base.'
                    : 'Ask a question and get an AI-generated summary with citations from your knowledge base.'
                  }
                </p>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
}

export default App; 