import { useState, useEffect } from 'react';
import Categorias from './components/Categorias';

function App() {
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

      <main className="app-main">
        <Categorias />
      </main>
    </div>
  );
}

export default App;
