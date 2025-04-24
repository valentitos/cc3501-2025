import os.path
import sys
from pathlib import Path

import numpy as np
import pyglet
import pyglet.gl as GL
import trimesh as tm

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__))))))
)

import grafica.transformations as tr
import utils.scene_graph as sg
import utils.helpers as hp
import utils.drawables as dr
import utils.shapes as sp

# este ejemplo muestra como aplicar una textura sobre un cuadrilatero
# y además muestra que es lo que ocurre al usar los filtros GL_LINEAR y GL_NEAREST
# Además muestra el orden en que se dibujan distintos elementos en pantalla al estár en 2D

if __name__ == "__main__":
    width = 600
    height = 600

    window = pyglet.window.Window(width, height)

    # Creamos un cuadrilatero base para colocar las texturas
    # más adelante, escalaremos uno de ellos para que tenga forma rectangular, y podamos tener varios
    # cubos de preguntas uno al lado del otro

    # en el caso del fantasma, usamos un cuadrilatero sin modificar
    quad_boo = dr.Model(sp.Square["position"], sp.Square["uv"], index_data=sp.Square["indices"])

    # En el caso de los bloques, cambiaremos sus coordenadas UV, para que vayan en el rango
    # [0, 10] (y así más adelante rellenar su superficie con 10 texturas repetidas)

    # las coordenadas XYZ, y UV del modelo pre-definido son las siguientes:
    # 'position': [             |   'uv': [
    #     -0.5, -0.5, 0.0,      |       0, 0,
    #      0.5, -0.5, 0.0,      |       1, 0,
    #      0.5,  0.5, 0.0,      |       1, 1,
    #     -0.5,  0.5, 0.0       |       0, 1
    #  ],                       |   ],

    # lo que hace el código simplificado de abajo es convertir los 1s en 10s en el arreglo UV, pero solo de
    # la coordenada X
    new_uv = [x * 10 if i % 2 == 0 else x for i, x in enumerate(sp.Square["uv"])]
    quad_question = dr.Model(sp.Square["position"], new_uv, index_data=sp.Square["indices"])

    # UV( 0, 1)                 UV( 10, 1)  
    # XY(-0.5,  0.5)            XY( 0.5,  0.5)
    #               *-----------*
    #               |           |
    #               |           |
    #               |           |
    #               |           |
    #               *-----------*
    # XY(-0.5,  -0.5)           XY( 0.5,  -0.5)   
    # UV( 0,  0)                UV( 10,  0) 

    # lo interesante es que como la textura del bloque (y practicamente cualquier otra textura)
    # está definida dentro del intervalo UV [0,1], entonces hay que ver que ocurre al intentar 
    # mapear esa textura en el espacio de la figura con UV en el rango [0, 10] horizontal
    # mas adelante veremos que produce el efecto de que la textura del bloque se rellena 10
    # veces en el espacio definido por el cuadrilatero (y más adelante en el grafo, se escala
    # para que no pierda las proporciones)


    with open(Path(os.path.dirname(__file__))/ "simple_vextex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__))/ "simple_fragment_program.glsl") as f:
        fragment_source_code = f.read()

    #Se define el pipeline
    vert_program = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    boo_pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    # creamos el grafo de escena 
    # ----------------------------------
    
    graph = sg.SceneGraph()

    graph.add_node("boo_scene", 
        transform=tr.identity()
    )

    # ojo: si no usamos nodos "administradores" de geometria (como en el ejemplo de los planetas), 
    # las transformaciones iniciales que apliquemos acá, deben ser re-administradas en el ciclo de update del programa
    # si es que el nodo va a tener movimiento.
    # (o bien, aplicar adecuadamente las propiedades de position, rotation y scale al momento de crear el nodo
    # del grafo)

    # además, en 2D, si no especificamos z-depth, el orden de dibujo es:
    # lo primero que se dibuja en el grafo, va más adelante en la pantalla

    # fantasma con filtro GL_NEAREST
    graph.add_node("boo",
        attach_to = "boo_scene",
        mesh = quad_boo,
        pipeline = boo_pipeline,
        transform= (
            tr.scale(0.5, 0.5, 1.0)
        ),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / "boo.png",
            sWrapMode=GL.GL_REPEAT,
            tWrapMode=GL.GL_REPEAT,
            minFilterMode=GL.GL_NEAREST,
            maxFilterMode=GL.GL_NEAREST,
        ),
        cull_face= False,
    )
    # cull_face -> si al dibujar el objeto "al reves", se descarte o no

    # fantasma con filtro GL_LINEAR
    graph.add_node("boo2",
        attach_to = "boo_scene",
        mesh = quad_boo,
        pipeline = boo_pipeline,
        transform= (
            tr.scale(0.5, 0.5, 1.0)
            @ tr.translate(0.0, 0.6, 0.0),
        ),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / "boo.png",
            sWrapMode=GL.GL_REPEAT,
            tWrapMode=GL.GL_REPEAT,
            minFilterMode=GL.GL_LINEAR,
            maxFilterMode=GL.GL_LINEAR,
        ),
        cull_face= False,
    )

    # mini fantasma antes de las cajas
    graph.add_node("mini_boo1",
        attach_to = "boo_scene",
        mesh = quad_boo,
        pipeline = boo_pipeline,
        transform= (
            tr.translate(-0.4, -0.4, 0)
            @ tr.scale(0.2, 0.2, 1)
        ),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / "boo.png",
            sWrapMode=GL.GL_REPEAT,
            tWrapMode=GL.GL_REPEAT,
            minFilterMode=GL.GL_NEAREST,
            maxFilterMode=GL.GL_NEAREST,
        ),
        cull_face= False,
    )

    # cajas con filtro GL_NEAREST
    graph.add_node("qbox",
        attach_to = "boo_scene",
        mesh = quad_question,
        pipeline = boo_pipeline,
        transform= (
            tr.translate(0, -0.7, 0)
            @ tr.scale(2, 0.2, 1)
        ),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / "question_box.png",
            sWrapMode=GL.GL_REPEAT,
            tWrapMode=GL.GL_REPEAT,
            minFilterMode=GL.GL_NEAREST,
            maxFilterMode=GL.GL_NEAREST,
        ),
        cull_face= False,
    )

    # cajas con filtro GL_LINEAR
    # que pasaría si se comenta la linea que escala esta figura?
    graph.add_node("qbox2",
        attach_to = "boo_scene",
        mesh = quad_question,
        pipeline = boo_pipeline,
        transform= (
            tr.translate(0, -0.5, 0)
            @ tr.scale(2, 0.2, 1)
        ),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / "question_box.png",
            sWrapMode=GL.GL_REPEAT,
            tWrapMode=GL.GL_REPEAT,
            minFilterMode=GL.GL_LINEAR,
            maxFilterMode=GL.GL_LINEAR,
        ),
        cull_face= False,
    )

    # mini fantasma detras de las cajas
    graph.add_node("mini_boo2",
        attach_to = "boo_scene",
        mesh = quad_boo,
        pipeline = boo_pipeline,
        transform= (
            tr.translate(0.4, -0.4, 0)
            @ tr.scale(0.2, 0.2, 1)
        ),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / "boo.png",
            sWrapMode=GL.GL_REPEAT,
            tWrapMode=GL.GL_REPEAT,
            minFilterMode=GL.GL_NEAREST,
            maxFilterMode=GL.GL_NEAREST,
        ),
        cull_face= False,
    )
    

    # ----------------------------------
    # como estamos en 2D, no es necesario configurar la camara ni la proyección
    window.program_state = {
        "scene_graph": graph,
        "draw_mode": True,
        "total_time": 0.0,
        "view": tr.lookAt(
            np.array([0, 0, 3]), # eye
            np.array([0, 0, 0]), # at
            np.array([0, 1, 0])  # up
        ),
        "projection": tr.perspective(45, float(width) / float(height), 0.1, 100),
    }


    @window.event
    def on_draw():
        GL.glClearColor(0.25, 0.25, 0.25, 1.0)
        GL.glLineWidth(2.0)

        if window.program_state["draw_mode"]:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        else:
            GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_LINE)

        
        GL.glEnable(GL.GL_DEPTH_TEST)
        
        # habilitar transparencia
        GL.glEnable(GL.GL_BLEND)
        GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
        window.clear()

        # configuramos la vista y proyección de los pipelines
        #boo_pipeline.use()
        #boo_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        #boo_pipeline["projection"] = window.program_state["projection"].reshape(16, 1, order="F")

        graph.draw()

    # esta función actualiza el grafo de escena en función del tiempo
    # en este caso, hace algo similar a lo que hemos hecho en ejemplos anteriores
    # al asignar movimiento que dependen del tiempo transcurrido en el programa
    def update(dt, window):
        window.program_state["total_time"] += dt
        total_time = window.program_state["total_time"]

        # animación de movimiento de los fantasmas en función del tiempo
        tx = 0.7 * np.sin(0.5 * total_time)
        ty = 0.2 * np.sin(5 * total_time)

        # reflex nos ayuda a "espejar" la figura, para 
        # mostrar que se mueve en la otra dirección
        # en particular, la textura tambien se refleja
        dtx = 0.7 * 0.5 * np.cos(0.5 * total_time)
        if dtx > 0:
            reflex = tr.identity()
        else:
            reflex = tr.scale(-1, 1, 1) 

        graph["boo"]["transform"] = (
            tr.translate(tx, ty, 0) 
            @ tr.scale(0.5, 0.5, 1.0)
            @ reflex
        )

        graph["boo2"]["transform"] = (
            tr.translate(0.0, 0.6, 0.0)
            @ tr.translate(tx, ty, 0) 
            @ tr.scale(0.5, 0.5, 1.0)
            @ reflex
        )

        graph.update()

    @window.event
    def on_key_press(symbol, modifiers):
        
        if symbol == pyglet.window.key.SPACE: 
            window.program_state["draw_mode"] = not window.program_state["draw_mode"]

    pyglet.clock.schedule_interval(update, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
