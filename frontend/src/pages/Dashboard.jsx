import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

const TIPO_COLORS = {
  RETIRO:   'bg-amber-100 text-amber-800',
  ESCUELA:  'bg-blue-100 text-blue-800',
  ULTREYA:  'bg-green-100 text-green-800',
  'REUNIÓN': 'bg-purple-100 text-purple-800',
  HORA:     'bg-orange-100 text-orange-800',
  OTRO:     'bg-slate-100 text-slate-600',
}

function tipoBadge(tipo) {
  const key = (tipo || 'OTRO').split(' ')[0]
  return TIPO_COLORS[key] || TIPO_COLORS.OTRO
}

export default function Dashboard() {
  const [eventos, setEventos] = useState([])
  const [flash, setFlash] = useState('')
  const [showCrear, setShowCrear] = useState(false)
  const [showNuevo, setShowNuevo] = useState(false)

  useEffect(() => {
    api.get('/api/eventos/abiertos').then(r => setEventos(r.data))
  }, [])

  async function crearEvento(e) {
    e.preventDefault()
    const fd = new FormData(e.target)
    await api.post('/api/eventos/crear', {
      nombre_evento: fd.get('nombre_evento'),
      tipo_evento: fd.get('tipo_evento'),
      fecha_evento: fd.get('fecha_evento'),
    })
    setShowCrear(false)
    setFlash('Evento creado correctamente')
    setTimeout(() => setFlash(''), 5000)
    const r = await api.get('/api/eventos/abiertos')
    setEventos(r.data)
  }

  async function agregarInvitado(e) {
    e.preventDefault()
    const fd = new FormData(e.target)
    const body = {}
    for (const [k, v] of fd.entries()) body[k] = v
    await api.post('/api/personas/', body)
    setShowNuevo(false)
    setFlash(`Invitado ${body.nombre} agregado exitosamente`)
    setTimeout(() => setFlash(''), 5000)
  }

  return (
    <div className="bg-page min-h-screen">
      <Navbar />
      <main className="max-w-7xl mx-auto px-5 lg:px-10 mt-4">
        {flash && (
          <div className="flex items-center justify-between bg-gradient-to-r from-amber-50 to-amber-100 border border-dorado-claro border-l-4 border-l-dorado rounded-btn px-5 py-3.5 mb-4 font-medium text-dorado-dark shadow-sm animate-fade-up">
            <span>✨ {flash}</span>
            <button onClick={() => setFlash('')} className="opacity-70 hover:opacity-100 text-lg">×</button>
          </div>
        )}

        <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6 pt-8 gap-4">
          <div>
            <h1 className="font-serif text-azul font-semibold text-2xl">Panel Principal</h1>
            <p className="text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide">Gestión de eventos y asistencia</p>
          </div>
          <div className="flex gap-2">
            <button onClick={() => setShowNuevo(true)} className="px-5 py-2.5 border-[1.5px] border-azul-claro text-azul-claro rounded-btn text-[0.88rem] font-semibold hover:bg-azul-hover hover:text-azul transition-all">
              👤 Nuevo Integrante
            </button>
            <button onClick={() => setShowCrear(true)} className="px-5 py-2.5 bg-gradient-to-br from-azul-med to-azul-claro text-white rounded-btn text-[0.9rem] font-semibold shadow-[0_3px_12px_rgba(30,79,128,.25)] hover:-translate-y-0.5 hover:shadow-[0_6px_20px_rgba(30,79,128,.35)] transition-all">
              📅 Crear Evento
            </button>
          </div>
        </header>

        {eventos.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {eventos.map(ev => (
              <div key={ev.nombre_evento} className="bg-white border border-gray-200 rounded-card p-7 shadow-sm hover:shadow-md transition-all animate-fade-up relative overflow-hidden">
                <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-azul-med via-azul-claro to-dorado" />
                <div className="border-b border-gray-200 pb-3 mb-3">
                  <span className={`inline-block px-2.5 py-0.5 rounded-full text-[0.7rem] font-bold tracking-wider uppercase mb-2 ${tipoBadge(ev.tipo_evento)}`}>
                    {ev.tipo_evento || 'OTRO'}
                  </span>
                  <h3 className="font-serif text-azul font-semibold text-[1.25rem] mb-1">{ev.nombre_evento}</h3>
                  <p className="text-[0.82rem] text-gray-500 font-medium">📅 {ev.fecha_evento}</p>
                </div>
                <div className="flex flex-col gap-2">
                  <Link to={`/tomar-lista/${encodeURIComponent(ev.nombre_evento)}`} className="block w-full text-center py-2.5 bg-gradient-to-br from-azul-med to-azul-claro text-white rounded-btn font-semibold text-[0.9rem] shadow-[0_3px_12px_rgba(30,79,128,.25)] hover:-translate-y-0.5 transition-all">
                    ✅ Tomar Asistencia
                  </Link>
                  <Link to={`/previa-cierre/${encodeURIComponent(ev.nombre_evento)}`} className="block w-full text-center py-2.5 border-[1.5px] border-red-500 text-red-500 rounded-btn font-semibold text-[0.88rem] hover:bg-red-50 transition-all">
                    🔒 Finalizar Evento
                  </Link>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white border border-gray-200 rounded-card p-16 text-center shadow-sm animate-fade-up">
            <div className="text-5xl opacity-25 mb-3">📅</div>
            <p className="font-serif text-slate-400 text-lg">Sin eventos abiertos</p>
            <p className="text-slate-400 text-[0.85rem] mb-4">Crea un evento para comenzar a registrar asistencia</p>
            <button onClick={() => setShowCrear(true)} className="px-8 py-2.5 bg-gradient-to-br from-azul-med to-azul-claro text-white rounded-btn font-semibold shadow-[0_3px_12px_rgba(30,79,128,.25)] hover:-translate-y-0.5 transition-all">
              📅 Crear Evento
            </button>
          </div>
        )}
      </main>

      {/* Modal Crear Evento */}
      {showCrear && (
        <Modal onClose={() => setShowCrear(false)}>
          <form onSubmit={crearEvento}>
            <h5 className="font-serif text-azul font-semibold text-[1.35rem] mb-0.5">📅 Nuevo Evento</h5>
            <p className="text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-4">Configura los datos del evento</p>
            <div className="space-y-3">
              <div>
                <label className="block text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-1">Nombre del Evento *</label>
                <input name="nombre_evento" required placeholder="Ej: Ultreya de Navidad" className="w-full border border-gray-300 rounded-lg px-3.5 py-2.5 text-[0.9rem] focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none" />
              </div>
              <div>
                <label className="block text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-1">Tipo de Evento *</label>
                <select name="tipo_evento" required className="w-full border border-gray-300 rounded-lg px-3.5 py-2.5 text-[0.9rem] focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none">
                  <option value="" disabled selected>Elige el tipo...</option>
                  <option value="RETIRO">RETIRO</option>
                  <option value="ESCUELA">ESCUELA</option>
                  <option value="ULTREYA">ULTREYA</option>
                  <option value="HORA APOSTÓLICA">HORA APOSTÓLICA</option>
                  <option value="REUNIÓN">REUNIÓN</option>
                  <option value="OTRO">OTRO</option>
                </select>
              </div>
              <div>
                <label className="block text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-1">Fecha *</label>
                <input name="fecha_evento" type="date" required className="w-full border border-gray-300 rounded-lg px-3.5 py-2.5 text-[0.9rem] focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none" />
              </div>
            </div>
            <button type="submit" className="w-full mt-5 py-3 bg-gradient-to-br from-verde to-[#1a5c3d] text-white rounded-btn font-semibold shadow-[0_3px_12px_rgba(42,125,85,.25)] hover:shadow-[0_6px_20px_rgba(42,125,85,.35)] transition-all">
              ✅ Publicar Evento
            </button>
          </form>
        </Modal>
      )}

      {/* Modal Nuevo Integrante */}
      {showNuevo && (
        <Modal onClose={() => setShowNuevo(false)} wide>
          <form onSubmit={agregarInvitado}>
            <h5 className="font-serif text-azul font-semibold text-[1.35rem] mb-0.5">👤 Nuevo Integrante</h5>
            <p className="text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-4">Agrega a la base de datos del movimiento</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <div className="md:col-span-2">
                <label className="block text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-1">Nombre Completo *</label>
                <input name="nombre" required placeholder="JUAN PÉREZ" className="w-full border border-gray-300 rounded-lg px-3.5 py-2.5 text-[0.9rem] uppercase focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none" />
              </div>
              <Input name="cedula" label="Cédula" placeholder="1234567890" />
              <Input name="estado" label="Estado" placeholder="Activo" />
              <div>
                <label className="block text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-1">Género</label>
                <select name="genero" className="w-full border border-gray-300 rounded-lg px-3.5 py-2.5 text-[0.9rem] focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none">
                  <option value="">Seleccione...</option>
                  <option value="MASCULINO">Masculino</option>
                  <option value="FEMENINO">Femenino</option>
                </select>
              </div>
              <Input name="celular" label="Celular" />
              <Input name="correo" label="Correo Electrónico" type="email" />
              <Input name="cumple" label="🎂 Cumpleaños" type="date" />
              <Input name="zona" label="Zona / Parroquia" />
              <Input name="equipo" label="Equipo Rector" />
              <div className="md:col-span-2">
                <label className="block text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-1">Talento / Servicio</label>
                <textarea name="talento" rows={2} className="w-full border border-gray-300 rounded-lg px-3.5 py-2.5 text-[0.9rem] focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none resize-y" />
              </div>
              <div className="md:col-span-2">
                <label className="block text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-1">Observaciones</label>
                <textarea name="observaciones" rows={2} className="w-full border border-gray-300 rounded-lg px-3.5 py-2.5 text-[0.9rem] focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none resize-y" />
              </div>
            </div>
            <div className="flex gap-2 mt-5 justify-end">
              <button type="button" onClick={() => setShowNuevo(false)} className="px-5 py-2.5 border border-azul-claro text-azul-claro rounded-btn font-semibold hover:bg-azul-hover transition-all">Cancelar</button>
              <button type="submit" className="px-8 py-2.5 bg-gradient-to-br from-azul-med to-azul-claro text-white rounded-btn font-semibold shadow-[0_3px_12px_rgba(30,79,128,.25)] transition-all">💾 Guardar</button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  )
}

function Input({ name, label, type = 'text', placeholder = '' }) {
  return (
    <div>
      <label className="block text-[0.82rem] text-gray-500 font-medium uppercase tracking-wide mb-1">{label}</label>
      <input name={name} type={type} placeholder={placeholder} className="w-full border border-gray-300 rounded-lg px-3.5 py-2.5 text-[0.9rem] focus:border-azul-claro focus:ring-2 focus:ring-azul-claro/10 outline-none" />
    </div>
  )
}

function Modal({ children, onClose, wide = false }) {
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm" onClick={onClose}>
      <div className={`bg-white rounded-card p-7 shadow-xl mx-4 max-h-[90vh] overflow-y-auto animate-fade-up ${wide ? 'w-full max-w-2xl' : 'w-full max-w-md'}`} onClick={e => e.stopPropagation()}>
        {children}
      </div>
    </div>
  )
}
