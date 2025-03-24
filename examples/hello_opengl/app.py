import pyglet
import pyglet.gl as GL
import trimesh as tm
import numpy as np
import os
from pathlib import Path

if __name__ == "__main__":
    # esta es una ventana de pyglet.
    # le damos la resolución como parámetro
    try:
        # si queremos más calidad visual (a un costo, claro) podemos activar antialiasing en caso de que esté disponible
        #config = pyglet.gl.Config(sample_buffers=1, samples=4)
        #window = pyglet.window.Window(960, 960, config=config)

        # en caso de que se vea una ventana gris, hay que desactivar lo anterior
        window = pyglet.window.Window(960, 960)
    except pyglet.window.NoSuchConfigException:
        # si no está disponible, hacemos una ventana normal
        window = pyglet.window.Window(960, 960)

    # cargaremos el modelo del conejo de Stanford.
    # esta es la versión descargable desde Wikipedia
    # el formato STL es binario!
    bunny = tm.load("assets/Stanford_Bunny.stl")
    
    # no sabemos de qué tamaño es el conejo.
    # y solo podemos dibujar en nuestro cubo de referencia
    # cuyas esquinas son [-1, -1, -1] y [1, 1, 1]
    # trimesh nos facilita manipular la geometría del modelo 3D
    # en este caso:
    # 1) lo movemos hacia el origen, es decir, le restamos el centroide
    bunny.apply_translation(-bunny.centroid)
    # 2) puede ser que sea muy grande (o muy pequeño) para verse en la ventana.
    # así que lo escalamos de acuerdo al tamaño
    # (de acuerdo a la documentación de trimesh, el valor scale es el largo de la arista
    # más grande de la caja que contiene al conejo)
    bunny.apply_scale(2.0 / bunny.scale)

    # el shader de vértices solo lee la posición de cada vértice
    # cada vértice es pintado de color blanco en este shader.
    with open(Path(os.path.dirname(__file__)) / "vertex_program.glsl") as f:
        vertex_source_code = f.read()

    # y el shader de píxeles solo lee el color correspondiente al píxel
    with open(Path(os.path.dirname(__file__)) / "fragment_program.glsl") as f:
        fragment_source_code = f.read()

    vert_shader = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_shader = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    pipeline = pyglet.graphics.shader.ShaderProgram(vert_shader, frag_shader)

    # ahora le entregaremos los datos de nuestro objeto a la GPU
    # afortunadamente trimesh tiene una función que convierte el modelo 3D
    # a la representación adecuada para uso con OpenGL :)
    bunny_vertex_list = tm.rendering.mesh_to_vertexlist(bunny)
    #print(bunny_vertex_list[6])
    # queremos dibujar al conejo con nuestro pipeline.
    # como dibujarlo dependerá de lo que contenga cada shader del pipeline,
    # tenemos que pedirle al pipeline que reserve espacio en la GPU
    # para copiar nuestro conejo a la memoria gráfica

    
    nvertices = bunny_vertex_list[0]
    vertices_index = bunny_vertex_list[3]
    vertices_coord = bunny_vertex_list[4][1]

    bunny_gpu = pipeline.vertex_list_indexed(
        nvertices,
        GL.GL_TRIANGLES,
        vertices_index
    )







    # en el código anterior no se copió la información a la GPU,
    # sino que se reservó espacio en la memoria para almacenar esos datos.
    # aquí los copiamos: directamente asignamos nuestra lista de vértices
    # al contenido del atributo position que recibe el pipeline.
    # este atributo se recibe a nivel de vértice
    # más adelante veremos que hay otro
    bunny_gpu.position[:] = bunny_vertex_list[4][1]

    
    # GAME LOOP
    @window.event
    def on_draw():
        # esta función define el color con el que queda una ventana vacía
        # noten que esto es algo de OpenGL, no de pyglet
        GL.glClearColor(0.5, 0.5, 0.75, 1.0)
        # GL_LINE => Wireframe
        # GL_FILL => pinta el interior de cada triángulo
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)
        GL.glLineWidth(1.0)

        # lo anterior no ejecuta esos cambios en la ventana,
        # más bien, configura OpenGL para cuando se ejecuten instrucciones
        # como la siguiente:
        window.clear()

        # del mismo modo, activamos el pipeline
        # activarlo no implica graficar nada de manera inmediata
        pipeline.use()
        # hasta que le pedimos a bunny_gpu que grafique sus triángulos
        # utilizando el pipeline activo
        bunny_gpu.draw(GL.GL_TRIANGLES)

    # aquí comienza pyglet a ejecutar su loop.
    pyglet.app.run()
    # ¡cuando ejecutemos el programa veremos al conejo en Wireframe!
