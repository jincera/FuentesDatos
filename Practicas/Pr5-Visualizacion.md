# Fuentes de Información

## Práctica 5: Publicación y Subscripción.  Visualizaciónde datos

### 1. Introducción

En esta práctica continuaremos con el proyecto de Internet de las Cosas en Fiware. En la práctica anterior nos familiarizamos con el componente central de Fiware, el Orion Context Broker (OCB), con el formato estandarizado de su API NGSIv2 y con su lenguaje para consultas. 

En esta ocasión introduciremos el muy importante concepto de **Suscripciones y Notificaciones** el cual utilizaremos para actualizar un panel para visualizar los datos generados por nuestros pseudo-objetos.  

Los temas que trataremos no son triviales, al menos  no la primera vez que se trabaja con ellos, por lo que iremos desarrollando el proyecto en etapas que a veces parecerán redundantes.  La intención es enfocarnos en un tema a la vez.

### Material

* La herramienta Insomnia
* Una cuenta en [Losant](https://www.losant.com)
* Un componente Orion Context Broker activo (de preferencia, el que utilizó en las prácticas anteriores)



### 2. Instrucciones

* La práctica se hace por binomios
* Tiempo de entrega: una semana  (28 de mayo)
* El reporte está conformado por:
  * Capturas de pantalla de cada ejercicio solicitado
  * Una **animación en video** (de preferencia en youtube) de la evolución de las gráficas y del display que se solicitan en la última sección



### 3. Suscripciones y notificaciones

En la práctica anterior estuvimos familiarizándonos con los métodos para crear, consultar y actualizar entidades en el Orion Context Broker. Sin embargo, en sistemas reales, una aplicación no debe estar consultando ("poleando") al OCB regularmente para conocer si ha habido un cambio en algún parámetro de interés (por ejemplo, si la temperatura ha rebasado un umbral en alguna habitación).  

En su lugar, es muy común utilizar un mecanismo a través del cual las entidades interesadas (por ejemplo, un individuo, una aplicación, una organización) expresan su intención en recibir notificiones sobre algún evento de interés (por ejemplo, el cambio en algún atributo) a través de un mecanismo de suscripciones.

El OCB cuenta con un mecanismo de notificaciones **asíncrono**. Básicamente, una aplicación se **suscribe** en el OCB para manifestarle su interés en recibir notificaciones cuando "algo suceda".  Si la entidad tiene una actualización que coincide con la suscripción registrada, se envía una notificación a la aplicación correspondiente.  El diagrama de flujo es básicamente el siguiente:

![](imagenes/flujosusc.JPG)

Este mecanismo es muy eficiente, pues por un lado reduce drásticamente el volumen de las consultas y el tráfico en la red. Por el otro, la aplicación encargada de recibir las notificaciones sólo se invocará cuando sea necesario.   

En la primera parte de esta práctica, en sustitución de la Aplicación utilizaremos alguna herramienta de depuración que permita ver el contenido enviado por las notificaciones.  Algunas herramientas de uso libre para ello son:

* [webhook.site](https://webhook.site/)
* [requestbin.net](http://requestbin.net/)
* [PutsReq.com](https://putsreq.com/)

Para esta práctica hemos lanzado un pseudo-servidor en PutsReq dando clic en el botón `Create a PutsReq`. 

<img src="imagenes/putsreq.JPG" alt="PutsReq" style="zoom:50%;" />



El URL que nos devuelve la herramienta es: `https://putsreq.com/LGc1rQucLcPpYEF5EHKa`

---

**EJERCICIO 1** Lance un pseudo-servidor con PutsReq para simular su Aplicación y muestre el URL correspondiente.

---

#### 3.1. Suscripciones

##### Registro

Una suscripción utiliza el método `POST`  en el punto `/v2/subscriptions` del OCB.  Vamos solicitar que se notifiquen los cambios de nivel de llenado (`fillingLevel`) de la entidad `ContenedorSTER-01`.  El método para ello es el siguiente:

```bash
http://XX.XX.XX.XX:1026/v2/subscriptions/
Método: POST
Headers: Content-Type:application/json
Body:
{
  "description": "Recibe notificaciones cuando el nivel de llenado del contenedor ha cambiado",
  "subject": {
    "entities": [
      {
        "id": "ContenedorSTER-01",
        "type": "WasteContainer"
      }
    ],
    "condition": {
      "attrs": [
        "fillingLevel"
      ]
    }
  },
  "notification": {
    "http": {
      "url": "https://putsreq.com/LGc1rQucLcPpYEF5EHKa"
    },
    "attrs": [
      "fillingLevel", "status", "temperature"
    ]
  },
  "expires": "2040-01-01T14:00:00.00Z",
  "throttling": 5
}
```

Este mensaje significa lo siguiente:

* El campo `entities` indica para qué entidad se hace el registro de la suscripción.

* El campo `attrs` dentro de `notifications` define el contenido de los mensajes de notificación: Se notifican los atributos `fillingLevel`, `status` y `temperature` de la entidad `ContenedorSTER-01`

* El campo `conditions` indica la condición que se debe cumplir para lanzar una notificación. En este caso, la notificación se lanzará simplemente cuando se actualice el atributo `fillingLevel`.

  Se puede tener una lista de atributos, en cuyo caso, la notificación se dispara si cualquiera de los atributos en la lista cambia (más específicamente, si la condición establecida como se verá más adelante, se cumple).  Hay que considerar la lista de atributos como una relación lógica OR.

  El atributo de condición y los atributos en la notificación, no tienen que ser los mismos. Por ejemplo, se puede consultar el atributo *status* y notificar el atributo *temperature*. 
  Puede dejar `conditions.attrs` vacíos para que cualquier  cambio de atributo de la entidad desencadene una notificación  (independientemente del nombre del atributo). 

* El campo `url` indica la URL donde está la aplicación que desea ser notificada. Sólo se permite una URL por suscripción. Sin embargo, se pueden tener varias suscripciones con distintas URLs en los mismos elementos de  contexto (es decir, la misma entidad y atributo). 

* Las suscripciones pueden tener una fecha de vencimiento (campo `expires`) especificado usando el formato estándar ISO 8601. Una vez que la  suscripción sobrepasa esa fecha, simplemente se ignora (sin embargo, aún se encuentra almacenada en la base de datos del OCB). Si se omite este campo, las suscripciones son permanentes (aunque pueden ser eliminadas). 
  Es posible ampliar la duración de una suscripción actualizándola (como  se describe más adelante). En el ejemplo se utiliza una fecha lo  suficientemente lejos en el tiempo (año 2040). 

* El campo `throttling` es opcional. Si se especifica, indica el intervalo mínimo en segundos entre una notificación y otra.  Eso permite reducir el número de notificaciones enviadas si la(s) condición(es) indicada(s) está(n) cambiando muy rápidamente, quizás por estar en una fase transitoria, por ejemplo.

Al registrar la subscripción, el OCB regresa un código HTTP 201 si la suscripción se creó exitosamente.  En el cuerpo de la respuesta se indica el identificador de la suscripción, que consiste en un número hexadecimal de 24 caracteres.  Este identificador es necesario para actualizar, suspender o eliminar la suscripción.

![](imagenes/susc1.JPG)

---

**EJERCICIO 2**  Registre una suscripción para alguna de las entidades que cargó en el OCB en la práctica anterior, apuntando hacia el pseudo-servidor que dio de alta en el ejercicio 1.  **La notificación se activa con el atributo `status` y reporta la temperatura.**

---

##### Otras operaciones

* Se pueden consultar las subscripciones resultadas con el método `GET` en la sección `/v2/subscriptions`, una sola suscripción especificando su identificador:  `GET http://.../v2/subscriptions/{subId}` 
* Las suscripciones se pueden actualizar utilizando la operación `PATCH /v2/subscription/{subId}`. 
* Una suscripción puede ser eliminada utilizando la operación `DELETE /v2/subscriptions/{subId}`. 

- Una suscripción puede ser pausada. Para hacer eso, se asigna al atributo `status` el valor `inactive`. Si desea reanudar la suscripción, se asigna el valor `active`:

```java
Método: PATCH 
URL:<XX.XX.XX.XX>:1026/v2/subscriptions/{subId}
  "status": "inactive"
}
```

---

**EJERCICIO 3.** 

* Registre una nueva suscripción apuntando a la misma pseudo-aplicación que se active con la temperatura y reporte la temperatura.   
* Muestre que las dos suscripciones están en el OCB. 
* Cambie su estado a inactiva
* Borre la suscripción

---



#### 3.2 Notificaciones

El OCB enviará una notificación cada vez que se actualiza alguna de las condiciones especificada en al suscrpición. Además, se envía una notificación en cuanto se registra la suscpripción (llamada *initial notification*). Esta notificación incluye a todas las entidades consideradas en la suscripción (se pueden utilizar caracteres comodines).  Si se desea evitar esta notificación inicial, en el registro de la suscrpición se puede agregar la opción `skipInitialNotification`:

- `POST /v2/subscriptions?options=skipInitialNotification`
- `PATCH /v2/subscriptions/?options=skipInitialNotification`

Veamos ahora cómo se presenta una notificación.

* En Insomnia, haremos la actualización del atributo `fillingLevel`para la entidad ContenedorSTER-01:

```java
http://XX.XX.XX.XX:1026/v2/entities/ContenedorSTER-01/attrs
Método: POST
Headers: Content-Type:application/json
Body:
{
  "fillingLevel": {
    "value": 0.3
  }
}
```

* Ahora vemos en la página de nuestra pseudo-aplicación en `PutsReq` el resultado:

![](imagenes/notif.JPG)



Efectivamente, se ha recibido el nuevo valor de `fillingLevel` y los valores de los demás atributos almacenados en el OCB como se indicó en la notificación.

---

**EJERCICIO 4**. Ahora le toca a usted.  Haga un cambio en el atributo que detona la notificación en su sucripción y muestre el resultado de la notificación.

___



#### 3.3 Algunas optimizaciones

El Orion Context Broker ofrece muchas funcionalidades adicionales para el registro de suscripciones y para el formato de las notificaciones. Por ejemplo, en vez de disparar una notificación cada vez que cambie un atributo, se puede especificar una expresión. Si ésta se cumple, se dispara la notificación.

En el siguiente ejemplo, *modificaremos* nuestra subscripción para que la notificación se dispare sólo si el nivel rebasa el 85%.  Además, solicitaremos que los datos se presenten como *keyValues*, en vez de JSON:

```bash
http://XX.XX.XX.XX:1026/v2/subscriptions/{subscriptionId}
Método: PATCH
Headers: Content-Type:application/json
Body:
{
  "subject": {
    "entities": [
      {
        "id": "ContenedorSTER-01",
        "type": "WasteContainer"
      }
    ],
    "condition": {
      "attrs": [
        "fillingLevel"
      ],
			"expression": {
				"q": "fillingLevel > 0.85"
			}
    }
  },
  "notification": {
    "http": {
      "url": "https://putsreq.com/LGc1rQucLcPpYEF5EHKa"
    },
		 "attrsFormat": "keyValues",
    "attrs": [
      "fillingLevel", "status", "temperature"
    ]
  }
}
```



Al modificar la suscripción, podemos confirmar que si se actualiza nivel a un valor menor a 85%, no se envía notificación, pero si es mayor, se envía notificación y su formato es en parejas key-value:

![](imagenes/notif2.JPG)

---

**EJERCICIO 5**. 

* Modifique su suscripción para que se envíen notificaciones si la temperatura rebasa los 30 grados
* Haga una nueva suscripción que envíe notificaciones si la temperatura es inferior a 17 grados
* Los datos en la notificación deben ser reportados como `keyValues
* Muestre que las notificaciones funcionan como se espera

---



Es posible reducir sustancialmente los datos que envía la notificación. De hecho, es posible solicitar que únicamente envíe el valor del atributo especificando `"attrsFormat":"values"`. 

De forma similar, se puede personalizar el formato de la notificación HTTP con la propiedad `httpCustom`.  En particular, se pueden hacer sustituciones de variables con la sintaxis `${...}`, donde entre las llaves se puede poner:

* `${id}`, se remplaza con el identificador de la entidad;
* `${type}` se remplaza con el tipo de la entidad;
* Cualquier otro atributo se remplaza con el valor de ese atributo o con un string nulo si el atributo no está incluido en la notificación.

En el siguiente ejemplo, se modifica la notificación para que el contenido sea texto plano y envíe una frase con el identificador de la entidad, su estado, temperatura y nivel de llenado.

```bash
"httpCustom": {
      "url": "https://putsreq.com/LGc1rQucLcPpYEF5EHKa",
			"headers": {
				"Content-Type":"text/plain"
								 },
			"payload":"El contenedor ${id} se encuentra ${status}, su temperatura es de ${temperature} grados con un nivel de ocupación de ${fillingLevel}"
    },
    "attrs": [
      "temperature", "status", "fillingLevel"
    ]
},
```

Al disparar la notificación, el mensaje HTTP recibido en nuestra pseudo-aplicación es:

![](imagenes/notif3.JPG)



---

**EJERCICIO 6**   Modifique la notificación para poder desplegar un texto solamente con el valor del atributo temperatura de esta forma:  T: xx 

---



### 4. Panel de Visualización

En un proyecto integral de Internet de las Cosas (IoT) es muy frecuente que se requiera de paneles o tableros de mando (*Dashboard*) para poder observar cómo evolucionan los parámetros de interés que están siendo monitoreados por los sensores. 

Existen muchas herramientas que permiten crear paneles para desplegar información visual (displays, gráficas, mapas, etc.).  En el entorno de IoT, la visualización es sólo una de las muchas acciones que se pueden realizar con los datos capturados por los dispositivos conectados a Internet.  Por ello, han surgido muchísimas plataformas que, además de la representación gráfica, permiten hacer analítica, procesamiento de eventos complejos, almacenamiento en lagos de datos, entre otros. 

Muchas de ellas, son  de hecho, alternativas al ecosistema Fiware, si bien no tienen ni la interfaz estandarizada, ni la riqueza y variedad de componentes genéricos (GE, *Generic Enablers*) de uso libre que ofrece Fiware.

Recientemente los tutoriales de Fiware recomiendan la herramienta [Grafana](http://grafana.com). Dado que los datos no sólo se utilizan para su visualización, se recomienda que Grafana "consuma" los datos desde otro componente genérico, [QuantumLeap](https://quantumleap.readthedocs.io/en/latest/), que almacena los datos en una base de datos orientada a series de tiempo para agilizar las consultas de información temporal.  

Sin embargo, este método requiere que QuantumLeap se agregue a la red formada por los demás componentes (OCB y la base de datos MongoDB), lo cual rebasa el alcance de este tutorial. 

Por ello, en esta práctica utilizaremos sólo los componentes de visualización de una de las plataformas para IoT: [Losant](https://www.losant.com). Siéntase libre de experimentar con cualquier otra plataforma como [ThingsBoard](https://thingsboard.io) [Kaa](https://www.kaaproject.org/), [thinger](https://thinger.io/) o [DeviceHive](https://www.devicehive.com/#home) ): Los conceptos básicos que veremos en esta práctica son  parecidos entre ellas.

#### 4.1 Creación de una aplicación

Losant es una plataforma muy poderosa para integración de proyectos de IoT que facilita la ingesta, integración y visualización de datos generados por los dispositivos conectados a Internet. Permite desplegar un ambiente de prueba (sandbok) gratuito en la nube, que es lo que utilizaremos en esta práctica.



1. Ingrese a la página de [Losant](https://www.losant.com/iot-platform/sandbox) y seleccione `IoT PLATFORM DEMOS/DEVELOPER SANDBOX`. De clic en `START BUILDING FOR FREE`

![](imagenes/losant1x.JPG)



2. Se le pedirá que ingrese a través de su cuenta en `GitHub` o que cree una nueva cuenta.  No se le solicitará ninguna cuenta bancaria.



![](imagenes/losant2x.JPG)

3. Una vez que ha creado la cuenta, puede recorrer el tutorial (Losant Walkthrough, que merece mucho la pena) o dar clic directamente en  `Add Application/Blank Application`. En la forma que aparece, de un nombre representativo y de clic en `Create Application`.

<img src="imagenes/losant3.JPG" style="zoom:67%;" />

4. Ahora vamos a agregar una instancia de un dispositivo.  De clic en `Add Device/Standalone`, pues nuestro "dispositivo" será capaz de comunicarse directamente con la plataforma sin necesidad de acceder a un Gateway.

   En la forma que aparece, asigne un nombre apropiado a su instancia y de clic en `Create Device`.

<img src="imagenes/losant4.JPG" style="zoom:67%;" />



5. Un dispositivo debe tener atributos. Para nuestro contenedor, añadiremos los atributos `temperature` cuyo tipo es `Number`, `fillingLevel`, también tipo `Number`, y `status` tipo `string`. Damos clic en `Update Attributes`.



<img src="imagenes/losant5.JPG" style="zoom:67%;" />



---

**EJERCICIO 7.** Cree una cuenta, una aplicación y añada un dispositivo "WasteContainer" en Losant

---



#### 4.2. Enviar datos del "dispositivo" a la entidad en Losant

Por seguridad, en Losant, todas las conexiones están protegidas con distintos niveles de seguridad. En la **comunicación REST** entre el "dispositivo", simulado por la aplicación Insomnia y nuestra aplicación, necesitaremos de tres elementos: El identificador del dispositivo (`deviceId`), el de la aplicación (`ApplicationId`) y un token de acceso de la aplicación (`API Token`).



1. Puede obtener el identificador del dispositivo dando clic a `Devices` en el panel izquierdo. Para copiarlo al porta-papeles, de clic en el ícono al lado del identificador.

<img src="imagenes/losant6.JPG" style="zoom:50%;" />



2. De forma similar, para obtener el identificador de la aplicación, de clic en el ìcono de `Applications` (el cubo rojo en el menú del extremo izquierdo) o en el nombre de su aplicación arriba a la izquierda.  Aparacera el canvas de su aplicación  De clic en el ícono al lado del identificador

<img src="imagenes/losant7.JPG" style="zoom:67%;" />



3. Para el token de acceso, de clic en `API Tokens` en el menú de la izquierda y en `Add Application Token`



![](imagenes/losant8.JPG)

En la forma que aparece, asigne un nombre apropiado, deje los demás parámetros con el valor por omisión y de clic en `Create Application Token`.  **Losant no lo almacena**, por lo que es muy importante que lo guarde en un archivo.  Lo necesitaremos más adelante.   

Después de guardar el archivo, de clic en la leyenda y en `Close Window`



##### Actualización directa

Muy bien. Tenemos todo lo necesario para enviar actualizaciones de los atributos de nuestro dispositivo a través de la API REST, desde Insomnia.  

Para observar los intentos de conexión, o los datos enviados por un productor, damos clic en `Devices`, y en nuestro sensor para poder acceder a la bitácora en tiempo real que se encuentra en  el extremo derecho de la pantalla.

<img src="imagenes/losant9.JPG" style="zoom:67%;" />



El `EndPoint` de la API REST para modificar los atributos (el `estado` en Losant) de un dispositivo utiliza el método `POST` hacia el URL: 

`api.losant.com/applications/{ApplicationId}/devices/{deviceId}/state`.   
**Sustituimos {ApplicationId} y {deviceId} por los valores indicados en los puntos 1 y 2 de la sección anterior**.



En el cuerpo del método formamos un objeto JSON con los atributos y los valores a enviar a Losant.  El formato es ligeramente distinto al que utilizamos en la práctica anterior, pues es una combinación de JSON y key-values:

```java
{
	"data": {
		"fillingLevel": 0.5,
		"temperature": 23,
		"status": "ok"
	}
}
```



Este mensaje debe ir **autenticado**. Para ello, en Insomnia agregaremos un encabezado de Autenticación dando clic en la pestaña `Auth` y seleccionamos `Bearer Token`.  En el campo `TOKEN` colocamos el `API Token` que guardamos en el archivo, como se indicó en el punto 3 de la sección anterior.

![](imagenes/losant10.JPG)



Si todo está bien, al dar clic en Insomnia, podrá verificar en la bitácora en Losant que se recibió el mensaje y que han llegado los atributos: 

![](imagenes/losant11.JPG)

---

**EJERCICIO 8**. Ahora es su turno. Configure el método POST en Insomnia y envíe una actualización de atributos a su dispositivo en Losant

---



#### 4.3 Panel de visualización

Ahora que hemos logrado enlazar nuestro "dispositivo" con Losant, podremos agregar un panel de visualización.  Estará conformado por cinco elementos (*widgets* o *blocks*): Dos gráficas lineales que muestran cómo evolucionan en el tiempo la temperatura y el nivel del contenedor, dos indicadores del último valor de temperatura y nivel de ocupación, y un indicador del status del contenedor.



1. En el panel de la izquierda de clic en `Dashboards/Add Dashboard` (o en el botón del canvas del contenedor en la figura anterior). Asigne un nombre apropiado para su panel y de clic en `Create Dashboard`. De clic en `Add Block`.
2. Para la serie de tiempo de temperatura, seleccione `Time Series Graph` y llene la forma que aparece:
   *  *Block Heder Text*: Temperatura del contenedor
   *  *Data Type*: Historical
   *  *Duration*: 60 minutes; *Resolution*: 30 seconds
   *  *Attribute*: temperature
   *  *Y Axis Min*: 0;  *Y Axis Max*: 100
   *  De clic en `Add Block`

3. De clic en el ícono de engrane para agregar un segundo bloque para el último valor de la temperatura. Seleccione `Gauge` y llene la forma que aparece:
	*  *Block Heder Text:* Último valor de temperatura
	* *Attribute*: Temperature;   *Aggregation*: Last
	* *Gauge Type*: Thermometer
	  * *Label*: Temperatura
	  * *Min*: 0;   *Max*: 100
	* *Precision Type*: Significant Digits;  *Digits*: 2 

---
**EJERCICIO 9.** Continúe agregando bloques para completar el panel.  Deberá ser similar al que se muestra en la figura. Observe que los valores de nivel de ocupación se dan en porcentajes. 


![](imagenes/losant12.JPG)

---



#### 4.4 Actualización por notificaciones

Por último, no deseamos que el dispositivo actualice directamente el panel, sino que esto se haga a través de una notificación.  Vamos a suscribir tres notificaciones.  

* Si hay un cambio en el nivel o la temperatura

* Si hay cambio en el status

* Si el nivel rebasa 85%. Para este caso, debe añadirse un indicador adicional que normalmente indica "NIVEL ACEPTABLE" y cambia a  "VACIAR CONTENEDOR" mientras el nivel esté por arriba de 85%.   

  

##### Cambio de nivel o temperatura

Registraremos una nueva suscripción en el OCB. Pondremos en las condiciones los atributos `fillingLevel` y `temperature` sin ninguna `expression`.  

La notificación es un poco más complicada: Debe contener el URL que utilizamos en la sección anterior para actualizar el panel, junto con el encabezado de autenticación. Observe más adelante que antes del `API Token` se debe añadir la palabra `Bearer`.  El cuerpo del mensaje debe tener una estructura similar a la del objeto JSON utilizada en la sección 4.2.  

Tenemos una complicación adicional pues por seguridad, el OCB prohíbe que se utilicen algunos caracteres en el cuerpo de un mensaje, entre ellos están las comillas dobles y las llaves.  Como necesitamos esos caracteres, utilizaremos su representación ASCII hexadecimal precedida del caracter "%".  Las comillas dobles se representarán con %22, la llave de apertura, "{", con %7B y la de cierre, "}", con %7D.

De esta manera, el cuerpo de la suscripción queda así:

```java
{
  "description": "Suscripción por cambio de temperatura o nivel en losant",
  "subject": {
    "entities": [
      {
        "id": "ContenedorSTER-01",
        "type": "WasteContainer"
      }
    ],
    "condition": {
      "attrs": [
        "temperature", "fillingLevel"
      ]
    }
  },
  "notification": {
    "httpCustom": {
      "url": "http://api.losant.com/applications/5ec025691ac8cb0006240eae/devices/5ec0260f85ea2400067944b8/state",		
			 "headers": {
         "Content-Type": "application/json",
				 "Accept":"application/json",
				  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZWMwMzI4YTg1ZWEyNDAwMDY3OTQ0ZDciLCJzdWJ0eXBlIjoiYXBpVG9rZW4iLCJzY29wZSI6WyJhbGwuQXBwbGljYXRpb24iXSwiaWF0IjoxNTg5NjU0MTU0LCJpc3MiOiJhcGkuZ2V0c3RydWN0dXJlLmlvIn0.SUccplEohfezwdUANj6AZCR1qtC7EtEVLtmNqFe2SMI"
      },
      "method": "POST",
			"payload":"{ %22data%22:%7b%22temperature%22: ${temperature}, %22fillingLevel%22:${fillingLevel}%7D}"
		},
    "attrs": [
      "temperature", "fillingLevel"
    ]
  }
}
```



Para verificar que la notificación está cumpliendo su función, enviaremos actualizaciones de los atributos **al Orion Context Broker**. Si los atributos afectados son `temperature` o `fillingLevel`, los nuevos valores se verán reflejados en el panel:



![](imagenes/doslecturas.JPG)



##### Cambio en el status

Con lo visto hasta ahora, esta suscripción será bastante trivial: Duplicamos en  Insomnia la suscripción anterior, le cambiamos de nombre y hacemos las adecuaciones correspondientes en los campos `condition-attrs`, `notification.payload` y `notification.attrs`:

```java
{
  "description": "Suscripción por cambio de status",
  "subject": {
    "entities": [
      {
        "id": "ContenedorSTER-01",
        "type": "WasteContainer"
      }
    ],
    "condition": {
      "attrs": ["status"]
    }
  },
  "notification": {
    "httpCustom": {
      "url": "http://api.losant.com/applications/5ec025691ac8cb0006240eae/devices/5ec0260f85ea2400067944b8/state",		
			 "headers": {
         "Content-Type": "application/json",
				 "Accept":"application/json",
				  "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1ZWMwMzI4YTg1ZWEyNDAwMDY3OTQ0ZDciLCJzdWJ0eXBlIjoiYXBpVG9rZW4iLCJzY29wZSI6WyJhbGwuQXBwbGljYXRpb24iXSwiaWF0IjoxNTg5NjU0MTU0LCJpc3MiOiJhcGkuZ2V0c3RydWN0dXJlLmlvIn0.SUccplEohfezwdUANj6AZCR1qtC7EtEVLtmNqFe2SMI"
      },
      "method": "POST",
			"payload":"{ %22data%22:%7b%22status%22:%22${status}%22%7D}"
		},
    "attrs": [ "status" ]
  }
}
```



---

**EJERCICIO 10.**  Agregue la notificación para cuando el nivel exceda un 85% de ocupación.  Recuerde que tendrá que agregar un indicador adicional a su panel. 

De hecho, tendrá que agregar una segunda notificación para que cuando el nivel baje del umbral, el mensaje en el nuevo indicador cambie.

---



**EJERCICIO 11.**  Haga un video (existen muchas herramientas para ello, inclusive en Windows 10) mostrando cómo, al hacer cambios en los atributos de la entidad *En el Orion Context Broker*, se reflejan los cambios en el Panel gracias al mecanismo de Suscripción-Notificación.



¡Muchas felicidades!   Ha logrado asimilar los conceptos básicos de casi todos los componentes utilizados al desplegar aplicaciones de IoT en la nube.

