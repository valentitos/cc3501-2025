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
# y además muestra que es lo que ocurre al usar los métodos GL_REPEAT y GL_CLAMP
# cuando las coordenadas UV se encuentran fuera del rango [0,1]


if __name__ == "__main__":
    width = 600
    height = 600

    window = pyglet.window.Window(width, height)

    # Creamos cuadrilatero para colocar las texturas
    # en particular, definiremos que sus vertices queden asociados a las coordenadas UV
    # [0,0] [0,2], [2,0] y [2,2], para mostrar que ocurre con la textura cuando
    # se enfrenta a valores fuera del rango [0,1]

    # las coordenadas XYZ, y UV del modelo pre-definido son las siguientes:
    # 'position': [             |   'uv': [
    #     -0.5, -0.5, 0.0,      |       0, 0,
    #      0.5, -0.5, 0.0,      |       1, 0,
    #      0.5,  0.5, 0.0,      |       1, 1,
    #     -0.5,  0.5, 0.0       |       0, 1
    #  ],                       |   ],

    # lo que hace el código simplificado de abajo es convertir los 1s en 2s en el arreglo UV

    new_uv = [x * 2 for i, x in enumerate(sp.Square["uv"])]
    quad_brick = dr.Model(sp.Square["position"], new_uv, index_data=sp.Square["indices"])

    # "dibujisticamente", el cuadrilatero queda:

    # UV( 0, 2)                 UV( 2, 2)  
    # XY(-0.5,  0.5)            XY( 0.5,  0.5)
    #               *-----------*
    #               |           |
    #               |           |
    #               |           |
    #               |           |
    #               *-----------*
    # XY(-0.5,  -0.5)           XY( 0.5,  -0.5)   
    # UV( 0,  0)                 UV( 2,  0) 

    # lo interesante es que como la textura del ladrillo (y practicamente cualquier otra textura)
    # está definida dentro del intervalo UV [0,1], entonces hay que ver que ocurre al intentar 
    # mapear esa textura en el espacio de la figura con UV en el rango [0,2]

    with open(Path(os.path.dirname(__file__))/ "simple_vextex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__))/ "simple_fragment_program.glsl") as f:
        fragment_source_code = f.read()

    # cargamos un 2° fragment, para mostrar que pasa si no se extiende la textura
    with open(Path(os.path.dirname(__file__))/ "discarduv_fragment_program.glsl") as f:
        fragment_d_source_code = f.read()

    #Se define el pipeline
    vert_program = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    brick_pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    frag_d_program = pyglet.graphics.shader.Shader(fragment_d_source_code, "fragment")
    brick_d_pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_d_program)


    # creamos el grafo de escena 
    # ----------------------------------
    
    graph = sg.SceneGraph()

    graph.add_node("brick_scene", 
        transform=tr.identity()
    )

    # dibujamos un cuadrilatero con textura de ladrillos
    graph.add_node("brick1",
        attach_to = "brick_scene",
        mesh = quad_brick,
        pipeline = brick_d_pipeline,
        transform = tr.identity(),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / "bricks.jpg",
            sWrapMode=GL.GL_CLAMP_TO_EDGE,
            tWrapMode=GL.GL_CLAMP_TO_EDGE,
            minFilterMode=GL.GL_LINEAR,
            maxFilterMode=GL.GL_LINEAR,
        ),
    )

    # ----------------------------------

    # configuración del programa.
    # view y projection no se utilizan en realidad, al ser un ejemplo 2D
    # pero se dejan de todos modos
    window.program_state = {
        "scene_graph": graph,
        "draw_mode": True,
        "tex_mode": "NO_REPEAT",
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
        #brick_pipeline.use()
        brick_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        brick_pipeline["projection"] = window.program_state["projection"].reshape(16, 1, order="F")
        
        # en el caso de sceneGraph, como cada nodo tiene asociado su pipeline,
        # draw se encarga de invocar el pipeline de cada nodo antes de dibujar
        graph.draw()


    # esta función actualiza el grafo de escena en función del tiempo
    def update(dt, window):
        window.program_state["total_time"] += dt
        total_time = window.program_state["total_time"]

        graph.update()


    @window.event
    def on_key_press(symbol, modifiers):
        
        if symbol == pyglet.window.key.SPACE: 
            window.program_state["draw_mode"] = not window.program_state["draw_mode"]

        if symbol == pyglet.window.key.X:

            actual_draw_mode = window.program_state["tex_mode"]
            
            # Ojo: openGL siempre intenta hacer "algo" con las coordenadas UV fuera del rango [0,1]
            # por lo que no existe un modo NO_REPEAT o similar
            # si queremos emularlo, tenemos que descartar los UV fuera de rango en el fragment_shader              
            # lo que podemos lograr cambiando el pipeline de dibujo
            # obviamente siempre lo mejor es que nuestras figuras tengan bien definidas
            # sus coordendas de textura dentro del rango [0,1]

            if actual_draw_mode == "NO_REPEAT":
                new_draw_mode = GL.GL_REPEAT
                new_pipeline = brick_pipeline
                window.program_state["tex_mode"] = "REPEAT"
            elif actual_draw_mode == "REPEAT":
                new_draw_mode = GL.GL_CLAMP_TO_EDGE
                new_pipeline = brick_pipeline
                window.program_state["tex_mode"] = "CLAMP"
            elif actual_draw_mode == "CLAMP":
                new_draw_mode = GL.GL_REPEAT
                new_pipeline = brick_d_pipeline
                window.program_state["tex_mode"] = "NO_REPEAT"
            
            graph["brick1"]["texture"] = sg.Texture(Path(os.path.dirname(__file__)) / "bricks.jpg",
                sWrapMode=new_draw_mode,
                tWrapMode=new_draw_mode,
                minFilterMode=GL.GL_LINEAR,
                maxFilterMode=GL.GL_LINEAR,
            )
            graph["brick1"]["pipeline"] = new_pipeline
            print(window.program_state["tex_mode"])

    pyglet.clock.schedule_interval(update, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
