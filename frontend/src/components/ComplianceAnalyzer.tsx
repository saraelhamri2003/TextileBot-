import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { CheckCircle, AlertTriangle, XCircle, FileText, Download, Loader2, Sparkles } from 'lucide-react';

interface ComplianceReport {
  id: number;
  product_name: string;
  fiber_composition: string;
  intended_market: string;
  label_text?: string;
  analysis_result: string;
  status: string;
  created_at: string;
}

interface ComplianceAnalyzerProps {
  onRefreshStats: () => void;
}

export const ComplianceAnalyzer: React.FC<ComplianceAnalyzerProps> = ({ onRefreshStats }) => {
  const [reports, setReports] = useState<ComplianceReport[]>([]);
  const [checking, setChecking] = useState(false);
  
  // Form values
  const [productName, setProductName] = useState('');
  const [composition, setComposition] = useState('');
  const [market, setMarket] = useState('Union Européenne');
  const [labelText, setLabelText] = useState('');
  
  const [activeReport, setActiveReport] = useState<ComplianceReport | null>(null);

  const isConditional = (status: string) => status === 'conditional' || status === 'warning';

  const fetchReports = async () => {
    try {
      const data = await api.get<ComplianceReport[]>('/compliance/reports');
      setReports(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchReports();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!productName || !composition) return;
    
    setChecking(true);
    try {
      const report = await api.post<ComplianceReport>('/compliance/check', {
        product_name: productName,
        fiber_composition: composition,
        intended_market: market,
        label_text: labelText
      });
      
      setActiveReport(report);
      // Reset form
      setProductName('');
      setComposition('');
      setLabelText('');
      
      await fetchReports();
      onRefreshStats();
    } catch (err) {
      alert("Erreur lors de l'analyse : " + (err as Error).message);
    } finally {
      setChecking(false);
    }
  };

  const handleDownload = async (reportId: number, filename: string) => {
    try {
      const response = await fetch(`http://127.0.0.1:8000/api/v1/compliance/reports/${reportId}/download`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      
      if (!response.ok) throw new Error("Échec du téléchargement");
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Rapport_${filename.replace(/\s+/g, '_')}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      alert("Erreur lors du téléchargement : " + (err as Error).message);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 animate-fade-in">
      
      {/* Form Submission */}
      <div className="lg:col-span-1 space-y-6">
        <div className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm">
          <div className="flex items-center space-x-2 mb-6">
            <Sparkles className="h-6 w-6 text-indigo-500" />
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Vérification Produit</h2>
          </div>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Nom du produit textile</label>
              <input
                type="text" required
                value={productName}
                onChange={e => setProductName(e.target.value)}
                placeholder="Ex: T-Shirt Coton Bio, Veste Laine"
                className="mt-1 block w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Composition des Fibres</label>
              <input
                type="text" required
                value={composition}
                onChange={e => setComposition(e.target.value)}
                placeholder="Ex: 80% Coton, 20% Polyester"
                className="mt-1 block w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Marché Cible</label>
              <select
                value={market}
                onChange={e => setMarket(e.target.value)}
                className="mt-1 block w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="Union Européenne">Union Européenne (Règlement 1007/2011)</option>
                <option value="USA">USA (FTC Rules)</option>
                <option value="France">France (Décrets Spécifiques)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-slate-700 dark:text-slate-300">Texte Complet de l'Étiquette (Optionnel)</label>
              <textarea
                value={labelText}
                onChange={e => setLabelText(e.target.value)}
                rows={3}
                placeholder="Collez ici le texte présent sur votre étiquette pour vérification..."
                className="mt-1 block w-full px-3 py-2 bg-slate-50 dark:bg-slate-900 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            <button
              type="submit" disabled={checking}
              className="w-full flex justify-center py-2.5 px-4 border border-transparent rounded-lg shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
            >
              {checking ? (
                <>
                  <Loader2 className="h-5 w-5 animate-spin mr-2" />
                  <span>Analyse RAG en cours...</span>
                </>
              ) : (
                'Lancer l\'analyse'
              )}
            </button>
          </form>
        </div>
      </div>

      {/* Analysis Results Display */}
      <div className="lg:col-span-2 space-y-6">
        {activeReport ? (
          <div className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm space-y-6 animate-scale-up">
            <div className="flex justify-between items-start">
              <div>
                <h3 className="text-2xl font-bold text-slate-900 dark:text-white">{activeReport.product_name}</h3>
                <p className="text-sm text-slate-500 mt-1">
                  Marché : {activeReport.intended_market} | Composition : {activeReport.fiber_composition}
                </p>
              </div>
              
              <div className="flex items-center space-x-2">
                {activeReport.status === 'compliant' ? (
                  <span className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
                    <CheckCircle className="h-4 w-4" />
                    <span>Conforme</span>
                  </span>
                ) : isConditional(activeReport.status) ? (
                  <span className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-600 dark:text-amber-400">
                    <AlertTriangle className="h-4 w-4" />
                    <span>Conforme avec réserve</span>
                  </span>
                ) : (
                  <span className="inline-flex items-center space-x-1 px-3 py-1.5 rounded-full text-xs font-semibold bg-red-500/10 text-red-600 dark:text-red-400">
                    <XCircle className="h-4 w-4" />
                    <span>Non conforme</span>
                  </span>
                )}
                
                <button
                  onClick={() => handleDownload(activeReport.id, activeReport.product_name)}
                  className="p-1.5 border border-slate-200 dark:border-slate-700 rounded-lg text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-700 transition"
                  title="Télécharger le rapport PDF"
                >
                  <Download className="h-5 w-5" />
                </button>
              </div>
            </div>

            <div className="border-t border-slate-100 dark:border-slate-700 pt-4">
              <h4 className="font-semibold text-slate-900 dark:text-white mb-2">Résultat de l'analyse :</h4>
              <div className="text-slate-600 dark:text-slate-300 text-sm whitespace-pre-line leading-relaxed">
                {activeReport.analysis_result}
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-2xl p-12 text-center text-slate-500 dark:text-slate-400 flex flex-col items-center justify-center h-full min-h-[300px]">
            <FileText className="h-16 w-16 text-slate-200 dark:text-slate-700 mb-4 animate-pulse" />
            <h3 className="text-lg font-bold text-slate-800 dark:text-white">Aucun rapport actif</h3>
            <p className="max-w-md text-sm mt-2 text-slate-400">
              Remplissez le formulaire de conformité à gauche pour lancer une analyse RAG basée sur votre corpus réglementaire.
            </p>
          </div>
        )}

        {/* Previous Reports */}
        <div className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900 dark:text-white mb-4">Historique des analyses</h3>
          {reports.length === 0 ? (
            <p className="text-sm text-slate-400">Aucune analyse précédente enregistrée.</p>
          ) : (
            <div className="space-y-3 max-h-96 overflow-y-auto pr-2">
              {reports.map(rep => (
                <div
                  key={rep.id}
                  onClick={() => setActiveReport(rep)}
                  className={`p-4 border rounded-xl cursor-pointer flex items-center justify-between transition ${
                    activeReport?.id === rep.id
                      ? 'border-indigo-500 bg-indigo-50/20 dark:bg-indigo-950/20'
                      : 'border-slate-100 dark:border-slate-700 hover:bg-slate-50 dark:hover:bg-slate-700/30'
                  }`}
                >
                  <div>
                    <h4 className="font-semibold text-sm text-slate-900 dark:text-white">{rep.product_name}</h4>
                    <p className="text-xs text-slate-400 mt-1">
                      {new Date(rep.created_at).toLocaleDateString('fr-FR')} - {rep.fiber_composition}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2" onClick={e => e.stopPropagation()}>
                    {rep.status === 'compliant' ? (
                      <CheckCircle className="h-5 w-5 text-emerald-500" />
                    ) : isConditional(rep.status) ? (
                      <AlertTriangle className="h-5 w-5 text-amber-500" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-500" />
                    )}
                    <button
                      onClick={() => handleDownload(rep.id, rep.product_name)}
                      className="p-1 text-slate-400 hover:text-slate-600 dark:hover:text-slate-300"
                    >
                      <Download className="h-4 w-4" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
