import { useState, useEffect } from 'react'
import { useParams, Link, useNavigate } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

export default function PreviaCierre() {
  const { nombreEvento } = useParams()
  const decoded = decodeURIComponent(nombreEvento)
  const navigate = useNavigate()
  const [data, setData] = useState(null)
  const [obs, setObs] = useState('')

  useEffect(() => {
    api.get(`/api/eventos/previa_cierre/${encodeURIComponent(decoded)}`).then(r => setData(r.data))
  }, [decoded])

  async function cerrar() {
    if (!confirm('¿Estás seguro? Esta acción cerrará el evento definitivamente.')) return
    await api.post('/api/eventos/cerrar', {
      nombre_evento: decoded,
      observaciones: obs,
    })
    navigate('/')
  }

  if (!data) return <div className="bg-page min-h-screen"><Navbar /><p className="text-center mt-20 text-gray-400">Cargando...</p></div>

  const cumpleNames = data.cumpleaneros.map(c => c.nombre)

  return (
    <div className="bg-page min-h-screen">
      <Navbar>
        <Link to={`/tomar-lista/${encodeURIComponent(decoded)}`} className="text-white/80 text-[0.87rem] font-medium px-4 py-1.5 rounded-lg hover:text-white hover:bg-white/10 transition-all no-underline">
          ← Volver al Evento
        </Link>
      </Navbar>
      <main className="max-w-[900px] mx-auto px-5 lg:px-10 mt-4">
        <header className="pt-8 mb-6">
          <h1 className="font-serif text-azul font-semibold text-2xl mb-1">🔒 Resumen Final del Evento</h1>
          <p className="text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide">Revisa los datos antes de cerrar definitivamente</p>
        </header>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-3 mb-4">
          <div className="bg-slate-50 border border-gray-200 rounded-xl p-5 text-center">
            <div className="text-[2.5rem] font-extrabold text-blue-800 leading-none">{data.total_asistentes}</div>
            <div className="text-[0.8rem] text-gray-500 mt-1">Asistentes Registrados</div>
          </div>
          <div className="bg-slate-50 border border-gray-200 rounded-xl p-5 text-center">
            <div className="text-[2.5rem] font-extrabold text-amber-600 leading-none">{data.cumpleaneros.length}</div>
            <div className="text-[0.8rem] text-gray-500 mt-1">Cumpleañeros este mes</div>
          </div>
          <div className="bg-slate-50 border border-gray-200 rounded-xl p-5 text-center">
            <div className="text-[2.5rem] font-extrabold text-green-600 leading-none">{data.evento.tipo_evento || '—'}</div>
            <div className="text-[0.8rem] text-gray-500 mt-1">Tipo de Evento</div>
          </div>
        </div>

        {/* Cumpleañeros */}
        <div className="bg-white border border-gray-200 rounded-card p-7 shadow-sm mb-4 animate-fade-up">
          <div className="flex items-center gap-2.5 mb-3">
            <span className="text-xl">🎂</span>
            <h2 className="font-serif text-azul font-semibold text-[1.2rem]">Cumpleañeros de {data.mes_nombre} entre los Asistentes</h2>
          </div>
          {data.cumpleaneros.length > 0 ? (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {data.cumpleaneros.map((c, i) => (
                <div key={i} className="bg-gradient-to-r from-blue-50 to-blue-100 border-l-[5px] border-l-blue-500 rounded-xl px-4 py-3 flex justify-between items-center">
                  <div>
                    <div className="font-bold text-blue-800 text-[0.95rem]">🎉 {c.nombre}</div>
                    <small className="text-gray-500">Cumpleaños: {c.cumple}</small>
                  </div>
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-[0.72rem] font-bold uppercase tracking-wider">Día {c.dia}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-[0.82rem] text-gray-500 font-medium">No hay cumpleañeros de {data.mes_nombre} entre los asistentes de este evento.</p>
          )}
        </div>

        {/* Asistentes chips */}
        <div className="bg-white border border-gray-200 rounded-card p-7 shadow-sm mb-4 animate-fade-up" style={{ animationDelay: '0.05s' }}>
          <div className="flex items-center gap-2.5 mb-3">
            <span className="text-xl">✅</span>
            <h2 className="font-serif text-azul font-semibold text-[1.2rem]">Lista de Asistentes ({data.total_asistentes})</h2>
          </div>
          <div className="max-h-[220px] overflow-y-auto">
            {data.asistentes.map((a, i) => (
              <span key={i} className={`inline-block m-1 px-3 py-1.5 rounded-lg text-[0.8rem] border ${
                cumpleNames.includes(a.nombre)
                  ? 'bg-blue-100 border-blue-300 text-blue-800'
                  : 'bg-slate-100 border-gray-200 text-gray-700'
              }`}>
                {cumpleNames.includes(a.nombre) && '🎂 '}{a.nombre}
              </span>
            ))}
          </div>
        </div>

        {/* Observaciones + cierre */}
        <div className="bg-white border border-gray-200 rounded-card p-7 shadow-sm mb-8 animate-fade-up" style={{ animationDelay: '0.1s' }}>
          <div className="flex items-center gap-2.5 mb-3">
            <span className="text-xl">📝</span>
            <h2 className="font-serif text-azul font-semibold text-[1.2rem]">Observaciones del Evento</h2>
          </div>
          <p className="text-[0.82rem] text-gray-500 font-medium mb-3">Agrega notas importantes antes de cerrar (opcional).</p>
          <textarea
            value={obs} onChange={e => setObs(e.target.value)}
            rows={4} placeholder="Ej: Asistencia baja por lluvia. Se repartieron materiales. Próximo encuentro el..."
            className="w-full border-2 border-gray-200 rounded-xl p-3.5 text-[0.95rem] resize-y focus:border-blue-500 focus:ring-2 focus:ring-blue-500/10 outline-none transition mb-5"
          />
          <div className="flex justify-between items-center">
            <Link to={`/tomar-lista/${encodeURIComponent(decoded)}`} className="px-5 py-2.5 border-[1.5px] border-azul-claro text-azul-claro rounded-btn text-[0.88rem] font-semibold hover:bg-azul-hover transition-all no-underline">
              ← Volver y seguir tomando lista
            </Link>
            <button onClick={cerrar} className="bg-gradient-to-r from-red-500 to-red-600 text-white rounded-xl px-8 py-3.5 text-base font-bold hover:opacity-90 transition">
              🔒 Confirmar Cierre del Evento
            </button>
          </div>
        </div>
      </main>
    </div>
  )
}
