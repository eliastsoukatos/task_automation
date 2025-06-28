# task_automation

Este programa permite crear una lista de acciones sencillas para automatizar tareas.

## Agregar acciones

Utiliza los botones **Add Click** y **Add Sleep** para crear tu secuencia de acciones.

1. **Add Click** abre el selector de coordenadas. Todas las pantallas se oscurecen y el cursor se vuelve una cruz. Haz clic en la posición deseada para guardar las coordenadas. Si tienes activado **Automatic Sleep**, justo después se agrega un Sleep con la duración configurada.
2. **Add Sleep** te permite definir un tiempo de espera (admite decimales) antes de continuar con la siguiente acción.

Las coordenadas capturadas se almacenan como posiciones globales en píxeles, por lo que cada clic ocurre exactamente en el punto seleccionado, incluso con varias pantallas o diferentes escalados.

Las acciones agregadas se muestran en la lista principal y se ejecutarán en orden.

Si necesitas modificar algún paso, selecciona la acción en la lista y pulsa **Edit Action** para cambiar sus parámetros.

## Guardar ciclos de acciones

Pulsa **Save Cycle** para guardar la lista actual de acciones con un nombre. Los ciclos guardados aparecen en la sección **Saved Cycles**, donde puedes renombrarlos, eliminarlos o insertarlos en la secuencia actual.

## Componer secuencias

Con los botones de **Insert**, puedes añadir un ciclo guardado al final de la lista de acciones. De esta forma es posible combinar varios ciclos y acciones sueltas antes de ejecutar la macro.

## Ejecutar

Selecciona el número de *Cycles* y presiona **Play** para repetir la secuencia de acciones.

## Modo de depuración

Activa la casilla **Debug** para mostrar un marcador rojo en cada coordenada
capturada y en cada clic ejecutado. En el registro se indican las coordenadas
globales obtenidas y la posición del mouse tras cada clic. Esto ayuda a
diagnosticar problemas si el cursor no coincide con el punto seleccionado.
