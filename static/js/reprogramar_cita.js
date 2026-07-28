document.addEventListener("DOMContentLoaded", () => {
    const contenedor = document.getElementById(
        "contenedor-reprogramacion"
    );

    if (!contenedor) {
        return;
    }

    const selectorProfesional = document.getElementById(
        "nuevo-profesional"
    );

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

    const resumenNuevoProfesional = document.getElementById(
        "resumen-nuevo-profesional"
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

    const profesionalActual =
        contenedor.dataset.profesionalActual || "";

    const profesionalSeleccionadoInicial =
        contenedor.dataset.profesionalSeleccionado
        || profesionalActual;

    const fechaActual =
        contenedor.dataset.fechaActual || "";

    const horaActual =
        contenedor.dataset.horaActual || "";

    const fechaSeleccionadaInicial =
        contenedor.dataset.fechaSeleccionada
        || fechaActual;

    const horaSeleccionadaInicial =
        contenedor.dataset.horaSeleccionada
        || horaActual;

    const hoy = new Date();

    hoy.setHours(0, 0, 0, 0);

    let mesVisible = new Date(
        hoy.getFullYear(),
        hoy.getMonth(),
        1
    );

    let solicitudCalendario = null;
    let solicitudHorarios = null;


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

        const texto = new Intl.DateTimeFormat(
            "es-EC",
            {
                weekday: "long",
                day: "numeric",
                month: "long",
                year: "numeric",
            }
        ).format(fecha);

        return (
            texto.charAt(0).toUpperCase()
            + texto.slice(1)
        );
    }


    function obtenerProfesionalSeleccionado() {
        if (!selectorProfesional) {
            return "";
        }

        return selectorProfesional.value;
    }


    function obtenerNombreProfesional() {
        if (
            !selectorProfesional
            || !selectorProfesional.value
        ) {
            return "Sin seleccionar";
        }

        const opcion =
            selectorProfesional.options[
                selectorProfesional.selectedIndex
            ];

        if (!opcion) {
            return "Sin seleccionar";
        }

        return opcion.textContent
            .replace("— Profesional actual", "")
            .replace(/\s+/g, " ")
            .trim();
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
        resumenNuevoProfesional.textContent =
            obtenerNombreProfesional();

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


    function mostrarCalendarioCargando() {
        calendarioDias.innerHTML = `
            <div class="estado-cargando calendario-vacio">
                <span class="cargador"></span>

                <p>
                    Cargando disponibilidad...
                </p>
            </div>
        `;
    }


    function mostrarHorariosVacios() {
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
    }


    function limpiarFechaYHora() {
        campoFecha.value = "";
        campoHora.value = "";

        fechaSeleccionadaTexto.textContent =
            "Selecciona una fecha verde.";

        mostrarHorariosVacios();

        actualizarResumen();
    }


    async function cargarCalendario() {
        ocultarMensaje();

        tituloMes.textContent =
            formatearMes(mesVisible);

        actualizarBotonMesAnterior();

        const profesionalId =
            obtenerProfesionalSeleccionado();

        if (!profesionalId) {
            calendarioDias.innerHTML = `
                <div class="estado-vacio calendario-vacio">
                    <span>👤</span>

                    <strong>
                        Selecciona un profesional
                    </strong>

                    <p>
                        El calendario aparecerá después
                        de seleccionar un profesional.
                    </p>
                </div>
            `;

            return;
        }

        if (solicitudCalendario) {
            solicitudCalendario.abort();
        }

        solicitudCalendario =
            new AbortController();

        mostrarCalendarioCargando();

        try {
            const parametros = new URLSearchParams({
                anio: String(
                    mesVisible.getFullYear()
                ),

                mes: String(
                    mesVisible.getMonth() + 1
                ),

                profesional_id: profesionalId,
            });

            const respuesta = await fetch(
                `${urlDisponibilidad}?${parametros}`,
                {
                    signal:
                        solicitudCalendario.signal,
                }
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
            if (error.name === "AbortError") {
                return;
            }

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

        } finally {
            solicitudCalendario = null;
        }
    }


    function renderizarCalendario(datos) {
        calendarioDias.innerHTML = "";

        for (
            let indice = 0;
            indice < datos.primer_dia_semana;
            indice += 1
        ) {
            const espacio =
                document.createElement("span");

            espacio.className = "dia-vacio";

            calendarioDias.appendChild(
                espacio
            );
        }

        datos.dias.forEach((dia) => {
            const boton =
                document.createElement("button");

            boton.type = "button";

            boton.className =
                `dia-calendario ${dia.estado}`;

            boton.textContent = String(
                dia.dia
            );

            boton.dataset.fecha =
                dia.fecha;

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

        const profesionalId =
            obtenerProfesionalSeleccionado();

        if (!profesionalId) {
            mostrarMensaje(
                "Selecciona primero un profesional."
            );

            return;
        }

        campoFecha.value =
            fechaSeleccionada;

        campoHora.value = "";

        document
            .querySelectorAll(
                ".dia-calendario"
            )
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

        if (solicitudHorarios) {
            solicitudHorarios.abort();
        }

        solicitudHorarios =
            new AbortController();

        try {
            const parametros = new URLSearchParams({
                fecha: fechaSeleccionada,

                profesional_id:
                    profesionalId,
            });

            const respuesta = await fetch(
                `${urlHorarios}?${parametros}`,
                {
                    signal:
                        solicitudHorarios.signal,
                }
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
            if (error.name === "AbortError") {
                return;
            }

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
            solicitudHorarios = null;

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

            campoHora.value = "";

            actualizarResumen();

            return;
        }

        horarios.forEach((hora) => {
            const boton =
                document.createElement("button");

            boton.type = "button";

            boton.className =
                "boton-horario-reprogramacion";

            boton.dataset.hora = hora;

            boton.textContent =
                hora.slice(0, 5);

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

        campoHora.value =
            hora.slice(0, 5);

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


    async function cambiarProfesional() {
        ocultarMensaje();

        limpiarFechaYHora();

        const fechaCita =
            fechaDesdeISO(fechaActual);

        mesVisible = new Date(
            hoy.getFullYear(),
            hoy.getMonth(),
            1
        );

        if (
            selectorProfesional.value
            === profesionalActual
            && fechaCita
            && fechaCita >= hoy
        ) {
            mesVisible = new Date(
                fechaCita.getFullYear(),
                fechaCita.getMonth(),
                1
            );
        }

        actualizarResumen();

        await cargarCalendario();
    }


    selectorProfesional.addEventListener(
        "change",
        cambiarProfesional
    );


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

            limpiarFechaYHora();

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

            limpiarFechaYHora();

            await cargarCalendario();
        }
    );


    formulario.addEventListener(
        "submit",
        (evento) => {
            ocultarMensaje();

            const profesionalId =
                obtenerProfesionalSeleccionado();

            if (!profesionalId) {
                evento.preventDefault();

                mostrarMensaje(
                    "Selecciona un profesional."
                );

                return;
            }

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

            const mismoProfesional =
                profesionalId
                === profesionalActual;

            const mismaFecha =
                campoFecha.value
                === fechaActual;

            const mismaHora =
                campoHora.value.slice(0, 5)
                === horaActual.slice(0, 5);

            if (
                mismoProfesional
                && mismaFecha
                && mismaHora
            ) {
                evento.preventDefault();

                mostrarMensaje(
                    "Selecciona un profesional, fecha u hora diferente."
                );

                return;
            }

            const confirmado = window.confirm(
                (
                    "¿Confirmas la nueva programación "
                    + "de la cita?"
                )
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
        if (
            selectorProfesional
            && profesionalSeleccionadoInicial
        ) {
            selectorProfesional.value =
                profesionalSeleccionadoInicial;
        }

        const fechaSeleccionada =
            fechaDesdeISO(
                fechaSeleccionadaInicial
            );

        if (
            fechaSeleccionada
            && fechaSeleccionada >= hoy
        ) {
            mesVisible = new Date(
                fechaSeleccionada.getFullYear(),
                fechaSeleccionada.getMonth(),
                1
            );
        }

        campoFecha.value =
            fechaSeleccionadaInicial;

        campoHora.value =
            horaSeleccionadaInicial;

        actualizarResumen();

        await cargarCalendario();

        if (
            fechaSeleccionada
            && fechaSeleccionada >= hoy
        ) {
            await seleccionarFecha(
                fechaSeleccionadaInicial,
                horaSeleccionadaInicial
            );

        } else {
            limpiarFechaYHora();
        }
    }


    iniciar();
});