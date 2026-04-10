import { useState, useEffect, useMemo } from 'react'
import { useParams, Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

const TAG_STYLES = {
  cedula:  'bg-red-50 text-red-600 border-red-600',
  cumple:  'bg-orange-50 text-orange-600 border-orange-600',
  celular: 'bg-yellow-50 text-yellow-600 border-yellow-600',
  correo:  'bg-green-50 text-green-600 border-green-600',
  zona:    'bg-blue-50 text-blue-600 border-blue-600',
}

export default function TomarLista() {
  const { nombreEvento } = useParams()
  const decoded = decodeURIComponent(nombreEvento)
  const [data, setData] = useState(null)
  const [search, setSearch] = useState('')
  const [selected, setSelected] = useState(new Set())
  const [fichaId, setFichaId] = useState(null)
  const [ficha, setFicha] = useState(null)
  const [historial, setHistorial] = useState([])

  async function load() {
    const r = await api.get(`/api/asistencia/lista/${encodeURIComponent(decoded)}`)
    setData(r.data)
  }

  useEffect(() => { load() }, [decoded])

  const filtered = useMemo(() => {
    if (!data) return []
    if (!search.trim()) return data.invitados
    const q = search.toLowerCase()
    return data.invitados.filter(i => i.nombre.toLowerCase().includes(q))
  }, [data, search])

  function toggleAll(checked) {
    if (checked) {
      setSelected(new Set(filtered.map(i => i.nro)))
    } else {
      setSelected(new Set())
    }
  }

  function toggle(id) {
    setSelected(prev => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  async function accionMasiva(accion) {
    if (selected.size === 0) return alert('Selecciona al menos una persona primero.')
    await api.post('/api/asistencia/masiva', {
      invitados_ids: [...selected],
      accion,
      evento_nombre: decoded,
      tipo_evento: data?.evento?.tipo_evento || 'Reunión',
    })
    setSelected(new Set())
    load()
  }

  async function openFicha(id) {
    setFichaId(id)
    const [p, h] = await Promise.all([
      api.get(`/api/personas/${id}`),
      api.get(`/api/asistencia/historial/${id}`),
    ])
    setFicha(p.data)
    setHistorial(h.data)
  }

  if (!data) return <div className="bg-page min-h-screen"><Navbar /><p className="text-center mt-20 text-gray-400">Cargando...</p></div>

  function missingTags(inv) {
    const tags = []
    if (!inv.cedula?.trim()) tags.push({ key: 'cedula', label: 'Sin cédula' })
    if (!inv.cumple?.trim()) tags.push({ key: 'cumple', label: 'Sin cumpleaños' })
    if (!inv.celular?.trim()) tags.push({ key: 'celular', label: 'Sin celular' })
    if (!inv.correo?.trim()) tags.push({ key: 'correo', label: 'Sin correo' })
    if (!inv.zona?.trim()) tags.push({ key: 'zona', label: 'Sin zona' })
    return tags
  }

  return (
    <div className="bg-page min-h-screen">
      <Navbar>
        <span className="bg-gradient-to-br from-azul-med to-azul-claro text-white rounded-xl px-5 py-2 text-[0.85rem] font-bold tracking-wider">
          <span className="inline-block w-2 h-2 bg-green-400 rounded-full mr-1.5 animate-pulse-dot" />
          EN VIVO
        </span>
        <Link to={`/previa-cierre/${encodeURIComponent(decoded)}`} className="text-red-400 border border-red-400/40 px-3.5 py-1.5 rounded-lg text-[0.82rem] font-semibold hover:bg-red-500/15 transition-all no-underline">
          🔒 Finalizar
        </Link>
      </Navbar>

      <main className="max-w-7xl mx-auto px-5 lg:px-10 mt-4">
        <header className="flex flex-col sm:flex-row justify-between items-start sm:items-end mb-3 pt-4 gap-2">
          <div>
            <span className="inline-block px-3 py-1 bg-azul-hover text-azul-claro border border-gray-300 rounded-full text-[0.72rem] font-bold uppercase tracking-wider mb-2">
              {data.evento.tipo_evento}
            </span>
            <h1 className="font-serif text-azul font-semibold text-2xl">{data.evento.nombre_evento}</h1>
          </div>
          <div className="text-right">
            <p className="text-[0.82rem] text-gray-500 font-medium">📅 {data.evento.fecha_evento}</p>
            <p className="text-[0.82rem] text-verde font-bold">✅ {data.total_registrados} registrados de {data.total_invitados}</p>
          </div>
        </header>

        {/* Search */}
        <div className="relative mb-3">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-base pointer-events-none">🔍</span>
          <input
            value={search} onChange={e => setSearch(e.target.value)}
            placeholder="Buscar por nombre..."
            className="w-full bg-white border-[1.5px] border-gray-200 rounded-xl py-3 pl-12 pr-5 text-base focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none transition"
          />
        </div>

        {/* Floating action bar */}
        <div className="sticky top-[78px] z-40 bg-white border border-gray-200 rounded-btn shadow-md flex justify-between items-center py-2.5 px-5 mb-3">
          <div className="flex items-center gap-3">
            <label className="flex items-center gap-2 cursor-pointer">
              <input type="checkbox" onChange={e => toggleAll(e.target.checked)} className="w-[18px] h-[18px] accent-azul-claro rounded" />
              <span className="text-[0.82rem] text-gray-500 font-medium">Seleccionar visibles</span>
            </label>
            <span className="px-3 py-1 bg-azul-hover text-azul-claro border border-gray-300 rounded-full text-[0.72rem] font-bold uppercase tracking-wider">
              {selected.size} seleccionados
            </span>
          </div>
          <div className="flex gap-2">
            <button onClick={() => accionMasiva('registrar')} className="px-4 py-2 bg-gradient-to-br from-verde to-[#1a5c3d] text-white rounded-lg text-[0.85rem] font-semibold transition-all hover:-translate-y-0.5">
              ✅ Marcar Presente
            </button>
            <button onClick={() => accionMasiva('quitar')} className="px-4 py-2 bg-gradient-to-br from-red-500 to-red-700 text-white rounded-lg text-[0.85rem] font-semibold transition-all hover:-translate-y-0.5">
              ❌ Quitar
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="bg-white border border-gray-200 rounded-card overflow-hidden shadow-sm animate-fade-up">
          <table className="w-full border-collapse">
            <thead>
              <tr className="bg-gradient-to-r from-slate-100 to-blue-50">
                <th className="px-4 py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500 w-[50px]" />
                <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Nombre</th>
                <th className="py-3.5 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Datos faltantes</th>
                <th className="py-3.5 text-center text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Estado</th>
                <th className="py-3.5 text-center text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Ficha</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map(inv => {
                const tags = missingTags(inv)
                const isComplete = tags.length === 0
                return (
                  <tr key={inv.nro} className={`border-b border-gray-100 hover:bg-blue-50/50 transition ${inv.presente ? 'bg-green-50/70' : ''}`}>
                    <td className="px-4 py-3">
                      <input
                        type="checkbox" checked={selected.has(inv.nro)} onChange={() => toggle(inv.nro)}
                        className="w-[18px] h-[18px] accent-azul-claro rounded cursor-pointer"
                      />
                    </td>
                    <td className="py-3 max-w-[260px]">
                      <div className="font-semibold text-[0.88rem] text-gray-800 uppercase">{inv.nombre}</div>
                      <small className="text-gray-400 text-[0.73rem]">{inv.estado}</small>
                    </td>
                    <td className="py-3 max-w-[260px]">
                      {isComplete ? (
                        <span className="inline-block px-2 py-0.5 rounded-md text-[0.7rem] font-semibold border bg-green-50 text-green-700 border-green-700">✓ Completo</span>
                      ) : (
                        tags.map(t => (
                          <span key={t.key} className={`inline-block px-2 py-0.5 rounded-md text-[0.7rem] font-semibold border mr-1 mb-0.5 ${TAG_STYLES[t.key]}`}>{t.label}</span>
                        ))
                      )}
                    </td>
                    <td className="py-3 text-center">
                      {inv.presente ? (
                        <span className="inline-block px-3 py-1 bg-verde-claro text-verde border border-verde/20 rounded-full text-[0.72rem] font-bold uppercase tracking-wider">✓ Presente</span>
                      ) : (
                        <span className="inline-block px-3 py-1 bg-gray-100 text-gray-500 border border-gray-200 rounded-full text-[0.72rem] font-bold uppercase tracking-wider">Ausente</span>
                      )}
                    </td>
                    <td className="py-3 text-center">
                      <button onClick={() => openFicha(inv.nro)} className="w-[34px] h-[34px] bg-gray-100 border border-gray-200 rounded-full inline-flex items-center justify-center hover:bg-azul-hover hover:border-azul-claro hover:scale-110 transition-all">
                        ℹ️
                      </button>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
          {filtered.length === 0 && search && (
            <p className="text-center py-10 text-gray-400 italic">No se encontraron resultados para tu búsqueda.</p>
          )}
        </div>
      </main>

      {/* Modal Ficha */}
      {fichaId && ficha && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={() => setFichaId(null)}>
          <div className="bg-white rounded-card p-7 w-full max-w-2xl mx-4 max-h-[90vh] overflow-y-auto shadow-xl animate-fade-up" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h5 className="font-serif text-azul font-semibold text-[1.2rem]">{ficha.nombre}</h5>
              <button onClick={() => setFichaId(null)} className="text-gray-400 hover:text-gray-600 text-xl">×</button>
            </div>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mb-4">
              {[
                ['Estado', ficha.estado], ['Género', ficha.genero], ['Cédula', ficha.cedula],
                ['Correo', ficha.correo], ['Celular', ficha.celular], ['Cumpleaños', ficha.cumple],
                ['Zona', ficha.zona], ['Equipo Rector', ficha.equipo],
              ].map(([label, val]) => (
                <div key={label} className="bg-slate-50 rounded-lg p-3">
                  <div className="text-[0.72rem] text-gray-500 uppercase tracking-wide font-medium">{label}</div>
                  <div className="text-[0.9rem] font-bold text-gray-800">{val || '—'}</div>
                </div>
              ))}
              <div className="col-span-2 md:col-span-3 bg-slate-50 rounded-lg p-3">
                <div className="text-[0.72rem] text-gray-500 uppercase tracking-wide font-medium">Talento / Servicio</div>
                <div className="text-[0.9rem] font-bold text-gray-800">{ficha.talento || '—'}</div>
              </div>
              <div className="col-span-2 md:col-span-3 bg-slate-50 rounded-lg p-3">
                <div className="text-[0.72rem] text-gray-500 uppercase tracking-wide font-medium">Observaciones</div>
                <div className="text-[0.9rem] font-bold text-gray-800">{ficha.observaciones || '—'}</div>
              </div>
            </div>
            <hr className="opacity-10 my-2" />
            <h6 className="text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-2">Historial reciente</h6>
            <div className="max-h-[180px] overflow-y-auto scroll-area">
              {historial.length > 0 ? historial.slice(0, 10).map((h, i) => (
                <div key={i} className="p-2 px-3 mb-1.5 bg-slate-50 rounded-lg border-l-[3px] border-l-azul-claro text-[0.83rem]">
                  <div className="font-semibold text-gray-800">{h.evento}</div>
                  <div className="text-gray-500">{h.fecha}</div>
                </div>
              )) : (
                <p className="text-gray-400 italic text-[0.85rem] p-2.5">Sin registros previos.</p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
