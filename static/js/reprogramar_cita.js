document.addEventListener("DOMContentLoaded", () => {
    const contenedor = document.getElementById(
        "contenedor-reprogramacion"
    );

    if (!contenedor) {
        return;
    }

    const calendarioDias = document.getElementById(
        "calendario-dias"
    );

    const tituloMes = document.getElementById(
        "titulo-mes"
    );

    const botonMesAnterior = document.getElementById(
        "mes-anterior"
    );

    const botonMesSiguiente = document.getElementById(
        "mes-siguiente"
    );

    const listaHorarios = document.getElementById(
        "lista-horarios"
    );

    const cargandoHorarios = document.getElementById(
        "cargando-horarios"
    );

    const fechaSeleccionadaTexto = document.getElementById(
        "fecha-seleccionada-texto"
    );

    const campoFecha = document.getElementById(
        "nueva-fecha"
    );

    const campoHora = document.getElementById(
        "nueva-hora"
    );

    const resumenNuevaFecha = document.getElementById(
        "resumen-nueva-fecha"
    );

    const resumenNuevaHora = document.getElementById(
        "resumen-nueva-hora"
    );

    const formulario = document.getElementById(
        "formulario-reprogramacion"
    );

    const botonConfirmar = document.getElementById(
        "boton-confirmar-reprogramacion"
    );

    const mensajeValidacion = document.getElementById(
        "mensaje-validacion"
    );

    const urlDisponibilidad =
        contenedor.dataset.urlDisponibilidad;

    const urlHorarios =
        contenedor.dataset.urlHorarios;

    const fechaActual =
        contenedor.dataset.fechaActual || "";

    const horaActual =
        contenedor.dataset.horaActual || "";

    const hoy = new Date();

    hoy.setHours(0, 0, 0, 0);

    let mesVisible = new Date(
        hoy.getFullYear(),
        hoy.getMonth(),
        1
    );


    function escaparTexto(texto) {
        const elemento = document.createElement("div");

        elemento.textContent = texto || "";

        return elemento.innerHTML;
    }


    function fechaDesdeISO(fechaTexto) {
        if (!fechaTexto) {
            return null;
        }

        const partes = fechaTexto
            .split("-")
            .map(Number);

        if (
            partes.length !== 3
            || partes.some(Number.isNaN)
        ) {
            return null;
        }

        return new Date(
            partes[0],
            partes[1] - 1,
            partes[2]
        );
    }


    function formatearMes(fecha) {
        const texto = new Intl.DateTimeFormat(
            "es-EC",
            {
                month: "long",
                year: "numeric",
            }
        ).format(fecha);

        return (
            texto.charAt(0).toUpperCase()
            + texto.slice(1)
        );
    }


    function formatearFecha(fechaTexto) {
        const fecha = fechaDesdeISO(fechaTexto);

        if (!fecha) {
            return "Sin seleccionar";
        }

        return new Intl.DateTimeFormat(
            "es-EC",
            {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric",
            }
        ).format(fecha);
    }


    function mostrarMensaje(mensaje) {
        mensajeValidacion.textContent = mensaje;

        mensajeValidacion.classList.remove(
            "oculto"
        );
    }


    function ocultarMensaje() {
        mensajeValidacion.textContent = "";

        mensajeValidacion.classList.add(
            "oculto"
        );
    }


    function actualizarResumen() {
        resumenNuevaFecha.textContent =
            campoFecha.value
            ? formatearFecha(campoFecha.value)
            : "Sin seleccionar";

        resumenNuevaHora.textContent =
            campoHora.value
            ? campoHora.value.slice(0, 5)
            : "Sin seleccionar";
    }


    function actualizarBotonMesAnterior() {
        const mesActual = new Date(
            hoy.getFullYear(),
            hoy.getMonth(),
            1
        );

        botonMesAnterior.disabled =
            mesVisible <= mesActual;
    }


    async function cargarCalendario() {
        tituloMes.textContent =
            formatearMes(mesVisible);

        actualizarBotonMesAnterior();

        calendarioDias.innerHTML = `
            <div class="estado-cargando calendario-vacio">
                <span class="cargador"></span>

                <p>
                    Cargando disponibilidad...
                </p>
            </div>
        `;

        try {
            const parametros = new URLSearchParams({
                anio: String(
                    mesVisible.getFullYear()
                ),

                mes: String(
                    mesVisible.getMonth() + 1
                ),
            });

            const respuesta = await fetch(
                `${urlDisponibilidad}?${parametros}`
            );

            const datos = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    datos.error
                    || "No se pudo cargar el calendario."
                );
            }

            renderizarCalendario(datos);

        } catch (error) {
            calendarioDias.innerHTML = `
                <div class="estado-vacio calendario-vacio">
                    <span>⚠️</span>

                    <strong>
                        No se pudo cargar el calendario
                    </strong>

                    <p>
                        ${escaparTexto(error.message)}
                    </p>
                </div>
            `;
        }
    }


    function renderizarCalendario(datos) {
        calendarioDias.innerHTML = "";

        for (
            let indice = 0;
            indice < datos.primer_dia_semana;
            indice += 1
        ) {
            const espacio = document.createElement(
                "span"
            );

            espacio.className = "dia-vacio";

            calendarioDias.appendChild(
                espacio
            );
        }

        datos.dias.forEach((dia) => {
            const boton = document.createElement(
                "button"
            );

            boton.type = "button";

            boton.className =
                `dia-calendario ${dia.estado}`;

            boton.textContent = String(
                dia.dia
            );

            boton.dataset.fecha = dia.fecha;

            if (dia.es_fecha_actual) {
                boton.classList.add(
                    "fecha-actual"
                );

                boton.title =
                    "Fecha actual de la cita";
            }

            if (
                campoFecha.value
                && campoFecha.value === dia.fecha
            ) {
                boton.classList.add(
                    "seleccionada"
                );
            }

            if (dia.estado !== "disponible") {
                boton.disabled = true;

                boton.setAttribute(
                    "aria-disabled",
                    "true"
                );

            } else {
                boton.addEventListener(
                    "click",
                    () => seleccionarFecha(
                        dia.fecha
                    )
                );
            }

            calendarioDias.appendChild(
                boton
            );
        });
    }


    async function seleccionarFecha(
        fechaSeleccionada,
        restaurarHora = ""
    ) {
        ocultarMensaje();

        campoFecha.value =
            fechaSeleccionada;

        campoHora.value = "";

        document
            .querySelectorAll(".dia-calendario")
            .forEach((dia) => {
                dia.classList.toggle(
                    "seleccionada",
                    dia.dataset.fecha
                    === fechaSeleccionada
                );
            });

        fechaSeleccionadaTexto.textContent =
            formatearFecha(
                fechaSeleccionada
            );

        actualizarResumen();

        listaHorarios.classList.add(
            "oculto"
        );

        cargandoHorarios.classList.remove(
            "oculto"
        );

        try {
            const parametros = new URLSearchParams({
                fecha: fechaSeleccionada,
            });

            const respuesta = await fetch(
                `${urlHorarios}?${parametros}`
            );

            const datos = await respuesta.json();

            if (!respuesta.ok) {
                throw new Error(
                    datos.error
                    || "No se pudieron cargar los horarios."
                );
            }

            renderizarHorarios(
                datos.horas,
                restaurarHora
                || datos.hora_actual
                || ""
            );

        } catch (error) {
            listaHorarios.innerHTML = `
                <div class="estado-vacio">
                    <span>⚠️</span>

                    <strong>
                        No se pudieron cargar los horarios
                    </strong>

                    <p>
                        ${escaparTexto(error.message)}
                    </p>
                </div>
            `;

        } finally {
            cargandoHorarios.classList.add(
                "oculto"
            );

            listaHorarios.classList.remove(
                "oculto"
            );
        }
    }


    function renderizarHorarios(
        horarios,
        horaRestaurada = ""
    ) {
        listaHorarios.innerHTML = "";

        if (!horarios.length) {
            listaHorarios.innerHTML = `
                <div class="estado-vacio">
                    <span>🚫</span>

                    <strong>
                        No quedan horarios disponibles
                    </strong>

                    <p>
                        Selecciona otra fecha verde.
                    </p>
                </div>
            `;

            return;
        }

        horarios.forEach((hora) => {
            const boton = document.createElement(
                "button"
            );

            boton.type = "button";

            boton.className =
                "boton-horario-reprogramacion";

            boton.dataset.hora = hora;

            boton.textContent = hora;

            boton.addEventListener(
                "click",
                () => seleccionarHora(
                    hora,
                    boton
                )
            );

            listaHorarios.appendChild(
                boton
            );

            if (
                horaRestaurada
                && horaRestaurada.slice(0, 5)
                === hora.slice(0, 5)
            ) {
                seleccionarHora(
                    hora,
                    boton
                );
            }
        });
    }


    function seleccionarHora(
        hora,
        botonSeleccionado
    ) {
        ocultarMensaje();

        campoHora.value = hora;

        document
            .querySelectorAll(
                ".boton-horario-reprogramacion"
            )
            .forEach((boton) => {
                boton.classList.remove(
                    "seleccionado"
                );
            });

        botonSeleccionado.classList.add(
            "seleccionado"
        );

        actualizarResumen();
    }


    botonMesAnterior.addEventListener(
        "click",
        async () => {
            const mesAnterior = new Date(
                mesVisible.getFullYear(),
                mesVisible.getMonth() - 1,
                1
            );

            const mesActual = new Date(
                hoy.getFullYear(),
                hoy.getMonth(),
                1
            );

            if (mesAnterior < mesActual) {
                return;
            }

            mesVisible = mesAnterior;

            campoFecha.value = "";
            campoHora.value = "";

            fechaSeleccionadaTexto.textContent =
                "Selecciona una fecha verde.";

            listaHorarios.innerHTML = `
                <div class="estado-vacio">
                    <span>🕐</span>

                    <strong>
                        Sin fecha seleccionada
                    </strong>

                    <p>
                        Los horarios disponibles aparecerán aquí.
                    </p>
                </div>
            `;

            actualizarResumen();

            await cargarCalendario();
        }
    );


    botonMesSiguiente.addEventListener(
        "click",
        async () => {
            mesVisible = new Date(
                mesVisible.getFullYear(),
                mesVisible.getMonth() + 1,
                1
            );

            campoFecha.value = "";
            campoHora.value = "";

            fechaSeleccionadaTexto.textContent =
                "Selecciona una fecha verde.";

            listaHorarios.innerHTML = `
                <div class="estado-vacio">
                    <span>🕐</span>

                    <strong>
                        Sin fecha seleccionada
                    </strong>

                    <p>
                        Los horarios disponibles aparecerán aquí.
                    </p>
                </div>
            `;

            actualizarResumen();

            await cargarCalendario();
        }
    );


    formulario.addEventListener(
        "submit",
        (evento) => {
            ocultarMensaje();

            if (!campoFecha.value) {
                evento.preventDefault();

                mostrarMensaje(
                    "Selecciona una nueva fecha."
                );

                return;
            }

            if (!campoHora.value) {
                evento.preventDefault();

                mostrarMensaje(
                    "Selecciona un nuevo horario."
                );

                return;
            }

            const mismaFecha =
                campoFecha.value === fechaActual;

            const mismaHora =
                campoHora.value.slice(0, 5)
                === horaActual.slice(0, 5);

            if (mismaFecha && mismaHora) {
                evento.preventDefault();

                mostrarMensaje(
                    "Selecciona una fecha u hora diferente a la actual."
                );

                return;
            }

            const confirmado = window.confirm(
                "¿Confirmas la nueva fecha y hora de la cita?"
            );

            if (!confirmado) {
                evento.preventDefault();
                return;
            }

            botonConfirmar.disabled = true;

            botonConfirmar.textContent =
                "Reprogramando cita...";
        }
    );


    async function iniciar() {
        const fechaCita = fechaDesdeISO(
            fechaActual
        );

        if (
            fechaCita
            && fechaCita >= hoy
        ) {
            mesVisible = new Date(
                fechaCita.getFullYear(),
                fechaCita.getMonth(),
                1
            );
        }

        await cargarCalendario();

        if (
            fechaCita
            && fechaCita >= hoy
        ) {
            await seleccionarFecha(
                fechaActual,
                horaActual
            );
        }

        actualizarResumen();
    }


    iniciar();
});