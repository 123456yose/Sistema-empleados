import pymysql
pymysql.install_as_MySQLdb()
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_mysqldb import MySQL
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "ClaveSecreta"
mysql = MySQL()

app.config['MYSQL_DATABASE_HOST'] = 'localhost'
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = ''
app.config['MYSQL_DATABASE_DB'] = 'sistema2'
mysql.init_app(app)

CARPETA = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'uploads')
app.config['CARPETA'] = CARPETA

@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
    return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/')
def index():
    with mysql.connection.cursor() as cursor:
        sql = "SELECT * FROM `sistema2`.`empleados`;"
        cursor.execute(sql)
        empleados = cursor.fetchall()
    return render_template('empleados/index.html', empleados=empleados)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        _nombre = request.form['txtNombre']
        _correo = request.form['txtCorreo']
        _foto = request.files['txtFoto']

        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")
        
        # Inicializamos nuevoNombreFoto
        nuevoNombreFoto = None

        if _foto.filename != '':
            nuevoNombreFoto = tiempo + '_' + _foto.filename
            _foto.save(os.path.join(app.config['CARPETA'], nuevoNombreFoto))

        # Aseguramos que siempre hay un valor para nuevoNombreFoto
        if nuevoNombreFoto is None:
            nuevoNombreFoto = 'default.jpg'  # Puedes usar un nombre de foto predeterminado

        sql = "INSERT INTO `empleados` (`ID`, `nombre`, `correo`, `foto`) VALUES (NULL, %s, %s, %s);"
        datos = (_nombre, _correo, nuevoNombreFoto)

        with mysql.connection.cursor() as cursor:
            cursor.execute(sql, datos)
            mysql.connection.commit()

        flash('Empleado agregado exitosamente.')
        return redirect(url_for('index'))

    return render_template('empleados/create.html')

@app.route('/destroy/<int:id>')
def destroy(id):
    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT foto FROM `sistema2`.`empleados` WHERE id=%s", (id,))
        fila = cursor.fetchone()

        if fila and fila[0]:
            os.remove(os.path.join(app.config['CARPETA'], fila[0]))

        cursor.execute("DELETE FROM `sistema2`.`empleados` WHERE id=%s", (id,))
        mysql.connection.commit()

    flash('Empleado eliminado correctamente.')
    return redirect('/')

@app.route('/edit/<int:id>')
def edit(id):
    with mysql.connection.cursor() as cursor:
        cursor.execute("SELECT * FROM `sistema2`.`empleados` WHERE id=%s", (id,))
        empleados = cursor.fetchall()

    if not empleados:
        flash('Empleado no encontrado.')
        return redirect(url_for('index'))

    return render_template('empleados/edit.html', empleados=empleados)

@app.route('/update', methods=['POST'])
def update():
    _nombre = request.form['txtNombre']
    _correo = request.form['txtCorreo']
    _foto = request.files['txtFoto']
    ID = request.form['txtID']

    # Inicializamos nuevoNombreFoto
    nuevoNombreFoto = None  

    sql = "UPDATE `sistema2`.`empleados` SET `nombre`=%s, `correo`=%s WHERE id=%s;"
    datos = (_nombre, _correo, ID)

    with mysql.connection.cursor() as cursor:
        cursor.execute(sql, datos)
        mysql.connection.commit()

        now = datetime.now()
        tiempo = now.strftime("%Y%H%M%S")

        if _foto.filename != '':
            nuevoNombreFoto = tiempo + '_' + _foto.filename
            _foto.save(os.path.join(app.config['CARPETA'], nuevoNombreFoto))

            cursor.execute("SELECT foto FROM `sistema2`.`empleados` WHERE id=%s", (ID,))
            fila = cursor.fetchone()

            if fila and fila[0]:
                os.remove(os.path.join(app.config['CARPETA'], fila[0]))

            cursor.execute("UPDATE `sistema2`.`empleados` SET `foto`=%s WHERE id=%s;", (nuevoNombreFoto, ID))
            mysql.connection.commit()

    flash('Empleado actualizado correctamente.')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)

