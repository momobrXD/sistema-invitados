import { useState, useEffect, useMemo } from 'react'
import Navbar from '../components/Navbar'
import api from '../api/client'
import { filterBySearch } from '../api/search'

export default function Reportes() {
  const [data, setData] = useState([])
  const [texto, setTexto] = useState('')
  const [mes, setMes] = useState('')

  useEffect(() => {
    api.get('/api/asistencia/reportes').then(r => setData(r.data))
  }, [])

  const meses = useMemo(() => [...new Set(data.map(a => a.mes).filter(Boolean))], [data])

  const filtered = useMemo(() => {
    const bySearch = filterBySearch(texto, data, ['nombre', 'evento', 'cedula', 'tipo_evento'])
    if (!mes) return bySearch
    return bySearch.filter(a => a.mes.toLowerCase() === mes.toLowerCase())
  }, [data, texto, mes])

  return (
    <div className="bg-page min-h-screen">
      <Navbar>
        <button onClick={() => window.print()} className="text-white/80 border border-white/20 px-3.5 py-1.5 rounded-lg text-[0.82rem] font-medium hover:bg-white/10 transition-all no-print">
          🖨️ Imprimir
        </button>
      </Navbar>
      <main className="max-w-7xl mx-auto px-5 lg:px-10 mt-4">
        <header className="flex justify-between items-center pt-8 mb-6">
          <div>
            <h1 className="font-serif text-azul font-semibold text-2xl mb-1">Reporte de Asistencias</h1>
            <p className="text-[0.82rem] text-gray-500 font-medium">{data.length} registros totales</p>
          </div>
        </header>

        {/* Filters */}
        <div className="bg-white border border-gray-200 rounded-card p-5 mb-4 shadow-sm no-print animate-fade-up">
          <div className="flex gap-2.5 flex-wrap items-center">
            <input
              value={texto} onChange={e => setTexto(e.target.value)}
              placeholder="🔍 Filtrar por nombre, evento o cédula..."
              className="flex-1 min-w-[160px] border border-gray-300 rounded-lg px-3.5 py-2.5 text-[0.9rem] focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none"
            />
            <select value={mes} onChange={e => setMes(e.target.value)} className="border border-gray-300 rounded-lg px-3.5 py-2.5 text-[0.9rem] max-w-[180px] focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none">
              <option value="">Todos los meses</option>
              {meses.map(m => <option key={m} value={m}>{m}</option>)}
            </select>
          </div>
          {(texto || mes) && (
            <p className="text-[0.78rem] text-gray-500 mt-2">{filtered.length} registros mostrados</p>
          )}
        </div>

        {/* Table */}
        <div className="bg-white border border-gray-200 rounded-card overflow-hidden shadow-sm animate-fade-up">
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gradient-to-r from-slate-100 to-blue-50">
                  <th className="px-4 py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Fecha</th>
                  <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Evento</th>
                  <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Tipo</th>
                  <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Cédula</th>
                  <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Nombre</th>
                  <th className="py-3.5 text-center text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Mes</th>
                </tr>
              </thead>
              <tbody>
                {filtered.length > 0 ? filtered.map((a, i) => (
                  <tr key={i} className="border-b border-gray-100 hover:bg-blue-50/50 transition">
                    <td className="px-4 py-3 text-azul-claro font-semibold text-[0.85rem] whitespace-nowrap">{a.fecha}</td>
                    <td className="py-3 text-[0.88rem] font-medium text-gray-800">{a.evento}</td>
                    <td className="py-3">
                      <span className="inline-block px-2.5 py-0.5 rounded-full text-[0.72rem] font-bold tracking-wider uppercase bg-blue-50 text-blue-800 border border-blue-100">
                        {a.tipo_evento}
                      </span>
                    </td>
                    <td className="py-3 text-gray-500 text-[0.85rem]">{a.cedula}</td>
                    <td className="py-3 uppercase font-semibold text-[0.85rem]">{a.nombre}</td>
                    <td className="py-3 text-center">
                      <span className="px-3 py-1 bg-azul-hover text-azul-claro border border-gray-300 rounded-full text-[0.72rem] font-bold uppercase tracking-wider">
                        {a.mes}
                      </span>
                    </td>
                  </tr>
                )) : (
                  <tr>
                    <td colSpan={6} className="text-center py-12 text-gray-400 italic">
                      No hay registros de asistencia aún.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </div>
  )
}
