from flask import Flask, jsonify, request
from flask_cors import CORS
from flasgger import Swagger
import bcrypt
import pymysql.cursors # Importar cursors específicamente para mayor claridad

app = Flask(__name__)
CORS(app)
swagger = Swagger(app)

# Conexión a la base de datos
def conectar(vhost, vuser, vpass, vdb):
    try:
        # Usar DictCursor para obtener resultados como diccionarios con nombres de columna
        # Se ha modificado la contraseña a una cadena vacía ya que el usuario 'root' no tiene contraseña asignada en MySQL.
        conn = pymysql.connect(host=vhost, user=vuser, password='', db=vdb, charset='utf8mb4',
                               cursorclass=pymysql.cursors.DictCursor)
        return conn
    except Exception as ex:
        print(f"Error al conectar a la base de datos: {ex}")
        raise # Volver a levantar la excepción para que el llamador la maneje

# Ruta para consulta general
@app.route("/", methods=['GET'])
def consulta_general():
    """
    consulta general
del baul de contraseñas
    ---
    responses:
      200:
        description: Lista de registros
    """
    try:
        conn = conectar('localhost', 'root', '', 'gestor_contrasena') # Contraseña vacía
        cur = conn.cursor()
        # Seleccionar las columnas con los nombres exactos de la base de datos
        # IMPORTANTE: Asegúrate que estos nombres (Id_baul, Plataforma, Usuario, Clave)
        # coincidan EXACTAMENTE con los de tu tabla en la base de datos, incluyendo mayúsculas y minúsculas.
        cur.execute("SELECT Id_baul, Plataforma, Usuario, Clave FROM Baul")
        datos = cur.fetchall() # Esto ya devuelve una lista de diccionarios debido a DictCursor

        # Mapear los nombres de las columnas de la DB a los nombres de las propiedades esperadas por el frontend
        formatted_data = []
        for row in datos:
            formatted_data.append({
                'password_id': row['Id_baul'],
                'platform': row['Plataforma'],
                'username': row['Usuario'],
                'password_value': row['Clave']
            })
        
        cur.close()
        conn.close()
        return jsonify({'baul': formatted_data, 'mensaje': 'Baul de contraseñas'})
    except Exception as ex:
        # Imprimir el traceback completo para una depuración más detallada
        import traceback
        traceback.print_exc()
        return jsonify({'mensaje': f'Error al consultar el baul de contraseñas: {str(ex)}'})

# Ruta para consulta individual
@app.route("/consulta_individual/<int:password_id>", methods=['GET'])
def consulta_individual(password_id):
    """
    consulta individual
del baul de contraseñas
    ---
    parameters:
      - name: password_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Registro encontrado
    """
    try:
        conn = conectar('localhost', 'root', '', 'gestor_contrasena') # Contraseña vacía
        cur = conn.cursor()
        # Usar el nombre de columna de la DB: Id_baul
        # IMPORTANTE: Asegúrate que el nombre 'Id_baul' coincida EXACTAMENTE con el de tu tabla.
        cur.execute("SELECT Id_baul, Plataforma, Usuario, Clave FROM Baul WHERE Id_baul = %s", (password_id,))
        dato = cur.fetchone() # Esto ya devuelve un diccionario o None

        cur.close()
        conn.close()
        if dato:
            # Mapear los nombres de las columnas de la DB a los nombres de las propiedades esperadas por el frontend
            dato_formato = {
                'password_id': dato['Id_baul'],
                'platform': dato['Plataforma'],
                'username': dato['Usuario'],
                'password_value': dato['Clave']
            }
            return jsonify({'baul': dato_formato, 'mensaje': 'Registro encontrado'})
        else:
            return jsonify({'mensaje': 'Registro no encontrado'})
    except Exception as ex:
        # Imprimir el traceback completo para una depuración más detallada
        import traceback
        traceback.print_exc()
        return jsonify({'mensaje': f'Error al consultar el registro: {str(ex)}'})

# Ruta para registro
@app.route("/registro", methods=['POST'])
def registro():
    """
    Registro nueva
contraseñas
    ---
    parameters:
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            platform:
              type: string
            username:
              type: string
            password_value:
              type: string
    responses:
      200:
        description: Registro exitoso
    """
    try:
        data = request.get_json()
        platform = data['platform']
        username = data['username']
        # Obtener el valor de la contraseña directamente del request
        password_value = data['password_value'] 
        hashed_password = bcrypt.hashpw(password_value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = conectar('localhost', 'root', '', 'gestor_contrasena') # Contraseña vacía
        cur = conn.cursor()
        # Usar los nombres de columna de la DB: Plataforma, Usuario, Clave
        # IMPORTANTE: Asegúrate que estos nombres coincidan EXACTAMENTE con los de tu tabla.
        cur.execute("INSERT INTO Baul (Plataforma, Usuario, Clave) VALUES (%s, %s, %s)",
                    (platform, username, hashed_password))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'mensaje': 'Registro exitoso'})
    except Exception as ex:
        # Imprimir el traceback completo para una depuración más detallada
        import traceback
        traceback.print_exc()
        return jsonify({'mensaje': f'Error al registrar el usuario: {str(ex)}'})

# Ruta para eliminar registro
@app.route("/eliminar/<int:password_id>", methods=['DELETE'])
def eliminar(password_id):
    """
    Eliminar registro
por 
    ---
    parameters:
      - name: password_id
        in: path
        required: true
        type: integer
    responses:
      200:
        description: Registro eliminado exitosamente
    """
    try:
        conn = conectar('localhost', 'root', '', 'gestor_contrasena') # Contraseña vacía
        cur = conn.cursor()
        # Usar el nombre de columna de la DB: Id_baul
        # IMPORTANTE: Asegúrate que el nombre 'Id_baul' coincida EXACTAMENTE con el de tu tabla.
        cur.execute("DELETE FROM Baul WHERE Id_baul = %s", (password_id,))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'mensaje': 'Registro eliminado exitosamente'})
    except Exception as ex:
        # Imprimir el traceback completo para una depuración más detallada
        import traceback
        traceback.print_exc()
        return jsonify({'mensaje': f'Error al eliminar el registro: {str(ex)}'})

# Ruta para actualizar registro
@app.route("/actualizar/<int:password_id>", methods=['PUT'])
def actualizar(password_id):
    """
    Actualizar
registro por 
    ---
    parameters:
      - name: password_id
        in: path
        required: true
        type: integer
      - name: body
        in: body
        required: true
        schema:
          type: object
          properties:
            platform:
              type: string
            username:
              type: string
            password_value:
              type: string
    responses:
      200:
        description: Registro actualizado exitosamente
    """
    try:
        data = request.get_json()
        platform = data['platform']
        username = data['username']
        # Obtener el valor de la contraseña directamente del request
        password_value = data['password_value'] 
        hashed_password = bcrypt.hashpw(password_value.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        conn = conectar('localhost', 'root', '', 'gestor_contrasena') # Contraseña vacía
        cur = conn.cursor()
        # Usar los nombres de columna de la DB: Plataforma, Usuario, Clave, Id_baul
        # IMPORTANTE: Asegúrate que estos nombres coincidan EXACTAMENTE con los de tu tabla.
        cur.execute("UPDATE Baul SET Plataforma = %s, Usuario = %s, Clave = %s WHERE Id_baul = %s",
                    (platform, username, hashed_password, password_id))
        conn.commit()
        cur.close()
        conn.close()
        
        return jsonify({'mensaje': 'Registro actualizado exitosamente'})
    except Exception as ex:
        # Imprimir el traceback completo para una depuración más detallada
        import traceback
        traceback.print_exc()
        return jsonify({'mensaje': f'Error al actualizar el registro: {str(ex)}'})
    
if __name__ == "__main__":
    app.run(debug=True)
