# lemarioExtactor
A python script to extract all RAE dictionary entries, a.k.a. Spanish lemario.

(VER ABAJO PARA ESPAÑOL)

# DISCLAIMER:
This code was developed under the hackathon proposal by Jaime Obregon (see https://github.com/JaimeObregon/drae-lemario#readme), that means that has been done in a quick way in order to work, but not in a fancy way. I want to upload the exact same version that I used to claim the success on twitter, and, maybe, I'll push fancier versions later ;)

# HOW IT WORKS
The overall idea is to use an in depth search with prefixes of the lowercase Spanish alphabet (a-zñáéíóúü) plus the dash char "-". If the returned results match the max limit of results (meaning that there are too many words for that prefix), we ignore the results (except to check if the current prefix is actually a valid word), and expand the prefix to be one char longer (with the first char in the alphabet), otherwise repeat the operation by replacing the last char of the prefix with the next one in the alphabet (in case we are already in the last letter, we srink the prefix by one and move to the next).

After this we have 3 extra scenarios: Capital words, uppercase words and expressions that contain spaces.
For the first one we repeat the process by capitalizing the prefixes.
For the second one we repeat the process by uppercassing the prefixes (it happens not to be needed as the previous scenario already covers this one, as the result for all the prefixes of size one do not exceed the max size, making this second scenario redundant).
For the third scenario, we change the search from prefix type to infix type, searching for words that contains "x y" for each combination of the alphabet for x,y (excluding the dash).

# TODOs
- Instead of defining the alphabet, we could compose it by searching words that contains any lowercase letter or symbol of the latin alphabet, in case the result hits the limit, we add that letter/symbol to our alphabet, otherwise, we add the result words (if any) to a list of rare words to be checked and added to the final result.
- The slower part of this algorithm is the 2-way latency of the requests, as once we expand a prefix we know that all the prefix+letter searches are going to be needed, we could parallelize them (with a limited set of worker threads to avoid overflowing local/remote resources), and cache the results so that the main thread can process them without waiting.

# -------------------------- ESPAÑOL ----------------------------------

# AVISO:
Este código ha sido desarrollado para el hackathon propuesto por Jaime Obregon (ver https://github.com/JaimeObregon/drae-lemario#readme), lo que significa que se ha echo de forma rápida con el objetivo de que funcione, pero no de una forma bonita. Quiero subir tal cual la versión con la que comuniqué en twitter que lo había logrado, y, tal vez, más adelante suba versiones más bonitas ;)

# COMO FUNCIONA
La idea general es realizar una búsqueda en profundidad con los prefijos posibles con el alfabeto español en minúsculas (a-zñáéíóúü) además del guión "-". Si el conjunto de valores devueltos coincide con el límite máximo de resultados (lo que significa que hay demasiadas palabras con ese prefijo), ignoramos los resultados (salvo para comprobar que el prefijo en si no sea una palabra válida), y añadimos al prefijo un carácter (el primero de nuestro alfabeto), en el resto de los casos, repetimos la búsqueda reemplazando la última letra del prefijo por la siguiente del alfabeto (si ya es la última, eliminamos la última letra y buscamos el siguiente prefijo "menor").

Tras esto, tenemos 3 escenarios adicionales: Palabras que empiezan por mayúsculas, palabras enteras en mayúsculas y expresiones con espacios.
Para el primer caso repetimos el proceso capitalizando la inicial de los prefijos.
Para el segundo caso repetimos el proceso capitalizando los prefijos enteros (aunque podemos omitir este resultado ya que el escenario anterior devuelve menos resultados de los máximos para todos los prefijos de una letra, haciendo que este escenario sea una repetición exacta del anterior).
Para el tercer caso cambiamos la búsqueda de tipo prefijo a tipo infijo, buscando entradas que contengan "x y" para todas las combinaciones posibles de x,y (exceptuando el guión).

# TODOs
- En vez de definir el alfabeto, podríamos componerlo buscando palabras que contengan cada letra minúscula y símbolo del alfabeto latino, en caso de que los resultados alcancen el límite, añadimos la letra/símbolo a nuestro alfabeto, en caso contrario, añadimos los resultados (si hay) a una lista de palabras raras que  comprobaremos y añadiremos a los resultados finales.
- La parte más lenta de este algoritmo es la latencia de ida/vuelta de las peticiones, como una vez decidimos que hay que expandir un prefijo sabemos que vamos a tener que buscar todas las combinaciones de ese prefijo más una letra del alfabeto, podemos paralelizar esas búsquedas (con un límite de hilos "trabajadores" para evitar saturar los recursos locales y remotos), y cacheamos los resultados para que el hilo principal pueda procesarlos sin tener que esperar.
