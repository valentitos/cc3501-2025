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

# Este ejemplo muestra las diferencias en el manejo de las texturas al disminuir su tamaño
# aplicando los filtros de minificado:
# - GL_LINEAR_MIPMAP_NEAREST
# - GL_NEAREST_MIPMAP_NEAREST
# - GL_LINEAR_MIPMAP_LINEAR

# Ojo: para que este ejemplo funcione es necesario actualizar las librerias auxiliares:
# utils -> drawables
# grafica -> textures
# las cuales se encuentran disponibles en el repositorio de catedras

# en particular, al usar la libreria auxiliar drawables -> textures, el manejo de los mipmaps es
# automatico (creación y administración) si es que al momento de crear la textura, se le pasa como
# parametro alguno de los filtros de minificado.
# Pueden revisar los detalles de la implementación en OpenGL en el archivo grafica -> textures -> textureWithMipMapSetup

if __name__ == "__main__":
    width = 1024
    height = 1024

    window = pyglet.window.Window(width, height)

    # Creamos cuadrilatero para colocar las texturas
    quad_brick = dr.Model(sp.Square["position"], sp.Square["uv"], index_data=sp.Square["indices"])

    with open(Path(os.path.dirname(__file__))/ "simple_vextex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__))/ "simple_fragment_program.glsl") as f:
        fragment_source_code = f.read()

    #Se define el pipeline
    vert_program = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    wood_pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    # creamos el grafo de escena 
    # ----------------------------------
    
    graph = sg.SceneGraph()

    # seleccionamos la imagen de la textura
    #img_name = "red_woodpecker.jpg"
    #img_name = "Amber.png"
    img_name = "fox.jpg"


    graph.add_node("wood_scene", 
        transform=tr.identity()
    )

    # Superior izquierda: Textura sin modificar
    graph.add_node("wood1",
        attach_to = "wood_scene",
        mesh = quad_brick,
        pipeline = wood_pipeline,
        transform = (
            tr.translate(-0.5, 0.5, 0)
            @ tr.scale(1,1,1)
        ),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / img_name,
            sWrapMode=GL.GL_CLAMP_TO_EDGE,
            tWrapMode=GL.GL_CLAMP_TO_EDGE,
            minFilterMode=GL.GL_LINEAR,
            maxFilterMode=GL.GL_LINEAR,
        ),
    )

    # Superior derecha: Textura con minFilter: GL_LINEAR_MIPMAP_NEAREST
    # costo-efectivo en calidad
    graph.add_node("wood2",
        attach_to = "wood_scene",
        mesh = quad_brick,
        pipeline = wood_pipeline,
        transform = (
            tr.translate(0.5, 0.5, 0)
            @ tr.scale(1,1,1)
        ),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / img_name,
            sWrapMode=GL.GL_CLAMP_TO_EDGE,
            tWrapMode=GL.GL_CLAMP_TO_EDGE,
            minFilterMode=GL.GL_LINEAR_MIPMAP_NEAREST,
            maxFilterMode=GL.GL_LINEAR,
        ),
    )

    # inferior izquierda: Textura con minFilter: GL_NEAREST_MIPMAP_NEAREST
    # rapido, pero no muy bonito
    graph.add_node("wood3",
        attach_to = "wood_scene",
        mesh = quad_brick,
        pipeline = wood_pipeline,
        transform = (
            tr.translate(-0.5, -0.5, 0)
            @ tr.scale(1,1,1)
        ),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / img_name,
            sWrapMode=GL.GL_CLAMP_TO_EDGE,
            tWrapMode=GL.GL_CLAMP_TO_EDGE,
            minFilterMode=GL.GL_NEAREST_MIPMAP_NEAREST,
            maxFilterMode=GL.GL_LINEAR,
        ),
    )

    # inferior derecha: Textura con minFilter: GL_LINEAR_MIPMAP_LINEAR
    # costoso, pero bonito
    graph.add_node("wood4",
        attach_to = "wood_scene",
        mesh = quad_brick,
        pipeline = wood_pipeline,
        transform = (
            tr.translate(0.5, -0.5, 0)
            @ tr.scale(1,1,1)
        ),
        texture = sg.Texture(Path(os.path.dirname(__file__)) / img_name,
            sWrapMode=GL.GL_CLAMP_TO_EDGE,
            tWrapMode=GL.GL_CLAMP_TO_EDGE,
            minFilterMode=GL.GL_LINEAR_MIPMAP_LINEAR,
            maxFilterMode=GL.GL_LINEAR,
        ),
    )

    # ----------------------------------

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
        "draw_scale": 1.0,
    }

    @window.event
    def on_draw():
        GL.glClearColor(0.25, 0.25, 0.25, 1.0)
        GL.glLineWidth(2.0)

        # elegir si ver en modo wireframe o no
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
        #wood_pipeline.use()
        #wood_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        #wood_pipeline["projection"] = window.program_state["projection"].reshape(16, 1, order="F")
        
        graph["wood1"]["pipeline"].use()
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
            pass


        # definimos la acción de achicar los dibujos al presionar tecla abajo
        # y agrandarlos con tecla arriba
        if symbol == pyglet.window.key.UP:

            new_scale = window.program_state["draw_scale"]
            if window.program_state["draw_scale"] < 1.0:
                new_scale = window.program_state["draw_scale"] + 2/60
            
            window.program_state["draw_scale"] = new_scale

            graph['wood1']['transform'] = (
                tr.translate(-0.5, 0.5, 0)
                @ tr.scale(new_scale, new_scale, 1)
            )
            graph['wood2']['transform'] = (
                tr.translate(0.5, 0.5, 0)
                @ tr.scale(new_scale, new_scale, 1)
            )
            graph['wood3']['transform'] = (
                tr.translate(-0.5, -0.5, 0)
                @ tr.scale(new_scale, new_scale, 1)
            )
            graph['wood4']['transform'] = (
                tr.translate(0.5, -0.5, 0)
                @ tr.scale(new_scale, new_scale, 1)
            )

            print("scale:", new_scale)

        if symbol == pyglet.window.key.DOWN:

            new_scale = window.program_state["draw_scale"]
            if window.program_state["draw_scale"] > 0.1:
                new_scale = window.program_state["draw_scale"] - 2/60
            
            window.program_state["draw_scale"] = new_scale

            graph['wood1']['transform'] = (
                tr.translate(-0.5, 0.5, 0)
                @ tr.scale(new_scale, new_scale, 1)
            )
            graph['wood2']['transform'] = (
                tr.translate(0.5, 0.5, 0)
                @ tr.scale(new_scale, new_scale, 1)
            )
            graph['wood3']['transform'] = (
                tr.translate(-0.5, -0.5, 0)
                @ tr.scale(new_scale, new_scale, 1)
            )
            graph['wood4']['transform'] = (
                tr.translate(0.5, -0.5, 0)
                @ tr.scale(new_scale, new_scale, 1)
            )

            print("scale:", new_scale)





    pyglet.clock.schedule_interval(update, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
