import { useState, useEffect } from 'react';
import { 
  Upload,
  FileText,
  Menu,
  X,
  BarChart3,
  MessageSquare,
  Clock,
  TrendingUp,
  CheckCircle,
  Loader2
} from 'lucide-react';
import { uploadDocument, getStats, getDocuments } from '../services/api';

interface ServiceSidebarProps {
  onSelectCategory: (category: string) => void;
}

interface Document {
  filename: string;
  uploaded_at?: string;
  chunks?: number;
  size?: number;
}

export function ServiceSidebar({ onSelectCategory }: ServiceSidebarProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [stats, setStats] = useState({
    total_documents: 0,
    collection_name: '',
    status: 'active'
  });
  const [isUploading, setIsUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState<string>('');
  const [isLoading, setIsLoading] = useState(true);

  // Fetch stats and documents on mount
  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const [statsData, docsData] = await Promise.all([
        getStats(),
        getDocuments()
      ]);
      
      setStats(statsData);
      setDocuments(docsData);
    } catch (error) {
      console.error('Error loading data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const files = event.target.files;
    if (!files || files.length === 0) return;

    setIsUploading(true);
    setUploadStatus('');

    try {
      for (const file of Array.from(files)) {
        setUploadStatus(`Uploading ${file.name}...`);
        const result = await uploadDocument(file);
        
        if (result) {
          setUploadStatus(`✓ ${file.name} uploaded successfully!`);
        }
      }
      
      // Reload data after successful uploads
      await loadData();
      
      // Clear status after 3 seconds
      setTimeout(() => setUploadStatus(''), 3000);
    } catch (error) {
      setUploadStatus('❌ Upload failed. Please try again.');
      console.error('Upload error:', error);
    } finally {
      setIsUploading(false);
      // Reset the input
      event.target.value = '';
    }
  };

  return (
    <>
      {/* Mobile menu button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="md:hidden fixed top-20 left-4 z-50 bg-blue-600 text-white p-2 rounded-lg shadow-lg"
      >
        {isOpen ? <X className="size-6" /> : <Menu className="size-6" />}
      </button>

      {/* Sidebar */}
      <div
        className={`${
          isOpen ? 'translate-x-0' : '-translate-x-full'
        } md:translate-x-0 fixed md:static inset-y-0 left-0 z-40 w-80 bg-white border-r border-gray-200 transition-transform duration-300 flex flex-col`}
      >
        {/* Upload Files Section */}
        <div className="p-4 border-b border-gray-200">
          <h2 className="text-blue-900 mb-3">Upload Documents</h2>
          
          <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-dashed border-gray-300 rounded-lg cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="flex flex-col items-center justify-center pt-5 pb-6">
              <Upload className="size-8 text-gray-400 mb-2" />
              <p className="text-sm text-gray-600">Click to upload files</p>
              <p className="text-xs text-gray-500">PDF, DOC, DOCX, TXT</p>
            </div>
            <input 
              type="file" 
              className="hidden" 
              multiple
              accept=".pdf,.doc,.docx,.txt"
              onChange={handleFileUpload}
            />
          </label>

          {/* Upload Status */}
          {uploadStatus && (
            <div className={`mt-3 p-2 rounded-lg text-xs ${
              uploadStatus.includes('✓') ? 'bg-green-50 text-green-700' : 
              uploadStatus.includes('❌') ? 'bg-red-50 text-red-700' : 
              'bg-blue-50 text-blue-700'
            }`}>
              {uploadStatus}
            </div>
          )}

          {isUploading && (
            <div className="mt-3 flex items-center gap-2 text-sm text-blue-600">
              <Loader2 className="size-4 animate-spin" />
              <span>Uploading...</span>
            </div>
          )}
        </div>

        {/* Stats Section */}
        <div className="p-4 border-b border-gray-200">
          <div className="flex items-center gap-2 mb-4">
            <BarChart3 className="size-5 text-blue-900" />
            <h2 className="text-blue-900">Statistics</h2>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="size-6 animate-spin text-blue-600" />
            </div>
          ) : (
            <div className="space-y-3">
              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white rounded-lg text-blue-600">
                    <FileText className="size-5" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-gray-600">Total Documents</p>
                    <p className="text-xl font-bold text-gray-900">{stats.total_documents}</p>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-white rounded-lg text-green-600">
                    <CheckCircle className="size-5" />
                  </div>
                  <div className="flex-1">
                    <p className="text-xs text-gray-600">Status</p>
                    <p className="text-sm font-semibold text-gray-900 capitalize">{stats.status}</p>
                  </div>
                </div>
              </div>

              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="text-sm font-semibold text-blue-900 mb-2">Collection</h3>
                <p className="text-xs text-blue-700 font-mono">{stats.collection_name || 'nepal_gov_docs'}</p>
              </div>
            </div>
          )}
        </div>

        {/* Uploaded Documents Section */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-blue-900">Uploaded Documents</h2>
            <span className="text-xs text-gray-500">{documents.length} files</span>
          </div>

          {isLoading ? (
            <div className="flex items-center justify-center py-8">
              <Loader2 className="size-6 animate-spin text-blue-600" />
            </div>
          ) : documents.length > 0 ? (
            <div className="space-y-2 max-h-96 overflow-y-auto">
              {documents.map((doc, index) => (
                <div key={index} className="flex items-start gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200 hover:border-blue-300 transition-colors">
                  <FileText className="size-4 text-blue-600 mt-0.5 flex-shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-medium text-gray-900 truncate">{doc.filename}</p>
                    {doc.chunks && (
                      <p className="text-xs text-gray-500 mt-1">{doc.chunks} chunks</p>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              <FileText className="size-8 mx-auto mb-2 text-gray-400" />
              <p className="text-sm">No documents uploaded yet</p>
              <p className="text-xs mt-1">Upload PDF, DOC, DOCX, or TXT files</p>
            </div>
          )}
        </div>

        {/* Emergency Info */}
        <div className="p-4 border-t border-gray-200 bg-gray-50">
          <div className="text-xs text-gray-600">
            <p>Emergency Hotlines:</p>
            <p className="mt-1">Police: 100</p>
            <p>Ambulance: 102</p>
            <p>Fire: 101</p>
          </div>
        </div>
      </div>

      {/* Mobile overlay */}
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-30"
          onClick={() => setIsOpen(false)}
        />
      )}
    </>
  );
}