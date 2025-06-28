# task_automation

Este programa permite crear una lista de acciones sencillas para automatizar tareas.

## Agregar acciones

Pulsa **Add Action** para elegir el tipo de acción:

1. **Click**: todas las pantallas se oscurecen y el cursor se vuelve una cruz. Haz clic en la posición deseada para guardar las coordenadas. Durante la ejecución el programa moverá el mouse y hará clic en ese punto.
2. **Sleep**: define un tiempo de espera (ahora admite decimales) antes de continuar con la siguiente acción.

Las coordenadas capturadas se almacenan como posiciones globales en píxeles, por lo que cada clic ocurre exactamente en el punto seleccionado, incluso con varias pantallas o diferentes escalados.

Las acciones agregadas se muestran en la lista principal y se ejecutarán en orden.

Si necesitas modificar algún paso, selecciona la acción en la lista y pulsa **Edit Action** para cambiar sus parámetros.

## Ejecutar

Selecciona el número de *Cycles* y presiona **Play** para repetir la secuencia de acciones.

## Modo de depuración

Activa la casilla **Debug** para mostrar un marcador rojo en cada coordenada
capturada y en cada clic ejecutado. En el registro se indican las coordenadas
globales obtenidas y la posición del mouse tras cada clic. Esto ayuda a
diagnosticar problemas si el cursor no coincide con el punto seleccionado.
