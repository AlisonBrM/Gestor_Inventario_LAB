import { useState, useEffect } from 'react';

export default function Categorias() {
  const [categorias, setCategorias] = useState([]);
  const [loading, setLoading] = useState(false);
  const [soloActivas, setSoloActivas] = useState(false);
  const [mensaje, setMensaje] = useState(null); // { tipo: 'success' | 'error', texto: string }

  // Estado del formulario de creación
  const [nuevoNombre, setNuevoNombre] = useState('');
  const [nuevaDescripcion, setNuevaDescripcion] = useState('');
  const [nuevoPlazo, setNuevoPlazo] = useState(15);

  // Estado de edición
  const [editandoId, setEditandoId] = useState(null);
  const [editNombre, setEditNombre] = useState('');
  const [editDescripcion, setEditDescripcion] = useState('');
  const [editPlazo, setEditPlazo] = useState(15);
  const [editActivo, setEditActivo] = useState(true);

  // Cargar categorías
  const cargarCategorias = async () => {
    setLoading(true);
    try {
      const res = await fetch(`/api/categorias?solo_activas=${soloActivas}`);
      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Error al obtener categorías');
      }
      const data = await res.json();
      setCategorias(data);
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    cargarCategorias();
  }, [soloActivas]);

  // Crear categoría
  const handleCrear = async (e) => {
    e.preventDefault();
    setMensaje(null);

    const payload = {
      nombre: nuevoNombre.trim(),
      descripcion: nuevaDescripcion.trim() || null,
      plazo_entrega: Number(nuevoPlazo),
    };

    try {
      const res = await fetch('/api/categorias', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al crear la categoría');
      }

      setMensaje({ tipo: 'success', texto: `Categoría "${data.nombre}" creada con éxito (ID: ${data.id})` });
      setNuevoNombre('');
      setNuevaDescripcion('');
      setNuevoPlazo(15);
      cargarCategorias();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    }
  };

  // Iniciar edición
  const iniciarEdicion = (cat) => {
    setEditandoId(cat.id);
    setEditNombre(cat.nombre);
    setEditDescripcion(cat.descripcion || '');
    setEditPlazo(cat.plazo_entrega);
    setEditActivo(cat.activo);
  };

  const cancelarEdicion = () => {
    setEditandoId(null);
  };

  // Guardar edición
  const handleGuardarEdicion = async (e) => {
    e.preventDefault();
    setMensaje(null);

    const payload = {
      nombre: editNombre.trim(),
      descripcion: editDescripcion.trim() || null,
      plazo_entrega: Number(editPlazo),
      activo: editActivo,
    };

    try {
      const res = await fetch(`/api/categorias/${editandoId}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al actualizar la categoría');
      }

      setMensaje({ tipo: 'success', texto: `Categoría #${data.id} actualizada correctamente` });
      setEditandoId(null);
      cargarCategorias();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    }
  };

  // Eliminar (Borrado lógico)
  const handleEliminar = async (id, nombre) => {
    if (!window.confirm(`¿Confirmas desactivar lógicamente la categoría "${nombre}" (ID: ${id})?`)) {
      return;
    }
    setMensaje(null);

    try {
      const res = await fetch(`/api/categorias/${id}`, {
        method: 'DELETE',
      });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Error al eliminar la categoría');
      }

      setMensaje({ tipo: 'success', texto: `Categoría "${data.nombre}" desactivada (borrado lógico: activo=false)` });
      cargarCategorias();
    } catch (err) {
      setMensaje({ tipo: 'error', texto: err.message });
    }
  };

  return (
    <div className="crud-container">
      <h2>Gestión de Categorías de Equipos</h2>

      {/* Alertas */}
      {mensaje && (
        <div className={`alert ${mensaje.tipo === 'error' ? 'alert-error' : 'alert-success'}`}>
          <span>{mensaje.texto}</span>
          <button className="alert-close" onClick={() => setMensaje(null)}>✕</button>
        </div>
      )}

      {/* Formulario de Creación */}
      <div className="card form-card">
        <h3>Nueva Categoría</h3>
        <form onSubmit={handleCrear} className="form-grid">
          <div className="form-group">
            <label htmlFor="nombre">Nombre *</label>
            <input
              id="nombre"
              type="text"
              required
              maxLength={100}
              placeholder="Ej. Equipos de Cómputo"
              value={nuevoNombre}
              onChange={(e) => setNuevoNombre(e.target.value)}
            />
          </div>

          <div className="form-group">
            <label htmlFor="plazo">Plazo de Entrega (1 - 180 días) *</label>
            <input
              id="plazo"
              type="number"
              min={1}
              max={180}
              required
              value={nuevoPlazo}
              onChange={(e) => setNuevoPlazo(e.target.value)}
            />
          </div>

          <div className="form-group full-width">
            <label htmlFor="descripcion">Descripción (opcional)</label>
            <input
              id="descripcion"
              type="text"
              maxLength={255}
              placeholder="Descripción breve de la categoría"
              value={nuevaDescripcion}
              onChange={(e) => setNuevaDescripcion(e.target.value)}
            />
          </div>

          <div className="form-actions full-width">
            <button type="submit" className="btn-primary">
              + Registrar Categoría
            </button>
          </div>
        </form>
      </div>

      {/* Formulario Modal/Flotante de Edición */}
      {editandoId && (
        <div className="card form-card edit-card">
          <h3>Editar Categoría (ID: {editandoId})</h3>
          <form onSubmit={handleGuardarEdicion} className="form-grid">
            <div className="form-group">
              <label htmlFor="edit-nombre">Nombre *</label>
              <input
                id="edit-nombre"
                type="text"
                required
                maxLength={100}
                value={editNombre}
                onChange={(e) => setEditNombre(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="edit-plazo">Plazo de Entrega (1 - 180 días) *</label>
              <input
                id="edit-plazo"
                type="number"
                min={1}
                max={180}
                required
                value={editPlazo}
                onChange={(e) => setEditPlazo(e.target.value)}
              />
            </div>

            <div className="form-group full-width">
              <label htmlFor="edit-desc">Descripción</label>
              <input
                id="edit-desc"
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
                  checked={editActivo}
                  onChange={(e) => setEditActivo(e.target.checked)}
                />
                {' '}Categoría Activa (desmarcar para borrado lógico, marcar para reactivar)
              </label>
            </div>

            <div className="form-actions full-width">
              <button type="submit" className="btn-primary">Guardar Cambios</button>
              <button type="button" className="btn-secondary" onClick={cancelarEdicion}>Cancelar</button>
            </div>
          </form>
        </div>
      )}

      {/* Lista de Categorías */}
      <div className="card table-card">
        <div className="table-header">
          <h3>Categorías Registradas ({categorias.length})</h3>
          <div className="table-controls">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={soloActivas}
                onChange={(e) => setSoloActivas(e.target.checked)}
              />
              {' '}Ver solo activas
            </label>
            <button type="button" className="btn-secondary" onClick={cargarCategorias}>
              🔄 Actualizar
            </button>
          </div>
        </div>

        {loading ? (
          <p>Cargando categorías...</p>
        ) : categorias.length === 0 ? (
          <p className="empty-message">No se encontraron categorías registradas.</p>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Descripción</th>
                  <th>Plazo Máximo</th>
                  <th>Estado</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {categorias.map((cat) => (
                  <tr key={cat.id} className={!cat.activo ? 'row-inactive' : ''}>
                    <td><strong>#{cat.id}</strong></td>
                    <td>{cat.nombre}</td>
                    <td>{cat.descripcion || <em>Sin descripción</em>}</td>
                    <td>{cat.plazo_entrega} días</td>
                    <td>
                      <span className={`badge ${cat.activo ? 'badge-active' : 'badge-inactive'}`}>
                        {cat.activo ? 'Activa' : 'Inactiva'}
                      </span>
                    </td>
                    <td className="actions-cell">
                      <button
                        className="btn-sm btn-edit"
                        onClick={() => iniciarEdicion(cat)}
                        title="Editar categoría"
                      >
                        ✏️ Editar
                      </button>
                      {cat.activo && (
                        <button
                          className="btn-sm btn-danger"
                          onClick={() => handleEliminar(cat.id, cat.nombre)}
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
