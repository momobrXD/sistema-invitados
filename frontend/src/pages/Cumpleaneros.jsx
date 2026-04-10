import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Navbar from '../components/Navbar'
import api from '../api/client'

export default function Cumpleaneros() {
  const [data, setData] = useState(null)

  useEffect(() => {
    api.get('/api/personas/cumpleaneros/mes').then(r => setData(r.data))
  }, [])

  if (!data) return <div className="bg-page min-h-screen"><Navbar /><p className="text-center mt-20 text-gray-400">Cargando...</p></div>

  return (
    <div className="bg-page min-h-screen">
      <Navbar />
      <main className="max-w-7xl mx-auto px-5 lg:px-10 mt-4">
        <header className="flex flex-col sm:flex-row justify-between items-start sm:items-center pt-8 mb-6 gap-3">
          <div>
            <h1 className="font-serif text-azul font-semibold text-2xl mb-1">🎂 Cumpleañeros de {data.mes_nombre}</h1>
            <p className="text-[0.82rem] text-gray-500 font-medium">
              {data.total > 0
                ? `${data.total} persona${data.total !== 1 ? 's celebran' : ' celebra'} su cumpleaños este mes`
                : 'Ningún cumpleaños registrado este mes'}
            </p>
          </div>
          <Link to="/" className="px-5 py-2.5 border-[1.5px] border-azul-claro text-azul-claro rounded-btn text-[0.88rem] font-semibold hover:bg-azul-hover hover:text-azul transition-all no-underline">
            ← Volver al Panel
          </Link>
        </header>

        {data.cumpleaneros.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {data.cumpleaneros.map(p => (
              <div key={p.nro} className="bg-white border border-gray-200 border-l-4 border-l-dorado rounded-card p-6 shadow-sm hover:-translate-y-0.5 hover:shadow-[0_8px_28px_rgba(201,151,58,.18)] transition-all animate-fade-up">
                <div className="flex items-center gap-3 mb-3">
                  <div className="bg-gradient-to-br from-dorado to-dorado-dark text-white text-[1.4rem] font-extrabold w-[52px] h-[52px] rounded-xl flex items-center justify-center shrink-0 font-serif">
                    {p.dia_orden ?? '?'}
                  </div>
                  <div>
                    <h5 className="font-serif text-azul font-semibold text-[1.05rem] leading-tight">{p.nombre}</h5>
                    <span className="px-3 py-1 bg-azul-hover text-azul-claro border border-gray-300 rounded-full text-[0.72rem] font-bold uppercase tracking-wider">
                      {data.mes_nombre}
                    </span>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-3">
                  {p.cedula && (
                    <div>
                      <span className="text-[0.72rem] text-gray-500 uppercase tracking-wide font-medium">🆔 Cédula</span>
                      <p className="text-[0.88rem] mt-0.5">{p.cedula}</p>
                    </div>
                  )}
                  {p.zona && (
                    <div>
                      <span className="text-[0.72rem] text-gray-500 uppercase tracking-wide font-medium">🗺️ Zona</span>
                      <p className="text-[0.88rem] mt-0.5">{p.zona}</p>
                    </div>
                  )}
                </div>

                <div className="flex gap-2 flex-wrap">
                  {p.celular && (
                    <a
                      href={`https://wa.me/593${p.celular.replace(/^0/, '')}?text=¡Feliz%20Cumpleaños%20${encodeURIComponent(p.nombre)}!%20🎂%20Te%20desea%20el%20MCC.`}
                      target="_blank" rel="noopener noreferrer"
                      className="inline-flex items-center gap-1.5 bg-[#25D366] text-white rounded-lg px-3.5 py-1.5 text-[0.78rem] font-semibold hover:brightness-90 transition no-underline"
                    >
                      📱 WhatsApp
                    </a>
                  )}
                  {p.correo && (
                    <a
                      href={`mailto:${p.correo}?subject=¡Feliz Cumpleaños!&body=Estimado/a ${p.nombre}, el Movimiento MCC te desea un feliz cumpleaños 🎂`}
                      className="inline-flex items-center gap-1.5 bg-slate-100 text-azul rounded-lg px-3.5 py-1.5 text-[0.78rem] font-semibold hover:bg-slate-200 transition no-underline"
                    >
                      📧 Email
                    </a>
                  )}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="bg-white border border-gray-200 rounded-card p-16 text-center shadow-sm animate-fade-up">
            <div className="text-5xl opacity-25 mb-4">🎂</div>
            <p className="font-serif text-slate-400 text-xl">Sin cumpleañeros en {data.mes_nombre}</p>
            <p className="text-slate-400 text-[0.85rem]">Los cumpleaños se muestran cuando hay fechas registradas</p>
          </div>
        )}
      </main>
    </div>
  )
}
