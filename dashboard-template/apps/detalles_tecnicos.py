from app import app
from dash import dcc
from dash import  html
import dash_bootstrap_components as dbc

layout = html.Div([
    dbc.Row([
        dbc.Col([

        ], style={'width':'5%'}),
        dbc.Col([
            dcc.Markdown(
                '''
                # Detalles técnicos
                '''
            )  
        ], style={'width':'90%', 'text-align':'center'}),
        dbc.Col([

        ], style={'width':'5%'})
    ]),

    dbc.Row([
        dbc.Col([
        ], style={'width':'5%'}),
        dbc.Col([
            dcc.Markdown(
                '''
                Este trabajo corresponde al proyecto ["*Contando historias con datos*"](https://mcd-unison.github.io/ing-caract/proyecto2/)
                del curso de Ingeniería de características de la [**Maestría en ciencia de datos de la Universidad de Sonora**](https://mcd.unison.mx/).
                '''
            ),
            html.Br(),
            html.Br(),
        ], style={'width':'90%', 'text-align':'justify'}),
        dbc.Col([
        ], style={'width':'5%'})

    ]),

    dbc.Row([
        dcc.Markdown(
            '''
            #### Autor: [Pedro Andrés Hernández Amador](https://www.linkedin.com/in/pedro-hdez/)

            '''
        ),
        html.Br(),
        html.Br(),
        html.Br(),
    ],style={'padding-left':'3%'}),
    dbc.Row([

        dcc.Markdown(
            '''
            Este dashboard se creó en Python utilizando el framework de [Dash](https://dash.plotly.com/).
            Los datos se han extraído directamente de YouTube utilizando su [API oficial](https://developers.google.com/youtube/v3).
            Si estás interesado en aprender a utilizar esta API he escrito [este artículo de Medium](https://medium.com/mcd-unison/youtube-data-api-v3-in-python-tutorial-with-examples-e829a25d2ebd) al respecto.
            La clasificación de los sentimientos en los comentarios se realiza utilizando el modelo preentrenado [senti-py](https://github.com/aylliote/senti-py)

            Los scripts necesarios para la extracción, tratamiento y carga de los datos, así como también la plantilla del dashboard se
            encuentran en este [repositorio de Github](google.com).

            Te invito a revisar el desempeño de estos otros canales:
            * [El Fedelobo](fedelobo-dashboard.herokuapp.com)
            * [JuegaGerman](https://juegagerman-dashboard.herokuapp.com/)
            * [elrubiusOMG](https://elrubiusomg-dashboard.herokuapp.com/)
            * [Luisito Comunica]()
            '''
        ),
        html.Br(),
        dcc.Markdown(
            '''
            ### Consideraciones

            El API de YouTube tiene una restricción en cuanto a su uso diario de 10,000 unidades.
            Entonces, cuando un canal tiene muchos videos publicados, es imposible extrar toda su
            información. Por este motivo, únicamente se toma en cuenta la información de los **últimos
            10,000 videos** del canal. Para realizar el análisis de sentimientos se descargan **los 
            100 comentarios más relevantes** de cada uno de los 10,000 videos extraídos.

            Cabe destacar que los procesos de extracción de datos y clasificación de los comentarios
            se realiza de manera automática todos los días a las 00:15 hrs. Los resultados se ven
            reflejados en el dashboard aproximadamente a las 9:00 hrs.

            A continuación, se explica el procedimiento general para la creación de cada una de las 
            gráficas e indicadores que se muestran en las diferentes secciones.
            '''
        ),
        html.Br(),
        dcc.Markdown(
            '''
            ### Sección General

            #### Tarjetas

            * **Reproducciones**: Para estimar el número total de reproducciones que tiene el canal se realiza la sumatoria del número de reproducciones de todos los videos extraídos.
            * **Suscriptores**: La API de YouTube entrega una estimación del número de suscriptores redondeado a tres cifras significativas para los canales con más de 1,000 suscriptores. Puede consultar este [enlace](https://developers.google.com/youtube/v3/revision_history#release_notes_09_10_2019) para mayor información.
            * **Videos**: Se utiliza el resultado entregado por la API de YouTube que representa el número de videos públicos del canal.
            * **Visitas al canal**: Se utliza el resultado entregado por la API de YouTube.

            #### Gráficas

            * **Nuevas reproducciones por día**: Para estimar las nuevas reproducciones que el canal ha ganado se realiza la diferencia entre el número de reproducciones actual y el número de reproducciones del día anterior.
            * **Suscripciones por día**: Se grafica directamente el número de suscriptores que la API regresa.
            * **Número de videos por mes**: El conjunto de datos que contiene la información de los videos se agrupa por año de publicación y después por mes de publicación. Seguido de ésto, se obtiene el número de videos correspondiente a cada dupla (año,mes).
            * **Proporción de likes**: Se suman el número de likes y dislikes de cada uno de los videos extraídos por la API. Después se obtiene la tasa de cada tipo de reacción.
            * **Sentimientos en los comentarios**: Primero se clasifican los 100 comentarios más relevantes de cada uno de los videos, después se obtiene la sumatoria de los comentarios clasificados por sentimiento.

            ### Sección Videos

            Debido a los problemas que pueden surgir al subir archivos muy pesados al servidor, las imágenes se descargan en el momento en el que el dashboard está siendo utilizado. Por este movito
            es probable que experimente un ligero retardo al momento de explorar esta sección.

            #### Gráficas

            * **Por tasa de likes**: Se obtienen todos los videos que fueron publicados en el año que el slider marca, después se obtienen los tres videos con mejor o peor tasa de likes.
            * **Por número de reproducciones**: Se obtienen todos los videos que fueron publicados en el año que el slider marca, después se obtienen los tres videos con los números más altos o más bajos de reproducciones.
            * **Por tasa de positividad en los comentarios**: Se obtienen todos los videos que fueron publicados en el año que el slider marca, después se obtienen los tres videos con mejor o peor tasa de comentarios positivos.

            ### Sección Comentarios

            Durante la etapa de desarrollo se ha notado que las nubes de palabras tardan una cantidad considerable de tiempo para construirse. De hecho,
            tardan más que el tiempo que se necesita para descargar tres imágenes en la sección de videos. Por este motivo las nubes de palabras sí se 
            construyen antes de subir los datos al servidor.

            * **Nube de palabras más utilizadas**: Se toman todos los comentarios clasificados como positivos, neutrales o negativos y espués se construye una nube de palabras con el número de palabras que el slider marque.
            * **Comentarios por mes**: El conjunto de comentarios se agrupa por año de publicación y después por mes de publicación. Luego, para cada dupa (año,mes) se obtiene la sumatoria de cada tipo de comentario.
            '''
        )
    ],style={'padding-left':'3%'})
])