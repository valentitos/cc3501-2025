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


# ejemplo que muestra los distintos modos de iluminación
# en un cubo con texturas


if __name__ == "__main__":
    width = 800
    height = 800

    window = pyglet.window.Window(width, height)


    draw_model = dr.Model(sp.Cube["position"], sp.Cube["uv"], normal_data=sp.Cube['normal'], index_data=sp.Cube["indices"])

    # ------------------------
    # pipeline FLAT

    with open(Path(os.path.dirname(__file__)) / "simple_tex_flat_vertex_program.glsl") as f:
        flat_vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "simple_tex_flat_fragment_program.glsl") as f:
        flat_fragment_source_code = f.read()

    #Se define el pipeline
    flat_vert_program = pyglet.graphics.shader.Shader(flat_vertex_source_code, "vertex")
    flat_frag_program = pyglet.graphics.shader.Shader(flat_fragment_source_code, "fragment")
    flat_pipeline = pyglet.graphics.shader.ShaderProgram(flat_vert_program, flat_frag_program)

    # ------------------------
    # pipeline GOURAUD

    with open(Path(os.path.dirname(__file__)) / "simple_tex_gouraud_vertex_program.glsl") as f:
        gouraud_vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "simple_tex_gouraud_fragment_program.glsl") as f:
        gouraud_fragment_source_code = f.read()

    #Se define el pipeline
    gouraud_vert_program = pyglet.graphics.shader.Shader(gouraud_vertex_source_code, "vertex")
    gouraud_frag_program = pyglet.graphics.shader.Shader(gouraud_fragment_source_code, "fragment")
    gouraud_pipeline = pyglet.graphics.shader.ShaderProgram(gouraud_vert_program, gouraud_frag_program)

    # ------------------------
    # pipeline PHONG

    with open(Path(os.path.dirname(__file__)) / "simple_tex_phong_vertex_program.glsl") as f:
        phong_vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "simple_tex_phong_fragment_program.glsl") as f:
        phong_fragment_source_code = f.read()

    #Se define el pipeline
    phong_vert_program = pyglet.graphics.shader.Shader(phong_vertex_source_code, "vertex")
    phong_frag_program = pyglet.graphics.shader.Shader(phong_fragment_source_code, "fragment")
    phong_pipeline = pyglet.graphics.shader.ShaderProgram(phong_vert_program, phong_frag_program)

    # ------------------------
    # pipeline NOLIGHTS

    with open(Path(os.path.dirname(__file__)) / "simple_tex_nolight_vertex_program.glsl") as f:
        nolight_vertex_source_code = f.read()

    with open(Path(os.path.dirname(__file__)) / "simple_tex_nolight_fragment_program.glsl") as f:
        nolight_fragment_source_code = f.read()

    #Se define el pipeline
    nolight_vert_program = pyglet.graphics.shader.Shader(nolight_vertex_source_code, "vertex")
    nolight_frag_program = pyglet.graphics.shader.Shader(nolight_fragment_source_code, "fragment")
    nolight_pipeline = pyglet.graphics.shader.ShaderProgram(nolight_vert_program, nolight_frag_program)

    
    # ----------------------------------
    # creamos las variables de iluminacion
    view_eye = np.array([3,3,3])

    # variables de iluminación
    light_variables = {
        "La": np.array([0.8, 0.8, 1.0]),
        "Ld": np.array([0.8, 0.8, 1.0]),
        "Ls": np.array([0.8, 0.8, 1.0]),
        "Ka": np.array([0.1, 0.1, 0.1]),
        "Kd": np.array([0.3, 0.3, 0.3]),
        "Ks": np.array([1.0, 1.0, 1.0]),
        "lightPosition": np.array([5, -5, 5]),
        "viewPosition": view_eye,
        "shininess": 128,
        "constantAttenuation": 0.0001,
        "linearAttenuation": 0.03,
        "quadraticAttenuation": 0.01
    }

    for var, value in light_variables.items():
        flat_pipeline[var] = value
        gouraud_pipeline[var] = value
        phong_pipeline[var] = value
        #nolight_pipeline[var] = value


    
    # ----------------------------------
    # creamos el grafo de escena      
    graph = sg.SceneGraph()

    tex_file = "fox.jpg"


    graph.add_node("cube_scene", 
        transform=tr.identity()
    )

    graph.add_node("cube",
        attach_to = "cube_scene",
        mesh = draw_model,
        transform=(
            tr.rotationY(0)
        ),
        #pipeline = nolight_pipeline,
        pipeline = flat_pipeline,
        cull_face= False,
        texture = sg.Texture(Path(os.path.dirname(__file__)) / tex_file,
            sWrapMode=GL.GL_REPEAT,
            tWrapMode=GL.GL_REPEAT,
            minFilterMode=GL.GL_NEAREST,
            maxFilterMode=GL.GL_NEAREST,
        ),
    )
    


    # ----------------------------------
    
    window.program_state = {
        "scene_graph": graph,
        "draw_mode": True,
        "total_time": 0.0,
        "camera_theta" : np.pi/4,
        "view": tr.lookAt(
            view_eye, # eye
            np.array([0, 0, 0]), # at
            np.array([0, 1, 0])  # up
            #np.array([0, 0, 1])  # up
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
        window.program_state['scene_graph']["cube"]["pipeline"].use()
        window.program_state['scene_graph']["cube"]["pipeline"]["view"] = window.program_state["view"].reshape(16, 1, order="F")
        window.program_state['scene_graph']["cube"]["pipeline"]["projection"] = window.program_state["projection"].reshape(16, 1, order="F")

        window.program_state['scene_graph'].draw()


    # esta función actualiza el grafo de escena en función del tiempo
    def update(dt, window):
        window.program_state["total_time"] += dt
        total_time = window.program_state["total_time"]

        graph['cube']['transform'] = (
           tr.rotationY(total_time/2)
        )

        window.program_state['scene_graph'].update()


    @window.event
    def on_key_press(symbol, modifiers):
        
        if symbol == pyglet.window.key.SPACE: 
            window.program_state["draw_mode"] = not window.program_state["draw_mode"]

        if symbol == pyglet.window.key.Q: 
            window.program_state["scene_graph"]['cube']['pipeline'] = nolight_pipeline
            print("pipeline: NO_LIGHTS")       

        if symbol == pyglet.window.key.W: 
            window.program_state["scene_graph"]['cube']['pipeline'] = flat_pipeline
            print("pipeline: FLAT")    

        if symbol == pyglet.window.key.E: 
            window.program_state["scene_graph"]['cube']['pipeline'] = gouraud_pipeline
            print("pipeline: GOURAND")   
        
        if symbol == pyglet.window.key.R: 
            window.program_state["scene_graph"]['cube']['pipeline'] = phong_pipeline
            print("pipeline: PHONG")   


    pyglet.clock.schedule_interval(update, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
