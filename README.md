# task_automation

Este programa permite crear una lista de acciones sencillas para automatizar tareas.

## Agregar acciones

Pulsa **Add Action** para elegir el tipo de acción:

1. **Click**: todas las pantallas se oscurecen y el cursor se vuelve una cruz. Haz clic en la posición deseada para guardar las coordenadas. Durante la ejecución el programa moverá el mouse y hará clic en ese punto.
2. **Sleep**: define un tiempo de espera (ahora admite decimales) antes de continuar con la siguiente acción.

Las coordenadas capturadas se ajustan automáticamente para configuraciones con varias pantallas y escalado de alta densidad, para que cada clic ocurra en el punto exacto seleccionado.

Las acciones agregadas se muestran en la lista principal y se ejecutarán en orden.

## Ejecutar

Selecciona el número de *Cycles* y presiona **Play** para repetir la secuencia de acciones.
