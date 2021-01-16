# lemarioExtactor
A python script to extract all RAE dictionary entries, a.k.a. Spanish lemario.

(VER ABAJO PARA ESPAÑOL)

## DISCLAIMER:
This code was developed under the hackathon proposal by Jaime Obregon (see https://github.com/JaimeObregon/drae-lemario#readme), that means that has been done in a quick way in order to work, but not in a fancy way. I want to upload the exact same version that I used to claim the success on twitter, and, maybe, I'll push fancier versions later ;)

## HOW IT WORKS
Run "lemario_extractor.py --help" to parameters description.
Warning: You will need a user and password to access dle.rae.es/data (the api that the rae mobile app uses). It is not hard to find it outthere ;)

The overall idea is to use an in depth search with prefixes of the lowercase Spanish alphabet (a-zñáéíóúü) plus the dash char "-". If the returned results match the max limit of results (meaning that there are too many words for that prefix), we expand the prefix to be one char longer (with the first char in the alphabet), otherwise repeat the operation by replacing the last char of the prefix with the next one in the alphabet (in case we are already in the last letter, we srink the prefix by one and move to the next).

After this we have 3 extra scenarios: 
- Words with uppercase letters: We search for words that contain each capital letter, as all of them return less results that the maximum, no prefix expansion is needed.
- Expressions that contain spaces: We search entries that contain "x y" for each combination of lowercase letters. Again, all of them return less than the maximum results, so no prefix is needed.
- Words with rare characters: We search entries that incude any of the following characters "àèìòùâêîôûäëïö‒". Only 'è', 'î' and '‒' (long dash) actually return results, but it is cheap to leave the remaining chars in case new words with them are included in the future.

At the end we will find duplicated and unordered resuts, which can be removed and sorted with external tools.

## OUTPUT
The script appends the results and traces to the given files, which default to stdout and stderr.

# ESPAÑOL

## AVISO:
Este código ha sido desarrollado para el hackathon propuesto por Jaime Obregon (ver https://github.com/JaimeObregon/drae-lemario#readme), lo que significa que se ha echo de forma rápida con el objetivo de que funcione, pero no de una forma bonita. Quiero subir tal cual la versión con la que comuniqué en twitter que lo había logrado, y, tal vez, más adelante suba versiones más bonitas ;)

## COMO FUNCIONA
Ejecuta "lemario_extractor.py" para ver una descripción de los parametros.
Aviso: Necesitaras un usario y contraseña para acceder a dle.rae.es/data (la api que usa la app móvil de la rae). No es difícil de encontrar por ahí fuera;)

La idea general es realizar una búsqueda en profundidad con los prefijos posibles con el alfabeto español en minúsculas (a-zñáéíóúü) además del guión "-". Si el conjunto de valores devueltos coincide con el límite máximo de resultados (lo que significa que hay demasiadas palabras con ese prefijo), añadimos al prefijo un carácter (el primero de nuestro alfabeto), en el resto de los casos, repetimos la búsqueda reemplazando la última letra del prefijo por la siguiente del alfabeto (si ya es la última, eliminamos la última letra y buscamos el siguiente prefijo "menor").

Tras esto, tenemos 3 escenarios adicionales:
- Palabras que contienen letras mayúsculas: Buscamos palabras que contengan cada una de las letras mayúsculas, como todas las búsquedas devuelven menos resultados del máximo, no es necesario expandir el prefijo.
- Expresiones con espacios: Buscamos entradas que contengan "x y" para cada combinación posible de letras minúsculas. De nuevo, todas las búsquedas devuelven menos resultados que el máximo y no es necesario expandir el prefijo.
- Palabras con caracteres raros: Buscamos entradas que incluyan los siguientes caracteres "àèìòùâêîôûäëïö‒". Solo 'è', 'î' y '‒' (guión largo) devuelven resultados, pero dejamos el resto por si se añadiesen palabras con ellos en un futuro.

Al finalizar obtendremos resultados duplicados y desordenados, que pueden facilmente eliminarse y ordenarse con herramientas externas.

## SALIDA
El script añade los resultados y trazas a los ficheros especificados, que por defecto son stdout y stderr.
