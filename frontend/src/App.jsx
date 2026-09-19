import { useState, useEffect } from 'react';
import Categorias from './components/Categorias';
import Equipos from './components/Equipos';
import Personas from './components/Personas';
import Prestamos from './components/Prestamos';

function App() {
  const [seccionActiva, setSeccionActiva] = useState('personas');
  const [backendStatus, setBackendStatus] = useState('Verificando conexión...');
  const [isHealthy, setIsHealthy] = useState(false);

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error('Respuesta no satisfactoria');
        return res.json();
      })
      .then((data) => {
        setBackendStatus(`Conectado al backend: ${data.app} (v${data.version})`);
        setIsHealthy(true);
      })
      .catch(() => {
        setBackendStatus('No se pudo conectar al backend (¿está corriendo en el puerto 8000?)');
        setIsHealthy(false);
      });
  }, []);

  return (
    <div className="app-layout">
      <header className="app-header">
        <h1>Sistema de Gestión de Préstamos - Laboratorio</h1>
        <p className="subtitle">Módulo de Administración de Inventario</p>
        <div className="status-container">
          <span className={`status-badge ${isHealthy ? 'status-online' : 'status-offline'}`}>
            {backendStatus}
          </span>
        </div>
      </header>

      <nav className="nav-tabs">
        <button
          className={`tab-btn ${seccionActiva === 'personas' ? 'active' : ''}`}
          onClick={() => setSeccionActiva('personas')}
        >
          👤 Personas
        </button>
        <button
          className={`tab-btn ${seccionActiva === 'equipos' ? 'active' : ''}`}
          onClick={() => setSeccionActiva('equipos')}
        >
          📦 Equipos de Laboratorio
        </button>
        <button
          className={`tab-btn ${seccionActiva === 'categorias' ? 'active' : ''}`}
          onClick={() => setSeccionActiva('categorias')}
        >
          🏷️ Categorías
        </button>
        <button
          className={`tab-btn ${seccionActiva === 'prestamos' ? 'active' : ''}`}
          onClick={() => setSeccionActiva('prestamos')}
        >
          📋 Préstamos
        </button>
      </nav>

      <main className="app-main">
        {seccionActiva === 'personas' && <Personas />}
        {seccionActiva === 'equipos' && <Equipos />}
        {seccionActiva === 'categorias' && <Categorias />}
        {seccionActiva === 'prestamos' && <Prestamos />}
      </main>
    </div>
  );
}

export default App;
