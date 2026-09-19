import { useState, useEffect } from 'react';

function App() {
  const [backendStatus, setBackendStatus] = useState('Verificando conexión...');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error('Respuesta no satisfactoria');
        return res.json();
      })
      .then((data) => {
        setBackendStatus(`Conectado al backend: ${data.app} (v${data.version})`);
        setLoading(false);
      })
      .catch((err) => {
        setBackendStatus('No se pudo conectar al backend (¿está corriendo en el puerto 8000?)');
        setLoading(false);
      });
  }, []);

  return (
    <div>
      <h1>Sistema de Gestión de Laboratorio</h1>
      <p>Esqueleto de Frontend minimalista para pruebas de API</p>
      <div className="card">
        <h2>Estado de Backend</h2>
        <p className="status-badge">{backendStatus}</p>
      </div>
    </div>
  );
}

export default App;
