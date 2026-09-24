import Link from 'next/link';
import { notFound } from 'next/navigation';
import { getStandardById } from '@/lib/db';

export default async function StandardDetailPage(props: { params: Promise<{ id: string }> }) {
  const params = await props.params;
  const standard = getStandardById(params.id) as any;
  
  if (!standard) {
    notFound();
  }

  return (
    <div className="container mx-auto py-10 px-4 max-w-5xl">
      <div className="mb-8 flex items-center gap-4">
        <Link 
          href="/standards" 
          className="text-gray-400 hover:text-white flex items-center gap-2 transition-colors text-sm font-medium bg-gray-900 px-4 py-2 rounded-lg border border-gray-800"
        >
          ← Back to Library
        </Link>
      </div>

      {/* Header Card */}
      <div className="bg-gradient-to-br from-indigo-950/50 to-slate-950 rounded-3xl p-8 border border-indigo-500/20 shadow-2xl mb-8 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/2"></div>
        <div className="relative z-10">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <span className="font-mono text-lg font-bold text-indigo-400 bg-indigo-500/10 px-3 py-1 rounded-md border border-indigo-500/20">
              {standard.is_number}
            </span>
            <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              {standard.life_cycle_status || 'Published'}
            </span>
            {standard.type_of_standard && (
              <span className="inline-flex items-center px-3 py-1 rounded-md text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/20">
                {standard.type_of_standard}
              </span>
            )}
          </div>
          
          <h1 className="text-3xl md:text-4xl font-bold text-white mb-6 leading-tight">
            {standard.title}
          </h1>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div className="space-y-3">
              <div className="flex gap-2 text-gray-400">
                <span className="w-32 flex-shrink-0">Department:</span>
                <span className="text-gray-200 font-medium">{standard.department_name || 'N/A'}</span>
              </div>
              <div className="flex gap-2 text-gray-400">
                <span className="w-32 flex-shrink-0">Committee:</span>
                <span className="text-gray-200 font-medium">{standard.technical_committee_name || 'N/A'}</span>
              </div>
              <div className="flex gap-2 text-gray-400">
                <span className="w-32 flex-shrink-0">Published:</span>
                <span className="text-gray-200 font-medium">{standard.published_on || 'N/A'}</span>
              </div>
            </div>
            
            <div className="space-y-3">
              <div className="flex gap-2 text-gray-400">
                <span className="w-32 flex-shrink-0">Revisions:</span>
                <span className="text-gray-200 font-medium">{standard.no_of_revisions}</span>
              </div>
              <div className="flex gap-2 text-gray-400">
                <span className="w-32 flex-shrink-0">Amendments:</span>
                <span className="text-gray-200 font-medium">{standard.no_of_amendments}</span>
              </div>
              <div className="flex gap-2 text-gray-400">
                <span className="w-32 flex-shrink-0">Language:</span>
                <span className="text-gray-200 font-medium">{standard.language || 'English'}</span>
              </div>
            </div>
          </div>
          
          {standard.source_url && (
            <div className="mt-8 pt-6 border-t border-gray-800/50">
              <a 
                href={standard.source_url} 
                target="_blank" 
                rel="noreferrer"
                className="inline-flex items-center text-sm text-indigo-400 hover:text-indigo-300 transition-colors"
              >
                View on Official BIS Portal ↗
              </a>
            </div>
          )}
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Classification Sidebar */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 shadow-lg">
            <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
              <span className="w-1 h-5 bg-indigo-500 rounded-full"></span>
              Classification
            </h2>
            
            <div className="space-y-5">
              <DetailRow label="Group" value={standard.group_name} />
              <DetailRow label="Sub-Group" value={standard.sub_group_name} />
              <DetailRow label="Sub-Sub-Group" value={standard.sub_sub_group_name} />
              <div className="h-px bg-gray-800 my-4"></div>
              <DetailRow label="Sector" value={standard.sector_name} />
              <DetailRow label="Sub-Sector" value={standard.sub_sector_name} />
              <div className="h-px bg-gray-800 my-4"></div>
              <DetailRow label="Certification" value={standard.certification} />
              <DetailRow label="Ministry" value={standard.relevant_ministry} />
              <DetailRow label="SDG Goals" value={standard.sustainable_development_goals} />
              <DetailRow label="Risk Level" value={standard.risk_level} />
            </div>
          </div>
        </div>

        {/* Main Content Area */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Cross References */}
          {standard.standards_referred && standard.standards_referred.length > 0 && (
            <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 shadow-lg">
              <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                <span className="w-1 h-5 bg-purple-500 rounded-full"></span>
                Cross References ({standard.standards_referred.length})
              </h2>
              
              <div className="space-y-4">
                {standard.standards_referred.map((ref: any, idx: number) => (
                  <div key={idx} className="p-4 rounded-xl bg-gray-800/50 border border-gray-700/50 hover:border-gray-600 transition-colors">
                    <div className="flex items-start gap-3">
                      <div className="mt-0.5">
                        <span className={`text-[10px] uppercase font-bold px-2 py-1 rounded ${ref.is_type === 1 ? 'bg-orange-500/20 text-orange-400' : 'bg-blue-500/20 text-blue-400'}`}>
                          {ref.is_type === 1 ? 'IND' : 'INTL'}
                        </span>
                      </div>
                      <div>
                        <div className="font-mono text-sm text-gray-200 font-semibold mb-1">{ref.referred_standard_number}</div>
                        <div className="text-sm text-gray-400 leading-snug">{ref.referred_standard_name}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Documents / Gazettes */}
          {standard.gazette_documents && standard.gazette_documents.length > 0 && (
            <div className="bg-gray-900 rounded-2xl border border-gray-800 p-6 shadow-lg">
              <h2 className="text-lg font-semibold text-white mb-6 flex items-center gap-2">
                <span className="w-1 h-5 bg-orange-500 rounded-full"></span>
                Gazette Notifications
              </h2>
              
              <div className="divide-y divide-gray-800">
                {standard.gazette_documents.map((gaz: any, idx: number) => (
                  <div key={idx} className="py-4 first:pt-0 last:pb-0 flex items-center justify-between">
                    <div>
                      <div className="text-sm font-medium text-gray-200">{gaz.so_number}</div>
                      {gaz.amendment_number && (
                        <div className="text-xs text-gray-500 mt-1">Amendment: {gaz.amendment_number}</div>
                      )}
                    </div>
                    {gaz.document && (
                      <div className="px-3 py-1.5 bg-gray-800 text-gray-300 text-xs font-medium rounded hover:bg-gray-700 transition-colors cursor-pointer">
                        View PDF
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
          
          {(!standard.standards_referred?.length && !standard.gazette_documents?.length) && (
            <div className="flex flex-col items-center justify-center p-12 bg-gray-900 rounded-2xl border border-gray-800 border-dashed">
              <div className="w-12 h-12 rounded-full bg-gray-800 flex items-center justify-center mb-4">
                <span className="text-gray-500 text-xl">📄</span>
              </div>
              <h3 className="text-gray-300 font-medium mb-1">No additional data found</h3>
              <p className="text-gray-500 text-sm text-center">This standard does not currently have any linked cross-references or gazette notifications in our database.</p>
            </div>
          )}

        </div>
      </div>
    </div>
  );
}

function DetailRow({ label, value }: { label: string, value: string }) {
  if (!value || value.trim() === '') return null;
  
  return (
    <div>
      <div className="text-xs text-gray-500 uppercase tracking-wider mb-1 font-medium">{label}</div>
      <div className="text-sm text-gray-200 leading-relaxed">{value}</div>
    </div>
  );
}
