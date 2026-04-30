from flask import Flask, request, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore
import os
import json
app = Flask(__name__)
CORS(app)


# =========================
# CONEXIÓN FIREBASE
# =========================
cred_dict = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
cred = credentials.Certificate(cred_dict)
firebase_admin.initialize_app(cred)
db = firestore.client()

# =========================
# ROLES CRUD
# =========================
@app.route('/roles', methods=['GET'])
def listar_roles():
    roles = []
    docs = db.collection('roles').stream()
    for doc in docs:
        rol = doc.to_dict()
        rol['id'] = doc.id
        roles.append(rol)
    return jsonify(roles)

@app.route('/roles', methods=['POST'])
def agregar_rol():
    data = request.json
    if not data.get('nombre'):
        return jsonify({"error": "El nombre es requerido"}), 400
    existente = db.collection('roles').where('nombre', '==', data['nombre']).get()
    if len(existente) > 0:
        return jsonify({"error": "El rol ya existe"}), 400
    doc_ref = db.collection('roles').add({'nombre': data['nombre']})
    return jsonify({"mensaje": "Rol creado", "id": doc_ref[1].id})

@app.route('/roles/<string:id>', methods=['PUT'])
def editar_rol(id):
    data = request.json
    if not data.get('nombre'):
        return jsonify({"error": "El nombre es requerido"}), 400
    rol_ref = db.collection('roles').document(id)
    if not rol_ref.get().exists:
        return jsonify({"error": "Rol no encontrado"}), 404
    rol_ref.update({'nombre': data['nombre']})
    return jsonify({"mensaje": "Rol actualizado"})

@app.route('/roles/<string:id>', methods=['DELETE'])
def eliminar_rol(id):
    usuarios = db.collection('usuarios').where('id_rol', '==', id).get()
    if len(usuarios) > 0:
        return jsonify({"error": "No se puede eliminar, hay usuarios con este rol"}), 400
    db.collection('roles').document(id).delete()
    return jsonify({"mensaje": "Rol eliminado"})

# =========================
# USUARIOS CRUD
# =========================
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = []
    docs = db.collection('usuarios').stream()
    for doc in docs:
        usuario = doc.to_dict()
        usuario['id'] = doc.id
        if usuario.get('id_rol'):
            rol_doc = db.collection('roles').document(usuario['id_rol']).get()
            usuario['rol'] = rol_doc.to_dict().get('nombre', '') if rol_doc.exists else ''
        usuarios.append(usuario)
    return jsonify(usuarios)

@app.route('/usuarios', methods=['POST'])
def agregar_usuario():
    data = request.json
    if not data.get('nombre') or not data.get('email') or not data.get('id_rol'):
        return jsonify({"error": "nombre, email e id_rol son requeridos"}), 400
    rol_doc = db.collection('roles').document(data['id_rol']).get()
    if not rol_doc.exists:
        return jsonify({"error": "El rol especificado no existe"}), 400
    existente = db.collection('usuarios').where('email', '==', data['email']).get()
    if len(existente) > 0:
        return jsonify({"error": "El email ya existe"}), 400
    doc_ref = db.collection('usuarios').add({
        'nombre': data['nombre'],
        'email': data['email'],
        'id_rol': data['id_rol']
    })
    return jsonify({"mensaje": "Usuario creado", "id": doc_ref[1].id})

@app.route('/usuarios/<string:id>', methods=['PUT'])
def editar_usuario(id):
    data = request.json
    usuario_ref = db.collection('usuarios').document(id)
    if not usuario_ref.get().exists:
        return jsonify({"error": "Usuario no encontrado"}), 404
    rol_doc = db.collection('roles').document(data['id_rol']).get()
    if not rol_doc.exists:
        return jsonify({"error": "El rol especificado no existe"}), 400
    existente = db.collection('usuarios').where('email', '==', data['email']).get()
    for u in existente:
        if u.id != id:
            return jsonify({"error": "El email ya está en uso por otro usuario"}), 400
    usuario_ref.update({
        'nombre': data['nombre'],
        'email': data['email'],
        'id_rol': data['id_rol']
    })
    return jsonify({"mensaje": "Usuario actualizado"})

@app.route('/usuarios/<string:id>', methods=['DELETE'])
def eliminar_usuario(id):
    pedidos = db.collection('pedidos').where('id_usuario', '==', id).get()
    if len(pedidos) > 0:
        return jsonify({"error": "No se puede eliminar, el usuario tiene pedidos asociados"}), 400
    db.collection('usuarios').document(id).delete()
    return jsonify({"mensaje": "Usuario eliminado"})

# =========================
# CATEGORIAS CRUD
# =========================
@app.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = []
    docs = db.collection('categorias').stream()
    for doc in docs:
        cat = doc.to_dict()
        cat['id'] = doc.id
        categorias.append(cat)
    return jsonify(categorias)

@app.route('/categorias', methods=['POST'])
def agregar_categoria():
    data = request.json
    if not data.get('nombre'):
        return jsonify({"error": "El nombre es requerido"}), 400
    existente = db.collection('categorias').where('nombre', '==', data['nombre']).get()
    if len(existente) > 0:
        return jsonify({"error": "La categoría ya existe"}), 400
    doc_ref = db.collection('categorias').add({'nombre': data['nombre']})
    return jsonify({"mensaje": "Categoria creada", "id": doc_ref[1].id})

@app.route('/categorias/<string:id>', methods=['PUT'])
def editar_categoria(id):
    data = request.json
    cat_ref = db.collection('categorias').document(id)
    if not cat_ref.get().exists:
        return jsonify({"error": "Categoría no encontrada"}), 404
    existente = db.collection('categorias').where('nombre', '==', data['nombre']).get()
    for c in existente:
        if c.id != id:
            return jsonify({"error": "Ya existe otra categoría con ese nombre"}), 400
    cat_ref.update({'nombre': data['nombre']})
    return jsonify({"mensaje": "Categoria actualizada"})

@app.route('/categorias/<string:id>', methods=['DELETE'])
def eliminar_categoria(id):
    productos = db.collection('productos').where('id_categoria', '==', id).get()
    if len(productos) > 0:
        return jsonify({"error": "No se puede eliminar, hay productos con esta categoría"}), 400
    db.collection('categorias').document(id).delete()
    return jsonify({"mensaje": "Categoria eliminada"})

# =========================
# PRODUCTOS CRUD
# =========================
@app.route('/productos', methods=['GET'])
def listar_productos():
    productos = []
    docs = db.collection('productos').stream()
    for doc in docs:
        producto = doc.to_dict()
        producto['id'] = doc.id
        if producto.get('id_categoria'):
            cat_doc = db.collection('categorias').document(producto['id_categoria']).get()
            producto['categoria'] = cat_doc.to_dict().get('nombre', '') if cat_doc.exists else ''
        productos.append(producto)
    return jsonify(productos)

@app.route('/productos', methods=['POST'])
def agregar_producto():
    data = request.json
    if not data.get('nombre') or not data.get('precio') or not data.get('id_categoria'):
        return jsonify({"error": "nombre, precio e id_categoria son requeridos"}), 400
    cat_doc = db.collection('categorias').document(data['id_categoria']).get()
    if not cat_doc.exists:
        return jsonify({"error": "La categoría especificada no existe"}), 400
    doc_ref = db.collection('productos').add({
        'nombre': data['nombre'],
        'precio': float(data['precio']),
        'id_categoria': data['id_categoria']
    })
    return jsonify({"mensaje": "Producto creado", "id": doc_ref[1].id})

@app.route('/productos/<string:id>', methods=['PUT'])
def editar_producto(id):
    data = request.json
    prod_ref = db.collection('productos').document(id)
    if not prod_ref.get().exists:
        return jsonify({"error": "Producto no encontrado"}), 404
    cat_doc = db.collection('categorias').document(data['id_categoria']).get()
    if not cat_doc.exists:
        return jsonify({"error": "La categoría especificada no existe"}), 400
    prod_ref.update({
        'nombre': data['nombre'],
        'precio': float(data['precio']),
        'id_categoria': data['id_categoria']
    })
    return jsonify({"mensaje": "Producto actualizado"})

@app.route('/productos/<string:id>', methods=['DELETE'])
def eliminar_producto(id):
    pedidos = db.collection('pedidos').where('id_producto', '==', id).get()
    if len(pedidos) > 0:
        return jsonify({"error": "No se puede eliminar, el producto tiene pedidos asociados"}), 400
    db.collection('productos').document(id).delete()
    return jsonify({"mensaje": "Producto eliminado"})

# =========================
# PEDIDOS CRUD
# =========================
@app.route('/pedidos', methods=['GET'])
def listar_pedidos():
    pedidos = []
    docs = db.collection('pedidos').stream()
    for doc in docs:
        pedido = doc.to_dict()
        pedido['id'] = doc.id
        if pedido.get('id_usuario'):
            u_doc = db.collection('usuarios').document(pedido['id_usuario']).get()
            pedido['usuario'] = u_doc.to_dict().get('nombre', '') if u_doc.exists else ''
        if pedido.get('id_producto'):
            p_doc = db.collection('productos').document(pedido['id_producto']).get()
            pedido['producto'] = p_doc.to_dict().get('nombre', '') if p_doc.exists else ''
        pedidos.append(pedido)
    return jsonify(pedidos)

@app.route('/pedidos', methods=['POST'])
def agregar_pedido():
    data = request.json
    if not data.get('id_usuario') or not data.get('id_producto') or not data.get('cantidad'):
        return jsonify({"error": "id_usuario, id_producto y cantidad son requeridos"}), 400
    u_doc = db.collection('usuarios').document(data['id_usuario']).get()
    if not u_doc.exists:
        return jsonify({"error": "El usuario especificado no existe"}), 400
    p_doc = db.collection('productos').document(data['id_producto']).get()
    if not p_doc.exists:
        return jsonify({"error": "El producto especificado no existe"}), 400
    if int(data['cantidad']) <= 0:
        return jsonify({"error": "La cantidad debe ser mayor a 0"}), 400
    doc_ref = db.collection('pedidos').add({
        'id_usuario': data['id_usuario'],
        'id_producto': data['id_producto'],
        'cantidad': int(data['cantidad']),
        'fecha': firestore.SERVER_TIMESTAMP
    })
    return jsonify({"mensaje": "Pedido creado", "id": doc_ref[1].id})

@app.route('/pedidos/<string:id>', methods=['PUT'])
def editar_pedido(id):
    data = request.json
    pedido_ref = db.collection('pedidos').document(id)
    if not pedido_ref.get().exists:
        return jsonify({"error": "Pedido no encontrado"}), 404
    u_doc = db.collection('usuarios').document(data['id_usuario']).get()
    if not u_doc.exists:
        return jsonify({"error": "El usuario especificado no existe"}), 400
    p_doc = db.collection('productos').document(data['id_producto']).get()
    if not p_doc.exists:
        return jsonify({"error": "El producto especificado no existe"}), 400
    if int(data['cantidad']) <= 0:
        return jsonify({"error": "La cantidad debe ser mayor a 0"}), 400
    pedido_ref.update({
        'id_usuario': data['id_usuario'],
        'id_producto': data['id_producto'],
        'cantidad': int(data['cantidad'])
    })
    return jsonify({"mensaje": "Pedido actualizado"})

@app.route('/pedidos/<string:id>', methods=['DELETE'])
def eliminar_pedido(id):
    db.collection('pedidos').document(id).delete()
    return jsonify({"mensaje": "Pedido eliminado"})

# =========================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
