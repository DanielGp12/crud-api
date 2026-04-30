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
# ROLES
# =========================
@app.route('/roles', methods=['GET'])
def listar_roles():
    roles = []
    for doc in db.collection('roles').stream():
        r = doc.to_dict()
        r['id'] = doc.id
        roles.append(r)
    return jsonify(roles)

@app.route('/roles', methods=['POST'])
def agregar_rol():
    data = request.json
    if not data.get('nombre'):
        return jsonify({"error": "El nombre es requerido"}), 400

    existente = db.collection('roles').where('nombre', '==', data['nombre']).get()
    if existente:
        return jsonify({"error": "El rol ya existe"}), 400

    doc_ref = db.collection('roles').document()
    doc_ref.set({'nombre': data['nombre']})

    return jsonify({"mensaje": "Rol creado", "id": doc_ref.id})

# =========================
# USUARIOS
# =========================
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    usuarios = []
    for doc in db.collection('usuarios').stream():
        u = doc.to_dict()
        u['id'] = doc.id

        if u.get('id_rol'):
            rol_doc = db.collection('roles').document(str(u['id_rol'])).get()
            u['rol'] = rol_doc.to_dict().get('nombre', '') if rol_doc.exists else ''

        usuarios.append(u)

    return jsonify(usuarios)

@app.route('/usuarios', methods=['POST'])
def agregar_usuario():
    data = request.json

    if not data.get('nombre') or not data.get('email') or not data.get('id_rol'):
        return jsonify({"error": "nombre, email e id_rol son requeridos"}), 400

    id_rol = str(data['id_rol'])

    rol_doc = db.collection('roles').document(id_rol).get()
    if not rol_doc.exists:
        return jsonify({"error": "El rol no existe"}), 400

    existente = db.collection('usuarios').where('email', '==', data['email']).get()
    if existente:
        return jsonify({"error": "El email ya existe"}), 400

    doc_ref = db.collection('usuarios').document()
    doc_ref.set({
        'nombre': data['nombre'],
        'email': data['email'],
        'id_rol': id_rol
    })

    return jsonify({"mensaje": "Usuario creado", "id": doc_ref.id})

# =========================
# CATEGORIAS
# =========================
@app.route('/categorias', methods=['GET'])
def listar_categorias():
    categorias = []
    for doc in db.collection('categorias').stream():
        c = doc.to_dict()
        c['id'] = doc.id
        categorias.append(c)
    return jsonify(categorias)

@app.route('/categorias', methods=['POST'])
def agregar_categoria():
    data = request.json

    if not data.get('nombre'):
        return jsonify({"error": "El nombre es requerido"}), 400

    existente = db.collection('categorias').where('nombre', '==', data['nombre']).get()
    if existente:
        return jsonify({"error": "Ya existe"}), 400

    doc_ref = db.collection('categorias').document()
    doc_ref.set({'nombre': data['nombre']})

    return jsonify({"mensaje": "Categoria creada", "id": doc_ref.id})

# =========================
# PRODUCTOS
# =========================
@app.route('/productos', methods=['POST'])
def agregar_producto():
    data = request.json

    if not data.get('nombre') or not data.get('precio') or not data.get('id_categoria'):
        return jsonify({"error": "datos incompletos"}), 400

    id_categoria = str(data['id_categoria'])

    cat_doc = db.collection('categorias').document(id_categoria).get()
    if not cat_doc.exists:
        return jsonify({"error": "Categoría no existe"}), 400

    doc_ref = db.collection('productos').document()
    doc_ref.set({
        'nombre': data['nombre'],
        'precio': float(data['precio']),
        'id_categoria': id_categoria
    })

    return jsonify({"mensaje": "Producto creado", "id": doc_ref.id})

# =========================
# PEDIDOS
# =========================
@app.route('/pedidos', methods=['POST'])
def agregar_pedido():
    data = request.json

    id_usuario = str(data['id_usuario'])
    id_producto = str(data['id_producto'])

    u_doc = db.collection('usuarios').document(id_usuario).get()
    if not u_doc.exists:
        return jsonify({"error": "Usuario no existe"}), 400

    p_doc = db.collection('productos').document(id_producto).get()
    if not p_doc.exists:
        return jsonify({"error": "Producto no existe"}), 400

    if int(data['cantidad']) <= 0:
        return jsonify({"error": "Cantidad inválida"}), 400

    doc_ref = db.collection('pedidos').document()
    doc_ref.set({
        'id_usuario': id_usuario,
        'id_producto': id_producto,
        'cantidad': int(data['cantidad']),
        'fecha': firestore.SERVER_TIMESTAMP
    })

    return jsonify({"mensaje": "Pedido creado", "id": doc_ref.id})

# =========================
if __name__ == '__main__':
    app.run(debug=True, port=5000)
