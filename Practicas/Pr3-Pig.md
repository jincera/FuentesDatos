# Pig, Pig Latin. Práctica 3

**José Incera, Abril 2020**

## Objetivos

+ Familiarizarse con el ambiente de programación interactivo de Pig  y los principales comandos de Pig Latin.

### Entregables

La fecha de entrega es el lunes 11 de mayo.  Se entrega un documento con:

+ Las respuestas a las preguntas en el desarrollo
+ El script solicitado al final de esta práctica

Se permite trabajar en equipos de dos personas

## Desarrollo

Haga una carpeta llamada `Hdp-Pr3` y copie en ella el archivo `votacion.csv` de la práctica 1.

Haga un archivo de prueba con los primeros 30 registros. Lo estaremos utilizando durante el desarrollo de esta práctica.

```bash
$ cd $HOME
$ mkdir Hdp-Pr3
$ cp Hdp-Pr1/data/votacion.csv Hdp-Pr3

$ cd Hdp-Pr3
$ head -30 votacion.csv > vtst.csv
```

Copie el archivo `Encuestas.csv` de la carpeta `/home/jincera/DatosFD/Pr3/`

```bash
$ cp /home/jincera/DatosFD/Pr3/Encuestas.csv .
$ ls
votacion.csv vtst.csv Encuestas.csv
```

**1. LOAD**

Inicie Pig en modo interactivo, lea el archivo *vtst.csv* y asígnelo a la relacion *A*.  Despliegue el primer campo del archivo leído (más adelante veremos el operador foreach)

```bash
$ pig -x local

grunt>A = load 'vtst.csv';
grunt>dump A
...
(16,H,5432,CAND4)
(10,M,7932,CAND4)

grunt>B = foreach A generate $0;
grunt>dump B
...
(16,H,5432,CAND4)
(10,M,7932,CAND4)
```

**¿Qué tipo de datos nos está entregando?** (Sugerencia: utilice el comando `describe A`)

Posiblemente no es lo que esperábamos.

Además, pig está desplegando mucha información innecesaria. Si le molesta esta información, ejecute los siguientes comandos para cambiar el nivel de mensajes desplegados en consola.

```bash
grunt>quit

$ echo 'log4j.rootLogger=fatal' > nolog.conf
$ pig -4 nolog.conf -x local
```
Cargue nuevamente el archivo pero esta vez defina un esquema para los campos leídos.

```bash
# El shell de Pig tiene memoria. Use la flecha hacia arriba para recuperar los comandos que ya haya introducido.
grunt>A = load 'vtst.csv' as (hora:int, gen:chararray, dist:int, cand:chararray);
grunt>B = foreach A generate $0;
grunt>dump B;
...
()
()
grunt>dump A;
...
(,,,)
(,,,)
grunt>describe A
A:{hora:int,gen: chararray,dist: int,cand: chararray}
```

Todavía no podemos aislar el primer campo, y de hecho, A está peor que antes.

Pig supone que por omisión, el separador de campos es un tablulador y nuestro archivo separa los campos con comas. Esto se corrige con el operador `PigStorage`:

```bash
grunt>A = load 'vtst.csv' using PigStorage(',') as (hora:int, gen:chararray, dist:int, cand:chararray);

grunt>B = foreach A generate $0;
grunt>dump B;
...
(16)
(10)
```
Ahora sí se puede aislar el primer campo y asignarlo a B.

**2. STORE**

Ejecute los siguientes comandos para guardar la relación A

```bash
grunt>store A into 'salida1';
grunt>store A into 'salida2' using PigStorage(':');
```
**Ubique los archivos de salida y compárelos con el archivo de entrada `vtst.csv`.**

**¿Qué significa part-m-00000? ¿Porqué la notación es distinta a la que teníamos en las prácticas anteriores?**

Es un buen momento para probar Pig interactivo en modo MapReduce.

Crearemos una relación sólo con hora y distrito y la guardaremos en *salida1*.

```bash
grunt>quit
# Puede omitir los parámetros en el siguiente comando si desea ver los mensajes de información 
$ pig -4 nolog.conf

grunt>A = load 'vtst.csv' using PigStorage(',') as (hora:int, gen:chararray, dist:int, cand:chararray);
grunt> B = foreach A generate hora, dist;
grunt>dump B;
```

Está marcando un error.  ¿Se imagina qué puede etar ocurriendo?  Como sugerencia, considere que se están tardando mucho más los comandos en ejecutarse.

¡Seguramente lo descubrió!  El archivo `vtst.csv` no está en el HDFS.

Salga de Pig, mande el archivo al HDFS e inténtelo de nuevo.

```bash
grunt>quit

$ hdfs dfs -put vtst.csv

$ pig -4 nolog.conf

grunt>A = load 'vtst.csv' using PigStorage(',') as (hora:int, gen:chararray, dist:int, cand:chararray);
grunt>B = foreach A generate hora, dist;
grunt>store B into 'salida1';
grunt>quit 
```
**¿En qué archivo quedó guardada la relación B?  Muestre las últimas cinco líneas**

Aunque el objetivo de estas sesiones es trabajar con Hadoop, por ahora continuaremos en el  modo local iterativo, que -como habrá observado- es más rápido.

**3. FILTER**

Filtre los votos que obtuvo el candidato CAND5 y ordénelos por orden descendente de hora y ascendente de distrito

```bash
$ pig -4 nolog.conf -x local

grunt>A = load 'vtst.csv' using PigStorage(',') as (hora:int, gen:chararray, dist:int, cand:chararray);

grunt>B = filter A by $3 == 'CAND5';
grunt>C = order B by hora DESC, $2 ASC;
grunt>dump C;
...
(8,M,5432,CAND5)
(8,M,8425,CAND5)
```

**¿Qué signfica $2 en la última operación?**

Guarde el resultado en una carpeta `salida3` y despliegue el contenido de la carpeta desde Pig para comprobar que el ambiente permite ejecutar algunos comandos del sistema operativo.

```bash
grunt>store C into 'salida3' using PigStorage(',');

grunt>ls salida3
```
Revise el archivo de salida (quizás deba dejar pig, aunque puede probar con el comando sh.  También Pig tiene el comando fs, que es equivalente a `hdfs dfs`).

**¿Qué significa el nombre del archivo de salida? ¿Cuántos registros se obtuvieron para ese candidato a las 9 de la mañana?  ¿Hasta qué hora se votó - para ese candidato?** 

**4. GROUP**

Agrupe los registros con base en la hora en que se hizo el voto.

```bash
-- Si salió de pig entre nuevamente y cargue la relación A

grunt>C = group A by hora;
grunt>dump C
...
(17,{(17,M,9184,CAND4),(17,H,5572,CAND4)})
grunt>describe C;
C: {group: int, A:{(hora:int,gen:chararrya,dist:int,cand:chararray)}}
```

Parece que los votantes no son muy madrugadores.  Más adelante podremos ver cómo contar los campos para estimar un histograma.

Con la última instrucción se mostró el schema de C. 
**Explique brevemente este schema**

**5. FOREACH**

Ya utilizamos este operador para desplegar el primer campo de una relación. Ahora lo utilizaremos para crear una relación reteniendo la hora y el candidato.

Para familiarizarnos con algunas operaciones para manejo de strings, al campo de hora se le agregará el sufijo ":00 HR".

```bash
grunt>B = foreach A generate hora as hr:chararray,cand; -- Hora de int a chararray
grunt>describe B;
B: {hr: chararray,cand:chararray}

grunt>C = foreach B generate CONCAT(hr,':00 HR'),cand; 
grunt>dump C
...
(16:00 HR, CAND4)
(10:00 HR, CAND4)
```
**Explique brevemente la instrucción que generó la relación C. Incluya en la explicación alguna diferencia que haya observado entre la descripción (`describe`) de B y de C.**

**6. FOREACH anidado**

Empecemos por contar cuántos votos obtuvo cada candidato.

```bash
grunt>B = group A by cand;
grunt>dump B

grunt>C = foreach B generate group,COUNT(A); 
grunt>dump C
...
(CAND4,14)
(CAND5,8)
```
**Explique brevemente la instrucción que generó la relación C**

**Ya tiene los elementos necesarios para calcular el histograma del número de votantes por hora. ¡Inténtelo!**

**¿A qué hora se tuvo el máximo y el mínimo número de votantes?**

Ahora veamos cuántos votos de mujeres obtuvo cada candidato

```bash
grunt>M = foreach B { 
       votosMujeres = filter A by gen == 'M';
        votosCand = votosMujeres.cand;
        generate group, COUNT(votosCand);
      };
```

Para comprobarlo, repita la operación anterior pero para evaluar cuántos votos de hombres obtuvo cada candidato.  La suma de las dos operaciones debe coincidir con el número de registros (30).

**7. SPLIT**

Las candidatas 1 y 3 son mujeres; los demás son hombres. Veamos cuántos votos obtuvieron las candidatas mujeres y cuántos los hombres.

Empezaremos por separar los votos de las candidatas 1 y 3 y los de los demás.

```bash
grunt>split A into cMujer if cand == 'CAND1' OR cand == 'CAND3', cHombre if cand == 'CAND2' OR cand == 'CAND4' OR cand == 'CAND5';
grunt>dump cMujer -- debe ver sólo tuplas de CAND1 y CAND3
grunt>dump cHombre -- debe ver las demás tuplas
```
**Muestre los resultados de los dos dump anteriores**

Ahora repita las instrucciones de la sección anterior para obtener los votos de cada candidato en las nuevas relaciones.  Por supuesto, los resultados deben coincidir con los que ya ha visto.

```bash
grunt>votMujeres = group cMujer by cand;
grunt>nVotMujeres = foreach votMujeres generate group,COUNT($1); 
grunt>votHombres = group cHombre by cand;
grunt>nVotHombres = foreach votHombres generate group,COUNT($1); 
grunt>dump nVotMujeres
grunt>dump nVotHombres
```

**Muestre los resultados de los dos dump anteriores**

**8. JOIN**

El archivo *Encuestas.csv* contiene una serie de datos sobre el grado de conocimiento (como porcentaje de la población encuestada) de los candidatos.  El grado de conocimiento se ha resumido en cinco valores: 10%, 30%, 50% 70% y 90% como valor medios de los cinco rangos en que se agruparon las encuestas.

Cada entrada en el archivo tiene tres campos: el candidato, la casa encuestadora y el nivel de conocimiento.

En esta sección veremos qué tanto se conoce a los candidatos en la población encuestada.

Abra el archivo *Encuestas.csv* y genere una nueva relación con la relación `A` que contiene los registros de *vtst.csv* con el campo común de candidato.

```bash
grunt>encuestas = load 'Encuestas.csv' using PigStorage(',') as (cand:chararray,casa:chararray,valor:int);
grunt>CandYEnc = join A by cand, encuestas by cand;
```
**Muestre los últimos tres registros de la relación CandYEnc**

Ahora hagamos una proyección sólo con el nombre del candidato y el porcentaje de conocimiento.  Como en el join hay campos con el mismo nombre, debemos utilizar el operador `::` para "derreferenciar" los campos, es decir, distinguir de qué relación provienen.

```bash
grunt>describe CandYEnc;
grunt>CandYPorc = foreach CandYEnc generate A::cand, encuestas::valor;
grunt>dump CandYPorc
...
(CAND5,10)
(CAND5,30)
(CAND5,50)
```
**Muestre los últimos tres registros de la relación CandYPorc**

Agrupemos la nueva relación por candidato y finalmente generemos con ella una proyección con el nombre del candidato (*group*) y el porcentaje de conocimiento obtenido de la última relación.

```bash
grunt>ConocPorCand = group CandYPorc by cand;
grunt>avgConocCand = foreach ConocPorCand generate group, AVG(CandYPorc.valor);
grunt>dump avgConocCand
```

**Queda como ejercicio opcional que analice si el conocimiento de los candidatos (o su género, o ambos) tienen alguna correlación con el número de votos obtenidos**

### Script

Haga un script para responder a las preguntas de las secciones 6 (FOREACH anidado), 7 (SPLIT) y 8 (JOIN) utilizando como entrada el archivo votacion.csv. 

