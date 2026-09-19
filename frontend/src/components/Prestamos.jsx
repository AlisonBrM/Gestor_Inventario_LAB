import { useState, useEffect } from 'react';

export default function Prestamos() {
  const [personas, setPersonas] = useState([]);
  const [equipos, setEquipos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [prestamos, setPrestamos] = useState([]);
  const [loadingDatos, setLoadingDatos] = useState(false);
  const [loadingPrestamos, setLoadingPrestamos] = useState(false);
  const [enviando, setEnviando] = useState(false);
  const [mensaje, setMensaje] = useState(null); // { tipo: 'success' | 'error', texto: string }
  const [prestamoCreado, setPrestamoCreado] = useState(null);

  // Formulario de creación
  const hoyStr = new Date().toISOString().split('T')[0];
  const [cedulaPersona, setCedulaPersona] = useState('');
  const [idEquipo, setIdEquipo] = useState('');
  const [fechaPrestamo, setFechaPrestamo] = useState(hoyStr);

  // Filtros de listado
  const [filtroCategoria, setFiltroCategoria] = useState('');
  const [filtroFechaDesde, setFiltroFechaDesde] = useState('');
  const [filtroFechaHasta, setFiltroFechaHasta] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('');

  // Cargar opciones para formulario y filtros
  const cargarOpciones = async () => {
    setLoadingDatos(true);
    try {
      const [resPersonas, resEquipos, resCategorias] = await Promise.all([
        fetch('/api/personas?solo_activas=true'),
        fetch('/api/equipos?solo_activos=true'),
        fetch('/api/categorias?solo_activas=true'),
      ]);

      if (resPersonas.ok) {
        const dataP = await resPersonas.json();
        setPersonas(dataP);
        if (dataP.length > 0 && !cedulaPersona) {
          setCedulaPersona(dataP[0].cedula);
        }
      }

      if (resEquipos.ok) {
        const dataE = await resEquipos.json();
        setEquipos(dataE);
        if (dataE.length > 0 && !idEquipo) {
          setIdEquipo(dataE[0].id);
        }
      }

      if (resCategorias.ok) {
        const dataC = await resCategorias.json();
        setCategorias(dataC);
      }
    } catch (err) {
      console.error('Error al cargar opciones:', err);
    } finally {
      setLoadingDatos(false);
    }
  };

  // Cargar lista de préstamos con filtros
  const cargarPrestamos = async () => {
    if (filtroFechaDesde && filtroFechaHasta && filtroFechaDesde > filtroFechaHasta) {
      setMensaje({
        tipo: 'error',
        texto: 'La fecha inicial ("Desde") no puede ser posterior a la fecha final ("Hasta").',
      });
      return;
    }

    setLoadingPrestamos(true);
    try {
      const params = new URLSearchParams();
      if (filtroCategoria) params.append('id_categoria', filtroCategoria);
      if (filtroFechaDesde) params.append('fecha_desde', filtroFechaDesde);
      if (filtroFechaHasta) params.append('fecha_hasta', filtroFechaHasta);
      if (filtroEstado) params.append('estado', filtroEstado);

      const qs = params.toString() ? `?${params.toString()}` : '';
      const res = await fetch(`/api/prestamos${qs}`);
      const data = await res.json().catch(() => []);

      if (!res.ok) {
        throw new Error(data.detail || 'Error al cargar los préstamos.');
      }

      setPrestamos(data);
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message || 'Error de conexión al obtener préstamos.' });
    } finally {
      setLoadingPrestamos(false);
    }
  };

  useEffect(() => {
    cargarOpciones();
  }, []);

  useEffect(() => {
    cargarPrestamos();
  }, [filtroCategoria, filtroFechaDesde, filtroFechaHasta, filtroEstado]);

  const limpiarFiltros = () => {
    setFiltroCategoria('');
    setFiltroFechaDesde('');
    setFiltroFechaHasta('');
    setFiltroEstado('');
  };

  const handleCrearPrestamo = async (e) => {
    e.preventDefault();
    setMensaje(null);
    setPrestamoCreado(null);

    if (!cedulaPersona.trim()) {
      setMensaje({ tipo: 'error', texto: 'Debes seleccionar o ingresar la cédula del solicitante.' });
      return;
    }
    if (!idEquipo) {
      setMensaje({ tipo: 'error', texto: 'Debes seleccionar un equipo.' });
      return;
    }

    const payload = {
      cedula_persona: cedulaPersona.trim(),
      id_equipo: Number(idEquipo),
      fecha_prestamo: fechaPrestamo || hoyStr,
    };

    setEnviando(true);
    try {
      const res = await fetch('/api/prestamos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json().catch(() => ({}));

      if (!res.ok) {
        const errorMsg = data.detail || 'Ocurrió un error al registrar el préstamo.';
        setMensaje({ tipo: 'error', texto: errorMsg });
        return;
      }

      setPrestamoCreado(data);
      setMensaje({
        tipo: 'success',
        texto: `¡Préstamo #${data.id} creado con éxito! Fecha esperada de devolución: ${data.fecha_devolucion_esperada}`,
      });
      // Recargar opciones y listado de préstamos
      cargarOpciones();
      cargarPrestamos();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message || 'Error de conexión con el servidor.' });
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div className="modulo-prestamos">
      {/* Alertas de retroalimentación */}
      {mensaje && (
        <div className={`alert ${mensaje.tipo === 'success' ? 'alert-success' : 'alert-error'}`}>
          <span>{mensaje.texto}</span>
          <button className="alert-close" onClick={() => setMensaje(null)}>✕</button>
        </div>
      )}

      {/* Formulario de registro de préstamo */}
      <div className="card">
        <h2>📋 Registrar Nuevo Préstamo</h2>
        <p className="subtitle" style={{ fontSize: '0.9rem', marginBottom: '1rem' }}>
          Asigna un equipo del laboratorio a un solicitante. El sistema validará automáticamente:
          <br />• <strong>Regla 1:</strong> Si el solicitante tiene un préstamo vencido sin devolver, será rechazado.
          <br />• <strong>Regla 2:</strong> Si el equipo está marcado en mantenimiento, será rechazado.
        </p>

        <form onSubmit={handleCrearPrestamo}>
          <div className="form-grid">
            {/* Solicitante */}
            <div className="form-group">
              <label htmlFor="select-persona">Solicitante (Persona Activa):</label>
              <select
                id="select-persona"
                value={cedulaPersona}
                onChange={(e) => setCedulaPersona(e.target.value)}
                disabled={enviando || loadingDatos}
              >
                <option value="">-- Selecciona una persona --</option>
                {personas.map((p) => (
                  <option key={p.cedula} value={p.cedula}>
                    {p.nombre_completo} (C.C. {p.cedula}) - {p.tipo_persona}
                  </option>
                ))}
              </select>
            </div>

            {/* O ingreso manual de cédula */}
            <div className="form-group">
              <label htmlFor="input-cedula">O ingresa Cédula directamente:</label>
              <input
                id="input-cedula"
                type="text"
                placeholder="Ej. 1001234567"
                value={cedulaPersona}
                onChange={(e) => setCedulaPersona(e.target.value)}
                disabled={enviando}
              />
            </div>

            {/* Equipo */}
            <div className="form-group full-width">
              <label htmlFor="select-equipo">Equipo del Laboratorio:</label>
              <select
                id="select-equipo"
                value={idEquipo}
                onChange={(e) => setIdEquipo(e.target.value)}
                disabled={enviando || loadingDatos}
              >
                <option value="">-- Selecciona un equipo --</option>
                {equipos.map((eq) => (
                  <option key={eq.id} value={eq.id}>
                    [ID: {eq.id}] {eq.nombre} ({eq.secuencial}) 
                    {eq.mantenimiento ? ' ⚠️ [EN MANTENIMIENTO]' : ' ✅ [Operativo]'}
                  </option>
                ))}
              </select>
            </div>

            {/* Fecha de Préstamo */}
            <div className="form-group">
              <label htmlFor="input-fecha">Fecha de Inicio del Préstamo:</label>
              <input
                id="input-fecha"
                type="date"
                value={fechaPrestamo}
                max={hoyStr}
                onChange={(e) => setFechaPrestamo(e.target.value)}
                disabled={enviando}
              />
            </div>

            <div className="form-group" style={{ display: 'flex', justifyContent: 'flex-end', alignItems: 'flex-end' }}>
              <button
                type="submit"
                className="btn-primary"
                disabled={enviando}
                style={{ width: '100%', padding: '0.65rem 1.25rem' }}
              >
                {enviando ? 'Validando y Registrando...' : '+ Registrar Préstamo'}
              </button>
            </div>
          </div>
        </form>
      </div>

      {/* Detalle del préstamo recién creado */}
      {prestamoCreado && (
        <div className="card edit-card" style={{ borderColor: '#16a34a', backgroundColor: '#f0fdf4' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <h3 style={{ margin: 0, color: '#15803d' }}>
              ✅ Préstamo #{prestamoCreado.id} Registrado Exitosamente
            </h3>
            <span className="badge badge-active">Activo</span>
          </div>

          <div className="form-grid" style={{ marginTop: '1rem' }}>
            <div>
              <strong>Solicitante:</strong>
              <div>{prestamoCreado.nombre_persona || 'N/A'} (C.C. {prestamoCreado.cedula_persona})</div>
            </div>
            <div>
              <strong>Equipo Prestado:</strong>
              <div>{prestamoCreado.nombre_equipo || `Equipo ID ${prestamoCreado.id_equipo}`} ({prestamoCreado.secuencial_equipo || 'S/N'})</div>
            </div>
            <div>
              <strong>Categoría:</strong>
              <div>{prestamoCreado.nombre_categoria || 'N/A'}</div>
            </div>
            <div>
              <strong>Fecha de Préstamo:</strong>
              <div>{prestamoCreado.fecha_prestamo}</div>
            </div>
            <div className="full-width" style={{ marginTop: '0.5rem', padding: '0.75rem', backgroundColor: '#dcfce7', borderRadius: '6px' }}>
              <strong style={{ color: '#166534' }}>📅 Fecha de Devolución Esperada (calculada):</strong>
              <div style={{ fontSize: '1.1rem', fontWeight: 600, color: '#14532d' }}>
                {prestamoCreado.fecha_devolucion_esperada}
              </div>
              <small style={{ color: '#15803d' }}>
                Calculada automáticamente según el plazo de entrega de la categoría asociada.
              </small>
            </div>
          </div>
        </div>
      )}

      {/* Listado y Filtros de Préstamos */}
      <div className="card table-card" style={{ marginTop: '1.5rem' }}>
        <div className="table-header">
          <h3>📋 Historial de Préstamos ({prestamos.length})</h3>
          <div className="table-controls" style={{ flexWrap: 'wrap', gap: '0.75rem' }}>
            {/* Filtro por Categoría */}
            <select
              value={filtroCategoria}
              onChange={(e) => setFiltroCategoria(e.target.value)}
              aria-label="Filtrar por categoría"
            >
              <option value="">Todas las categorías</option>
              {categorias.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.nombre}
                </option>
              ))}
            </select>

            {/* Filtro por Fecha Desde */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <small style={{ color: '#64748b' }}>Desde:</small>
              <input
                type="date"
                value={filtroFechaDesde}
                onChange={(e) => setFiltroFechaDesde(e.target.value)}
                style={{ padding: '0.4rem 0.6rem', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '0.85rem' }}
                aria-label="Fecha desde"
              />
            </div>

            {/* Filtro por Fecha Hasta */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
              <small style={{ color: '#64748b' }}>Hasta:</small>
              <input
                type="date"
                value={filtroFechaHasta}
                onChange={(e) => setFiltroFechaHasta(e.target.value)}
                style={{ padding: '0.4rem 0.6rem', border: '1px solid #cbd5e1', borderRadius: '6px', fontSize: '0.85rem' }}
                aria-label="Fecha hasta"
              />
            </div>

            {/* Filtro por Estado */}
            <select
              value={filtroEstado}
              onChange={(e) => setFiltroEstado(e.target.value)}
              aria-label="Filtrar por estado"
            >
              <option value="">Todos los estados</option>
              <option value="vigente">🟢 Vigente</option>
              <option value="vencido">🔴 Vencido</option>
            </select>

            {/* Botón limpiar */}
            {(filtroCategoria || filtroFechaDesde || filtroFechaHasta || filtroEstado) && (
              <button
                type="button"
                className="btn-secondary btn-sm"
                onClick={limpiarFiltros}
                title="Limpiar filtros"
              >
                ✕ Limpiar
              </button>
            )}

            {/* Botón actualizar */}
            <button
              type="button"
              className="btn-secondary btn-sm"
              onClick={cargarPrestamos}
              disabled={loadingPrestamos}
            >
              🔄 {loadingPrestamos ? 'Cargando...' : 'Actualizar'}
            </button>
          </div>
        </div>

        {loadingPrestamos ? (
          <p>Cargando préstamos...</p>
        ) : prestamos.length === 0 ? (
          <p className="empty-message">No se encontraron préstamos con los criterios seleccionados.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th># ID</th>
                  <th>Solicitante</th>
                  <th>Equipo</th>
                  <th>Categoría</th>
                  <th>Fecha Préstamo</th>
                  <th>Fecha Devolución Esperada</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {prestamos.map((p) => (
                  <tr key={p.id}>
                    <td><strong>#{p.id}</strong></td>
                    <td>
                      <div>{p.nombre_persona || 'N/A'}</div>
                      <small style={{ color: '#64748b' }}>C.C. {p.cedula_persona}</small>
                    </td>
                    <td>
                      <div>{p.nombre_equipo || `Equipo #${p.id_equipo}`}</div>
                      <small style={{ color: '#64748b' }}>Sec: {p.secuencial_equipo || 'S/N'}</small>
                    </td>
                    <td>{p.nombre_categoria || '-'}</td>
                    <td>{p.fecha_prestamo}</td>
                    <td>{p.fecha_devolucion_esperada}</td>
                    <td>
                      {p.estado === 'vigente' && (
                        <span className="badge badge-active">🟢 Vigente</span>
                      )}
                      {p.estado === 'vencido' && (
                        <span className="badge badge-danger">🔴 Vencido</span>
                      )}
                      {p.estado === 'devuelto' && (
                        <span className="badge badge-inactive">⚪ Devuelto</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
