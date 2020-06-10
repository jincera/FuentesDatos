# Hadoop y Map Reduce. Práctica 1
**José Incera, Julio, 2017**


## Objetivo

+  Reafirmar conceptos básicos de la arquitectura Hadoop y el modelo de programación MapReduce.
+	Mostrar el uso de la API Hadoop Streaming para lanzar funciones *Map* y *Reduce* en lenguajes de programación distintos de Java.

### Entregables

La fecha de entrega es el **martes 25 de julio** a las 19:00.  Se entregan:

+ Los scripts de los ejercicios
+ Un  reporte con **los resultados obtenidos** y, donde lo considere adecuado, **capturas de pantalla**.

## Introducción

En un escenario electoral hipotético, se realizaron encuestas de salida para conocer las preferencias de los electores, así como algunos datos demográficos.  De estas encuestas se generó el archivo *votacion.csv* el cual contiene cuatro campos:

1. Hora.- Número entero en el rango [8:17], registra la hora en que se aplicó la encuesta al elector
2. Género.- H = Hombre, M = Mujer, se trata del género del elector
3. Distrito.- Un código que representa el distrito electoral en el que se aplicó la encuesta
4. Candidato.- Número entero en el rango [1:5], representa cada uno de los cinco candidatos que se postularon.

Aunque el archivo *votacion.csv* es muy pequeño, en esta práctica se almacenará en una instancia de Hadoop en su máquina virtual y se realizarán algunos análisis básicos con el modelo MapReduce utilizando guiones (scripts) en Python.

Esta práctica también permitirá experimentar con algunos comandos básicos de Unix/Linux.

## Desarrollo

*Si no está familiarizado con el ambiente Hadoop e instaló el Sandbox en su propia computadora, consulte el anexo*.


### Preparación de datos

En esta práctica trabajaremos exclusivamente a través de la interfaz de la línea de comandos (CLI). Si no lo ha hecho, conéctese a la máquina virtual de su ambiente Hadoop.  

**NOTA: Si está utilizando el servidor remoto para practicar que se ha instalado en el ITAM (ver nota al final de este documento) debe sustituir la cuenta root por su nombre de usuario en los siguientes comandos.**

```bash
host>ssh root@127.0.0.1 -p 2222
root@127.0.0.1's password: hortonworks

hdp>
```

Para poder ejecutar las prácticas debemos crear un directorio en HDFS para nuestro usuario.

```bash
hdp>hdfs dfs -mkdir /user/root
```

**1.-** En su directorio `$HOME` cree la carpeta `bigdata/Practica1` con dos subcarpetas: `code` y `data`.

```bash
hdp>cd
hdp>mkdir -p bigdata/Practica1/code
hdp>mkdir -p bigdata/Practica1/data
hdp>ls -l bigdata/Practica1
total 8
drxwr-xr-x 2 root root 4096 may 21 18:40 code
drxwr-xr-x 2 root root 4096 may 21 18:40 data
```
 
**2.-** Descargue los archivos *EjMapper.py* y *EjReducer.py* y guárdelos en la carpeta `code` creada anteriormente.  De la misma forma, descargue el archivo *votacion.csv* y guárdelo en la carpeta `data`.

```bash
hdp>cd bigdata/Practica1/code
hdp>wget --quiet -O EjReducer.py https://rawgit.com/jincera/Test-Repo/master/EjReducer.py
hdp>wget --quiet -O EjMapper.py https://rawgit.com/jincera/Test-Repo/master/EjMapper.py
hdp>ls
EjMapper.py  EjReducer.py

hdp>cd ../data
hdp>wget --quiet -O votacion.csv https://rawgit.com/jincera/Test-Repo/master/votacion.csv
hdp>ls
votacion.csv
```

**3.-** Ubique el archivo *votacion.csv*  y despliegue las primeras líneas.

```bash
hdp>head -3 votacion.csv
12,M,1048,CAND5
15,H,7932,CAND1
13,H,7373,CAND4
```
Como puede observar, se trata de un archivo csv en el que los campos están separados por comas y no tiene encabezado.

Es una buena práctica probar los scripts de Map y Reduce con un conjunto pequeño de datos y, dentro de lo posible, paso a paso desde la línea de comandos, aprovechando los *pipes* de Linux. 

**4.-** Prepare un archivo de prueba con los primeros 100 registros

```bash
hdp>head -100 votacion.csv > vottst.csv
```

Los archivos se encuentran en el sistema de archivos local.  Hay que enviarlos a HDFS, el sistema de archivos distribuido de Hadoop:

```bash
hdp>hdfs dfs -put votacion.csv
hdp>hdfs dfs -ls
...
-rw-r--r-- 1 root hds 1591000 2017-05-21 18:59 votacion.csv
...
```

El comando *hdfs dfs* (o el equivalente *hadoop fs* en la versión anterior) indica a Linux que se introducirá una directiva para el sistema de archivos HDFS.  Los argumentos siguientes son la directiva y posibles parámetros.  Consulte la presentación de la primera sesión del curso para conocer algunos comandos de HDFS.

### Programación de scripts

En esta sesión se desarrollarán los scripts con el lenguaje de programación Python. Al ser un lenguaje interpretado, será muy sencillo verificar el comportamiento de los programas map y reduce con pipes de Linux.

Empezaremos por calcular las preferencias electorales para cada uno de los candidatos.

Los archivos *EjMapper.py* y *EjReducer.py* en la carpeta `code`,  son ejemplos de un código mapper y de un reducer, respectivamente.  El primero lee registros desde la entrada estándar (*stdin*, típicamente el teclado), selecciona dos campos y los imprime en la salida estándar (*stdout*, típicamente la pantalla).  Estos dos campos son la tupla *< key,value >* que el reducer tomará para continuar con el procesamiento.

Haga una copia de los archivos `EjMapper.py` y `EjReducer.py` como respaldo en caso de que algo salga mal durante la ejecución de la práctica

```bash
hdp>cp EjMapper.py EjMapper.py.bak
hdp>cp EjReducer.py EjReducer.py.bak
```

**5.-** Edite el archivo *EjMapper.py*. Revise el código y modifique la última línea para que se imprima en stdout la columna correspondiente al candidato (key) y un "1" (value). El código del reducer simplemente sumará estas instancias.  

**6.-** Posiciónese en la carpeta *code* y revise los permisos de los archivos *EjMapper.py* y  *EjReducer.py*

```bash
hdp>cd ~/bigdata/Practica1/code 
hdp>ls -l
total 8
-rw-r--r-- 1 root root 422 may 21 18:44 EjMapper.py
-rw-r--r-- 1 root root 819 may 21 18:45 EjReducer.py
```
Para Linux estos archivos no contienen código ejecutable; sólo tienen permisos de lectura y escritura (rw-).  Modifique los permisos para que también puedan ser ejecutados:

```bash
hdp>chmod 764 *py
hdp>ls -l
total 8
-rwxrw-r- 1 root root 422 may 21 18:44 EjMapper.py
-rwxrw-r- 1 root root 819 may 21 18:45 EjReducer.py
```
El comando anterior otorga permisos de lectura, escritura y ejecución (7) al dueño, lectura y escritura (6) a los miembros del grupo y sólo lectura (4) a los demás usuarios.

**7.-** Con ayuda del encadenamiento de comandos (pipelining) en Linux, verifique que el código parece funcionar correctamente.

```bash
hdp>cat ../data/vottst.csv |./EjMapper.py
...
CAND5	1
CAND4	1
CAND4	1
```

El comando *cat* lee y despliega en pantalla el archivo.  El "pipe" (|) toma esa salida y la pasa al siguiente comando, nuestro script *EjMapper.py*, como su propia entrada estándar.

**8.-** Abra el archivo *EjReducer.py* y analice su contenido.

Este archivo tiene un acumulador para contar el número de ocurrencias de un operador.  Dado que a un proceso *Reduce* llegan los datos ordenados, solo hay que incrementar el acumulador mientras el campo operador (key) no cambie.  En principio, este código no debe ser modificado.

**9.-** Nuevamente usaremos los pipes de Linux, para verificar que el Reducer parece hacer su función.  El comando *sort* en la siguiente instrucción ordena la salida de nuestro mapper, imitando la operación *shuffle* de MapReduce en Hadoop.  La salida del sort se toma como entrada para el script *EjReducer.py*.

```bash
hdp>cat ../data/vottst.csv | ./EjMapper.py | sort | ./EjReducer.py
CAND1	8
CAND2	5
CAND3	17
CAND4	48
CAND5	22
```

### Ejecución en Hadoop
Ahora que todo parece funcionar correctamente, se puede enviar el código para ser  ejecutado en Hadoop.  Dado que los programas están escritos en Python, se requiere de la API *hadoop streaming*, la cual permite lanzar tareas MapReduce escritas en prácticamente cualquier lenguaje capaz de recibir datos de la entrada estándar y de escribir resultados en la salida estándar.

**10.-**	Desde la terminal, ejecute el siguiente comando:

```bash
hdp>hadoop jar /usr/hdp/current/hadoop-mapreduce-client/hadoop-streaming-2,7,3,2,6,0,3-8.jar -files EjMapper.py,EjReducer.py -input votacion.csv -output OpcionElectoral 
-mapper EjMapper.py -reducer EjReducer.py
```
Los argumentos de la instrucción anterior son:

- files: Como los scripts no están en el ambiente Hadoop, deben ser enviados junto con el jar para que a su vez se distribuyan a los jobTrackers (o a los contenedores).  En versiones recientes, ya no es necesario incluir este parámetro
- input: El archivo de donde se leerán los datos que se envían a los procesos Map
- output: El directorio donde se almacenan los resultados (o los mensajes de error)
- mapper, reducer: Los scripts con los códigos para los procesos Map y Reduce

Como vamos a estar utilizando frecuentemente esta API, quizás le gustaría crear una variable de ambiente con la ruta del archivo jar para simplificar la escritura del comando:

```bash
hdp>export STRJAR=/usr/hdp/current/hadoop-mapreduce-client/hadoop-streaming-2,7,3,2,6,0,3-8.jar  
```
De esta manera, el comando anterior se invocaría así:

```bash
hdp>hadoop jar $STRJAR -files EjMapper.py, ...
```
Revise brevemente la salida, compruebe que no hubo herrores, identifique cuántas tareas map y reduce se dispararon.

**11.-** Verifique que el resultado se generó correctamente:

```bash
hdp>hadoop fs -cat OpcionElectoral/part-00000
1	10056
2	9884
3	15051
4	40018
5	24991
```

Así se nombran los archivos de salida en la primera versión de MapReduce. En la versión más reciente se nombran part-[m|r]-xxxxx para indicar si el archivo se generó a la salida de un Mapper (m) o de un Reducer (r).  El número (xxxxx) es un identificador único en esa carpeta para distinguir entre los resultados de (potencialmente) muchas tareas.

### Programación de scripts en R

(*Es posible que en esta ocasión no se haga la programación de scripts en R porque todavía no se ha instalado.  Si ese es el caso, en vez del código en R, escriba el script de bash que se muestra más adelante*).

Como habrá observado, los scripts proporcionados en Python reportan el número de votos que obtuvo cada candidato.   El código mapper simplemente lee líneas de la entrada estándar, separa los campos y envía a la salida estándar una línea con el candidato y un valor "1".   Hagamos lo mismo en un script de R.

**12.-** Escriba el siguiente script de R (asegúrese de que entiende qué hace cada comando).  Guárdelo como *miMapper.R*

```bash
#!/usr/bin/env Rscript

library(stringi)
stdin<-file('stdin',open='r')
while(length(x<-readLines(con=stdin,n=1))>0) {
  miVector<-(strsplit(x,','))
  y<-miVector[[1]]
  cat(stri_paste(y[4],"1",sep='\t'),sep='\n')
}
```
Alternativamente, éste es el script de bash. Guárdelo como miMapper.sh
```bash
#!/bin/bash
awk -F , '{print $4,"\t","1"}'
```

Si está familiarizado con C/C++, también puede implementar el código de los mappers y reducers en este lenguaje.  El siguiente es un ejemplo muy simple de un Mapper en c:

```bash
/* *******************
miMapper.c
Código muy simple para leer
el archivo votación.csv y sacar dos campos.

NO SE ESTÁN VALIDANDO ENTRADAS ni se está
privilegiando la modularidad
************************** */
#include<stdio.h>
#include<stdlib.h>
main()
{
   char linea[1024],hora[5],gen[2],dist[10],cand[10];
   char *p;
   int i=0;
   
   while(fgets(linea,1024,stdin)) // Toma una línea
   {
      p=linea;
      while (*p !0 ',')
         hora[i++] = *p++; // toma uno a uno caracteres
      hora[i]='\0'; // Termina string
      i=0;  // reinicia indice
      p++; //brinca coma
      while (*p !0 ',')
         gen [i++] = *p++; 
      gen[i]='\0'; 
      i=0;  
      p++; 
      while (*p !0 ',')
         dist[i++] = *p++;
      dist[i]='\0';
      i=0;
      p++; 
      while (*p !0 ',')
         cand[i++] = *p++; 
      cand[i]='\0'; 
      
      printf("%s\t%s\n",cand,"1");
   }
}

hdp>gcc miMapper.c -o miMapper.out
```

Puede compilar el código anterio

**13.**	Asigne permisos de ejecución al script (miMapper.R, miMapper.sh o miMapper.o)

**14.**	Antes de invocar Hadoop streaming, probemos con los pipes de unix (con el mapper que haya implementado)

```bash
hdp>cat ../data/vottst.csv|./miMapper.[R|sh|out] | sort -n|./EjReducer.py
```

**16.-** Ahora lance el job con la API de Hadoop streaming y el archivo votación.  **Aprovecharemos para mostrar cómo se invoca la ejecución de varias tareas Reducer, lo que puede ser útil para procesar grandes volúmenes de datos**.

```bash
hdp>hadoop jar $STRJAR -input votacion.csv -output OpcionElectoral2  
-mapper miMapper.R -reducer EjReducer.py -file miMapper.R -file EjReducer.py -numReduceTasks 2
```
Observe que estamos especificando un nuevo directorio de salida.  Hadoop no permite reescribir archivos.

Verifique que obtuvo los mismos resultados, solo que en dos archivos de salida:

```bash
hdp>hdfs dfs -ls OpcionElectoral2
-rw-r--r--  1 root hdfs   0 2017-05-21  22:48 OpcionElectoral2/_SUCCESS
-rw-r--r--  1 root hdfs   0 2017-05-21  22:48 OpcionElectoral2/part-00000
-rw-r--r--  1 root hdfs   0 2017-05-21  22:48 OpcionElectoral2/part-00001

hdp>hdfs dfs -cat OpcionElectoral2/part-00000
CAND1  10056
CAND3  15051
CAND5  24991

hdp>hdfs dfs -cat OpcionElectoral2/part-00001
CAND2  9884
CAND4  40018
```
El ambiente decidió por sí mismo cómo distribuir las llaves entre los dos Reducers. De lo que podemos tener certeza, es que todos los registros con la misma llave, llegaron al mismo Reducer.
	
  **¡Felicidades!  Ahora puede escribir programas MapReduce en Java, R o Python!** 

## Ejercicios

Ahora que se ha familiarizado con el entorno Hadoop y con el despliegue de aplicaciones en distintos lenguajes de programación, desarrolle los códigos necesarios para responder a las siguientes preguntas.

Puede escribir los programas en el lenguaje de su elección. Debe entregar el código y los resultados obtenidos.

I.	¿Cuántos distritos electorales contiene el archivo votacion.csv?

II.	¿Cuántas encuestas se obtuvieron por distrito electoral? ¿En qué distrito se capturaron más encuestas? ¿En cuál menos?

III. ¿Cuántos votos obtuvo cada candidato en cada distrito electoral? ¿Cuántos obtuvo el candidato 1 en el distrito 1232? ¿Cuántos el candidato 5 en el distrito 9184?

IV. ¿Cómo se distribuyó el voto por género para cada candidato en cada distrito electoral? ¿En qué distrito y para qué candidato se obtuvo la menor preferencia electoral de los varones?

V.	Calcule el histograma de votación por hora para todo el proceso electoral.


#Anexo. Hortonworks sandbox
Junio 2017

Hortonworks Sandbox HDP es un ambiente de evaluación que se instala en una máquina virtual. Se descarga de la siguiente liga: [https://hortonworks.com/](https://hortonworks.com/products/sandbox/#install). Nosotros lo instalamos en VirtualBox.

Se siguió el tutorial de [Learning the ropes of the Hortonworks Sandbox.](https://es.hortonworks.com/hadoop-tutorial/learning-the-ropes-of-the-hortonworks-sandbox/). 

En primer lugar, se debe agregar el identificador sandbox.hortonworks.com al archivo `/etc/hosts` para la resolución de nombres de dominio:

```bash
echo 127.0.0.1 sandbox.hortonworks.com | sudo tee -a /etc/hosts
```

Se puede verificar que se ha instalado corretamente el ambiente si desde un navegador en el host se accede a la página de bienvenida en la dirección `127.0.0.1:8888`.

Si se desea lanzar el dashboard, se deben usar las contraseñas del tutorial que se desee seguir.  Puede probar, por ejemplo, con `user: maria_dev, passwd: maria_dev`.  Más adelante veremos cómo entrar como administrador y cómo cambiar las contraseñas.

Para la ejecución de comandos desde la terminal, las credenciales son `user: root, passwd: hadoop`.  Lo primero que se solicitará es cambiar la contraseña.  Se puede acceder de tres maneras:

1.- Desde el host via ssh (ese es el método que utilizaremos en las sesiones prácticas):

```bash
ssh root@127.0.0.1 -p 2222
```

2.- Desde un cliente de shell en web accediendo a la página `127.0.0.1:4200`

3.- Directamente entrando a la máquina virtual dando `ALT-F5`. Ojo: El host en esta VM no es sandbox.hortonworks.com


Para entrar al ambiente de sandbox y cambiar la contraseña de root, desde el host hacer:

```bash
ssh root@127.0.0.1 -p 4200
```

Para poder entrar a Ambari, es necesario cambiar la contraseña.  Se puede entrar desde una ventana con:

```bash
host>ssh root@127.0.0.1 -p 2222
hdp>ambari-admin-password-reset
hdp>usr:admin password: admin
```

Ahora sí, en un navegador en el host, se puede teclear `http:127.0.0.1:8080` y vemos una consola de administración Ambari todos los servicios que se levantaron en la sandbox.  En la segunda práctica utilizaremos este ambiente.  Por ahora trabajaremos desde la línea de comandos.

#### Acceso al servidor para practicar

1.- Acceder a la máquina para acceso remoto de la siguiente forma:

```bash
host>ssh ufdatos@148.205.50.194
```
La contraseña es `ft3sdat0s` (el 3er caracter es un tres y el penúltimo
un cero)

2.- Desde ahí acceder a la VM del sandbox HDP. Su cuenta es uXXXXX,
donde XXXXX es su clave única sin ceros a la izquierda, y su contraseña
es ft3sdat0s (la pueden cambiar dentro del sandbox con el comando passwd)

Por ejemplo, si mi clave unica es 000123456, entraría de esta forma:

```bash
vm>ssh u123456@127.0.0.1 -p 2222
passwd: ft3sdat0s
```


  



