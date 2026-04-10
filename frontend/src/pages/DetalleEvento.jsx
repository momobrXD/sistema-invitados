import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

export default function DetalleEvento() {
  const { nombreEvento } = useParams()
  const decoded = decodeURIComponent(nombreEvento)
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get(`/api/eventos/detalle/${encodeURIComponent(decoded)}`).then(r => setData(r.data))
  }, [decoded])

  if (!data) return <div className="bg-page min-h-screen"><Navbar /><p className="text-center mt-20 text-gray-400">Cargando...</p></div>

  return (
    <div className="bg-page min-h-screen">
      <Navbar />
      <main className="max-w-[1000px] mx-auto px-5 lg:px-10 mt-4">

        {data.cumpleaneros.length > 0 && (
          <div className="bg-blue-50 border-l-[5px] border-l-blue-500 rounded-lg p-4 shadow-sm mb-4 animate-fade-up">
            <h5 className="text-blue-700 font-semibold mb-2">🎂 Cumpleañeros de {data.mes_nombre} en este evento:</h5>
            <div className="flex flex-wrap gap-2">
              {data.cumpleaneros.map((c, i) => (
                <span key={i} className="bg-blue-600 text-white rounded-full px-3 py-1 text-[0.82rem] font-semibold">
                  {c.nombre} (Día {c.dia_cumple})
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="bg-white border border-gray-200 rounded-card p-7 shadow-sm mb-4 animate-fade-up">
          <div className="flex items-center gap-2.5 mb-3">
            <span className="text-xl">📅</span>
            <h2 className="font-serif text-azul font-semibold text-[1.3rem]">Evento: {decoded}</h2>
          </div>
          <p className="text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-3">
            Asistentes Registrados: <strong>{data.total}</strong>
          </p>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gradient-to-r from-slate-100 to-blue-50">
                  <th className="py-3.5 px-4 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Nombre</th>
                  <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Cédula</th>
                  <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Teléfono</th>
                  <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Estado</th>
                  <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Talento</th>
                  <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Observaciones</th>
                </tr>
              </thead>
              <tbody>
                {data.asistentes.map((a, i) => (
                  <tr key={i} className="border-b border-gray-100 hover:bg-blue-50/50 transition">
                    <td className="px-4 py-3 font-bold text-[0.88rem]">
                      {a.nombre} {a.es_cumple && '🎂'}
                    </td>
                    <td className="py-3 text-[0.85rem]">{a.cedula || '—'}</td>
                    <td className="py-3 text-[0.85rem]">{a.celular || '—'}</td>
                    <td className="py-3">
                      {a.estado ? (
                        <span className="bg-verde-claro text-verde rounded-md px-2 py-0.5 text-[0.78rem] font-bold">{a.estado}</span>
                      ) : '—'}
                    </td>
                    <td className="py-3 text-[0.83rem] text-gray-600">{a.talento || '—'}</td>
                    <td className="py-3 text-[0.83rem] text-gray-500 italic">{a.observaciones || '—'}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        <div className="text-center mb-8">
          <Link to="/consultas" className="px-5 py-2.5 border-[1.5px] border-azul-claro text-azul-claro rounded-btn text-[0.88rem] font-semibold hover:bg-azul-hover transition-all no-underline">
            ← Volver a Consultas
          </Link>
        </div>
      </main>
    </div>
  )
}
