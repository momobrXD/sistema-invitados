import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

const FIELDS = [
  { key: 'nombre', label: 'Nombre Completo', span: 2, upper: true },
  { key: 'cedula', label: '🆔 Cédula' },
  { key: 'estado', label: 'Estado' },
  { key: 'correo', label: '📧 Correo Electrónico' },
  { key: 'celular', label: '📱 Celular' },
  { key: 'cumple', label: '🎂 Fecha de Cumpleaños' },
  { key: 'zona', label: '🗺️ Zona / Parroquia' },
  { key: 'equipo', label: '👥 Equipo Rector' },
  { key: 'genero', label: '⚥ Género', select: true },
  { key: 'talento', label: '🎵 Talento / Servicio', span: 3, textarea: true },
  { key: 'observaciones', label: '📋 Observaciones', span: 3, textarea: true },
]

const DEFAULTS = {
  cedula: 'No registrada', estado: 'No definido', correo: 'No registrado',
  celular: 'No registrado', cumple: 'No registrada', zona: 'No registrada',
  equipo: 'No registrado', genero: 'No definido', talento: 'No registrado',
  observaciones: 'Sin observaciones',
}

export default function HistorialPersonal() {
  const { idInv } = useParams()
  const [data, setData] = useState(null)
  const [editing, setEditing] = useState(false)
  const [form, setForm] = useState({})
  const [toast, setToast] = useState(null)

  useEffect(() => {
    api.get(`/api/personas/${idInv}/historial`).then(r => {
      setData(r.data)
      setForm(r.data.persona)
    })
  }, [idInv])

  function showToast(msg, error = false) {
    setToast({ msg, error })
    setTimeout(() => setToast(null), 3500)
  }

  async function save(e) {
    e.preventDefault()
    try {
      await api.put(`/api/personas/${idInv}`, form)
      setEditing(false)
      showToast('✅ Datos guardados correctamente')
      const r = await api.get(`/api/personas/${idInv}/historial`)
      setData(r.data)
      setForm(r.data.persona)
    } catch {
      showToast('❌ Error al guardar', true)
    }
  }

  if (!data) return <div className="bg-page min-h-screen"><Navbar /><p className="text-center mt-20 text-gray-400">Cargando...</p></div>

  const p = data.persona

  return (
    <div className="bg-page min-h-screen">
      <Navbar />
      <main className="max-w-[1000px] mx-auto px-5 lg:px-10 mt-4">
        {/* Profile card */}
        <div className="bg-white border border-gray-200 rounded-card p-7 shadow-sm mb-4 animate-fade-up">
          <div className="flex justify-between items-start mb-5">
            <div>
              <span className="px-3 py-1 bg-azul-hover text-azul-claro border border-gray-300 rounded-full text-[0.72rem] font-bold uppercase tracking-wider mb-2 inline-block">Ficha Personal</span>
              <h2 className="font-serif text-azul font-semibold text-[1.5rem]">👤 {p.nombre || 'Sin nombre'}</h2>
              <p className="text-[0.82rem] text-gray-500 font-medium mt-1">ID del Sistema: {p.nro}</p>
            </div>
            {!editing && (
              <button onClick={() => setEditing(true)} className="bg-gradient-to-r from-blue-500 to-blue-700 text-white rounded-xl px-5 py-2.5 text-[0.85rem] font-semibold hover:opacity-90 transition">
                ✏️ Editar Ficha
              </button>
            )}
          </div>

          <form onSubmit={save}>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {FIELDS.map(f => (
                <div key={f.key} className={f.span === 2 ? 'md:col-span-2' : f.span === 3 ? 'md:col-span-3' : ''}>
                  <div className="bg-slate-50 border border-gray-200 rounded-xl p-3">
                    <label className="block text-[0.72rem] text-gray-500 uppercase tracking-wider font-medium mb-1">{f.label}</label>
                    {editing ? (
                      f.select ? (
                        <select value={form[f.key] || ''} onChange={e => setForm({ ...form, [f.key]: e.target.value })} className="w-full border-2 border-blue-500 rounded-lg px-2.5 py-1.5 text-[0.9rem] bg-white focus:ring-2 focus:ring-blue-500/15 outline-none">
                          <option value="">Seleccione...</option>
                          <option value="MASCULINO">Masculino</option>
                          <option value="FEMENINO">Femenino</option>
                        </select>
                      ) : f.textarea ? (
                        <textarea value={form[f.key] || ''} onChange={e => setForm({ ...form, [f.key]: e.target.value })} rows={2} className="w-full border-2 border-blue-500 rounded-lg px-2.5 py-1.5 text-[0.9rem] bg-white focus:ring-2 focus:ring-blue-500/15 outline-none resize-y" />
                      ) : (
                        <input value={form[f.key] || ''} onChange={e => setForm({ ...form, [f.key]: e.target.value })} className={`w-full border-2 border-blue-500 rounded-lg px-2.5 py-1.5 text-[0.9rem] bg-white focus:ring-2 focus:ring-blue-500/15 outline-none ${f.upper ? 'uppercase' : ''}`} />
                      )
                    ) : (
                      <div className={`text-[0.95rem] font-semibold break-words ${p[f.key] ? 'text-gray-800' : 'text-gray-400 font-normal italic'}`}>
                        {p[f.key] || DEFAULTS[f.key] || '—'}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            {editing && (
              <div className="flex gap-2 mt-5">
                <button type="submit" className="bg-gradient-to-r from-emerald-500 to-emerald-600 text-white rounded-xl px-6 py-2.5 text-[0.85rem] font-semibold">💾 Guardar Cambios</button>
                <button type="button" onClick={() => { setEditing(false); setForm(p) }} className="bg-slate-100 text-gray-600 border border-gray-200 rounded-xl px-5 py-2.5 text-[0.85rem]">✕ Cancelar</button>
              </div>
            )}
          </form>
        </div>

        {/* History */}
        <div className="bg-white border border-gray-200 rounded-card p-7 shadow-sm mb-8 animate-fade-up" style={{ animationDelay: '0.05s' }}>
          <div className="flex items-center gap-2.5 mb-3">
            <span className="text-xl">📆</span>
            <h2 className="font-serif text-azul font-semibold text-[1.2rem]">Historial de Participaciones</h2>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="bg-gradient-to-r from-slate-100 to-blue-50">
                  <th className="py-3 px-4 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Fecha</th>
                  <th className="py-3 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Evento</th>
                  <th className="py-3 text-left text-[0.75rem] font-bold uppercase tracking-wider text-gray-500">Tipo de Evento</th>
                </tr>
              </thead>
              <tbody>
                {data.historial.length > 0 ? data.historial.map((h, i) => (
                  <tr key={i} className="border-b border-gray-100 hover:bg-blue-50/50 transition">
                    <td className="px-4 py-3 text-[0.88rem]">{h.fecha}</td>
                    <td className="py-3 font-bold text-[0.88rem]">{h.evento}</td>
                    <td className="py-3">
                      <span className="px-2.5 py-0.5 bg-blue-50 text-blue-800 border border-blue-100 rounded-full text-[0.72rem] font-bold uppercase tracking-wider">
                        {h.tipo_evento}
                      </span>
                    </td>
                  </tr>
                )) : (
                  <tr><td colSpan={3} className="text-center py-10 text-gray-400 italic">No se encontraron registros de participación.</td></tr>
                )}
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

      {/* Toast */}
      {toast && (
        <div className={`fixed bottom-8 right-8 px-6 py-3.5 rounded-xl text-white font-semibold text-[0.9rem] z-[9999] shadow-[0_8px_32px_rgba(0,0,0,.15)] ${toast.error ? 'bg-red-500' : 'bg-emerald-500'}`}>
          {toast.msg}
        </div>
      )}
    </div>
  )
}
