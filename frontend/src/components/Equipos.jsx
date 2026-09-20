import { useState, useEffect } from 'react';

export default function Equipos() {
  const [equipos, setEquipos] = useState([]);
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(false);
  const [mensaje, setMensaje] = useState(null); // { tipo: 'success' | 'error', texto: string }

  // Filtros
  const [soloActivos, setSoloActivos] = useState(true);
  const [filtroCategoria, setFiltroCategoria] = useState('');
  const [filtroMantenimiento, setFiltroMantenimiento] = useState('');

  // Formulario de creación
  const [idCategoria, setIdCategoria] = useState('');
  const [nombre, setNombre] = useState('');
  const [secuencial, setSecuencial] = useState('');
  const [descripcion, setDescripcion] = useState('');

  // Formulario de edición
  const [editandoId, setEditandoId] = useState(null);
  const [editIdCategoria, setEditIdCategoria] = useState('');
  const [editNombre, setEditNombre] = useState('');
  const [editSecuencial, setEditSecuencial] = useState('');
  const [editDescripcion, setEditDescripcion] = useState('');
  const [editMantenimiento, setEditMantenimiento] = useState(false);
  const [editActivo, setEditActivo] = useState(true);

  // Cargar lista de categorías activas para los selectores
  const cargarCategorias = async () => {
    try {
      const res = await fetch('/api/categorias?solo_activas=true');
      if (res.ok) {
        const data = await res.json();
        setCategorias(data);
        if (data.length > 0 && !idCategoria) {
          setIdCategoria(data[0].id);
        }
      }
    } catch (err) {
      console.error('Error al cargar categorías:', err);
    }
  };

  // Cargar lista de equipos aplicando filtros
  const cargarEquipos = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('solo_activos', soloActivos);
      if (filtroCategoria) {
        params.append('id_categoria', filtroCategoria);
      }
      if (filtroMantenimiento !== '') {
        params.append('en_mantenimiento', filtroMantenimiento === 'true');
      }

      const res = await fetch(`/api/equipos?${params.toString()}`);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Error al obtener equipos');
      }
      const data = await res.json();
      setEquipos(data);
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCategorias();
  }, []);

  useEffect(() => {
    cargarEquipos();
  }, [soloActivos, filtroCategoria, filtroMantenimiento]);

  // Manejar creación de equipo
  const handleCrear = async (e) => {
    e.preventDefault();
    setMensaje(null);

    if (!idCategoria) {
      setMensaje({ tipo: 'error', texto: 'Debes seleccionar una categoría activa válida.' });
      return;
    }

    const payload = {
      id_categoria: Number(idCategoria),
      nombre: nombre.trim(),
      secuencial: secuencial.trim(),
      descripcion: descripcion.trim() || null,
    };

    try {
      const res = await fetch('/api/equipos', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al crear el equipo');
      }

      setMensaje({
        tipo: 'success',
        texto: `Equipo "${data.nombre}" (${data.secuencial}) registrado con éxito (ID: ${data.id})`,
      });
      setNombre('');
      setSecuencial('');
      setDescripcion('');
      cargarEquipos();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    }
  };

  // Iniciar edición
  const iniciarEdicion = (eq) => {
    setEditandoId(eq.id);
    setEditIdCategoria(eq.id_categoria);
    setEditNombre(eq.nombre);
    setEditSecuencial(eq.secuencial);
    setEditDescripcion(eq.descripcion || '');
    setEditMantenimiento(eq.mantenimiento);
    setEditActivo(eq.activo);
  };

  const cancelarEdicion = () => {
    setEditandoId(null);
  };

  // Guardar edición
  const handleGuardarEdicion = async (e) => {
    e.preventDefault();
    setMensaje(null);

    const payload = {
      id_categoria: Number(editIdCategoria),
      nombre: editNombre.trim(),
      secuencial: editSecuencial.trim(),
      descripcion: editDescripcion.trim() || null,
      mantenimiento: editMantenimiento,
      activo: editActivo,
    };

    try {
      const res = await fetch(`/api/equipos/${editandoId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al actualizar el equipo');
      }

      setMensaje({
        tipo: 'success',
        texto: `Equipo #${data.id} (${data.secuencial}) actualizado correctamente`,
      });
      setEditandoId(null);
      cargarEquipos();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    }
  };

  // Borrado lógico
  const handleEliminar = async (id, nombre, secuencial) => {
    if (!window.confirm(`¿Confirmas desactivar lógicamente el equipo "${nombre}" [${secuencial}] (ID: ${id})?`)) {
      return;
    }
    setMensaje(null);

    try {
      const res = await fetch(`/api/equipos/${id}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al desactivar el equipo');
      }

      setMensaje({
        tipo: 'success',
        texto: `Equipo "${data.nombre}" (${data.secuencial}) desactivado (borrado lógico: activo=false)`,
      });
      cargarEquipos();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    }
  };

  // Sacar de mantenimiento
  const handleSacarMantenimiento = async (id, nombre, secuencial) => {
    if (!window.confirm(`¿Confirmas marcar el equipo "${nombre}" [${secuencial}] (ID: ${id}) como disponible y sacarlo de mantenimiento?`)) {
      return;
    }
    setMensaje(null);

    try {
      const res = await fetch(`/api/equipos/${id}/sacar-mantenimiento`, {
        method: 'POST',
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al sacar el equipo de mantenimiento');
      }

      setMensaje({
        tipo: 'success',
        texto: `Equipo "${data.nombre}" (${data.secuencial}) marcado como disponible. Mantenimiento finalizado exitosamente.`,
      });
      cargarEquipos();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    }
  };

  return (
    <div className="crud-container">
      <h2>Gestión de Equipos de Laboratorio</h2>

      {/* Alertas */}
      {mensaje && (
        <div className={`alert ${mensaje.tipo === 'error' ? 'alert-error' : 'alert-success'}`}>
          <span>{mensaje.texto}</span>
          <button className="alert-close" onClick={() => setMensaje(null)}>✕</button>
        </div>
      )}

      {/* Formulario de Creación */}
      <div className="card form-card">
        <h3>Nuevo Equipo</h3>
        <form onSubmit={handleCrear} className="form-grid">
          <div className="form-group">
            <label htmlFor="categoria">Categoría *</label>
            <select
              id="categoria"
              required
              value={idCategoria}
              onChange={(e) => setIdCategoria(e.target.value)}
            >
              <option value="" disabled>Selecciona una categoría activa</option>
              {categorias.map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {cat.nombre} (Plazo: {cat.plazo_entrega} días)
                </option>
              ))}
            </select>
          </div>

          <div className="form-group">
            <label htmlFor="secuencial">Secuencial Interno *</label>
            <input
              id="secuencial"
              type="text"
              required
              maxLength={50}
              placeholder="Ej. OSC-001 o LAP-2024"
              value={secuencial}
              onChange={(e) => setSecuencial(e.target.value)}
            />
          </div>

          <div className="form-group full-width">
            <label htmlFor="nombre">Nombre del Equipo *</label>
            <input
              id="nombre"
              type="text"
              required
              maxLength={150}
              placeholder="Ej. Osciloscopio Digital Rigol 100MHz"
              value={nombre}
              onChange={(e) => setNombre(e.target.value)}
            />
          </div>

          <div className="form-group full-width">
            <label htmlFor="descripcion">Descripción (opcional)</label>
            <input
              id="descripcion"
              type="text"
              maxLength={255}
              placeholder="Ej. Incluye puntas de prueba y cable de alimentación"
              value={descripcion}
              onChange={(e) => setDescripcion(e.target.value)}
            />
          </div>

          <div className="form-actions full-width">
            <button type="submit" className="btn-primary">
              + Registrar Equipo
            </button>
          </div>
        </form>
      </div>

      {/* Formulario de Edición */}
      {editandoId && (
        <div className="card form-card edit-card">
          <h3>Editar Equipo (ID: {editandoId})</h3>
          <form onSubmit={handleGuardarEdicion} className="form-grid">
            <div className="form-group">
              <label htmlFor="edit-categoria">Categoría *</label>
              <select
                id="edit-categoria"
                required
                value={editIdCategoria}
                onChange={(e) => setEditIdCategoria(e.target.value)}
              >
                {categorias.map((cat) => (
                  <option key={cat.id} value={cat.id}>
                    {cat.nombre}
                  </option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="edit-secuencial">Secuencial Interno *</label>
              <input
                id="edit-secuencial"
                type="text"
                required
                maxLength={50}
                value={editSecuencial}
                onChange={(e) => setEditSecuencial(e.target.value)}
              />
            </div>

            <div className="form-group full-width">
              <label htmlFor="edit-nombre">Nombre del Equipo *</label>
              <input
                id="edit-nombre"
                type="text"
                required
                maxLength={150}
                value={editNombre}
                onChange={(e) => setEditNombre(e.target.value)}
              />
            </div>

            <div className="form-group full-width">
              <label htmlFor="edit-descripcion">Descripción</label>
              <input
                id="edit-descripcion"
                type="text"
                maxLength={255}
                value={editDescripcion}
                onChange={(e) => setEditDescripcion(e.target.value)}
              />
            </div>

            <div className="form-group full-width checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={editMantenimiento}
                  onChange={(e) => setEditMantenimiento(e.target.checked)}
                />
                {' '}En Mantenimiento (marcar si el equipo no está operativo o está en reparación)
              </label>
            </div>

            <div className="form-group full-width checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={editActivo}
                  onChange={(e) => setEditActivo(e.target.checked)}
                />
                {' '}Equipo Activo (desmarcar para borrado lógico, marcar para reactivar)
              </label>
            </div>

            <div className="form-actions full-width">
              <button type="submit" className="btn-primary">Guardar Cambios</button>
              <button type="button" className="btn-secondary" onClick={cancelarEdicion}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de Equipos */}
      <div className="card table-card">
        <div className="table-header">
          <h3>Equipos Registrados ({equipos.length})</h3>
          <div className="table-controls">
            {/* Filtro Categoría */}
            <select
              value={filtroCategoria}
              onChange={(e) => setFiltroCategoria(e.target.value)}
              aria-label="Filtrar por categoría"
            >
              <option value="">Todas las categorías</option>
              {categorias.map((c) => (
                <option key={c.id} value={c.id}>{c.nombre}</option>
              ))}
            </select>

            {/* Filtro Mantenimiento */}
            <select
              value={filtroMantenimiento}
              onChange={(e) => setFiltroMantenimiento(e.target.value)}
              aria-label="Filtrar por mantenimiento"
            >
              <option value="">Todos los estados</option>
              <option value="false">Operativos</option>
              <option value="true">En Mantenimiento</option>
            </select>

            {/* Filtro Activos */}
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={soloActivos}
                onChange={(e) => setSoloActivos(e.target.checked)}
              />
              {' '}Solo activos
            </label>

            <button type="button" className="btn-secondary" onClick={cargarEquipos}>
              🔄 Actualizar
            </button>
          </div>
        </div>

        {loading ? (
          <p>Cargando equipos...</p>
        ) : equipos.length === 0 ? (
          <p className="empty-message">No se encontraron equipos registrados.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Secuencial</th>
                  <th>Nombre</th>
                  <th>Categoría</th>
                  <th>Fecha Registro</th>
                  <th>Mantenimiento</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {equipos.map((eq) => (
                  <tr key={eq.id} className={!eq.activo ? 'row-inactive' : ''}>
                    <td><strong>#{eq.id}</strong></td>
                    <td><code>{eq.secuencial}</code></td>
                    <td>
                      <div><strong>{eq.nombre}</strong></div>
                      {eq.descripcion && <small style={{ color: '#64748b' }}>{eq.descripcion}</small>}
                    </td>
                    <td>{eq.nombre_categoria || `Cat #${eq.id_categoria}`}</td>
                    <td>{eq.fecha_creacion}</td>
                    <td>
                      <span className={`badge ${eq.mantenimiento ? 'badge-warning' : 'badge-active'}`}>
                        {eq.mantenimiento ? '🔧 En Mantenimiento' : '✅ Operativo'}
                      </span>
                    </td>
                    <td>
                      <span className={`badge ${eq.activo ? 'badge-active' : 'badge-inactive'}`}>
                        {eq.activo ? 'Activo' : 'Inactivo'}
                      </span>
                    </td>
                    <td className="actions-cell">
                      {eq.mantenimiento && eq.activo && (
                        <button
                          className="btn-sm btn-success"
                          onClick={() => handleSacarMantenimiento(eq.id, eq.nombre, eq.secuencial)}
                          title="Sacar de mantenimiento y marcar como disponible"
                        >
                          ✅ Disponible
                        </button>
                      )}
                      <button
                        className="btn-sm btn-edit"
                        onClick={() => iniciarEdicion(eq)}
                        title="Editar equipo"
                      >
                        ✏️ Editar
                      </button>
                      {eq.activo && (
                        <button
                          className="btn-sm btn-danger"
                          onClick={() => handleEliminar(eq.id, eq.nombre, eq.secuencial)}
                          title="Borrado lógico"
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
