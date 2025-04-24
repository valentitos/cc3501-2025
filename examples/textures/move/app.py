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


# este ejemplo muestra como editar dinamicamente los valores UV en el vertex shader
# para simular un desplazamiento
# esto produce que se elijan diferentes puntos UV en cada frame del renderizado


if __name__ == "__main__":
    width = 600
    height = 600

    window = pyglet.window.Window(width, height)

    # Creamos cuadrilatero para colocar las texturas

    quad_tex = dr.Model(sp.Square["position"], sp.Square['uv'], index_data=sp.Square["indices"])

    # "dibujisticamente", el cuadrilatero queda:

    # UV( 0, 1)                 UV( 1, 1)  
    # XY(-0.5,  0.5)            XY( 0.5,  0.5)
    #               *-----------*
    #               |           |
    #               |           |
    #               |           |
    #               |           |
    #               *-----------*
    # XY(-0.5,  -0.5)           XY( 0.5,  -0.5)   
    # UV( 0,  0)                 UV( 1,  0) 

    # lo interesante es que como la textura del ladrillo (y practicamente cualquier otra textura)
    # está definida dentro del intervalo UV [0,1], entonces hay que ver que ocurre al ir 
    # editando dinamicamente las coordenadas UV asociadas a los vertices de la figura

    with open(Path(os.path.dirname(__file__))/ "uv_edit_vextex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__))/ "simple_fragment_program.glsl") as f:
        fragment_source_code = f.read()

    #Se define el pipeline
    vert_program = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    move_pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    # creamos el grafo de escena 
    # ----------------------------------
    
    graph = sg.SceneGraph()

    graph.add_node("move_scene", 
        transform=tr.identity()
    )

    # dibujamos un cuadrilatero con textura de ladrillos
    graph.add_node("move1",
        attach_to = "move_scene",
        mesh = quad_tex,
        pipeline = move_pipeline,
        transform = tr.identity(),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / "bricks.jpg",
            sWrapMode=GL.GL_REPEAT,
            tWrapMode=GL.GL_REPEAT,
            minFilterMode=GL.GL_NEAREST,
            maxFilterMode=GL.GL_NEAREST,
        ),
    )

    # ----------------------------------

    # speed -> cuantos frames por segundo queremos mostrar?
    move_pipeline["speed"] = 0.5


    # configuración del programa.
    # view y projection no se utilizan en realidad, al ser un ejemplo 2D
    # pero se dejan de todos modos
    window.program_state = {
        "scene_graph": graph,
        "draw_mode": True,
        "tex_source": ["bricks.jpg", "boo.png", "question_box.png", "fox.jpg"],
        "tex_index": 0,
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
        #move_pipeline.use()
        #move_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        #move_pipeline["projection"] = window.program_state["projection"].reshape(16, 1, order="F")

        # le pasamos al vertex shader el tiempo actual
        move_pipeline['time'] = window.program_state["total_time"]

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
            
            # al presionar X, cambia la textura por la siguiente registrada en la lista
            tex_index = (window.program_state['tex_index'] + 1)%len(window.program_state['tex_source'])
            new_tex = window.program_state['tex_source'][tex_index]
            window.program_state['tex_index'] = tex_index
            
            graph["move1"]["texture"] = sg.Texture(Path(os.path.dirname(__file__)) / new_tex,
                sWrapMode=GL.GL_REPEAT,
                tWrapMode=GL.GL_REPEAT,
                minFilterMode=GL.GL_NEAREST,
                maxFilterMode=GL.GL_NEAREST,
            )
            
            print(new_tex)

    pyglet.clock.schedule_interval(update, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
