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


# este programa muestra como aplicar una textura sobre distintas superficies
# en particular, como hay que especificar las coordenadas UV en los vertices/caras de una
# figura 3D, para aplicar distintos "recortes" de las texturas a las distintas caras de la figura



if __name__ == "__main__":
    width = 600
    height = 600

    window = pyglet.window.Window(width, height)

    # Creamos un cuadrilatero para colocar las texturas

    # como nuestra textura almacena las 6 caras del dado, tenemos que "mapear"
    # manualmente que partes de la textura le corresponden a cada cada del dado.
    # por cada 4 vertices que definen una cara del cuadrilatero, definimos 4
    # pares de coordenadas UV.
    # Estas coordenadas representan el "recorte" de textura que le corresponderá 
    # a cada cara.
    new_uv = [0, 1/3, 1/2, 1/3, 1/2, 0, 0, 0,       # cara 1
              1/2, 1, 1, 1, 1, 2/3, 1/2, 2/3,       # cara 2
              0, 1, 1/2, 1, 1/2, 2/3, 0, 2/3,       # cara 3
              1/2, 1/3, 1, 1/3, 1, 0, 1/2, 0,       # cara 4
              1/2, 2/3, 1, 2/3, 1, 1/3, 1/2, 1/3,   # cara 5
              0, 2/3, 1/2, 2/3, 1/2, 1/3, 0, 1/3    # cara 6
            ]
    
    # revisen en detalle la definición del modelo del cubo, definida en shapes -> cube,
    # para ver cual es la correspondencia entre cada vertice de la figura y el UV definido arriba
    quad_cube = dr.Model(sp.Cube["position"], new_uv, index_data=sp.Cube["indices"])

    with open(Path(os.path.dirname(__file__))/ "simple_vextex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__))/ "simple_fragment_program.glsl") as f:
        fragment_source_code = f.read()

    #Se define el pipeline
    vert_program = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    quad_pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    # creamos el grafo de escena 
    # ----------------------------------
    
    graph = sg.SceneGraph()

    graph.add_node("dice_scene", 
        transform=tr.identity()
    )

    graph.add_node("dice",
        attach_to = "dice_scene",
        mesh = quad_cube,
        pipeline = quad_pipeline,
        texture = sg.Texture(Path(os.path.dirname(__file__)) / "dice.jpg",
            sWrapMode=GL.GL_REPEAT,
            tWrapMode=GL.GL_REPEAT,
            minFilterMode=GL.GL_NEAREST,
            maxFilterMode=GL.GL_NEAREST,
        ),
        cull_face= False,
    )

    # ----------------------------------

    window.program_state = {
        "scene_graph": graph,
        "draw_mode": True,
        "dice_state": "WHITE",
        "total_time": 0.0,
        "view": tr.lookAt(
            np.array([2, 2, 2]), # eye
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
        quad_pipeline.use()
        quad_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        quad_pipeline["projection"] = window.program_state["projection"].reshape(16, 1, order="F")

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

        # si presionamos las teclas C, V o B, podemos rotar el cubo en alguno de sus ejes
        if symbol == pyglet.window.key.C:
            graph["dice"]["transform"] = (
                tr.rotationX(np.pi/6)
                @ graph["dice"]["transform"]
            )

        if symbol == pyglet.window.key.V:
            graph["dice"]["transform"] = (
                tr.rotationY(np.pi/6)
                @ graph["dice"]["transform"]
            )
        if symbol == pyglet.window.key.B:
            graph["dice"]["transform"] = (
                tr.rotationZ(np.pi/6)
                @ graph["dice"]["transform"]
            )

        if symbol == pyglet.window.key.X:
            if window.program_state["dice_state"] == "WHITE":
                new_dice_file = "dice_blue.jpg"
                window.program_state["dice_state"] = "BLUE"
            elif window.program_state["dice_state"] == "BLUE":
                new_dice_file = "dice_wire.jpg"
                window.program_state["dice_state"] = "WIRE"
            elif window.program_state["dice_state"] == "WIRE":
                # bonus: tambien podemos colocar texturas que no sean un dado
                # en este caso, hay que tener en cuenta que como la textura de ladrillo
                # no es "rectangular" como la de los dados, los trozos de textura que se
                # mapeen finalmente a las caras puede que no sean "perfectos"
                new_dice_file = "bricks.jpg"
                window.program_state["dice_state"] = "BRICKS"
            elif window.program_state["dice_state"] == "BRICKS":
                # bonus2: tambien podemos colocar una textura de un dibujo o escena
                # podemos ver que "trocitos" de la imagen son mapeados en distintas
                # partes del cubo
                new_dice_file = "fox.jpg"
                window.program_state["dice_state"] = "FOX"
            elif window.program_state["dice_state"] == "FOX":
                new_dice_file = "dice.jpg"
                window.program_state["dice_state"] = "WHITE"
            
            # reconfiguramos la textura asociada dependiendo del estado del programa
            graph["dice"]["texture"] = sg.Texture(Path(os.path.dirname(__file__)) / new_dice_file,
                sWrapMode=GL.GL_REPEAT,
                tWrapMode=GL.GL_REPEAT,
                minFilterMode=GL.GL_NEAREST,
                maxFilterMode=GL.GL_NEAREST,
            )
            print(window.program_state["dice_state"])        
        

    pyglet.clock.schedule_interval(update, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
