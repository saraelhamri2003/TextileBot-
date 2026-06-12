import React from 'react';
import { FileText, ShieldAlert, CheckCircle, MessageSquare } from 'lucide-react';

interface DashboardProps {
  stats: {
    docsCount: number;
    reportsCount: number;
    convsCount: number;
    compliantCount: number;
  };
  onNavigate: (page: string) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ stats, onNavigate }) => {
  return (
    <div className="space-y-8 animate-fade-in">
      <div>
        <h1 className="text-3xl font-bold tracking-tight text-slate-900 dark:text-white">Tableau de bord</h1>
        <p className="mt-2 text-slate-500 dark:text-slate-400">
          Suivez la conformité de vos produits textiles et gérez votre bibliothèque réglementaire.
        </p>
      </div>

      {/* Grid Stats */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Documents Card */}
        <div className="bg-white dark:bg-slate-800 overflow-hidden shadow rounded-xl p-5 border border-slate-100 dark:border-slate-700/50 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-blue-500/10 text-blue-600 dark:text-blue-400">
            <FileText className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400 truncate">Réglementations</p>
            <p className="text-2xl font-semibold text-slate-900 dark:text-white">{stats.docsCount}</p>
          </div>
        </div>

        {/* Discussions Card */}
        <div className="bg-white dark:bg-slate-800 overflow-hidden shadow rounded-xl p-5 border border-slate-100 dark:border-slate-700/50 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-purple-500/10 text-purple-600 dark:text-purple-400">
            <MessageSquare className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400 truncate">Conversations</p>
            <p className="text-2xl font-semibold text-slate-900 dark:text-white">{stats.convsCount}</p>
          </div>
        </div>

        {/* Analyses Card */}
        <div className="bg-white dark:bg-slate-800 overflow-hidden shadow rounded-xl p-5 border border-slate-100 dark:border-slate-700/50 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-amber-500/10 text-amber-600 dark:text-amber-400">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400 truncate">Analyses Produits</p>
            <p className="text-2xl font-semibold text-slate-900 dark:text-white">{stats.reportsCount}</p>
          </div>
        </div>

        {/* Conformes Card */}
        <div className="bg-white dark:bg-slate-800 overflow-hidden shadow rounded-xl p-5 border border-slate-100 dark:border-slate-700/50 flex items-center space-x-4">
          <div className="p-3 rounded-lg bg-emerald-500/10 text-emerald-600 dark:text-emerald-400">
            <CheckCircle className="h-6 w-6" />
          </div>
          <div>
            <p className="text-sm font-medium text-slate-500 dark:text-slate-400 truncate">Conformes</p>
            <p className="text-2xl font-semibold text-slate-900 dark:text-white">{stats.compliantCount}</p>
          </div>
        </div>
      </div>

      {/* Main Layout Cards */}
      <div className="grid grid-cols-1 gap-6 md:grid-cols-2">
        <div className="bg-gradient-to-br from-indigo-500 to-purple-600 rounded-2xl p-6 text-white shadow-lg flex flex-col justify-between h-56">
          <div>
            <h2 className="text-xl font-bold">Assistant IA Textile</h2>
            <p className="mt-2 text-indigo-100 text-sm">
              Posez des questions sur l'étiquetage, les exigences douanières, les dénominations réglementaires et obtenez des réponses basées uniquement sur vos documents.
            </p>
          </div>
          <button
            onClick={() => onNavigate('chat')}
            className="self-start mt-4 px-4 py-2 bg-white text-indigo-600 rounded-lg text-sm font-medium hover:bg-indigo-50 transition"
          >
            Lancer le Chat
          </button>
        </div>

        <div className="bg-white dark:bg-slate-800 border border-slate-100 dark:border-slate-700/50 rounded-2xl p-6 shadow-sm flex flex-col justify-between h-56">
          <div>
            <h2 className="text-xl font-bold text-slate-900 dark:text-white">Analyse de Conformité</h2>
            <p className="mt-2 text-slate-500 dark:text-slate-400 text-sm">
              Soumettez une fiche produit textile avec sa composition de fibres et son étiquetage pour recevoir un rapport de conformité PDF instantané.
            </p>
          </div>
          <button
            onClick={() => onNavigate('compliance')}
            className="self-start mt-4 px-4 py-2 bg-slate-900 dark:bg-white text-white dark:text-slate-900 rounded-lg text-sm font-medium hover:bg-slate-800 dark:hover:bg-slate-100 transition"
          >
            Vérifier un produit
          </button>
        </div>
      </div>
    </div>
  );
};
