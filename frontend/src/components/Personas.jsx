import { useState, useEffect } from 'react';

export default function Personas() {
  const [personas, setPersonas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState(null); // { tipo: 'success' | 'error', texto: string }

  // Filtros
  const [soloActivas, setSoloActivas] = useState(true);
  const [filtroTipo, setFiltroTipo] = useState('');
  const [filtroFacultad, setFiltroFacultad] = useState('');
  const [filtroBusqueda, setFiltroBusqueda] = useState('');

  // Formulario de creación
  const [cedula, setCedula] = useState('');
  const [nombreCompleto, setNombreCompleto] = useState('');
  const [correo, setCorreo] = useState('');
  const [telefono, setTelefono] = useState('');
  const [tipoPersona, setTipoPersona] = useState('estudiante');
  const [facultad, setFacultad] = useState('');

  // Formulario de edición
  const [editandoCedula, setEditandoCedula] = useState(null);
  const [editNombreCompleto, setEditNombreCompleto] = useState('');
  const [editCorreo, setEditCorreo] = useState('');
  const [editTelefono, setEditTelefono] = useState('');
  const [editTipoPersona, setEditTipoPersona] = useState('estudiante');
  const [editFacultad, setEditFacultad] = useState('');
  const [editActivo, setEditActivo] = useState(true);

  // Cargar lista de personas aplicando filtros
  const cargarPersonas = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('solo_activas', soloActivas);
      if (filtroTipo) {
        params.append('tipo_persona', filtroTipo);
      }
      if (filtroFacultad.trim()) {
        params.append('facultad', filtroFacultad.trim());
      }
      if (filtroBusqueda.trim()) {
        params.append('busqueda', filtroBusqueda.trim());
      }

      const res = await fetch(`/api/personas?${params.toString()}`);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Error al obtener personas');
      }
      const data = await res.json();
      setPersonas(data);
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarPersonas();
  }, [soloActivas, filtroTipo, filtroFacultad, filtroBusqueda]);

  // Manejador de creación
  const handleCrear = async (e) => {
    e.preventDefault();
    setMensaje(null);

    const payload = {
      cedula: cedula.trim(),
      nombre_completo: nombreCompleto.trim(),
      correo: correo.trim() || null,
      telefono: telefono.trim(),
      tipo_persona: tipoPersona,
      facultad: facultad.trim(),
    };

    try {
      const res = await fetch('/api/personas', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al registrar persona');
      }

      setMensaje({
        tipo: 'success',
        texto: `Persona "${data.nombre_completo}" (Cédula: ${data.cedula}) registrada con éxito.`,
      });

      // Limpiar formulario
      setCedula('');
      setNombreCompleto('');
      setCorreo('');
      setTelefono('');
      setTipoPersona('estudiante');
      setFacultad('');

      cargarPersonas();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    }
  };

  // Iniciar modo de edición
  const iniciarEdicion = (persona) => {
    setEditandoCedula(persona.cedula);
    setEditNombreCompleto(persona.nombre_completo);
    setEditCorreo(persona.correo || '');
    setEditTelefono(persona.telefono);
    setEditTipoPersona(persona.tipo_persona);
    setEditFacultad(persona.facultad);
    setEditActivo(persona.activo);
  };

  const cancelarEdicion = () => {
    setEditandoCedula(null);
  };

  // Guardar edición
  const handleGuardarEdicion = async (e) => {
    e.preventDefault();
    setMensaje(null);

    const payload = {
      nombre_completo: editNombreCompleto.trim(),
      correo: editCorreo.trim() || null,
      telefono: editTelefono.trim(),
      tipo_persona: editTipoPersona,
      facultad: editFacultad.trim(),
      activo: editActivo,
    };

    try {
      const res = await fetch(`/api/personas/${editandoCedula}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al actualizar persona');
      }

      setMensaje({
        tipo: 'success',
        texto: `Persona con cédula ${editandoCedula} actualizada exitosamente.`,
      });
      setEditandoCedula(null);
      cargarPersonas();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    }
  };

  // Borrado lógico
  const handleDesactivar = async (cedula) => {
    if (!window.confirm(`¿Estás seguro de desactivar la persona con cédula "${cedula}"?`)) {
      return;
    }
    setMensaje(null);

    try {
      const res = await fetch(`/api/personas/${cedula}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al desactivar persona');
      }

      setMensaje({
        tipo: 'success',
        texto: `Persona con cédula "${cedula}" desactivada correctamente.`,
      });
      cargarPersonas();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    }
  };

  return (
    <div className="personas-module">
      {/* Alertas y Mensajes */}
      {mensaje && (
        <div className={`alert alert-${mensaje.tipo}`}>
          <span>{mensaje.texto}</span>
          <button className="btn-close-alert" onClick={() => setMensaje(null)}>
            ✕
          </button>
        </div>
      )}

      {/* Formulario de Edición (aparece solo si se está editando) */}
      {editandoCedula && (
        <div className="card edit-card">
          <h2>✏️ Editar Persona: Cédula {editandoCedula}</h2>
          <form onSubmit={handleGuardarEdicion}>
            <div className="form-grid">
              <div className="form-group">
                <label>Cédula (Identificador inmutable)</label>
                <input type="text" value={editandoCedula} disabled style={{ backgroundColor: '#f1f5f9' }} />
              </div>

              <div className="form-group">
                <label>Nombre Completo *</label>
                <input
                  type="text"
                  value={editNombreCompleto}
                  onChange={(e) => setEditNombreCompleto(e.target.value)}
                  maxLength={100}
                  required
                />
              </div>

              <div className="form-group">
                <label>Tipo de Persona *</label>
                <select
                  value={editTipoPersona}
                  onChange={(e) => setEditTipoPersona(e.target.value)}
                  required
                >
                  <option value="estudiante">Estudiante</option>
                  <option value="profesor">Profesor</option>
                </select>
              </div>

              <div className="form-group">
                <label>Teléfono Celular *</label>
                <input
                  type="text"
                  value={editTelefono}
                  onChange={(e) => setEditTelefono(e.target.value)}
                  minLength={7}
                  maxLength={15}
                  required
                />
              </div>

              <div className="form-group">
                <label>Correo Electrónico (Opcional)</label>
                <input
                  type="email"
                  value={editCorreo}
                  onChange={(e) => setEditCorreo(e.target.value)}
                  maxLength={150}
                  placeholder="ejemplo@universidad.edu.co"
                />
              </div>

              <div className="form-group">
                <label>Facultad *</label>
                <input
                  type="text"
                  value={editFacultad}
                  onChange={(e) => setEditFacultad(e.target.value)}
                  maxLength={150}
                  required
                />
              </div>

              <div className="form-group full-width checkbox-group">
                <label className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={editActivo}
                    onChange={(e) => setEditActivo(e.target.checked)}
                  />
                  {' '}Persona Activa (Habilitada para préstamos)
                </label>
              </div>
            </div>

            <div className="form-actions">
              <button type="submit" className="btn-primary">
                Guardar Cambios
              </button>
              <button type="button" className="btn-secondary" onClick={cancelarEdicion}>
                Cancelar
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Formulario de Creación */}
      <div className="card">
        <h2>👤 Registrar Nueva Persona</h2>
        <form onSubmit={handleCrear}>
          <div className="form-grid">
            <div className="form-group">
              <label>Cédula de Identificación *</label>
              <input
                type="text"
                value={cedula}
                onChange={(e) => setCedula(e.target.value)}
                placeholder="Ej. 1001234567 (6-15 dígitos)"
                minLength={6}
                maxLength={15}
                required
              />
            </div>

            <div className="form-group">
              <label>Nombre Completo *</label>
              <input
                type="text"
                value={nombreCompleto}
                onChange={(e) => setNombreCompleto(e.target.value)}
                placeholder="Ej. Juan Manuel Pérez Gómez"
                maxLength={100}
                required
              />
            </div>

            <div className="form-group">
              <label>Tipo de Persona *</label>
              <select
                value={tipoPersona}
                onChange={(e) => setTipoPersona(e.target.value)}
                required
              >
                <option value="estudiante">Estudiante</option>
                <option value="profesor">Profesor</option>
              </select>
            </div>

            <div className="form-group">
              <label>Teléfono Celular *</label>
              <input
                type="text"
                value={telefono}
                onChange={(e) => setTelefono(e.target.value)}
                placeholder="Ej. 3001234567 (7-15 dígitos)"
                minLength={7}
                maxLength={15}
                required
              />
            </div>

            <div className="form-group">
              <label>Correo Electrónico (Opcional)</label>
              <input
                type="email"
                value={correo}
                onChange={(e) => setCorreo(e.target.value)}
                placeholder="ejemplo@universidad.edu.co"
                maxLength={150}
              />
            </div>

            <div className="form-group">
              <label>Facultad *</label>
              <input
                type="text"
                value={facultad}
                onChange={(e) => setFacultad(e.target.value)}
                placeholder="Ej. Facultad de Ingeniería"
                maxLength={150}
                required
              />
            </div>
          </div>

          <div className="form-actions">
            <button type="submit" className="btn-primary">
              + Registrar Persona
            </button>
          </div>
        </form>
      </div>

      {/* Listado y Filtros */}
      <div className="card">
        <div className="table-header">
          <h2>📋 Directorio de Personas</h2>
          <div className="table-controls">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={soloActivas}
                onChange={(e) => setSoloActivas(e.target.checked)}
              />
              {' '}Solo activas
            </label>
          </div>
        </div>

        {/* Barra de Filtros */}
        <div className="form-grid" style={{ marginBottom: '1.25rem' }}>
          <div className="form-group">
            <label>Filtrar por Tipo</label>
            <select
              value={filtroTipo}
              onChange={(e) => setFiltroTipo(e.target.value)}
            >
              <option value="">Todos los tipos</option>
              <option value="estudiante">Estudiantes</option>
              <option value="profesor">Profesores</option>
            </select>
          </div>

          <div className="form-group">
            <label>Buscar por Cédula o Nombre</label>
            <input
              type="text"
              value={filtroBusqueda}
              onChange={(e) => setFiltroBusqueda(e.target.value)}
              placeholder="Escribe para buscar..."
            />
          </div>

          <div className="form-group full-width">
            <label>Filtrar por Facultad</label>
            <input
              type="text"
              value={filtroFacultad}
              onChange={(e) => setFiltroFacultad(e.target.value)}
              placeholder="Filtrar por nombre de facultad..."
            />
          </div>
        </div>

        {loading ? (
          <p>Cargando personas...</p>
        ) : personas.length === 0 ? (
          <p style={{ color: '#64748b' }}>No se encontraron personas con los filtros seleccionados.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Cédula</th>
                  <th>Nombre Completo</th>
                  <th>Tipo</th>
                  <th>Teléfono</th>
                  <th>Correo</th>
                  <th>Facultad</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {personas.map((p) => (
                  <tr key={p.cedula} className={!p.activo ? 'row-inactive' : ''}>
                    <td style={{ fontWeight: 600 }}>{p.cedula}</td>
                    <td>{p.nombre_completo}</td>
                    <td>
                      <span className="badge" style={{ backgroundColor: p.tipo_persona === 'profesor' ? '#ede9fe' : '#e0f2fe', color: p.tipo_persona === 'profesor' ? '#5b21b6' : '#0369a1' }}>
                        {p.tipo_persona === 'profesor' ? '👨‍🏫 Profesor' : '🎓 Estudiante'}
                      </span>
                    </td>
                    <td>{p.telefono}</td>
                    <td>{p.correo || <em style={{ color: '#94a3b8' }}>No registrado</em>}</td>
                    <td>{p.facultad}</td>
                    <td>
                      <span className={`badge ${p.activo ? 'badge-active' : 'badge-inactive'}`}>
                        {p.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="actions-cell">
                      <button
                        className="btn-sm btn-edit"
                        onClick={() => iniciarEdicion(p)}
                        title="Editar persona"
                      >
                        ✏️ Editar
                      </button>
                      {p.activo && (
                        <button
                          className="btn-sm btn-danger"
                          onClick={() => handleDesactivar(p.cedula)}
                          title="Desactivar persona"
                        >
                          🗑️ Desactivar
                        </button>
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
