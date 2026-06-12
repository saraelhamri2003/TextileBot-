import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { Upload, Trash2, FileText, CheckCircle, RefreshCw, AlertCircle } from 'lucide-react';

interface Document {
  id: number;
  filename: string;
  file_type: string;
  file_size: number;
  upload_date: string;
  status: string;
}

interface DocumentManagerProps {
  onRefreshStats: () => void;
}

export const DocumentManager: React.FC<DocumentManagerProps> = ({ onRefreshStats }) => {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = async () => {
    try {
      const data = await api.get<Document[]>('/documents/');
      setDocuments(data);
    } catch (err: any) {
      setError(err.message || 'Impossible de charger les documents.');
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0) return;
    const file = e.target.files[0];
    
    setUploading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      await api.post('/documents/upload', formData);
      await fetchDocuments();
      onRefreshStats();
    } catch (err: any) {
      setError(err.message || "Erreur pendant l'upload.");
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Voulez-vous vraiment supprimer ce document réglementaire ?')) return;
    try {
      await api.delete(`/documents/${id}`);
      setDocuments(prev => prev.filter(doc => doc.id !== id));
      onRefreshStats();
    } catch (err: any) {
      setError(err.message || 'Impossible de supprimer le document.');
    }
  };

  const formatSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Documents Réglementaires</h1>
        <p className="mt-2 text-slate-500 dark:text-slate-400">
          Uploadez les directives, normes ou règlements textiles (PDF, DOCX, TXT) qui serviront de base de connaissances RAG.
        </p>
      </div>

      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-4 rounded-xl flex items-start space-x-3 text-red-600 dark:text-red-400">
          <AlertCircle className="h-5 w-5 mt-0.5" />
          <span>{error}</span>
        </div>
      )}

      {/* Upload Zone */}
      <div className="bg-white dark:bg-slate-800 border-2 border-dashed border-slate-300 dark:border-slate-700 rounded-2xl p-8 text-center flex flex-col items-center justify-center transition-all hover:border-indigo-500/50">
        <div className="p-4 bg-indigo-500/10 rounded-full text-indigo-600 dark:text-indigo-400 mb-4">
          <Upload className="h-8 w-8" />
        </div>
        <h3 className="text-lg font-semibold text-slate-950 dark:text-white">Glissez ou sélectionnez un fichier</h3>
        <p className="text-sm text-slate-500 dark:text-slate-400 mt-1 mb-4">Formats acceptés : PDF, DOCX, TXT jusqu'à 20 Mo</p>
        
        <label className={`relative cursor-pointer bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-6 rounded-lg transition-colors inline-flex items-center space-x-2 ${uploading ? 'opacity-50 pointer-events-none' : ''}`}>
          {uploading ? (
            <>
              <RefreshCw className="h-4 w-4 animate-spin" />
              <span>Indexation en cours...</span>
            </>
          ) : (
            <>
              <span>Choisir un fichier</span>
            </>
          )}
          <input type="file" accept=".pdf,.docx,.txt" className="hidden" onChange={handleFileUpload} disabled={uploading} />
        </label>
      </div>

      {/* Document List */}
      <div className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-2xl shadow-sm overflow-hidden">
        <div className="p-5 border-b border-slate-100 dark:border-slate-700">
          <h2 className="text-xl font-bold text-slate-900 dark:text-white">Bibliothèque Active ({documents.length})</h2>
        </div>
        
        {documents.length === 0 ? (
          <div className="p-12 text-center text-slate-500 dark:text-slate-400">
            <FileText className="h-12 w-12 mx-auto text-slate-300 dark:text-slate-600 mb-3" />
            <p>Aucun document réglementaire importé pour le moment.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-slate-200 dark:divide-slate-700">
              <thead className="bg-slate-50 dark:bg-slate-900/50 text-slate-500 dark:text-slate-400 uppercase text-xs font-semibold">
                <tr>
                  <th className="px-6 py-3 text-left">Nom</th>
                  <th className="px-6 py-3 text-left">Type</th>
                  <th className="px-6 py-3 text-left">Taille</th>
                  <th className="px-6 py-3 text-left">Date d'import</th>
                  <th className="px-6 py-3 text-left">Statut RAG</th>
                  <th className="px-6 py-3 text-center w-20">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-200 dark:divide-slate-700 text-sm text-slate-700 dark:text-slate-300">
                {documents.map(doc => (
                  <tr key={doc.id} className="hover:bg-slate-50/50 dark:hover:bg-slate-700/20">
                    <td className="px-6 py-4 font-medium text-slate-900 dark:text-white flex items-center space-x-3 truncate max-w-xs">
                      <FileText className="h-5 w-5 text-indigo-500 shrink-0" />
                      <span className="truncate">{doc.filename}</span>
                    </td>
                    <td className="px-6 py-4 uppercase text-xs font-mono">{doc.file_type}</td>
                    <td className="px-6 py-4">{formatSize(doc.file_size)}</td>
                    <td className="px-6 py-4">{new Date(doc.upload_date).toLocaleDateString('fr-FR')}</td>
                    <td className="px-6 py-4">
                      {doc.status === 'indexed' ? (
                        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                          <CheckCircle className="h-3.5 w-3.5" />
                          <span>Indexé</span>
                        </span>
                      ) : doc.status === 'processing' ? (
                        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-full text-xs font-medium bg-blue-500/10 text-blue-600 dark:text-blue-400">
                          <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                          <span>Indexation...</span>
                        </span>
                      ) : (
                        <span className="inline-flex items-center space-x-1.5 px-2.5 py-1.5 rounded-full text-xs font-medium bg-red-500/10 text-red-600 dark:text-red-400">
                          <AlertCircle className="h-3.5 w-3.5" />
                          <span>Échec</span>
                        </span>
                      )}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <button onClick={() => handleDelete(doc.id)} className="text-slate-400 hover:text-red-500 dark:hover:text-red-400 transition-colors p-1">
                        <Trash2 className="h-5 w-5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
};
