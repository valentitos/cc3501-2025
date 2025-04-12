import os.path
import sys
from pathlib import Path

import numpy as np
import pyglet
import pyglet.gl as GL
import trimesh as tm

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
)

import grafica.transformations as tr
import utils.scene_graph as sg
import utils.helpers as hp


# Este ejemplo es una simplificación del ejemplo de grafos de escena original
# Es una implementación que muestra como utilizar la libreria auxiliar utils.scene_graph
# para crear y administrar el grafo de escena.


# esta función se encarga de construir el grafo de escena
# sol -> tierra -> luna
# pero cada elemento tiene a su vez un geometry (su modelo 3d, una esfera)
#
# cosas como el pipeline correspondiente a cada malla y los atributos que reciben los pipelines
# son almacenadas como atributos de cada nodo de la red.
def create_solar_system(mesh, mesh_pipeline):

    # en el caso de SceneGraph, creamos directamente el objeto grafo, sin necesidad de designar una raiz
    graph = sg.SceneGraph()

    # luego, el primer nodo que agreguemos, adquirira el rol de raiz
    graph.add_node("sun", 
        transform=tr.identity()
    )

    # Hay dos principales diferencias al usar SceneGraph
    # - al momento de agregar un nodo, hay que completar el parametro "attach_to"
    #   que indica a que nodo "de mas arriba" conectaremos este nodo
    # - No hay que formalizar la relación de dependencia creando un arco entre los nodos
    #   ya que lo anterior se encarga explicitamente de eso
    graph.add_node("sun_geometry",
        attach_to="sun",
        mesh=mesh,
        pipeline=mesh_pipeline,
        transform=tr.uniformScale(0.8),
        color=np.array((1.0, 0.73, 0.03)),
    )

    graph.add_node("earth",
        attach_to="sun",
        transform=tr.translate(2.5, 0.0, 0.0)
    )

    graph.add_node("earth_geometry",
        attach_to="earth",
        transform=tr.uniformScale(0.3),
        mesh=mesh,
        pipeline=mesh_pipeline,
        color=np.array((0.0, 0.59, 0.78)),
    )

    graph.add_node("moon",
        attach_to="earth", 
        transform=tr.translate(0.5, 0.0, 0.0)
    )

    graph.add_node("moon_geometry",
        attach_to="moon",
        transform=tr.uniformScale(0.1),
        mesh=mesh,
        pipeline=mesh_pipeline,
        color=np.array((0.3, 0.3, 0.3)),
    )

    graph.add_node("mercury",
        attach_to="sun",
        transform=tr.translate(1.5, 0.0, 0.0)
    )

    graph.add_node("mercury_geometry",
        attach_to="mercury",
        transform=tr.uniformScale(0.2),
        mesh=mesh,
        pipeline=mesh_pipeline,
        color=np.array((1.0, 0.0, 0.0)),
    )

    return graph


if __name__ == "__main__":
    width = 960
    height = 960

    window = pyglet.window.Window(width, height)

    # cargamos una esfera y la convertimos en una bola de diámetro 1
    mesh = hp.mesh_from_file("assets/sphere.off")[0]['mesh']
    # a diferencia del programa con networkx puro, acá usamos la función auxiliar
    # mesh_from_file, que se encarga de cargar automaticamente la malla, y reservar
    # espacio en la GPU.

    with open(Path(os.path.dirname(__file__)) / "simple_vertex_program.glsl") as f:
        vertex_source_code = f.read()

    with open(
        Path(os.path.dirname(__file__)) / "simple_fragment_program.glsl") as f:
        fragment_source_code = f.read()

    #Se define el pipeline
    vert_program = pyglet.graphics.shader.Shader(vertex_source_code, "vertex")
    frag_program = pyglet.graphics.shader.Shader(fragment_source_code, "fragment")
    solar_pipeline = pyglet.graphics.shader.ShaderProgram(vert_program, frag_program)

    # creamos el grafo de escena con la función definida más arriba
    graph = create_solar_system(mesh, solar_pipeline)

    # el estado del programa almacena el grafo de escena en vez de los modelos 3D
    window.program_state = {
        "scene_graph": graph,
        "total_time": 0.0,
        "view": tr.lookAt(
            np.array([5, 5, 5]), # eye
            np.array([0, 0, 0]), # at
            np.array([0, 1, 0])  # up
        ),
        "projection": tr.perspective(45, float(width) / float(height), 0.1, 100),
    }


    @window.event
    def on_draw():
        GL.glClearColor(0.25, 0.5, 0.25, 0.5)
        GL.glLineWidth(2.0)
        GL.glPolygonMode(GL.GL_FRONT_AND_BACK, GL.GL_FILL)
        GL.glEnable(GL.GL_DEPTH_TEST)

        window.clear()

        # configuramos la vista y proyección de los pipelines
        solar_pipeline.use()
        solar_pipeline["view"] = window.program_state["view"].reshape(16, 1, order="F")
        solar_pipeline["projection"] = window.program_state["projection"].reshape(16, 1, order="F")

        # al usar SceneGraph, podemos usar .draw directamente, que se encarga de dibujar los elementos
        # del grafo de escena. Todo el recorrido DFS y administración de la cadena de transformaciones
        # queda delegada implicitamente a esta función
        graph.draw()

    # esta función actualiza el grafo de escena en función del tiempo
    # en este caso, hace algo similar a lo que hemos hecho en ejemplos anteriores
    # al asignar rotaciones que dependen del tiempo transcurrido en el programa
    def update_solar_system(dt, window):
        window.program_state["total_time"] += dt
        total_time = window.program_state["total_time"]
        

        # para acceder a un nodo del grafo utilizamos su atributo .nodes
        # cada nodo es almacenado como un diccionario
        # por tanto, accedemos a él y a sus atributos con llaves de diccionario
        # que conocemos porque nosotres construimos el grafo

        # ojo, acá estamos editando la "orbita" de los planetas, y no la 
        # geometria.

        graph["earth"]["transform"] = (
            tr.rotationY(2 * total_time) 
            @ tr.translate(2.5, 0.0, 0.0)
        )
        graph["moon"]["transform"] = (
            tr.rotationY(3 * total_time) 
            @ tr.translate(0.5, 0.0, 0.0)
        )

        graph["mercury"]["transform"] = (
            tr.rotationY(4 * total_time) 
            @ tr.translate(1.0, 0.0, 0.0)
        )

        # y un detalle importante, es necesario invocar a graph.update, para "confirmar"
        # los cambios anteriores
        graph.update()

    pyglet.clock.schedule_interval(update_solar_system, 1 / 60.0, window)
    pyglet.app.run(1 / 60.0)
