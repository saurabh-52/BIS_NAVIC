import Link from 'next/link';
import { getAllStandards } from '@/lib/db';

export default function StandardsPage() {
  const standards = getAllStandards() as any[];

  return (
    <div className="container mx-auto py-10 px-4">
      <div className="flex flex-col gap-8">
        <div className="flex items-center justify-between">
          <h1 className="text-4xl font-bold tracking-tight text-white">BIS Standards Library</h1>
          <div className="px-4 py-2 bg-indigo-500/20 text-indigo-300 rounded-full text-sm font-medium border border-indigo-500/30">
            {standards.length} Standards Found
          </div>
        </div>
        
        <div className="text-gray-400 max-w-3xl">
          <p>This is a complete list of all Indian Standards published by the AYUSH department. 
          Click on any standard to view its classification details and cross-references.</p>
        </div>

        <div className="bg-gray-900 border border-gray-800 rounded-2xl overflow-hidden shadow-xl">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-gray-950/50 border-b border-gray-800">
                  <th className="p-4 text-sm font-medium text-gray-400">IS Number</th>
                  <th className="p-4 text-sm font-medium text-gray-400">Title</th>
                  <th className="p-4 text-sm font-medium text-gray-400 hidden md:table-cell">Published On</th>
                  <th className="p-4 text-sm font-medium text-gray-400">Status</th>
                  <th className="p-4 text-sm font-medium text-gray-400 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-800">
                {standards.map((std) => (
                  <tr key={std.id} className="hover:bg-gray-800/50 transition-colors group">
                    <td className="p-4">
                      <span className="font-mono text-sm font-semibold text-indigo-400">{std.is_number}</span>
                    </td>
                    <td className="p-4 font-medium text-gray-200">
                      {std.title}
                    </td>
                    <td className="p-4 text-sm text-gray-500 hidden md:table-cell">
                      {std.published_on || 'N/A'}
                    </td>
                    <td className="p-4">
                      <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
                        {std.life_cycle_status || 'Unknown'}
                      </span>
                    </td>
                    <td className="p-4 text-right">
                      <Link 
                        href={`/standards/${std.id}`}
                        className="inline-flex items-center justify-center px-4 py-2 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-500 transition-all opacity-0 group-hover:opacity-100 focus:opacity-100"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
