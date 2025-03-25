# Computación Gráfica y Modelamiento para Ingenieros e Ingenieras

# Edición 2025 Semestre Otoño

Profs:
- Sección 2: Valentín Muñoz 
- Sección 3: Nancy Hitschfeld

Este repositorio es un fork del repositorio de CC3501 del Prof. Eduardo Graells, con los ejemplos, instrucciones y modificaciones que usaremos en esta edición del curso para los ejemplos de Cátedra

Tambien existe el repositorio de Auxiliares, donde están los códigos y ejemplos vistos en clase auxiliar: [Link al Repo](https://github.com/asouris/CC3501/tree/main)

## Ambiente de trabajo

Hay 2 formas para instalar el ambiente de trabajo para estos códigos:

### Instalar un VirtualEnv propio

Para ello, pueden seguir las instrucciones que dejó Julieta en su repositorio: [Link a la guía](https://github.com/asouris/CC3501/blob/main/Setup.md)

### Instalar el ambiente Conda

Para ello, pueden seguir las siguientes instrucciones (cortesía del Prof. Eduardo Graells):

1. **Instalar `conda`**. Se puede descargar aquí: https://docs.anaconda.com/free/anaconda/install/windows/ (les más valientes pueden intentarlo con Miniconda: https://docs.anaconda.com/free/miniconda/ y les más valientes aun instalar `mamba`).

1. **Crear el entorno**. En el botón de inicio de Windows hay que ejecutar "Anaconda Prompt". Eso abrirá una consola. Allí deben ir a la carpeta del curso (recuerden los comandos `cd` y `dir`, o `ls` si están en GNU/Linux). En la carpeta raíz del repositorio hay un archivo llamado `environment.yml`. En la consola deben ejecutar:

    ```
    conda env create -n grafica -f environment.yml
    ```
    (si instalaron `mamba`, puede ser `mamba env create [...]`).

## "Instalar" los códigos

- Pueden descargarlo directamente (.zip) y usarlo directamente en una carpeta o ambiente de trabajo
- Pueden clonarlo usando git, y así estar al tanto de las últimas actualizaciones (realizando _pull_ de las versiones futuras)

## ¿Como usar los códigos?

Para ver si todo está en orden, lo primero que tienen que hacer es activar su ambiente de trabajo. 

- Si siguieron la guía de Julieta para instalar un VirtualEnv, entonces deberán ejecutar el siguiente comando, dependiendo de donde guardaron su ambiente, y su sistema operativo:

  - Windows: ```.\venv\Scripts\Activate```
  - Linux: ```source ~/Grafica/venv/bin/activate```
  - MacOs: ```source ~/Grafica/venv/bin/activate```

  Para mas detalles, vean nuevamente el tutorial de Julieta.

- Si instalaron conda, entonces pueden activar el entorno con el siguiente comando:
  
  ```
  conda activate grafica
  ```

Si todo salió bien, debiesen estar en condiciones de ejecutar los códigos del curso. El más básico es el hola mundo:

```
python examples/hello_world/app.py
```

## Configurar tu editor favorito

Pueden utilizar el editor que más les acomode (`notepad++`, `sublime`, `VScode`, etc...)

En mi caso uso `VScode`, pues tiene la facilidad de integrar en una misma interfaz, la edición del código y la ejecución del código (y facilitar la integración con GIT para obtener los últimos updates).

El detalle es que hay que indicarle a VScode el entorno/ambiente de trabajo a usar. Para ello, hay que hacer clic en la esquina inferior derecha (donde dice “Python: gráfica [...]”) y elegir el entorno que acaban de instalar. Después pueden presionar el botón de _play_ en la esquina superior derecha. 


