import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api/client'

export default function Login() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    try {
      const { data } = await api.post('/api/login', { username, password })
      localStorage.setItem('token', data.access_token)
      navigate('/')
    } catch {
      setError('Usuario o clave incorrectos')
    }
  }

  return (
    <>
      <nav className="flex items-center justify-between px-10 h-[66px] bg-azul sticky top-0 z-50 shadow-[0_2px_20px_rgba(26,58,92,.35)]">
        <div className="flex items-center">
          <img src="/logo.jpg" alt="MCC" className="h-[42px] rounded-md brightness-105" />
        </div>
        <div className="flex items-center gap-1.5">
          <span className="text-white/80 text-[0.87rem] px-4 py-1.5">Inicio</span>
        </div>
      </nav>

      <main className="grid grid-cols-1 lg:grid-cols-[1fr_420px] min-h-[calc(100vh-66px)] bg-gradient-to-br from-[#0f2240] via-azul to-[#0a1a30]">
        {/* Left side */}
        <section className="hidden lg:flex flex-col justify-center px-[70px] py-[60px] text-white/90">
          <h1 className="font-serif text-[2.4rem] font-bold leading-tight mb-5 text-white">
            Un encuentro con Cristo que transforma la vida
          </h1>
          <p className="text-white/70 text-base leading-relaxed max-w-[480px]">
            El Movimiento de Cursillos de Cristiandad acompaña a las personas
            en su camino de fe, fortaleciendo la amistad y el compromiso cristiano
            en comunidad.
          </p>
          <img src="/amigo.jpg" alt="Amistad cristiana" className="mt-10 w-full max-w-[440px] rounded-2xl opacity-85 shadow-[0_20px_60px_rgba(0,0,0,.4)]" />
        </section>

        {/* Right side — login form */}
        <section className="flex items-center justify-center p-10 bg-white/[.04] border-l border-white/[.08] backdrop-blur-xl">
          <div className="w-full max-w-[360px]">
            <img src="/welcome.jpg" alt="Bienvenida" className="w-[90px] h-[90px] rounded-full object-cover border-[3px] border-dorado/50 mb-6 block" />
            <h2 className="font-serif text-[2rem] font-semibold text-white mb-2">Bienvenido</h2>
            <p className="text-white/50 text-[0.85rem] mb-1">Sistema de Gestión MCC</p>

            {error && (
              <div className="bg-red-500/10 border border-red-400/30 text-red-300 rounded-btn px-5 py-3 mt-4 text-[0.88rem] font-medium">
                ⚠️ {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="flex flex-col gap-4 mt-5">
              <div>
                <label className="block text-white/60 text-[0.82rem] font-medium uppercase tracking-wide mb-1.5">Usuario</label>
                <input
                  type="text" value={username} onChange={e => setUsername(e.target.value)}
                  placeholder="Ej: admin" required autoComplete="username"
                  className="w-full bg-white/[.08] border border-white/15 text-white rounded-lg px-4 py-3 text-[0.95rem] placeholder:text-white/30 focus:bg-white/[.12] focus:border-dorado focus:ring-2 focus:ring-dorado/20 outline-none transition"
                />
              </div>
              <div>
                <label className="block text-white/60 text-[0.82rem] font-medium uppercase tracking-wide mb-1.5">Contraseña</label>
                <input
                  type="password" value={password} onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••" required autoComplete="current-password"
                  className="w-full bg-white/[.08] border border-white/15 text-white rounded-lg px-4 py-3 text-[0.95rem] placeholder:text-white/30 focus:bg-white/[.12] focus:border-dorado focus:ring-2 focus:ring-dorado/20 outline-none transition"
                />
              </div>
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-dorado to-dorado-dark text-white font-semibold py-3.5 rounded-btn text-[0.97rem] shadow-[0_4px_20px_rgba(201,151,58,.35)] hover:shadow-[0_8px_28px_rgba(201,151,58,.45)] hover:-translate-y-0.5 active:translate-y-0 transition-all mt-1"
              >
                Ingresar al Sistema
              </button>
            </form>
          </div>
        </section>
      </main>
    </>
  )
}
