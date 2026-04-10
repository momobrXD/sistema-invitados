import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

export default function Consultas() {
  const [eventos, setEventos] = useState([])
  const [personas, setPersonas] = useState([])
  const [busqueda, setBusqueda] = useState('')

  useEffect(() => {
    Promise.all([
      api.get('/api/eventos/cerrados'),
      api.get('/api/personas/'),
    ]).then(([ev, per]) => {
      setEventos(ev.data)
      setPersonas(per.data)
    })
  }, [])

  const filtradas = busqueda.length >= 2
    ? personas.filter(p =>
        (p.nombre + ' ' + p.cedula).toLowerCase().includes(busqueda.toLowerCase())
      )
    : []

  return (
    <div className="bg-page min-h-screen">
      <Navbar />
      <main className="max-w-7xl mx-auto px-5 lg:px-10 mt-4">
        <header className="pt-8 mb-6">
          <h1 className="font-serif text-azul font-semibold text-2xl mb-1">Centro de Consultas</h1>
          <p className="text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide">Historial de eventos y personas del movimiento</p>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-[5fr_7fr] gap-4">
          {/* Eventos cerrados */}
          <div className="bg-white border border-gray-200 rounded-card p-7 shadow-sm h-fit animate-fade-up">
            <div className="flex items-center gap-3 mb-3">
              <span className="text-xl">📂</span>
              <div>
                <h2 className="font-serif text-azul font-semibold text-[1.2rem]">Eventos Concluidos</h2>
                <p className="text-[0.82rem] text-gray-500 font-medium">{eventos.length} evento{eventos.length !== 1 ? 's' : ''}</p>
              </div>
            </div>
            <div className="max-h-[360px] overflow-y-auto scroll-area">
              {eventos.length > 0 ? eventos.map(ev => (
                <Link key={ev.nombre_evento} to={`/detalle-evento/${encodeURIComponent(ev.nombre_evento)}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-azul-hover hover:translate-x-0.5 transition-all mb-1.5 no-underline text-gray-800 border border-transparent hover:border-gray-200">
                  <div className="flex flex-col gap-0.5">
                    <span className="font-semibold text-[0.92rem]">{ev.nombre_evento}</span>
                    <span className="text-[0.76rem] text-gray-500">{ev.fecha_evento} • {ev.tipo_evento}</span>
                  </div>
                  <span className="px-3 py-1 bg-azul-hover text-azul-claro border border-gray-300 rounded-full text-[0.72rem] font-bold uppercase tracking-wider shrink-0">Ver →</span>
                </Link>
              )) : (
                <p className="text-center py-8 text-gray-400 italic">No hay eventos cerrados aún.</p>
              )}
            </div>
          </div>

          {/* Historial por persona */}
          <div className="bg-white border border-gray-200 rounded-card p-7 shadow-sm animate-fade-up" style={{ animationDelay: '0.05s' }}>
            <div className="flex items-center gap-3 mb-3">
              <span className="text-xl">👤</span>
              <div>
                <h2 className="font-serif text-azul font-semibold text-[1.2rem]">Historial por Persona</h2>
                <p className="text-[0.82rem] text-gray-500 font-medium">{personas.length} integrantes en la base</p>
              </div>
            </div>
            <div className="relative mb-2">
              <span className="absolute left-3.5 top-1/2 -translate-y-1/2 text-[0.85rem] pointer-events-none">🔍</span>
              <input
                value={busqueda} onChange={e => setBusqueda(e.target.value)}
                placeholder="Nombre o cédula (mín. 2 caracteres)..."
                autoFocus
                className="w-full bg-gray-100 border border-gray-200 rounded-lg pl-10 pr-4 py-2.5 text-[0.9rem] focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none"
              />
            </div>
            {busqueda.length >= 2 && (
              <p className="text-[0.78rem] text-gray-500 mb-1">{filtradas.length} resultado{filtradas.length !== 1 ? 's' : ''}</p>
            )}
            <div className="max-h-[360px] overflow-y-auto scroll-area">
              {busqueda.length < 2 ? (
                <p className="text-center py-8 text-gray-400 italic">Ingresa al menos 2 caracteres para buscar...</p>
              ) : filtradas.length === 0 ? (
                <p className="text-center py-8 text-gray-400 italic">Sin resultados para tu búsqueda.</p>
              ) : (
                filtradas.map(p => (
                  <Link key={p.nro} to={`/historial/${p.nro}`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-azul-hover hover:translate-x-0.5 transition-all mb-1.5 no-underline text-gray-800 border border-transparent hover:border-gray-200">
                    <div className="flex flex-col gap-0.5">
                      <span className="font-semibold text-[0.92rem]">{p.nombre}</span>
                      <span className="text-[0.76rem] text-gray-500">Cédula: {p.cedula || '—'} • {p.zona || '—'}</span>
                    </div>
                    <span className="px-3 py-1 bg-verde-claro text-verde rounded-full text-[0.72rem] font-bold uppercase tracking-wider shrink-0">Ver ficha</span>
                  </Link>
                ))
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
