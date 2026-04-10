import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import Dashboard from './pages/Dashboard'
import TomarLista from './pages/TomarLista'
import Consultas from './pages/Consultas'
import Cumpleaneros from './pages/Cumpleaneros'
import Reportes from './pages/Reportes'
import DetalleEvento from './pages/DetalleEvento'
import HistorialPersonal from './pages/HistorialPersonal'
import PreviaCierre from './pages/PreviaCierre'

function PrivateRoute({ children }) {
  const token = localStorage.getItem('token')
  return token ? children : <Navigate to="/login" replace />
}

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<PrivateRoute><Dashboard /></PrivateRoute>} />
      <Route path="/tomar-lista/:nombreEvento" element={<PrivateRoute><TomarLista /></PrivateRoute>} />
      <Route path="/consultas" element={<PrivateRoute><Consultas /></PrivateRoute>} />
      <Route path="/cumpleaneros" element={<PrivateRoute><Cumpleaneros /></PrivateRoute>} />
      <Route path="/reportes" element={<PrivateRoute><Reportes /></PrivateRoute>} />
      <Route path="/detalle-evento/:nombreEvento" element={<PrivateRoute><DetalleEvento /></PrivateRoute>} />
      <Route path="/historial/:idInv" element={<PrivateRoute><HistorialPersonal /></PrivateRoute>} />
      <Route path="/previa-cierre/:nombreEvento" element={<PrivateRoute><PreviaCierre /></PrivateRoute>} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
