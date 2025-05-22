import webbrowser
import threading
import os

from flask import Flask, render_template, request, redirect, url_for, flash
from sistema import SistemaInspeccion

app = Flask(__name__)
app.secret_key = 'clave_secreta'  # necesaria para mostrar mensajes flash

# Instancia del sistema
sistema = SistemaInspeccion(
    "data/ordenes.json",
    "data/sismografos.json",
    "data/empleados.json"
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ordenes')
def ver_ordenes():
    ordenes = sistema.get_ordenes_finalizadas()
    ordenes.sort(key=lambda o: o.fechaHoraFinalizacion)
    return render_template('ordenes.html', ordenes=ordenes)

@app.route('/orden/<int:orden_id>', methods=['GET', 'POST'])
def cerrar_orden(orden_id):
    orden = sistema.get_orden_por_id(orden_id)
    sismografo = sistema.get_sismografo(orden.sismografoAsignado)

    if request.method == 'POST':
        observacion = request.form['observacion']
        motivos = []

        tipos_seleccionados = request.form.getlist("motivo_tipo")
        for tipo in tipos_seleccionados:
            comentario = request.form.get(f"comentario_{tipo}")
            motivos.append({
                "comentario": comentario,
                "motivoTipo": tipo
            })

        sistema.cerrar_orden(orden_id, observacion, motivos)
        flash('Orden cerrada correctamente.', 'success')
        return redirect(url_for('ver_ordenes'))

    # Este bloque se ejecuta para método GET o si hubo error en POST
    motivos_tipo = sistema.get_motivos_fuera_servicio()
    return render_template('cerrar_orden.html', orden=orden, motivos_tipo=motivos_tipo)



if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        threading.Timer(1, lambda: webbrowser.open_new("http://localhost:5000")).start()
    app.run(debug=True)