# Análisis de bitácoras de redes móviles con Hadoop MapReduce. Práctica 2

**José Incera, Abril 2020**

## Objetivos

+  Mostrar la capacidad de las tecnologías de BigData para analizar y "descubrir" información contextual no relacionada directamente con el objeto de estudio.
+	Conocer algunos parámetros y métricas de calidad de servicio utilizadas en redes móviles
+	Aplicar los conocimientos del paradigma MapReduce sobre Hadoop para realizar un análisis de bitácoras de calidad de servicio (y de mercado) de redes móviles

### Entregables
La fecha de entrega es el lunes 4 de mayo a las 18:00.  Se entregan:

+ Las respuestas a las preguntas en el desarrollo
+ El código de los scripts y las respuestas de al menos cinco de las preguntas al final de la práctica
+ Un  reporte con **los resultados obtenidos** y, donde lo considere adecuado, **capturas de pantalla**.
+ Se permite trabajar en equipos de dos o tres personas

## Introducción

### Calidad de experiencia y calidad de servicio

El desempeño de un servicio de telecomunicaciones se mide de acuerdo a las necesidades o expectativas del usuario del servicio; esto se conoce como **calidad de la experiencia** (QoE) y define la calidad aceptable para el servicio, es subjetiva y depende del usuario [1]. 

Las expectativas que un usuario tiene sobre el desempeño de la red están fuertemente ligadas a las características de la misma, por lo que se busca relacionar la calidad de experiencia (subjetiva), a la evaluación de un conjunto de métricas cuantitativas (objetivas) sobre el comportamiento de la red.

La **calidad del servicio** (QoS) se define como un conjunto de parámetros medibles (métricas) que, dentro de ciertos límites, garantizan la calidad de la experiencia del usuario [2]. Para los servicios de transferencia de datos, que son los que se analizan en esta práctica, cuatro que sobresalen por su impacto potencial en la calidad de la experiencia son: el retardo o latencia, la variación en la latencia, la tasa de pérdida de paquetes y la velocidad de transferencia [3].

En los últimos años ha surgido un número creciente de herramientas de monitoreo basadas en aplicaciones para dispositivos móviles comerciales.  Su premisa central es que al medir los parámetros de calidad de servicio en los dispositivos que utilizan los usuarios, los resultados obtenidos dan una idea más precisa del comportamiento de las redes.  Ejemplos característicos de estas aplicaciones son Internet Speed Test [4] y Speed Test [5].

### Bitácoras de calidad de servicio

Imagine que se ha desarrollado una aplicación para dispositivos móviles que lanza periódicamente un proceso de evaluación de QoS y genera un registro con la información obtenida: parámetros de calidad de servicio (para transferencia de datos), características del operador que lo presta, coordenadas geográficas donde se demandó el servicio así como algunas características del dispositivo móvil utilizado, entre otros.

El anexo muestra todos los campos que conforman un registro de QoS en la bitácora.

Si la App es desplegada en (cientos de) miles de dispositivos, el análisis de estos registros dará una idea bastante precisa sobre la calidad del servicio que prestan los operadores móviles, así como de las características del sector móvil. Sin embargo, los archivos resultantes son de gran tamaño, lo que justifica el uso de herramientas de Big Data.

En esta práctica se desarrollarán algunas herramientas para un análisis básico de esta información.

## Desarrollo

### Preparación de datos

**1.** Conéctese al servidor:

```bash
$ ssh <su_cuenta>@148.205.176.167
password: 
$ 
```
**2.**  En su directorio `$HOME` cree la carpeta `Hdp-Pr2` con dos subcarpetas: `code` y `data`. 

```bash
$ cd
$ mkdir -p Hdp-Pr2/code
$ mkdir -p Hdp-Pr2/data
$ ls -l Hdp-Pr2
total 8
drxwr-xr-x 2 root root 4096 may 22 14:27 code
drxwr-xr-x 2 root root 4096 may 22 14:27 data
```

**3.-** Copie los archivos `Pr2mOSMap.py` y `Pr2mOSReduce.py` de la carpeta `home/jincera/DatosFD/Pr2` y guárdelos en la carpeta `code` creada anteriormente.  De la misma forma, descargue los archivos `RegQoS500k.csv.gz` y `EncabezadosRegQoS.txt`y guárdelo en la carpeta `data`.

```bash
$ cd $HOME/Hdp-Pr2/code
$ cp /home/jincera/DatosFD/Pr2/Pr2mOSMap.py .
$ cp /home/jincera/DatosFD/Pr2/Pr2mOSRed.py .
$ ls
Pr2mOSMap.py  Pr2mOSRed.py

$ cd ../data
$ pwd
/home/<su_cuenta>/Hdp-Pr2/data

$ cp /home/jincera/DatosFD/Pr2/RegQoS500k.csv.gz . 
$ cp /home/jincera/DatosFD/Pr2/EncabezadosRegQoS.txt 
$ ls
RegQoS.csv.gz EncabezadosRegQoS.txt
```

El archivo `RegQos.csv.gz` contiene una serie de registros que simula el ambiente siguiente:

+	Corrida del 3 de noviembre al 21 de diciembre de 2014
+	Mil dispositivos móviles
+	Quince zonas metropolitanas
+	Se generó un total de 500,000 registros

El archivo `EncabezadosRegQoS.txt` contiene únicamente el título de cada columna.

**3.**	Descomprima el archivo *RegQos.csv.gz*.  

```bash
$ cd $HOME/Hdp-Pr2/data
$ gunzip RegQos500k.csv.gz
```

**4.**	Prepare un archivo de prueba con los primeros 1000 registros. Podemos preparar el archivo de prueba sin descomprimir el archivo original:

```bash
gzip -cd RegQoS500k.csv.gz | head -1000 > regtst.csv
```

**5.**	Transfiera los archivos de datos `RegQoS500k.csv.gz` y `regtst.csv` a HDFS desde la línea de comandos (recuerde que el comando es `hdfs dfs -put`) y verifique que fueron transferidos (`hdfs dfs -ls`)

### Programación de scripts

Empecemos por desarrollar el código Map/Reduce para obtener la distribución de los sistemas operativos móviles (mOS) en el archivo.  Si el número de dispositivos con la App instalada es representativo del mercado nacional, esta distribución reflejará la participación de mercado de cada sistema operativo móvil.

El código de Map seleccionará el campo correspondiente (el cuarto campo) e imprimirá en la salida estándar ese campo (*key*) y un "1" (value).  El código Reduce simplemente sumará estas instancias.

**6.**	Con ayuda de un editor de textos verifique que los scripts que copió (`Pr2mOSMap.py`, `Pr2mOSRed.py`) tienen el código siguiente: 

```python
#!/usr/bin/python
# Código de mapper

import sys

for Line in sys.stdin:
    Data = Line.strip().split(",")
    if len(Data) == 19:
        imei,marca,mod,mos, exito,error,fecha,
        hora,mnc,tred,rb,lat,longi,db,
        tasaDn,tasaUp,tasaLoss,delay,jitter =Data
        print "{0}\t{1}".format(mos,1)	
```
```python
#!/usr/bin/python
# Código de reducer

import sys
acumulados = 0
MOSAnt = None

for line in sys.stdin:
    DataIn = line.strip().split("\t")
    if len(DataIn) != 2:
        # Hay algo raro, ignora esta linea
        continue

    esteMOS, esteValor  = DataIn

    if MOSAnt and MOSAnt!= esteMOS:
        print MOSAnt, "\t", acumulados
        MOSAnt = esteMOS;
        acumulados = 0

    MOSAnt = esteMOS
    acumulados += 1

if MOSAnt!= None:
    print MOSAnt, "\t", acumulados
```

**Asegúrese de entender qué hacen estos códigos**

**7.**	Con ayuda del encadenamiento de comandos en Linux, verifique que el código parece funciona correctamente.  Recuerde que quizás debe cambiar los permisos de ejecución de los archivos que contienen el código de los scripts.

```bash
cd ~/Hdp-Pr2/code 
cat ../data/regtst.csv |./Pr2mOSMap.py

...
Android  1
Android  1
Android  1
```

```bash
cat ../data/regtst.csv|./Pr2mOSMap.py|sort|./Pr2mOSRed.py
```

**¿Cuántos sistemas operativos móviles detectó en el archivo de prueba?**

**¿Cuál es su porcentaje de participación en el mercado? (Recuerde que el archivo tiene 1,000 registros)**


### Ejecución en Hadoop

Ahora que todo parece funcionar correctamente, se puede enviar el código para ser  ejecutado en Hadoop.  Revise la práctica anterior y utilice la API Hadoop streaming para enviar los archivos y ejecutar las tareas map y reduce en Hadoop.

**8.**	Es recomendable que primero ejecute las tareas con el archivo de prueba. Nombre al directorio de salida (opción -output) *distrMOStst*

Si todo se ejecutó correctamente,  encontrará en HDFS el directorio de salida y dentro de él, un archivo *part-00000*.  Revíselo:

```bash
$ hdfs dfs -cat distrMOStst/part-00000
```
**¿Los resultados coinciden con los obtenidos en Linux?  Si detectó alguna diferencia, ¿A qué cree que pueda deberse?**

**9.**	Ejecute nuevamente las tareas pero ahora invoque como archivo de entrada, el archivo con la bitácora de registros completa **y comprimido**. Hadoop se encargará de descomprimir el archivo para la ejecución.  

Recuerde que debe cambiar el nombre del directorio de salida.

**¿Cuántos sistemas operativos móviles detectó en la bitácora?**
**¿Cuál es su porcentaje de participación en el mercado? (Recuerde que se evaluaron 500,000 registros)**

**10.**	Revise la información desplegada en la pantalla por HDFS al ejecutar las tareas MapReduce

**¿Cuántos procesos map y reduce se utilizaron para evaluar la bitácora completa?**  

**¿Cuánto tiempo tomó procesar el archivo de bitácora?** 

**¿Cuánta memoria física se utilizó?**

**10.a** Veamos cuánto tiempo toma y cuánta memoria consume procesar el trabajo si el archivo fuente no está comprimido.

```bash
$ cd ~/Hdp-Pr2/data
$ gunzip RegQoS500k.csv.gz
$ hdfs dfs -put RegQoS500k.csv

$ hadoop jar /usr/hdp/current/hadoop-mapreduce-client/hadoop-streaming-2.7.3.2.6.0.3-8.jar -files Pr2mOSMap.py,Pr2mOSRed.py -input RegQoS500k.csv -output saleUnzip 
-mapper Pr2mOSMap.py -reducer Pr2mOSRed.py
```
Verifique que los resultados son los mismos que en el punto anterior, revise cuánta memoria física se consumió y cuánto tiempo tomó procesar el archivo.

**¿Qué conclusiones obtiene de estos resultados?**

El siguiente código  desplegaría la intensidad de señal por operador y global. Escriba los scripts y ejecútelos en Hadoop.

CUIDADO:  PYTHON ES MUY SENSIBLE A LA CORRECTA IDENTACIÓN DEL CÓDIGO

```python
#!/usr/bin/python
#EjMap

import sys

for Line in sys.stdin:
    Data = Line.strip().split(",")
    if len(Data) == 19:
        imei,marca,mod,mos, exito,error,fecha,
        hora,mnc,tred,rb,lat,longi,db,
        tasaDn,tasaUp,tasaLoss,delay,jitter =Data

       print "{0}\t{1}".format(mnc,db)
```

```python
#!/usr/bin/python
# EjReduce

import sys

dbGlobal=0.0 
regsGlobal=0
dbMNC=0.0
regsMNC=0
mncAnt = None

for line in sys.stdin:
    DataIn = line.strip().split("\t")
    if len(DataIn) != 2:
        continue

    esteMNC, estedb  = DataIn
    x= int(estedb)
   if x < -144 or x > -44:
      continue;
  
   if mncAnt  and mncAnt != esteMNC:
       if regsMNC !=0:
           avgdbMNC=dbMNC/regsMNC
           print mncAnt, "\t", avgdbMNC
       else:
           print mncAnt, "\t", 0.0

      dbMNC = 0.0
      regsMNC = 0

   mncAnt = esteMNC
   dbMNC += x
   regsMNC += 1
   dbGlobal += x
   regsGlobal += 1

if mncAnt != None:
   if regsMNC != 0:
           avgdbMNC=dbMNC/regsMNC
           print mncAnt, "\t",avgdbMNC
       else:
           print mncAnt, "\t",0.0

if regsGlobal != 0:
           avgdbGlobal=dbGlobal/regsGlobal
           print "Intensidad global: \t",avgdbGlobal
       else:
           print "Intensidad global: \t",0.0
```


**¿Cuál es la intensidad promedio que obtuvo en el archivo de prueba? ¿Cuál con todos los registros en la bitácora?**

**¿Qué operador móvil reportó la intensidad de señal más baja promedio durante el periodo evaluado? ¿Cuál la mayor intensidad de señal?**

## Ejercicios

Ahora que se ha familiarizado con el entorno Hadoop y con el despliegue de aplicaciones en Python, desarrolle los códigos necesarios para responder a las siguientes preguntas.  

Como en la práctica anterior, siéntase libre de desarrollar los scripts en Python, R, C++ o Java.

Debe entregar el código y las respuestas de al menos ocho de las preguntas.

I. Distribución en el mercado de: 
 +	Los operadores móviles
 +  Los fabricantes y los modelos de dispositivos móviles
 +  Las tecnologías de red desplegadas

II.	¿Qué operador ofrece qué tecnologías de red?

III. Distribución del tipo de dispositivo por operador 

IV. ¿Qué modelo de dispositivo tiene: 
 +  El retardo promedio más alto 
 +  El retardo promedio más bajo
 +  La mayor tasa de pérdida promedio, la menor tasa de pérdida promedio
 +  ¿Los datos sugieren que quizás se tenga una correlación entre retardos y tasas de pérdida? 

V. Porcentaje de registros con error.  Distribución de las causas de error

VI. Distribución de los fallos "red no disponible" por tipo de dispositivo y por operador móvil

VII. ¿Cuál es el operador que ofrece las más altas tasas de transferencia promedio de subida? ¿De bajada?

VIII.	Trate de obtener la distribución (histograma) de las tasas de transferencia, retardo y tasa de pérdida por (a) tecnología de red, y (b) por operador

IX.	Histograma con los valores globales de intensidad de señal

X.	Identifique las cinco radio bases que ofrecen, respectivamente, la  menor y la mayor latencia promedio. ¿Están asociadas a alguna tecnología de red en particular?


#### Trabajos citados
[1]	ITU-T, "P.10/G.100 Vocabulary for performance and Quality of Service," 2006.

[2]	ITU-T, "E.800 Definitions of terms related to quality of service," 2008.

[3]	Syed Asan Hussain, Active and Programmable Networks for Adaptive Architectures and Services.: Auerbach Publications, 2007.

[4]	V-Speed.eu. (2014) Internet Speed Test. [Online]. https://play.google.com/store/apps/details?id=pl.speedtest.android&hl=en

[5]	BeMobile. (2014) Speed Test. [Online]. https://play.google.com/store/apps/details?id=com.kbudev.speedtest&hl=en

[6]	ITU-T, QUALITY OF SERVICE AND DEPENDABILITY VOCABULARY, Quality of services; concepts, models, objectives, dependability planning.  Terms and definitions related to the quality of telecommunication services , 2008.

[7]	wikipedia. Wikipedia - Crowdsourcing. [Online]. http://en.wikipedia.org/wiki/Crowdsourcing



## Anexo. Formato de un registro QoE

1.	**Identificador de dispositivo**
*Descripción*:	Cadena que permite identificar de manera única al dispositivo.

*Formato*: 	Entero

*Nota*: 	En Android, este identificador sería el IMEI (International Mobile Equipment Identity).  iOS no es posible obtener el IMEI y, a partir de la versión 7, tampoco el identificador de dispositivo.  Sin embargo, sí se cuenta con un identificador particular instanciado para cada vendedor

2.	**Fabricante**

*Descripción*:	Nombre del fabricante del dispositivo.

*Formato*: 	String 

*Ejemplo*: Samsung, Motorola

3.	**Modelo**

*Descripción*:	Modelo del dispositivo

*Formato*: 	String 

*Ejemplo*:	XT919, Nexus 4 (Se consideran cuatro modelos para cada fabricante)

4.	**Sistema operativo**

*Descripción*:	Sistema operativo móvil del fabricante

*Formato*: 	String 

*Nota*:	Solamente se consideran dispositivos móviles con sistema operativo Android o iOS

5. **Éxito y código de error**

*Descripción*:	Indica si la prueba se realizó con éxito o, en caso contrario, la causa del error

*Formato*: Éxito: binario; código: string

*Rango*: Éxito: 1=éxito, 0=prueba fallida.
Código: NO HAY RED, Plan apagado

6.	**Fecha y hora**

*Descripción*:	Momento en que fue tomada la prueba 

*Formato*: 	dd/mm/aa HH:MM

7.	**MNC**

*Descripción*:	Mobile Network Code. Identificador del operador móvil

*Formato*: 	Entero

*Rango*: 	La siguiente tabla muestra los valores de los operadores considerados actualmente

020: Telcel

030: Movistar

040: Iusacell/Unefon

050: Iusacell

090: Nextel


8.	**Tipo de red**

*Descripción*:	Tipo de red en la que se está prestando el servicio

*Formato*: 	String 

*Rango*: La siguiente lista muestra los tipos de red considerados actualmente

1-GPRS

2-EDGE

3-UMTS

4-CDMA

5-EV_DO

6-HSPA

7-HSPA+

8-LTE

9-iDen

9. **Identificador de la radio base**

*Descripción*:	Identificador de la radio base que está brindando el servicio

*Formato*: Entero


10.	**Coordenadas**

*Descripción*: Latitud y Longitud del punto donde se inició la prueba

*Formato*: Dos números de punto flotante con precisión de 6 dígitos

11.	**Intensidad de señal**

*Descripción*:	Intensidad de la señal reportada en dbM 

*Formato*: 	Entero 

*Rango*: 	[-144 a -44]  

(-120 = Malo  -110 = pobre, -100=medio, -75=aceptable, -60=muy bueno)

12.	**Tasa de subida**

*Descripción*:	Velocidad para enviar datos del dispositivo a la red obtenida en las pruebas de QoS en Mb/s

*Formato*: 	Punto flotante 

13.	**Tasa de bajada**

*Descripción*:	Velocidad para enviar datos de la red al dispositivo obtenida en las pruebas de QoS en Mb/s

*Formato*: 	Punto flotante 

14.	**Tasa de pérdida**

*Descripción*:		Porcentaje de paquetes perdidos en las pruebas de QoS

*Formato*: 	Punto flotante  

15.	**Latencia**

*Descripción*:	Retardo de ida y vuelta medido en las pruebas de QoS, en mili segundos

*Formato*: Arreglo de enteros.  Se reportan valores mínimo, máximo y promedio

16.	**Variación de la latencia**

*Descripción*:	Variabilidad del retardo obtenido durante las pruebas de latencia, en mili segundos

*Formato*: 	Entero 



