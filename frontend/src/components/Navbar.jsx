import { Link, useNavigate } from 'react-router-dom'

export default function Navbar({ children }) {
  const navigate = useNavigate()

  function logout() {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <nav className="flex items-center justify-between px-10 h-[66px] bg-azul sticky top-0 z-50 shadow-[0_2px_20px_rgba(26,58,92,.35)]">
      <Link to="/" className="flex items-center">
        <img src="/logo.jpg" alt="MCC" className="h-[42px] rounded-md brightness-105" />
      </Link>
      <div className="flex items-center gap-1.5">
        {children}
        <NavLink to="/cumpleaneros" className="text-dorado bg-dorado/10 border border-dorado/25">
          🎂 Cumpleañeros
        </NavLink>
        <NavLink to="/consultas">📊 Historial</NavLink>
        <NavLink to="/reportes">📋 Reportes</NavLink>
        <button
          onClick={logout}
          className="text-red-300/90 border border-red-400/25 px-4 py-1.5 rounded-lg text-[0.87rem] font-medium hover:bg-red-500/15 transition-all"
        >
          ⎋ Salir
        </button>
      </div>
    </nav>
  )
}

function NavLink({ to, children, className = '' }) {
  return (
    <Link
      to={to}
      className={`text-white/80 text-[0.87rem] font-medium px-4 py-1.5 rounded-lg hover:text-white hover:bg-white/10 transition-all ${className}`}
    >
      {children}
    </Link>
  )
}
